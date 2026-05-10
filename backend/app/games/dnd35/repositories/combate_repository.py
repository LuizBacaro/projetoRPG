"""Repository específico para Combate e histórico."""

from typing import List, Optional

from sqlalchemy import update
from sqlalchemy.orm import Session

from app.games.dnd35.models.combate import Combate, CombateHistorico
from app.repositories.base import BaseRepository, commit_with_rollback


class CombateRepository(BaseRepository[Combate]):
    """
    Repository para operações de banco de dados de Combate
    """

    def __init__(self, db: Session):
        super().__init__(Combate, db)

    def get_ativo(self) -> Optional[Combate]:
        """Busca o combate ativo (apenas um pode estar ativo)"""
        return self.db.query(Combate).filter(Combate.ativo == True).first()

    def existe_combate_ativo(self) -> bool:
        """Verifica se existe combate ativo"""
        return self.get_ativo() is not None

    def finalizar_todos(self) -> int:
        """
        Finaliza todos os combates ativos com um único UPDATE.
        Retorna o número de combates finalizados.
        """
        result = self.db.execute(
            update(Combate)
            .where(Combate.ativo == True)
            .values(ativo=False)
            .execution_options(synchronize_session="fetch")
        )
        commit_with_rollback(self.db)
        return result.rowcount

    def criar_historico(self, historico: CombateHistorico) -> CombateHistorico:
        self.db.add(historico)
        commit_with_rollback(self.db)
        self.db.refresh(historico)
        return historico

    def listar_historico(
        self, skip: int = 0, limit: int = 20
    ) -> List[CombateHistorico]:
        return (
            self.db.query(CombateHistorico)
            .order_by(CombateHistorico.finalizado_em.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def contar_historico(self) -> int:
        return self.db.query(CombateHistorico).count()
