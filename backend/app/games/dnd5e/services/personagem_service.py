"""Regras de negócio — personagens D&D 5e."""

from __future__ import annotations

from typing import List, Optional

from app.games.dnd5e.models.personagem import Dnd5ePersonagem
from app.games.dnd5e.ports import Dnd5ePersonagemRepositoryProtocol
from app.games.dnd5e.rules.condicoes_ficha import (
    CHAVE_FICHA_ARENA_CONDICOES,
    condicoes_ficha_de_resposta,
    sincronizar_condicoes_por_hp,
)
from app.games.dnd5e.rules.ficha import validar_ficha_para_gravacao
from app.games.dnd5e.rules.habilidades import AbilityScores, PersonagemHabilidades
from app.games.dnd5e.schemas.personagem import (
    Dnd5ePersonagemCreate,
    Dnd5ePersonagemResponse,
    Dnd5ePersonagemUpdate,
    ficha_json_para_resposta,
    normalizar_ficha_para_gravacao,
)
from app.repositories.base import commit_with_rollback
from app.shared.exceptions.custom_exceptions import ArenaBaseException, DadosInvalidos
from app.shared.models.usuario import PerfilUsuario, Usuario


class Dnd5ePersonagemService:
    def __init__(self, repo: Dnd5ePersonagemRepositoryProtocol):
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

    @staticmethod
    def _normalizar_ficha_entrada(
        ficha: dict, *, nivel: int
    ) -> dict:
        if not ficha:
            return {}
        try:
            return validar_ficha_para_gravacao(ficha, nivel=nivel)
        except ValueError as e:
            raise DadosInvalidos(str(e)) from e

    @staticmethod
    def _personagem_habilidades(ent: Dnd5ePersonagem) -> PersonagemHabilidades:
        return PersonagemHabilidades(
            abilities=AbilityScores(
                strength=ent.strength,
                dexterity=ent.dexterity,
                constitution=ent.constitution,
                intelligence=ent.intelligence,
                wisdom=ent.wisdom,
                charisma=ent.charisma,
            ),
            nivel=ent.nivel,
        )

    def _to_response(self, ent: Dnd5ePersonagem) -> Dnd5ePersonagemResponse:
        ph = self._personagem_habilidades(ent)
        return Dnd5ePersonagemResponse(
            id=ent.id,
            dono_id=ent.dono_id,
            tipo=ent.tipo,
            nome=ent.nome,
            jogador_nome=ent.jogador_nome,
            foto_url=ent.foto_url,
            nivel=ent.nivel,
            experiencia=ent.experiencia,
            strength=ent.strength,
            dexterity=ent.dexterity,
            constitution=ent.constitution,
            intelligence=ent.intelligence,
            wisdom=ent.wisdom,
            charisma=ent.charisma,
            hp_max=ent.hp_max,
            hp_atual=ent.hp_atual,
            ficha=ficha_json_para_resposta(ent.ficha_json),
            strength_mod=ph.strength_mod,
            dexterity_mod=ph.dexterity_mod,
            constitution_mod=ph.constitution_mod,
            intelligence_mod=ph.intelligence_mod,
            wisdom_mod=ph.wisdom_mod,
            charisma_mod=ph.charisma_mod,
            bonus_proficiencia=ph.bonus_proficiencia,
        )

    def listar_todos(
        self,
        tipo: Optional[str],
        *,
        usuario: Usuario,
        skip: int = 0,
        limit: int = 100,
        apenas_meus: bool = False,
    ) -> List[Dnd5ePersonagemResponse]:
        if usuario.perfil == PerfilUsuario.JOGADOR:
            if tipo:
                rows = self.repo.get_by_owner_and_tipo(
                    usuario.id, tipo, skip=skip, limit=limit
                )
            else:
                rows = self.repo.get_by_owner(usuario.id, skip=skip, limit=limit)
            return [self._to_response(r) for r in rows]

        if apenas_meus:
            if tipo:
                rows = self.repo.get_by_owner_and_tipo(
                    usuario.id, tipo, skip=skip, limit=limit
                )
            else:
                rows = self.repo.get_by_owner(usuario.id, skip=skip, limit=limit)
            return [self._to_response(r) for r in rows]

        if tipo:
            rows = self.repo.get_by_tipo(tipo, skip=skip, limit=limit)
        else:
            rows = self.repo.get_all(skip=skip, limit=limit)
        return [self._to_response(r) for r in rows]

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

    def obter_por_id(self, personagem_id: int) -> Dnd5ePersonagem:
        p = self.repo.get_by_id(personagem_id)
        if not p:
            raise ArenaBaseException("Personagem nao encontrado", status_code=404)
        return p

    def obter_resposta(self, personagem_id: int) -> Dnd5ePersonagemResponse:
        return self._to_response(self.obter_por_id(personagem_id))

    def criar(
        self, usuario: Usuario, payload: Dnd5ePersonagemCreate
    ) -> Dnd5ePersonagemResponse:
        self._validar_tipo(payload.tipo)
        if (
            usuario.perfil == PerfilUsuario.JOGADOR
            and payload.tipo.lower() != "jogador"
        ):
            raise DadosInvalidos("Jogadores so podem criar fichas do tipo jogador")
        nome = (payload.nome or "").strip()
        if not nome:
            raise DadosInvalidos("Nome e obrigatorio")

        hp_atual = payload.hp_atual
        if hp_atual is None:
            hp_atual = payload.hp_max

        try:
            self._personagem_habilidades(
                Dnd5ePersonagem(
                    strength=payload.strength,
                    dexterity=payload.dexterity,
                    constitution=payload.constitution,
                    intelligence=payload.intelligence,
                    wisdom=payload.wisdom,
                    charisma=payload.charisma,
                    nivel=payload.nivel,
                )
            )
        except ValueError as e:
            raise DadosInvalidos(str(e)) from e

        ent = Dnd5ePersonagem(
            dono_id=self._resolver_dono(usuario, payload.tipo),
            tipo=payload.tipo.lower(),
            nome=nome,
            jogador_nome=(payload.jogador_nome or "").strip() or None,
            nivel=payload.nivel,
            experiencia=payload.experiencia,
            strength=payload.strength,
            dexterity=payload.dexterity,
            constitution=payload.constitution,
            intelligence=payload.intelligence,
            wisdom=payload.wisdom,
            charisma=payload.charisma,
            hp_max=payload.hp_max,
            hp_atual=hp_atual,
            ficha_json=normalizar_ficha_para_gravacao(
                self._normalizar_ficha_entrada(payload.ficha or {}, nivel=payload.nivel)
            ),
        )
        self.repo.db.add(ent)
        commit_with_rollback(self.repo.db)
        self.repo.db.refresh(ent)
        return self._to_response(ent)

    def atualizar(
        self, personagem_id: int, payload: Dnd5ePersonagemUpdate
    ) -> Dnd5ePersonagemResponse:
        ent = self.obter_por_id(personagem_id)
        data = payload.model_dump(exclude_unset=True)
        ficha = data.pop("ficha", None)

        for key, val in data.items():
            setattr(ent, key, val)

        if ficha is not None:
            nivel = int(data.get("nivel", ent.nivel))
            ficha_atual = ficha_json_para_resposta(ent.ficha_json)
            ficha_mesclada = {**ficha_atual, **ficha}
            ent.ficha_json = normalizar_ficha_para_gravacao(
                self._normalizar_ficha_entrada(ficha_mesclada, nivel=nivel)
            )

        try:
            self._personagem_habilidades(ent)
        except ValueError as e:
            raise DadosInvalidos(str(e)) from e

        if "hp_max" in data and "hp_atual" not in data:
            ent.hp_atual = min(ent.hp_atual or 0, ent.hp_max or 0)

        if "hp_atual" in data:
            ficha_atual = ficha_json_para_resposta(ent.ficha_json)
            condicoes = sincronizar_condicoes_por_hp(
                ent.hp_atual or 0,
                condicoes_ficha_de_resposta(ficha_atual),
            )
            ficha_atual[CHAVE_FICHA_ARENA_CONDICOES] = condicoes
            ent.ficha_json = normalizar_ficha_para_gravacao(
                self._normalizar_ficha_entrada(ficha_atual, nivel=ent.nivel)
            )

        commit_with_rollback(self.repo.db)
        self.repo.db.refresh(ent)
        return self._to_response(ent)
