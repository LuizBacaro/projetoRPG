from datetime import datetime

from sqlalchemy import Column, DateTime


class SoftDeleteMixin:
    """Adiciona suporte simples a soft delete com timestamp."""

    deleted_at = Column(DateTime, nullable=True, index=True)

    def soft_delete(self) -> None:
        self.deleted_at = datetime.utcnow()

    def restore(self) -> None:
        self.deleted_at = None