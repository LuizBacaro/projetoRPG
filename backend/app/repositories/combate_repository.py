"""Repository específico para Combate e histórico."""

from typing import List, Optional
from sqlalchemy.orm import Session
from .base import BaseRepository, commit_with_rollback
from ..models.combate import Combate, CombateHistorico


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
        Finaliza todos os combates ativos
        Retorna o número de combates finalizados
        """
        combates_ativos = self.db.query(Combate).filter(Combate.ativo == True).all()
        count = len(combates_ativos)
        
        for combate in combates_ativos:
            combate.finalizar()
        
        commit_with_rollback(self.db)
        return count

    def criar_historico(self, historico: CombateHistorico) -> CombateHistorico:
        self.db.add(historico)
        commit_with_rollback(self.db)
        self.db.refresh(historico)
        return historico

    def listar_historico(self, skip: int = 0, limit: int = 20) -> List[CombateHistorico]:
        return (
            self.db.query(CombateHistorico)
            .order_by(CombateHistorico.finalizado_em.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def contar_historico(self) -> int:
        return self.db.query(CombateHistorico).count()