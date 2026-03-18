"""
Repository específico para Combatente
SRP: Responsável apenas por acesso a dados de Combatente
SOLID: DIP via Session injetada no constructor
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from .base import BaseRepository
from ..models.combatente import Combatente


class CombatenteRepository(BaseRepository[Combatente]):
    """
    Repository para operações de banco de dados de Combatente.
    lazy='selectin' no model garante carregamento automático de:
      - ataques
      - magias_slots
      - magias_preparadas (+ magia via joinedload no model)
    """

    def __init__(self, db: Session):
        super().__init__(Combatente, db)

    def get_by_tipo(self, tipo: str) -> List[Combatente]:
        """Busca combatentes por tipo."""
        return (
            self.db.query(Combatente)
            .filter(Combatente.tipo == tipo)
            .all()
        )

    def get_by_ids(self, combatente_ids: List[int]) -> List[Combatente]:
        """Busca múltiplos combatentes por lista de IDs."""
        return (
            self.db.query(Combatente)
            .filter(Combatente.id.in_(combatente_ids))
            .all()
        )

    def get_vivos_by_ids(self, combatente_ids: List[int]) -> List[Combatente]:
        """Busca combatentes vivos (hp_atual > 0) de uma lista de IDs."""
        return (
            self.db.query(Combatente)
            .filter(
                Combatente.id.in_(combatente_ids),
                Combatente.hp_atual > 0,
            )
            .all()
        )

    def ordenar_por_iniciativa(self, combatentes: List[Combatente]) -> List[Combatente]:
        """Ordena combatentes por iniciativa decrescente (em memória)."""
        return sorted(combatentes, key=lambda c: c.iniciativa, reverse=True)

    def resetar_todos_hp(self) -> int:
        """
        Reseta HP de todos os combatentes para o máximo.
        Retorna o número de combatentes resetados.
        """
        combatentes = self.get_all()
        for combatente in combatentes:
            combatente.resetar_hp()
        self.db.commit()
        return len(combatentes)