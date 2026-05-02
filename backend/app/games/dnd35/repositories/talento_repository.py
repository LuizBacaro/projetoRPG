"""
Repository de Talento (D&D 3.5)

Localização: `app.games.dnd35.repositories.talento_repository`. Shim em
`app.repositories.talento_repository` durante a reorganização multi-jogo.
"""

from typing import Optional

from sqlalchemy import and_, asc
from sqlalchemy.orm import Session, aliased

from app.games.dnd35.models.talento import Talento, TalentoJogador
from app.games.dnd35.schemas.talento import TalentoCreate, TalentoJogadorCreate
from app.repositories.base import (
    apply_not_deleted,
    commit_with_rollback,
    soft_delete_entity,
)


class TalentoRepository:
    """Operações de banco de dados para talentos"""

    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _payload_data(payload, exclude_unset: bool = False) -> dict:
        if hasattr(payload, "model_dump"):
            return payload.model_dump(exclude_unset=exclude_unset)
        if exclude_unset:
            return payload.dict(exclude_unset=True)
        return payload.dict()

    def restaurar_talento(self, db_talento: Talento, talento: TalentoCreate) -> Talento:
        db_talento.deleted_at = None
        db_talento.ativo = True
        for key, value in self._payload_data(talento).items():
            setattr(db_talento, key, value)
        commit_with_rollback(self.db)
        self.db.refresh(db_talento)
        return db_talento

    def criar_talento(self, talento: TalentoCreate) -> Talento:
        """Cria um novo talento"""
        db_talento = Talento(**self._payload_data(talento))
        self.db.add(db_talento)
        commit_with_rollback(self.db)
        self.db.refresh(db_talento)
        return db_talento

    def obter_talento(self, talento_id: int) -> Optional[Talento]:
        """Obtém um talento por ID"""
        return (
            apply_not_deleted(self.db.query(Talento), Talento)
            .filter(Talento.id == talento_id)
            .first()
        )

    def obter_talento_por_nome(self, nome: str) -> Optional[Talento]:
        """Obtém um talento por nome"""
        return self.db.query(Talento).filter(Talento.nome == nome).first()

    def listar_talentos(self, skip: int = 0, limit: int = 100) -> list[Talento]:
        """Lista todos os talentos com paginação"""
        return (
            apply_not_deleted(self.db.query(Talento), Talento)
            .filter(Talento.ativo == True)  # noqa: E712
            .order_by(asc(Talento.nome))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def atualizar_talento(self, talento_id: int, talento_data: dict) -> Optional[Talento]:
        """Atualiza um talento"""
        db_talento = (
            apply_not_deleted(self.db.query(Talento), Talento)
            .filter(Talento.id == talento_id)
            .first()
        )
        if db_talento:
            for key, value in talento_data.items():
                if value is not None:
                    setattr(db_talento, key, value)
            commit_with_rollback(self.db)
            self.db.refresh(db_talento)
        return db_talento

    def deletar_talento(self, talento_id: int) -> bool:
        """Deleta um talento"""
        db_talento = (
            apply_not_deleted(self.db.query(Talento), Talento)
            .filter(Talento.id == talento_id)
            .first()
        )
        if db_talento:
            return soft_delete_entity(self.db, db_talento)
        return False


class TalentoJogadorRepository:
    """Operações de banco de dados para talentos do jogador"""

    def __init__(self, db: Session):
        self.db = db

    def adicionar_talento(
        self,
        combatente_id: int,
        talento_jogador: TalentoJogadorCreate,
    ) -> TalentoJogador:
        """Adiciona um talento ao combatente"""
        db_existente = (
            self.db.query(TalentoJogador)
            .filter(
                and_(
                    TalentoJogador.combatente_id == combatente_id,
                    TalentoJogador.talento_id == talento_jogador.talento_id,
                )
            )
            .first()
        )

        if db_existente:
            return db_existente

        db_talento_jogador = TalentoJogador(
            combatente_id=combatente_id,
            talento_id=talento_jogador.talento_id,
        )
        self.db.add(db_talento_jogador)
        commit_with_rollback(self.db)
        self.db.refresh(db_talento_jogador)
        return db_talento_jogador

    def obter_talentos_jogador(self, combatente_id: int) -> list[TalentoJogador]:
        """Obtém todos os talentos de um combatente"""
        return (
            self.db.query(TalentoJogador)
            .filter(TalentoJogador.combatente_id == combatente_id)
            .all()
        )

    def obter_talentos_jogador_detalhado(self, combatente_id: int) -> list[dict]:
        """Obtém talentos do jogador com aliases explícitos para evitar ambiguidade em joins."""
        tal_jogador = aliased(TalentoJogador, name="tal_jogador")
        tal_catalogo = aliased(Talento, name="tal_catalogo")

        rows = (
            self.db.query(
                tal_jogador.talento_id.label("talento_id"),
                tal_catalogo.nome.label("talento_nome"),
                tal_catalogo.descricao.label("talento_descricao"),
                tal_catalogo.pagina_referencia.label("talento_pagina_referencia"),
                tal_catalogo.prerequisitos.label("talento_prerequisitos"),
                tal_catalogo.secao.label("talento_secao"),
            )
            .join(tal_catalogo, tal_catalogo.id == tal_jogador.talento_id)
            .filter(
                tal_jogador.combatente_id == combatente_id,
                tal_catalogo.deleted_at.is_(None),
            )
            .order_by(tal_catalogo.nome.asc())
            .all()
        )

        return [dict(row._mapping) for row in rows]

    def remover_talento(self, combatente_id: int, talento_id: int) -> bool:
        """Remove um talento do combatente"""
        db_talento_jogador = (
            self.db.query(TalentoJogador)
            .filter(
                and_(
                    TalentoJogador.combatente_id == combatente_id,
                    TalentoJogador.talento_id == talento_id,
                )
            )
            .first()
        )

        if db_talento_jogador:
            self.db.delete(db_talento_jogador)
            commit_with_rollback(self.db)
            return True
        return False
