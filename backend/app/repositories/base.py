"""
Repository genérico (Generic Repository Pattern)
Implementa DIP - Dependency Inversion Principle
"""

from datetime import datetime, timezone
from typing import Generic, TypeVar, Type, List, Optional
from sqlalchemy.orm import Query, Session
from ..core.database import Base

ModelType = TypeVar("ModelType", bound=Base)


def commit_with_rollback(db: Session) -> None:
    """Executa commit com rollback automático em caso de erro."""
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise


def supports_soft_delete(model_or_entity: object) -> bool:
    return hasattr(model_or_entity, "deleted_at")


def apply_not_deleted(query: Query, model: Type[ModelType]) -> Query:
    if supports_soft_delete(model):
        return query.filter(model.deleted_at.is_(None))
    return query


def soft_delete_entity(db: Session, entity: ModelType) -> bool:
    if not supports_soft_delete(entity):
        db.delete(entity)
        commit_with_rollback(db)
        return True

    entity.deleted_at = datetime.now(timezone.utc)
    if hasattr(entity, "ativo"):
        entity.ativo = False
    commit_with_rollback(db)
    return True


class BaseRepository(Generic[ModelType]):
    """
    Repository genérico com operações CRUD básicas
    Princípio SOLID: Single Responsibility - apenas acesso a dados
    """

    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db    = db

    def get_by_id(self, entity_id: int) -> Optional[ModelType]:
        """Busca entidade por ID"""
        query = self.db.query(self.model).filter(self.model.id == entity_id)
        return apply_not_deleted(query, self.model).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Lista todas as entidades"""
        return apply_not_deleted(self.db.query(self.model), self.model).offset(skip).limit(limit).all()

    def create(self, entity: ModelType) -> ModelType:
        """Cria uma nova entidade"""
        self.db.add(entity)
        commit_with_rollback(self.db)
        self.db.refresh(entity)
        return entity

    def update(self, entity: ModelType) -> ModelType:
        """Atualiza uma entidade existente"""
        commit_with_rollback(self.db)
        self.db.refresh(entity)
        return entity

    def delete(self, entity: ModelType) -> bool:
        """Deleta uma entidade"""
        return soft_delete_entity(self.db, entity)

    def count(self) -> int:
        """Conta o total de entidades"""
        return apply_not_deleted(self.db.query(self.model), self.model).count()  # ✅ CORRIGIDO: estava com quebra de linha