"""
Repository de armaduras/itens de proteção
SRP: operações de banco de dados
"""

from typing import Optional

from sqlalchemy import and_
from sqlalchemy.orm import Session, aliased

from app.games.dnd35.models.armadura_protecao import (
    ArmaduraProtecao,
    ArmaduraProtecaoJogador,
)
from app.games.dnd35.schemas.armadura_protecao import (
    ArmaduraProtecaoCreate,
    ArmaduraProtecaoJogadorCreate,
)
from app.repositories.base import commit_with_rollback


class ArmaduraProtecaoRepository:
    def __init__(self, db: Session):
        self.db = db

    def criar_item(self, item: ArmaduraProtecaoCreate) -> ArmaduraProtecao:
        db_item = ArmaduraProtecao(**item.model_dump())
        self.db.add(db_item)
        commit_with_rollback(self.db)
        self.db.refresh(db_item)
        return db_item

    def obter_por_id(self, item_id: int) -> Optional[ArmaduraProtecao]:
        return (
            self.db.query(ArmaduraProtecao)
            .filter(ArmaduraProtecao.id == item_id)
            .first()
        )

    def obter_por_nome(self, nome: str) -> Optional[ArmaduraProtecao]:
        return (
            self.db.query(ArmaduraProtecao)
            .filter(ArmaduraProtecao.nome == nome)
            .first()
        )

    def listar(self, skip: int = 0, limit: int = 100) -> list[ArmaduraProtecao]:
        return (
            self.db.query(ArmaduraProtecao)
            .filter(ArmaduraProtecao.ativo == True)
            .order_by(ArmaduraProtecao.nome.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )


class ArmaduraProtecaoJogadorRepository:
    def __init__(self, db: Session):
        self.db = db

    def adicionar_item(
        self,
        combatente_id: int,
        payload: ArmaduraProtecaoJogadorCreate,
    ) -> ArmaduraProtecaoJogador:
        db_existente = (
            self.db.query(ArmaduraProtecaoJogador)
            .filter(
                and_(
                    ArmaduraProtecaoJogador.combatente_id == combatente_id,
                    ArmaduraProtecaoJogador.item_id == payload.item_id,
                )
            )
            .first()
        )
        if db_existente:
            return db_existente

        db_item = ArmaduraProtecaoJogador(
            combatente_id=combatente_id,
            item_id=payload.item_id,
        )
        self.db.add(db_item)
        commit_with_rollback(self.db)
        self.db.refresh(db_item)
        return db_item

    def listar_detalhado(self, combatente_id: int) -> list[dict]:
        rel = aliased(ArmaduraProtecaoJogador, name="rel")
        item = aliased(ArmaduraProtecao, name="item")

        rows = (
            self.db.query(
                rel.item_id.label("item_id"),
                item.nome.label("item_nome"),
                item.tipo.label("item_tipo"),
                item.bonus_ca.label("item_bonus_ca"),
                item.des_max.label("item_des_max"),
                item.penalidade.label("item_penalidade"),
                item.falha_arcana.label("item_falha_arcana"),
                item.deslocamento.label("item_deslocamento"),
                item.peso.label("item_peso"),
                item.propriedades_especiais.label("item_propriedades_especiais"),
            )
            .join(item, item.id == rel.item_id)
            .filter(rel.combatente_id == combatente_id, item.ativo == True)
            .order_by(item.nome.asc())
            .all()
        )

        return [dict(row._mapping) for row in rows]

    def remover_item(self, combatente_id: int, item_id: int) -> bool:
        db_item = (
            self.db.query(ArmaduraProtecaoJogador)
            .filter(
                and_(
                    ArmaduraProtecaoJogador.combatente_id == combatente_id,
                    ArmaduraProtecaoJogador.item_id == item_id,
                )
            )
            .first()
        )
        if not db_item:
            return False

        self.db.delete(db_item)
        commit_with_rollback(self.db)
        return True
