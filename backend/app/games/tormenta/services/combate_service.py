"""Regras de negócio — combate Tormenta 20 (Arena)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.games.tormenta.models.combate import TormentaCombate
from app.games.tormenta.models.personagem import TormentaPersonagem
from app.games.tormenta.repositories.combate_repository import TormentaCombateRepository
from app.games.tormenta.repositories.personagem_repository import (
    TormentaPersonagemRepository,
)
from app.games.tormenta.schemas.combate import TormentaCombateCondicaoMbItem
from app.games.tormenta.schemas.personagem import TormentaPersonagemResponse
from app.shared.exceptions.custom_exceptions import (
    ArenaBaseException,
    CombateJaAtivoError,
    CombateNotFoundError,
    DadosInvalidos,
)


class TormentaCombateService:
    def __init__(
        self,
        combate_repo: TormentaCombateRepository,
        personagem_repo: TormentaPersonagemRepository,
        usuario_id: int,
    ):
        self.combate_repo = combate_repo
        self.personagem_repo = personagem_repo
        self.usuario_id = usuario_id

    @staticmethod
    def _ordenar_para_arena(
        personagens: List[TormentaPersonagem],
    ) -> List[TormentaPersonagem]:
        def chave(p: TormentaPersonagem) -> tuple:
            ini = int(p.iniciativa) if p.iniciativa is not None else 0
            nome = (p.nome or "").lower()
            return (-ini, nome)

        return sorted(personagens, key=chave)

    def obter_combate_ativo(self) -> Optional[TormentaCombate]:
        return self.combate_repo.get_ativo_por_usuario(self.usuario_id)

    def montar_status(
        self, combate: Optional[TormentaCombate], incluir_personagens: bool = True
    ) -> Dict[str, Any]:
        if not combate or not combate.ativo:
            return {
                "ativo": False,
                "message": "Nenhum combate Tormenta ativo",
                "resumido": not incluir_personagens,
            }

        raw_cond = combate.condicoes_mb_json
        cond_map: Dict[str, Any] = raw_cond if isinstance(raw_cond, dict) else {}

        payload: Dict[str, Any] = {
            "id": combate.id,
            "usuario_id": combate.usuario_id,
            "personagens_ids": combate.personagens_ids,
            "turno_atual": combate.turno_atual,
            "rodada_atual": combate.rodada_atual,
            "ativo": combate.ativo,
            "personagem_ativo_id": combate.obter_personagem_ativo_id(),
            "resumido": not incluir_personagens,
            "condicoes_mb": cond_map,
        }

        if incluir_personagens:
            pers = self.personagem_repo.get_by_ids(list(combate.personagens_ids or []))
            by_id = {p.id: p for p in pers}
            ordenados = [by_id[i] for i in combate.personagens_ids if i in by_id]
            payload["personagens"] = [
                TormentaPersonagemResponse.model_validate(p).model_dump()
                for p in ordenados
            ]

        return payload

    def obter_status_combate(self, incluir_personagens: bool = True) -> Dict[str, Any]:
        combate = self.obter_combate_ativo()
        return self.montar_status(combate, incluir_personagens=incluir_personagens)

    def iniciar_combate(self, personagem_ids: List[int]) -> TormentaCombate:
        if self.combate_repo.existe_combate_ativo_por_usuario(self.usuario_id):
            raise CombateJaAtivoError(
                "Ja existe um combate Tormenta ativo para sua conta. Encerre-o antes de iniciar outro."
            )

        ids_unicos = list(dict.fromkeys(personagem_ids))
        personagens = self.personagem_repo.get_by_ids(ids_unicos)
        if len(personagens) != len(ids_unicos):
            raise ArenaBaseException(
                "Alguns personagens nao foram encontrados", status_code=404
            )

        ordenados = self._ordenar_para_arena(personagens)
        ids_ordenados = [p.id for p in ordenados]

        combate = TormentaCombate(
            usuario_id=self.usuario_id,
            personagens_ids=ids_ordenados,
            turno_atual=0,
            rodada_atual=1,
            ativo=True,
            condicoes_mb_json={},
        )
        return self.combate_repo.create(combate)

    def avancar_turno(self) -> TormentaCombate:
        combate = self.obter_combate_ativo()
        if not combate:
            raise CombateNotFoundError("Nenhum combate Tormenta ativo")
        combate.avancar_turno()
        return self.combate_repo.update(combate)

    def finalizar_combate(self) -> bool:
        combate = self.obter_combate_ativo()
        if not combate:
            raise CombateNotFoundError("Nenhum combate Tormenta ativo")
        combate.finalizar()
        self.combate_repo.update(combate)
        return True

    def aplicar_condicoes_mb(
        self, por_personagem: Dict[str, TormentaCombateCondicaoMbItem]
    ) -> TormentaCombate:
        combate = self.obter_combate_ativo()
        if not combate:
            raise CombateNotFoundError("Nenhum combate Tormenta ativo")
        permitidos = {int(x) for x in (combate.personagens_ids or [])}
        atual: Dict[str, Any] = {}
        raw = combate.condicoes_mb_json
        if isinstance(raw, dict):
            atual = {str(k): v for k, v in raw.items()}

        for k, item in por_personagem.items():
            try:
                pid = int(str(k).strip())
            except (TypeError, ValueError) as exc:
                raise DadosInvalidos(f"Id de personagem invalido: {k}") from exc
            if pid not in permitidos:
                raise DadosInvalidos("Personagem nao participa deste combate")
            rotulos = list(item.rotulos)
            tips = list(item.tips)
            if not rotulos and not tips:
                atual.pop(str(pid), None)
            else:
                atual[str(pid)] = {"rotulos": rotulos, "tips": tips}

        combate.condicoes_mb_json = atual
        return self.combate_repo.update(combate)

    def _exigir_combate_ativo(self) -> TormentaCombate:
        combate = self.obter_combate_ativo()
        if not combate:
            raise CombateNotFoundError("Nenhum combate Tormenta ativo")
        return combate

    def _personagem_no_combate(
        self, combate: TormentaCombate, pid: int
    ) -> TormentaPersonagem:
        permitidos = {int(x) for x in (combate.personagens_ids or [])}
        if pid not in permitidos:
            raise DadosInvalidos("Personagem nao participa deste combate")
        p = self.personagem_repo.get_by_id(pid)
        if not p:
            raise ArenaBaseException("Personagem nao encontrado", status_code=404)
        return p

    def _mods_condicoes_personagem(
        self, combate: TormentaCombate, pid: int
    ) -> Dict[str, int]:
        from app.games.tormenta.rules.combate_t20 import modificadores_de_condicoes_mb

        raw = (
            combate.condicoes_mb_json
            if isinstance(combate.condicoes_mb_json, dict)
            else {}
        )
        entry = raw.get(str(pid)) or {}
        rotulos = entry.get("rotulos") if isinstance(entry, dict) else []
        if not isinstance(rotulos, list):
            rotulos = []
        return modificadores_de_condicoes_mb([str(x) for x in rotulos])

    def rolar_iniciativa_combate(self, personagem_ids: List[int]) -> Dict[str, Any]:
        from app.games.tormenta.rules.atributos_t20 import contribuicao_atributo_t20
        from app.games.tormenta.rules.combate_t20 import rolar_iniciativa
        from app.games.tormenta.rules.regra_versao_t20 import regra_versao_de_ficha

        combate = self._exigir_combate_ativo()
        resultados: List[Dict[str, Any]] = []
        for pid in personagem_ids:
            p = self._personagem_no_combate(combate, int(pid))
            rv = regra_versao_de_ficha(p.ficha_json)
            des_mod = contribuicao_atributo_t20(int(p.des_valor or 10), rv)
            roll = rolar_iniciativa(des_mod)
            p.iniciativa = int(roll["total"])
            self.personagem_repo.update(p)
            resultados.append(
                {
                    "personagem_id": p.id,
                    "nome": p.nome,
                    **roll,
                }
            )
        resultados.sort(key=lambda x: (-x["total"], (x.get("nome") or "").lower()))
        ordenados = [r["personagem_id"] for r in resultados]
        combate.personagens_ids = ordenados
        combate.turno_atual = 0
        self.combate_repo.update(combate)
        return {"resultados": resultados, "ordem": ordenados}

    def rolar_ataque_combate(
        self,
        atacante_id: int,
        alvo_id: int,
        bab: int,
        mod_atributo: int,
        bonus_arma: int = 0,
        penalidades: int = 0,
        ca_alvo: Optional[int] = None,
    ) -> Dict[str, Any]:
        from app.games.tormenta.rules.combate_t20 import rolar_ataque

        combate = self._exigir_combate_ativo()
        atacante = self._personagem_no_combate(combate, atacante_id)
        alvo = self._personagem_no_combate(combate, alvo_id)
        ca = int(ca_alvo if ca_alvo is not None else (alvo.ca or 10))
        mods = self._mods_condicoes_personagem(combate, atacante_id)
        roll = rolar_ataque(
            bab,
            mod_atributo,
            bonus_arma=bonus_arma,
            penalidades=penalidades,
            modificador_condicoes=mods.get("ataque", 0),
            ca_alvo=ca,
        )
        return {
            "atacante_id": atacante_id,
            "alvo_id": alvo_id,
            "atacante_nome": atacante.nome,
            "alvo_nome": alvo.nome,
            "modificador_condicoes_ataque": mods.get("ataque", 0),
            **roll,
        }

    def rolar_dano_combate(
        self,
        formula_dano: str,
        mod_atributo: int = 0,
        confirmar_critico: bool = False,
        aplicar_ao_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        from app.games.tormenta.rules.combate_t20 import rolar_dano
        from app.games.tormenta.rules.conjuracao_combate_t20 import (
            processar_concentracao_apos_dano_mb,
        )

        combate = self._exigir_combate_ativo()
        roll = rolar_dano(
            formula_dano,
            mod_atributo,
            confirmar_critico=confirmar_critico,
        )
        out: Dict[str, Any] = dict(roll)
        if aplicar_ao_id is not None:
            alvo = self._personagem_no_combate(combate, int(aplicar_ao_id))
            pv = int(alvo.pv_atual or 0)
            dano = int(roll["dano"])
            alvo.pv_atual = max(0, pv - dano)
            conc = processar_concentracao_apos_dano_mb(
                alvo.ficha_json if isinstance(alvo.ficha_json, dict) else {},
                dano=dano,
                con_valor=int(alvo.con_valor or 10),
                nivel=int(alvo.nivel or 1),
                fort_total=int(alvo.fort_total or 0),
            )
            if conc.get("tinha_concentracao"):
                alvo.ficha_json = conc.get("ficha_json") or {}
                out["concentracao"] = {
                    "tinha_concentracao": True,
                    "perdida": bool(conc.get("concentracao_perdida")),
                    "magia_anterior": conc.get("concentracao_anterior"),
                    "teste": conc.get("teste"),
                }
            self.personagem_repo.update(alvo)
            out["alvo_id"] = alvo.id
            out["alvo_nome"] = alvo.nome
            out["pv_antes"] = pv
            out["pv_depois"] = int(alvo.pv_atual or 0)
        return out

    def testar_resistencia_magia_combate(
        self,
        *,
        alvo_id: int,
        tipo: str,
        cd: Optional[int] = None,
        circulo_magia: Optional[int] = None,
        conjurador_id: Optional[int] = None,
        magia_slug: Optional[str] = None,
        falha_voluntaria: bool = False,
    ) -> Dict[str, Any]:
        from app.games.tormenta.rules.catalogo_t20 import metadados_magia_mb_por_slug
        from app.games.tormenta.rules.conjuracao_combate_t20 import (
            bonus_resistencia_magia_efetivo_mb,
            cd_teste_resistencia_magia_mb,
            inferir_tipo_resistencia_mb,
            mod_habilidade_chave_conjurador_mb,
            normalizar_tipo_resistencia_request,
            rolar_teste_resistencia_magia_mb,
        )

        combate = self._exigir_combate_ativo()
        alvo = self._personagem_no_combate(combate, int(alvo_id))

        tipo_res: Optional[str] = None
        if tipo:
            tipo_res = normalizar_tipo_resistencia_request(tipo)
        if not tipo_res and magia_slug:
            meta = metadados_magia_mb_por_slug(magia_slug)
            tipo_res = inferir_tipo_resistencia_mb((meta or {}).get("resistencia"))
        if not tipo_res:
            raise DadosInvalidos(
                "Informe tipo (fortitude/reflexos/vontade) ou magia_slug com teste no catálogo"
            )

        cd_final: Optional[int] = int(cd) if cd is not None else None
        circ = circulo_magia
        conj_nome: Optional[str] = None

        if cd_final is None:
            if circ is None and magia_slug:
                meta = metadados_magia_mb_por_slug(magia_slug)
                if meta:
                    circ = int(meta.get("circulo", 0) or 0)
            if circ is None:
                raise DadosInvalidos(
                    "Informe cd ou circulo_magia (ou magia_slug com círculo no catálogo)"
                )
            if conjurador_id is None:
                raise DadosInvalidos(
                    "Informe conjurador_id para calcular CD (10 + círculo + mod. chave)"
                )
            conj = self._personagem_no_combate(combate, int(conjurador_id))
            conj_nome = conj.nome
            fj_conj = conj.ficha_json if isinstance(conj.ficha_json, dict) else {}
            classe = str(fj_conj.get("tormenta_classe_mb_slug") or "").strip().lower()
            mod_chave = mod_habilidade_chave_conjurador_mb(
                classe_slug=classe,
                int_valor=int(conj.int_valor or 10),
                sab_valor=int(conj.sab_valor or 10),
                car_valor=int(conj.car_valor or 10),
            )
            cd_final = cd_teste_resistencia_magia_mb(int(circ), mod_chave)

        fj = alvo.ficha_json if isinstance(alvo.ficha_json, dict) else {}
        bonus_rm = bonus_resistencia_magia_efetivo_mb(fj)

        if falha_voluntaria:
            return {
                "alvo_id": alvo.id,
                "alvo_nome": alvo.nome,
                "conjurador_id": conjurador_id,
                "conjurador_nome": conj_nome,
                "tipo": tipo_res,
                "cd": cd_final,
                "falha_voluntaria": True,
                "passou": False,
                "bonus_base": (
                    int(alvo.fort_total or 0)
                    if tipo_res == "fortitude"
                    else (
                        int(alvo.ref_total or 0)
                        if tipo_res == "reflexos"
                        else int(alvo.von_total or 0)
                    )
                ),
                "bonus_resistencia_magia": bonus_rm,
                "bonus_total": 0,
                "d20": None,
                "total": None,
                "margem": None,
                "sucesso": False,
            }

        teste = rolar_teste_resistencia_magia_mb(
            tipo=tipo_res,
            fort_total=int(alvo.fort_total or 0),
            ref_total=int(alvo.ref_total or 0),
            von_total=int(alvo.von_total or 0),
            bonus_rm=bonus_rm,
            cd=int(cd_final),
        )
        return {
            "alvo_id": alvo.id,
            "alvo_nome": alvo.nome,
            "conjurador_id": conjurador_id,
            "conjurador_nome": conj_nome,
            "magia_slug": magia_slug,
            "circulo_magia": circ,
            "falha_voluntaria": False,
            **teste,
        }
