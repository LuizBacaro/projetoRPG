"""Regras de negócio — personagens GURPS."""

from __future__ import annotations

from decimal import Decimal, ROUND_FLOOR
from typing import List, Optional

from app.games.gurps.core.dano_st import dano_thr_sw_por_st
from app.games.gurps.core.pericias_lite import (
    listar_pericias_lite,
    validar_pre_requisitos_lite,
)
from app.games.gurps.models.personagem import (
    GurpsPersonagem,
    GurpsPersonagemDesvantagem,
    GurpsPersonagemPericia,
    GurpsPersonagemVantagem,
)
from app.games.gurps.ports import GurpsPersonagemRepositoryProtocol
from app.games.gurps.schemas.personagem import (
    GurpsPersonagemCreate,
    GurpsPersonagemResponse,
    GurpsPersonagemUpdate,
    normalizar_extras_para_gravacao,
)
from app.repositories.base import commit_with_rollback
from app.shared.exceptions.custom_exceptions import ArenaBaseException, DadosInvalidos
from app.shared.models.usuario import PerfilUsuario, Usuario


class GurpsPersonagemService:
    def __init__(self, repo: GurpsPersonagemRepositoryProtocol):
        self.repo = repo

    @staticmethod
    def _tipos_validos() -> set:
        return {"jogador", "monstro", "npc"}

    def _resolver_dono(self, usuario: Usuario, tipo: str) -> Optional[int]:
        t = (tipo or "").lower()
        if usuario.perfil in (
            PerfilUsuario.ADMINISTRADOR,
            PerfilUsuario.MESTRE,
        ):
            if t in ("monstro", "npc"):
                return None
        return usuario.id

    def _validar_tipo(self, tipo: str) -> None:
        if (tipo or "").lower() not in self._tipos_validos():
            raise DadosInvalidos("tipo deve ser jogador, monstro ou npc")

    def catalogo_pericias_lite(self) -> List[dict]:
        return listar_pericias_lite()

    def _validar_pre_requisitos_pericias(self, *, pericias: List[dict], st: int, dx: int, iq: int, ht: int, per: int) -> None:
        erros = validar_pre_requisitos_lite(
            pericias=pericias,
            st_valor=st,
            dx_valor=dx,
            iq_valor=iq,
            ht_valor=ht,
            percepcao_valor=per,
        )
        if erros:
            raise DadosInvalidos("; ".join(erros))

    @staticmethod
    def _calcular_velocidade_basica(ht_valor: int, dx_valor: int) -> Decimal:
        return (Decimal(ht_valor) + Decimal(dx_valor)) / Decimal("4")

    @staticmethod
    def _calcular_deslocamento_basico(velocidade_valor: Decimal) -> int:
        return int(velocidade_valor.to_integral_value(rounding=ROUND_FLOOR))

    @staticmethod
    def _calcular_esquiva_basica(velocidade_valor: Decimal) -> int:
        # GURPS Lite: Esquiva = parte inteira da VB + 3.
        return int(velocidade_valor.to_integral_value(rounding=ROUND_FLOOR)) + 3

    def listar_todos(
        self,
        tipo: Optional[str],
        *,
        usuario: Usuario,
        skip: int = 0,
        limit: int = 100,
        apenas_meus: bool = False,
    ) -> List[GurpsPersonagemResponse]:
        # Jogador: apenas personagens próprios (paridade com D&D 3.5).
        if usuario.perfil == PerfilUsuario.JOGADOR:
            if tipo:
                rows = self.repo.get_by_owner_and_tipo(
                    usuario.id, tipo, skip=skip, limit=limit
                )
            else:
                rows = self.repo.get_by_owner(usuario.id, skip=skip, limit=limit)
            return [GurpsPersonagemResponse.model_validate(r) for r in rows]

        if apenas_meus:
            if tipo:
                rows = self.repo.get_by_owner_and_tipo(
                    usuario.id, tipo, skip=skip, limit=limit
                )
            else:
                rows = self.repo.get_by_owner(usuario.id, skip=skip, limit=limit)
            return [GurpsPersonagemResponse.model_validate(r) for r in rows]

        if tipo:
            rows = self.repo.get_by_tipo(tipo, skip=skip, limit=limit)
        else:
            rows = self.repo.get_all(skip=skip, limit=limit)
        return [GurpsPersonagemResponse.model_validate(r) for r in rows]

    def contar_todos(
        self,
        tipo: Optional[str],
        *,
        usuario: Usuario,
        apenas_meus: bool = False,
    ) -> int:
        if usuario.perfil == PerfilUsuario.JOGADOR:
            if tipo:
                return self.repo.count_by_owner_and_tipo(usuario.id, tipo)
            return self.repo.count_by_owner(usuario.id)

        if apenas_meus:
            if tipo:
                return self.repo.count_by_owner_and_tipo(usuario.id, tipo)
            return self.repo.count_by_owner(usuario.id)

        if tipo:
            return self.repo.count_by_tipo(tipo)
        return self.repo.count_all()

    def obter_por_id(self, personagem_id: int) -> GurpsPersonagem:
        p = self.repo.get_by_id(personagem_id)
        if not p:
            raise ArenaBaseException("Personagem nao encontrado", status_code=404)
        return p

    def criar(self, usuario: Usuario, payload: GurpsPersonagemCreate) -> GurpsPersonagemResponse:
        self._validar_tipo(payload.tipo)
        if usuario.perfil == PerfilUsuario.JOGADOR and payload.tipo.lower() != "jogador":
            raise DadosInvalidos("Jogadores so podem criar fichas do tipo jogador")
        nome = (payload.nome or "").strip()
        if not nome:
            raise DadosInvalidos("Nome e obrigatorio")

        pvs_valor = payload.pvs_valor
        if "pvs_valor" not in payload.model_fields_set:
            pvs_valor = payload.st_valor
        fadiga_valor = payload.fadiga_valor
        if "fadiga_valor" not in payload.model_fields_set:
            fadiga_valor = payload.ht_valor
        vontade_valor = payload.vontade_valor
        if "vontade_valor" not in payload.model_fields_set:
            vontade_valor = payload.iq_valor
        percepcao_valor = payload.percepcao_valor
        if "percepcao_valor" not in payload.model_fields_set:
            percepcao_valor = payload.iq_valor

        pvs_atual = payload.pvs_atual if payload.pvs_atual is not None else pvs_valor
        fadiga_atual = payload.fadiga_atual if payload.fadiga_atual is not None else fadiga_valor

        velocidade_valor = payload.velocidade_valor
        if "velocidade_valor" not in payload.model_fields_set:
            velocidade_valor = self._calcular_velocidade_basica(payload.ht_valor, payload.dx_valor)
        deslocamento_valor = payload.deslocamento_valor
        if "deslocamento_valor" not in payload.model_fields_set:
            deslocamento_valor = self._calcular_deslocamento_basico(velocidade_valor)
        esquiva_valor = payload.esquiva
        if "esquiva" not in payload.model_fields_set:
            esquiva_valor = self._calcular_esquiva_basica(velocidade_valor)
        dano_impacto = payload.dano_impacto
        dano_balanco = payload.dano_balanco
        if "dano_impacto" not in payload.model_fields_set or "dano_balanco" not in payload.model_fields_set:
            thr, sw = dano_thr_sw_por_st(payload.st_valor)
            if "dano_impacto" not in payload.model_fields_set:
                dano_impacto = thr
            if "dano_balanco" not in payload.model_fields_set:
                dano_balanco = sw
        self._validar_pre_requisitos_pericias(
            pericias=[s.model_dump() for s in (payload.pericias or [])],
            st=payload.st_valor,
            dx=payload.dx_valor,
            iq=payload.iq_valor,
            ht=payload.ht_valor,
            per=percepcao_valor,
        )

        ent = GurpsPersonagem(
            dono_id=self._resolver_dono(usuario, payload.tipo),
            campanha_id=payload.campanha_id,
            tipo=payload.tipo.lower(),
            nome=nome,
            conceito=payload.conceito or "",
            reacao=payload.reacao or "",
            idade=payload.idade or "",
            iniciativa=payload.iniciativa,
            st_custo=payload.st_custo,
            st_valor=payload.st_valor,
            dx_custo=payload.dx_custo,
            dx_valor=payload.dx_valor,
            iq_custo=payload.iq_custo,
            iq_valor=payload.iq_valor,
            ht_custo=payload.ht_custo,
            ht_valor=payload.ht_valor,
            vontade_custo=payload.vontade_custo,
            vontade_valor=vontade_valor,
            percepcao_custo=payload.percepcao_custo,
            percepcao_valor=percepcao_valor,
            pvs_custo=payload.pvs_custo,
            pvs_valor=pvs_valor,
            pvs_atual=pvs_atual,
            fadiga_custo=payload.fadiga_custo,
            fadiga_valor=fadiga_valor,
            fadiga_atual=fadiga_atual,
            velocidade_custo=payload.velocidade_custo,
            velocidade_valor=velocidade_valor,
            deslocamento_custo=payload.deslocamento_custo,
            deslocamento_valor=deslocamento_valor,
            esquiva=esquiva_valor,
            aparar=payload.aparar,
            bloqueio=payload.bloqueio,
            dano_impacto=dano_impacto or "",
            dano_balanco=dano_balanco or "",
            pontos_atributos=payload.pontos_atributos,
            pontos_vantagens=payload.pontos_vantagens,
            pontos_desvantagens=payload.pontos_desvantagens,
            pontos_pericias=payload.pontos_pericias,
            pontos_total=payload.pontos_total,
            extras_json=normalizar_extras_para_gravacao(
                payload.extras if isinstance(payload.extras, dict) else {}
            ),
        )
        for v in payload.vantagens or []:
            ent.vantagens.append(
                GurpsPersonagemVantagem(nome=v.nome.strip(), custo=v.custo)
            )
        for d in payload.desvantagens or []:
            ent.desvantagens.append(
                GurpsPersonagemDesvantagem(nome=d.nome.strip(), custo=d.custo)
            )
        for s in payload.pericias or []:
            ent.pericias.append(
                GurpsPersonagemPericia(
                    nome=s.nome.strip(),
                    tipo=s.tipo.strip(),
                    nh=s.nh,
                    custo=s.custo,
                )
            )

        self.repo.db.add(ent)
        commit_with_rollback(self.repo.db)
        self.repo.db.refresh(ent)
        return GurpsPersonagemResponse.model_validate(ent)

    def atualizar(
        self, personagem_id: int, payload: GurpsPersonagemUpdate
    ) -> GurpsPersonagemResponse:
        ent = self.obter_por_id(personagem_id)
        data = payload.model_dump(exclude_unset=True)
        campos_enviados = set(payload.model_fields_set)
        list_v = data.pop("vantagens", None)
        list_d = data.pop("desvantagens", None)
        list_p = data.pop("pericias", None)
        extras = data.pop("extras", None)

        for key, val in data.items():
            setattr(ent, key, val)

        if "velocidade_valor" not in campos_enviados and (
            "ht_valor" in campos_enviados or "dx_valor" in campos_enviados
        ):
            nova_vb = self._calcular_velocidade_basica(ent.ht_valor or 0, ent.dx_valor or 0)
            ent.velocidade_valor = nova_vb
            if "deslocamento_valor" not in campos_enviados:
                ent.deslocamento_valor = self._calcular_deslocamento_basico(nova_vb)
            if "esquiva" not in campos_enviados:
                ent.esquiva = self._calcular_esquiva_basica(nova_vb)

        if "velocidade_valor" in campos_enviados and "esquiva" not in campos_enviados:
            ent.esquiva = self._calcular_esquiva_basica(ent.velocidade_valor or Decimal("0"))

        if "st_valor" in campos_enviados and "pvs_valor" not in campos_enviados:
            novo_pv_max = ent.st_valor or 0
            pv_atual_antigo = ent.pvs_atual or 0
            ent.pvs_valor = novo_pv_max
            if "pvs_atual" not in campos_enviados:
                ent.pvs_atual = min(pv_atual_antigo, novo_pv_max)
        if "st_valor" in campos_enviados and (
            "dano_impacto" not in campos_enviados or "dano_balanco" not in campos_enviados
        ):
            thr, sw = dano_thr_sw_por_st(ent.st_valor or 0)
            if "dano_impacto" not in campos_enviados:
                ent.dano_impacto = thr
            if "dano_balanco" not in campos_enviados:
                ent.dano_balanco = sw

        if "ht_valor" in campos_enviados and "fadiga_valor" not in campos_enviados:
            nova_fad_max = ent.ht_valor or 0
            fad_atual_antiga = ent.fadiga_atual or 0
            ent.fadiga_valor = nova_fad_max
            if "fadiga_atual" not in campos_enviados:
                ent.fadiga_atual = min(fad_atual_antiga, nova_fad_max)

        if "iq_valor" in campos_enviados and "vontade_valor" not in campos_enviados:
            ent.vontade_valor = ent.iq_valor or 0
        if "iq_valor" in campos_enviados and "percepcao_valor" not in campos_enviados:
            ent.percepcao_valor = ent.iq_valor or 0
        if extras is not None:
            ent.extras_json = normalizar_extras_para_gravacao(
                extras if isinstance(extras, dict) else {}
            )

        if list_v is not None:
            ent.vantagens.clear()
            for v in list_v:
                ent.vantagens.append(
                    GurpsPersonagemVantagem(nome=v["nome"].strip(), custo=v["custo"])
                )
        if list_d is not None:
            ent.desvantagens.clear()
            for d in list_d:
                ent.desvantagens.append(
                    GurpsPersonagemDesvantagem(nome=d["nome"].strip(), custo=d["custo"])
                )
        if list_p is not None:
            self._validar_pre_requisitos_pericias(
                pericias=list_p,
                st=ent.st_valor or 0,
                dx=ent.dx_valor or 0,
                iq=ent.iq_valor or 0,
                ht=ent.ht_valor or 0,
                per=ent.percepcao_valor or 0,
            )
            ent.pericias.clear()
            for s in list_p:
                ent.pericias.append(
                    GurpsPersonagemPericia(
                        nome=s["nome"].strip(),
                        tipo=s["tipo"].strip(),
                        nh=s["nh"],
                        custo=s["custo"],
                    )
                )

        commit_with_rollback(self.repo.db)
        self.repo.db.refresh(ent)
        return GurpsPersonagemResponse.model_validate(ent)
