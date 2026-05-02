"""Regras de negócio — personagens GURPS."""

from __future__ import annotations

from typing import List, Optional

from app.games.gurps.models.personagem import (
    GurpsPersonagem,
    GurpsPersonagemDesvantagem,
    GurpsPersonagemPericia,
    GurpsPersonagemVantagem,
)
from app.games.gurps.repositories.personagem_repository import GurpsPersonagemRepository
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
    def __init__(self, repo: GurpsPersonagemRepository):
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

        pvs_atual = payload.pvs_atual if payload.pvs_atual is not None else payload.pvs_valor
        fadiga_atual = (
            payload.fadiga_atual if payload.fadiga_atual is not None else payload.fadiga_valor
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
            vontade_valor=payload.vontade_valor,
            percepcao_custo=payload.percepcao_custo,
            percepcao_valor=payload.percepcao_valor,
            pvs_custo=payload.pvs_custo,
            pvs_valor=payload.pvs_valor,
            pvs_atual=pvs_atual,
            fadiga_custo=payload.fadiga_custo,
            fadiga_valor=payload.fadiga_valor,
            fadiga_atual=fadiga_atual,
            velocidade_custo=payload.velocidade_custo,
            velocidade_valor=payload.velocidade_valor,
            deslocamento_custo=payload.deslocamento_custo,
            deslocamento_valor=payload.deslocamento_valor,
            esquiva=payload.esquiva,
            aparar=payload.aparar,
            bloqueio=payload.bloqueio,
            dano_impacto=payload.dano_impacto or "",
            dano_balanco=payload.dano_balanco or "",
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
        list_v = data.pop("vantagens", None)
        list_d = data.pop("desvantagens", None)
        list_p = data.pop("pericias", None)
        extras = data.pop("extras", None)

        for key, val in data.items():
            setattr(ent, key, val)
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
