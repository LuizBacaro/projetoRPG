"""
Repository de armaduras/itens de proteção
SRP: operações de banco de dados
"""

from sqlalchemy import and_
from sqlalchemy.orm import Session, aliased
from typing import Optional

from app.models.armadura_protecao import ArmaduraProtecao, ArmaduraProtecaoJogador
from app.schemas.armadura_protecao import ArmaduraProtecaoCreate, ArmaduraProtecaoJogadorCreate
from app.repositories.base import commit_with_rollback


class ArmaduraProtecaoRepository:
    @staticmethod
    def criar_item(db: Session, item: ArmaduraProtecaoCreate) -> ArmaduraProtecao:
        db_item = ArmaduraProtecao(**item.model_dump())
        db.add(db_item)
        commit_with_rollback(db)
        db.refresh(db_item)
        return db_item

    @staticmethod
    def obter_por_id(db: Session, item_id: int) -> Optional[ArmaduraProtecao]:
        return db.query(ArmaduraProtecao).filter(ArmaduraProtecao.id == item_id).first()

    @staticmethod
    def obter_por_nome(db: Session, nome: str) -> Optional[ArmaduraProtecao]:
        return db.query(ArmaduraProtecao).filter(ArmaduraProtecao.nome == nome).first()

    @staticmethod
    def listar(db: Session, skip: int = 0, limit: int = 100) -> list[ArmaduraProtecao]:
        return (
            db.query(ArmaduraProtecao)
            .filter(ArmaduraProtecao.ativo == True)
            .order_by(ArmaduraProtecao.nome.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )


class ArmaduraProtecaoJogadorRepository:
    @staticmethod
    def adicionar_item(
        db: Session,
        combatente_id: int,
        payload: ArmaduraProtecaoJogadorCreate,
    ) -> ArmaduraProtecaoJogador:
        db_existente = db.query(ArmaduraProtecaoJogador).filter(
            and_(
                ArmaduraProtecaoJogador.combatente_id == combatente_id,
                ArmaduraProtecaoJogador.item_id == payload.item_id,
            )
        ).first()
        if db_existente:
            return db_existente

        db_item = ArmaduraProtecaoJogador(
            combatente_id=combatente_id,
            item_id=payload.item_id,
        )
        db.add(db_item)
        commit_with_rollback(db)
        db.refresh(db_item)
        return db_item

    @staticmethod
    def listar_detalhado(db: Session, combatente_id: int) -> list[dict]:
        rel = aliased(ArmaduraProtecaoJogador, name="rel")
        item = aliased(ArmaduraProtecao, name="item")

        rows = (
            db.query(
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

    @staticmethod
    def remover_item(db: Session, combatente_id: int, item_id: int) -> bool:
        db_item = db.query(ArmaduraProtecaoJogador).filter(
            and_(
                ArmaduraProtecaoJogador.combatente_id == combatente_id,
                ArmaduraProtecaoJogador.item_id == item_id,
            )
        ).first()
        if not db_item:
            return False

        db.delete(db_item)
        commit_with_rollback(db)
        return True
