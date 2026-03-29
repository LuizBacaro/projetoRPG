"""
Repository genérico (Generic Repository Pattern)
Implementa DIP - Dependency Inversion Principle
"""

from typing import Generic, TypeVar, Type, List, Optional
from sqlalchemy.orm import Session
from ..core.database import Base

ModelType = TypeVar("ModelType", bound=Base)


def commit_with_rollback(db: Session) -> None:
    """Executa commit com rollback automático em caso de erro."""
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise


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
        return self.db.query(self.model).filter(self.model.id == entity_id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Lista todas as entidades"""
        return self.db.query(self.model).offset(skip).limit(limit).all()

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
        self.db.delete(entity)
        commit_with_rollback(self.db)
        return True

    def count(self) -> int:
        """Conta o total de entidades"""
        return self.db.query(self.model).count()  # ✅ CORRIGIDO: estava com quebra de linha