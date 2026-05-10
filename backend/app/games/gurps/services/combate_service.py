"""Regras de negócio — combate GURPS (Arena)."""

import re
from typing import Any, Dict, List, Optional

from app.games.gurps.core.rolagem import (
    avaliar_teste_3d6,
    parse_expressao_dano,
    rolar_dano,
)
from app.games.gurps.models.combate import GurpsCombate
from app.games.gurps.ports import (
    GurpsCombateRepositoryProtocol,
    GurpsPersonagemRepositoryProtocol,
)
from app.games.gurps.schemas.personagem import GurpsPersonagemResponse
from app.repositories.base import commit_with_rollback
from app.shared.exceptions.custom_exceptions import (
    ArenaBaseException,
    CombateJaAtivoError,
    CombateNotFoundError,
)


class GurpsCombateService:
    def __init__(
        self,
        combate_repo: GurpsCombateRepositoryProtocol,
        personagem_repo: GurpsPersonagemRepositoryProtocol,
    ):
        self.combate_repo = combate_repo
        self.personagem_repo = personagem_repo
        self._manobra_default = "fazer_nada"
        self._postura_default = "em_pe"
        self._bonus_esquiva_defesa_total = 2
        self._penalidade_por_defesa_adicional = 1
        self._mods_postura = {
            "em_pe": {"ataque": 0, "defesa": 0, "alvo": 0, "mov_mult": 1.0},
            "agachado": {"ataque": -2, "defesa": -2, "alvo": -2, "mov_mult": 0.5},
            "deitado": {"ataque": -4, "defesa": -3, "alvo": -4, "mov_mult": 0.2},
        }
        self._condicao_default = "normal"

    def _penalidade_cumulativa_defesa(
        self, personagem_id: int, combate: GurpsCombate
    ) -> int:
        qtd_defesas = int((combate.defesas_na_rodada or {}).get(str(personagem_id), 0))
        return max(0, qtd_defesas) * self._penalidade_por_defesa_adicional

    def _mod_postura(self, personagem_id: int, combate: GurpsCombate, eixo: str) -> int:
        postura = (combate.posturas_por_personagem or {}).get(
            str(personagem_id), self._postura_default
        )
        return int(self._mods_postura.get(postura, {}).get(eixo, 0))

    def _movimento_efetivo(
        self, personagem_id: int, deslocamento_base: int, combate: GurpsCombate
    ) -> int:
        postura = (combate.posturas_por_personagem or {}).get(
            str(personagem_id), self._postura_default
        )
        mov_mult = float(self._mods_postura.get(postura, {}).get("mov_mult", 1.0))
        return max(0, int(int(deslocamento_base or 0) * mov_mult))

    def _esquiva_efetiva(
        self, personagem_id: int, esquiva_base: int, combate: GurpsCombate
    ) -> int:
        manobra = (combate.manobras_por_personagem or {}).get(
            str(personagem_id), self._manobra_default
        )
        bonus = self._bonus_esquiva_defesa_total if manobra == "defesa_total" else 0
        mod_postura = self._mod_postura(personagem_id, combate, "defesa")
        penalidade = self._penalidade_cumulativa_defesa(personagem_id, combate)
        return max(0, int(esquiva_base or 0) + bonus + mod_postura - penalidade)

    def _bloqueio_para_int(self, bloqueio: Any) -> int:
        texto = str(bloqueio or "").strip()
        m = re.search(r"-?\d+", texto)
        if not m:
            return 0
        return max(0, int(m.group(0)))

    def _aparar_efetivo(self, personagem: Any, combate: GurpsCombate) -> int:
        base = int(personagem.aparar or 0)
        mod_postura = self._mod_postura(personagem.id, combate, "defesa")
        penalidade = self._penalidade_cumulativa_defesa(personagem.id, combate)
        return max(0, base + mod_postura - penalidade)

    def _bloqueio_efetivo(self, personagem: Any, combate: GurpsCombate) -> int:
        base = self._bloqueio_para_int(personagem.bloqueio)
        mod_postura = self._mod_postura(personagem.id, combate, "defesa")
        penalidade = self._penalidade_cumulativa_defesa(personagem.id, combate)
        return max(0, base + mod_postura - penalidade)

    def _resolver_defesa_ativa(
        self, tipo_defesa: str, personagem: Any, combate: GurpsCombate
    ) -> tuple[str, int]:
        opcoes = {
            "esquiva": self._esquiva_efetiva(
                personagem.id, personagem.esquiva or 0, combate
            ),
            "aparar": self._aparar_efetivo(personagem, combate),
            "bloqueio": self._bloqueio_efetivo(personagem, combate),
        }
        tipo = str(tipo_defesa or "auto").strip().lower()
        if tipo == "auto":
            tipo = max(opcoes.items(), key=lambda kv: kv[1])[0]
        if tipo not in opcoes:
            raise ArenaBaseException("tipo_defesa inválido", status_code=422)
        return tipo, int(opcoes[tipo])

    def _rd_alvo(self, personagem: Any) -> int:
        extras = (
            personagem.extras_json if isinstance(personagem.extras_json, dict) else {}
        )
        candidatos = [
            extras.get("rd"),
            extras.get("armadura_rd"),
            (
                (extras.get("armadura") or {}).get("rd")
                if isinstance(extras.get("armadura"), dict)
                else None
            ),
            (
                ((extras.get("equipamento") or {}).get("armadura") or {}).get("rd")
                if isinstance(extras.get("equipamento"), dict)
                else None
            ),
        ]
        for c in candidatos:
            try:
                return max(0, int(c))
            except (TypeError, ValueError):
                continue
        return 0

    def _condicao_por_pv(self, personagem: Any) -> str:
        pvs_atual = int(personagem.pvs_atual or 0)
        pvs_max = max(1, int(personagem.pvs_valor or 1))
        if pvs_atual <= -pvs_max:
            return "morto"
        if pvs_atual <= 0:
            return "inconsciente"
        return "normal"

    def iniciar_combate(self, personagem_ids: List[int]) -> GurpsCombate:
        if self.combate_repo.existe_combate_ativo():
            raise CombateJaAtivoError(
                "Ja existe um combate GURPS ativo. Finalize-o antes de iniciar outro."
            )

        personagens = self.personagem_repo.get_by_ids(personagem_ids)
        if len(personagens) != len(set(personagem_ids)):
            raise ArenaBaseException(
                "Alguns personagens nao foram encontrados", status_code=404
            )

        ordenados = self.personagem_repo.ordenar_para_turno_gurps(personagens)
        ids_ordenados = [p.id for p in ordenados]

        combate = GurpsCombate(
            personagens_ids=ids_ordenados,
            manobras_por_personagem={
                str(pid): self._manobra_default for pid in ids_ordenados
            },
            posturas_por_personagem={
                str(pid): self._postura_default for pid in ids_ordenados
            },
            condicoes_por_personagem={
                str(pid): self._condicao_default for pid in ids_ordenados
            },
            defesas_na_rodada={},
            turno_atual=0,
            rodada_atual=1,
            ativo=True,
        )
        return self.combate_repo.create(combate)

    def obter_combate_ativo(self) -> Optional[GurpsCombate]:
        return self.combate_repo.get_ativo()

    def montar_status(
        self, combate: Optional[GurpsCombate], incluir_personagens: bool = True
    ) -> Dict[str, Any]:
        if not combate:
            return {
                "ativo": False,
                "message": "Nenhum combate GURPS ativo",
                "resumido": not incluir_personagens,
            }

        payload: Dict[str, Any] = {
            "id": combate.id,
            "personagens_ids": combate.personagens_ids,
            "turno_atual": combate.turno_atual,
            "rodada_atual": combate.rodada_atual,
            "ativo": combate.ativo,
            "personagem_ativo_id": combate.obter_personagem_ativo_id(),
            "manobras_por_personagem": combate.manobras_por_personagem or {},
            "posturas_por_personagem": combate.posturas_por_personagem or {},
            "condicoes_por_personagem": combate.condicoes_por_personagem or {},
            "defesas_na_rodada": combate.defesas_na_rodada or {},
            "manobra_ativa": combate.obter_manobra_ativa() or self._manobra_default,
            "postura_ativa": combate.obter_postura_ativa() or self._postura_default,
            "condicao_ativa": combate.obter_condicao_ativa() or self._condicao_default,
            "resumido": not incluir_personagens,
        }

        if incluir_personagens:
            pers = self.personagem_repo.get_by_ids(list(combate.personagens_ids or []))
            by_id = {p.id: p for p in pers}
            ordenados = [by_id[i] for i in combate.personagens_ids if i in by_id]
            manobras = combate.manobras_por_personagem or {}
            posturas = combate.posturas_por_personagem or {}
            condicoes = combate.condicoes_por_personagem or {}
            personagens_payload: list[dict[str, Any]] = []
            for p in ordenados:
                base = GurpsPersonagemResponse.model_validate(p).model_dump()
                manobra = manobras.get(str(p.id), self._manobra_default)
                postura = posturas.get(str(p.id), self._postura_default)
                esquiva_base = int(base.get("esquiva") or 0)
                deslocamento_base = int(base.get("deslocamento_valor") or 0)
                base["manobra_atual"] = manobra
                base["postura_atual"] = postura
                base["condicao_atual"] = condicoes.get(
                    str(p.id), self._condicao_por_pv(p)
                )
                base["esquiva_efetiva"] = self._esquiva_efetiva(
                    p.id, esquiva_base, combate
                )
                base["deslocamento_efetivo"] = self._movimento_efetivo(
                    p.id, deslocamento_base, combate
                )
                base["mod_ataque_postura"] = self._mod_postura(p.id, combate, "ataque")
                base["mod_alvo_postura"] = self._mod_postura(p.id, combate, "alvo")
                base["defesas_rodada"] = int(
                    (combate.defesas_na_rodada or {}).get(str(p.id), 0)
                )
                personagens_payload.append(base)
            payload["personagens"] = personagens_payload

        return payload

    def obter_status_combate(self, incluir_personagens: bool = True) -> Dict[str, Any]:
        combate = self.obter_combate_ativo()
        return self.montar_status(combate, incluir_personagens=incluir_personagens)

    def avancar_turno(self) -> GurpsCombate:
        combate = self.obter_combate_ativo()
        if not combate:
            raise CombateNotFoundError("Nenhum combate GURPS ativo")
        combate.avancar_turno()
        return self.combate_repo.update(combate)

    def finalizar_combate(self) -> bool:
        combate = self.obter_combate_ativo()
        if not combate:
            raise CombateNotFoundError("Nenhum combate GURPS ativo")
        combate.finalizar()
        self.combate_repo.update(combate)
        return True

    def definir_manobra_ativa(self, manobra: str) -> GurpsCombate:
        combate = self.obter_combate_ativo()
        if not combate:
            raise CombateNotFoundError("Nenhum combate GURPS ativo")
        ativo_id = combate.obter_personagem_ativo_id()
        if ativo_id is None:
            raise CombateNotFoundError("Combate sem personagem ativo")
        condicao_ativa = (combate.condicoes_por_personagem or {}).get(
            str(ativo_id), self._condicao_default
        )
        if condicao_ativa == "atordoado" and manobra != "fazer_nada":
            raise ArenaBaseException(
                "Personagem atordoado só pode usar Fazer Nada",
                status_code=422,
            )
        mapa = dict(combate.manobras_por_personagem or {})
        mapa[str(ativo_id)] = manobra
        combate.manobras_por_personagem = mapa
        if manobra == "fazer_nada" and condicao_ativa == "atordoado":
            mapa_condicoes = dict(combate.condicoes_por_personagem or {})
            mapa_condicoes[str(ativo_id)] = self._condicao_default
            combate.condicoes_por_personagem = mapa_condicoes
        return self.combate_repo.update(combate)

    def definir_postura_ativa(self, postura: str) -> GurpsCombate:
        combate = self.obter_combate_ativo()
        if not combate:
            raise CombateNotFoundError("Nenhum combate GURPS ativo")
        ativo_id = combate.obter_personagem_ativo_id()
        if ativo_id is None:
            raise CombateNotFoundError("Combate sem personagem ativo")
        mapa = dict(combate.posturas_por_personagem or {})
        mapa[str(ativo_id)] = postura
        combate.posturas_por_personagem = mapa
        return self.combate_repo.update(combate)

    def executar_ataque(
        self,
        alvo_id: int,
        nh_ataque: int | None,
        tipo_ataque: str,
        tipo_defesa: str,
        expressao_dano: Optional[str] = None,
        *,
        dados_ataque: Optional[List[int]] = None,
        dados_defesa: Optional[List[int]] = None,
        dados_dano: Optional[List[int]] = None,
    ) -> Dict[str, Any]:
        combate = self.obter_combate_ativo()
        if not combate:
            raise CombateNotFoundError("Nenhum combate GURPS ativo")
        atacante_id = combate.obter_personagem_ativo_id()
        if atacante_id is None:
            raise CombateNotFoundError("Combate sem personagem ativo")
        ids = list(combate.personagens_ids or [])
        if alvo_id not in ids:
            raise ArenaBaseException("Alvo fora do combate", status_code=404)
        if alvo_id == atacante_id:
            raise ArenaBaseException(
                "Alvo não pode ser o próprio atacante", status_code=422
            )

        pers = self.personagem_repo.get_by_ids([atacante_id, alvo_id])
        by_id = {p.id: p for p in pers}
        atacante = by_id.get(atacante_id)
        alvo = by_id.get(alvo_id)
        if atacante is None or alvo is None:
            raise ArenaBaseException("Atacante ou alvo não encontrado", status_code=404)
        if not atacante.esta_consciente():
            raise ArenaBaseException(
                "Atacante inconsciente não pode agir", status_code=422
            )
        if not alvo.esta_consciente():
            raise ArenaBaseException("Alvo já está inconsciente", status_code=422)

        # Registrar escolha de manobra do turno atual no estado do combate.
        mapa_manobras = dict(combate.manobras_por_personagem or {})
        mapa_manobras[str(atacante_id)] = "ataque"
        combate.manobras_por_personagem = mapa_manobras
        self.combate_repo.update(combate)

        tipo = str(tipo_ataque or "arma").strip().lower()
        if tipo not in {"arma", "soco", "chute"}:
            raise ArenaBaseException("tipo_ataque inválido", status_code=422)

        nh_base = (
            int(nh_ataque) if nh_ataque is not None else int(atacante.dx_valor or 10)
        )
        if tipo == "chute":
            nh_base -= 2
        nh_ataque_efetivo = (
            int(nh_base)
            + self._mod_postura(atacante_id, combate, "ataque")
            + self._mod_postura(alvo_id, combate, "alvo")
        )
        teste_ataque = avaliar_teste_3d6(nh_ataque_efetivo, dados=dados_ataque)
        if not teste_ataque.sucesso:
            return {
                "atacante_id": atacante_id,
                "alvo_id": alvo_id,
                "nh_ataque": nh_base,
                "nh_ataque_efetivo": nh_ataque_efetivo,
                "tipo_ataque": tipo,
                "ataque": {
                    "total": teste_ataque.total,
                    "dados": teste_ataque.dados,
                    "sucesso": False,
                    "margem": teste_ataque.margem,
                    "sucesso_decisivo": teste_ataque.sucesso_decisivo,
                    "falha_critica": teste_ataque.falha_critica,
                },
                "defesa": None,
                "dano": None,
                "pvs_alvo_antes": alvo.pvs_atual,
                "pvs_alvo_depois": alvo.pvs_atual,
            }

        defesa_tipo, defesa_valor = self._resolver_defesa_ativa(
            tipo_defesa, alvo, combate
        )
        teste_defesa = avaliar_teste_3d6(defesa_valor, dados=dados_defesa)
        mapa_defesas = dict(combate.defesas_na_rodada or {})
        mapa_defesas[str(alvo.id)] = int(mapa_defesas.get(str(alvo.id), 0)) + 1
        combate.defesas_na_rodada = mapa_defesas
        self.combate_repo.update(combate)
        if teste_defesa.sucesso:
            return {
                "atacante_id": atacante_id,
                "alvo_id": alvo_id,
                "nh_ataque": nh_base,
                "nh_ataque_efetivo": nh_ataque_efetivo,
                "tipo_ataque": tipo,
                "ataque": {
                    "total": teste_ataque.total,
                    "dados": teste_ataque.dados,
                    "sucesso": True,
                    "margem": teste_ataque.margem,
                    "sucesso_decisivo": teste_ataque.sucesso_decisivo,
                    "falha_critica": teste_ataque.falha_critica,
                },
                "defesa": {
                    "tipo": defesa_tipo,
                    "valor_efetivo": defesa_valor,
                    "esquiva_efetiva": (
                        defesa_valor if defesa_tipo == "esquiva" else None
                    ),
                    "total": teste_defesa.total,
                    "dados": teste_defesa.dados,
                    "sucesso": True,
                    "margem": teste_defesa.margem,
                },
                "dano": None,
                "pvs_alvo_antes": alvo.pvs_atual,
                "pvs_alvo_depois": alvo.pvs_atual,
            }

        expr = (expressao_dano or atacante.dano_impacto or "1d").strip()
        if expressao_dano is None and tipo in {"soco", "chute"}:
            try:
                parsed = parse_expressao_dano(expr)
                mod = parsed.modificador - 1 if tipo == "soco" else parsed.modificador
                sinal = f"+{mod}" if mod >= 0 else str(mod)
                expr = (
                    f"{parsed.quantidade_dados}d{sinal}"
                    if mod != 0
                    else f"{parsed.quantidade_dados}d"
                )
            except ValueError:
                # fallback seguro para casos legados de dano_impacto fora do formato Nd+M
                expr = "1d-1" if tipo == "soco" else "1d"
        try:
            dano = rolar_dano(expr, dados_forcados=dados_dano)
        except ValueError as e:
            raise ArenaBaseException(str(e), status_code=422) from e
        rd = self._rd_alvo(alvo)
        dano_bruto = int(dano.total)
        dano_liquido = max(0, dano_bruto - rd)
        pvs_antes = int(alvo.pvs_atual or 0)
        pvs_virtual = pvs_antes - dano_liquido
        pvs_depois = max(0, pvs_virtual)
        alvo.pvs_atual = pvs_depois
        pvs_max_alvo = max(1, int(alvo.pvs_valor or 1))
        if dano_liquido <= 0:
            condicao_alvo = self._condicao_default
        elif pvs_virtual <= -pvs_max_alvo:
            condicao_alvo = "morto"
        elif pvs_virtual <= 0:
            condicao_alvo = "inconsciente"
        else:
            condicao_alvo = "atordoado"
        mapa_condicoes = dict(combate.condicoes_por_personagem or {})
        mapa_condicoes[str(alvo.id)] = condicao_alvo
        combate.condicoes_por_personagem = mapa_condicoes
        self.combate_repo.update(combate)
        self.personagem_repo.db.add(alvo)
        commit_with_rollback(self.personagem_repo.db)

        return {
            "atacante_id": atacante_id,
            "alvo_id": alvo_id,
            "nh_ataque": nh_base,
            "nh_ataque_efetivo": nh_ataque_efetivo,
            "tipo_ataque": tipo,
            "ataque": {
                "total": teste_ataque.total,
                "dados": teste_ataque.dados,
                "sucesso": True,
                "margem": teste_ataque.margem,
                "sucesso_decisivo": teste_ataque.sucesso_decisivo,
                "falha_critica": teste_ataque.falha_critica,
            },
            "defesa": {
                "tipo": defesa_tipo,
                "valor_efetivo": defesa_valor,
                "esquiva_efetiva": defesa_valor if defesa_tipo == "esquiva" else None,
                "total": teste_defesa.total,
                "dados": teste_defesa.dados,
                "sucesso": False,
                "margem": teste_defesa.margem,
            },
            "dano": {
                "expressao": dano.expressao,
                "dados_rolados": dano.dados_rolados,
                "modificador": dano.modificador,
                "total_bruto": dano_bruto,
                "rd_aplicada": rd,
                "total_liquido": dano_liquido,
                "total": dano_liquido,
            },
            "pvs_alvo_antes": pvs_antes,
            "pvs_alvo_depois": pvs_depois,
            "condicao_alvo": condicao_alvo,
        }

    def ajustar_pv_alvo(self, alvo_id: int, delta_pv: int) -> Dict[str, Any]:
        combate = self.obter_combate_ativo()
        if not combate:
            raise CombateNotFoundError("Nenhum combate GURPS ativo")
        ids = list(combate.personagens_ids or [])
        if alvo_id not in ids:
            raise ArenaBaseException("Alvo fora do combate", status_code=404)

        alvo = self.personagem_repo.get_by_id(alvo_id)
        if alvo is None:
            raise ArenaBaseException("Alvo não encontrado", status_code=404)

        pvs_antes = int(alvo.pvs_atual or 0)
        pvs_max = int(alvo.pvs_valor or pvs_antes)
        pvs_depois = max(0, min(pvs_max, pvs_antes + int(delta_pv)))
        alvo.pvs_atual = pvs_depois
        self.personagem_repo.db.add(alvo)
        commit_with_rollback(self.personagem_repo.db)
        return {
            "alvo_id": alvo_id,
            "delta_pv": int(delta_pv),
            "pvs_alvo_antes": pvs_antes,
            "pvs_alvo_depois": pvs_depois,
            "pvs_alvo_max": pvs_max,
        }

    def aplicar_esforco_ativo(
        self,
        *,
        custo_fadiga: int = 1,
        usar_surto: bool = False,
        descricao: Optional[str] = None,
    ) -> Dict[str, Any]:
        combate = self.obter_combate_ativo()
        if not combate:
            raise CombateNotFoundError("Nenhum combate GURPS ativo")
        ativo_id = combate.obter_personagem_ativo_id()
        if ativo_id is None:
            raise CombateNotFoundError("Combate sem personagem ativo")
        personagem = self.personagem_repo.get_by_id(ativo_id)
        if personagem is None:
            raise ArenaBaseException("Personagem ativo não encontrado", status_code=404)

        fadiga_antes = int(personagem.fadiga_atual or 0)
        if fadiga_antes <= 0:
            raise ArenaBaseException(
                "Sem fadiga disponível para esforço", status_code=422
            )

        custo = max(1, int(custo_fadiga))
        fadiga_depois = max(0, fadiga_antes - custo)
        personagem.fadiga_atual = fadiga_depois
        self.personagem_repo.db.add(personagem)
        commit_with_rollback(self.personagem_repo.db)
        return {
            "personagem_id": ativo_id,
            "usar_surto": bool(usar_surto),
            "descricao": (descricao or "").strip() or None,
            "custo_fadiga": custo,
            "fadiga_antes": fadiga_antes,
            "fadiga_depois": fadiga_depois,
            "fadiga_max": int(personagem.fadiga_valor or fadiga_antes),
        }
