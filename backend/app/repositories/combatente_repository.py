"""
Repository específico para Combatente
Princípio SOLID: SRP - Responsável apenas por acesso a dados de Combatente
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from .base import BaseRepository
from ..models.combatente import Combatente


class CombatenteRepository(BaseRepository[Combatente]):
    """
    Repository para operações de banco de dados de Combatente.
    Herda CRUD do BaseRepository.
    lazy='selectin' no model já garante carregamento dos relacionamentos.
    """

    def __init__(self, db: Session):
        super().__init__(Combatente, db)

    def get_by_tipo(self, tipo: str) -> List[Combatente]:
        """Busca combatentes por tipo"""
        return self.db.query(Combatente).filter(Combatente.tipo == tipo).all()

    def get_by_ids(self, combatente_ids: List[int]) -> List[Combatente]:
        """Busca múltiplos combatentes por lista de IDs"""
        return (
            self.db.query(Combatente)
            .filter(Combatente.id.in_(combatente_ids))
            .all()
        )

    def get_vivos_by_ids(self, combatente_ids: List[int]) -> List[Combatente]:
        """Busca combatentes vivos de uma lista de IDs"""
        return (
            self.db.query(Combatente)
            .filter(
                Combatente.id.in_(combatente_ids),
                Combatente.hp_atual > 0
            )
            .all()
        )

    def ordenar_por_iniciativa(self, combatentes: List[Combatente]) -> List[Combatente]:
        """Ordena combatentes por iniciativa (decrescente)"""
        return sorted(combatentes, key=lambda c: c.iniciativa, reverse=True)

    def resetar_todos_hp(self) -> int:
        """
        Reseta o HP de todos os combatentes para o máximo.
        Retorna o número de combatentes resetados.
        """
        combatentes = self.get_all()
        for combatente in combatentes:
            combatente.resetar_hp()
        self.db.commit()
        return len(combatentes)