"""
Repository específico para Combate
Princípio SOLID: SRP - Responsável apenas por acesso a dados de Combate
"""
from typing import Optional
from sqlalchemy.orm import Session
from .base import BaseRepository, commit_with_rollback
from ..models.combate import Combate


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