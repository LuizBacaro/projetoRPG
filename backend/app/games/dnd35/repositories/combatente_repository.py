"""
Repository específico para Combatente
SRP: Responsável apenas por acesso a dados de Combatente
SOLID: DIP via Session injetada no constructor
"""
from typing import List, Optional
from sqlalchemy.orm import Session
import sqlalchemy as sa

from app.games.dnd35.models.campanha import Campanha
from app.games.dnd35.models.combatente import Combatente
from app.repositories.base import BaseRepository, apply_not_deleted, commit_with_rollback


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

    def get_by_tipo(self, tipo: str, skip: int = 0, limit: int = 100) -> List[Combatente]:
        """Busca combatentes por tipo."""
        return (
            apply_not_deleted(self.db.query(Combatente), Combatente)
            .filter(Combatente.tipo == tipo)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_owner(self, dono_id: int, skip: int = 0, limit: int = 100) -> List[Combatente]:
        """Busca combatentes de um dono específico."""
        return (
            apply_not_deleted(self.db.query(Combatente), Combatente)
            .filter(Combatente.dono_id == dono_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_owner_and_tipo(self, dono_id: int, tipo: str, skip: int = 0, limit: int = 100) -> List[Combatente]:
        """Busca combatentes de um dono filtrando por tipo."""
        return (
            apply_not_deleted(self.db.query(Combatente), Combatente)
            .filter(
                Combatente.dono_id == dono_id,
                Combatente.tipo == tipo,
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count_all(self) -> int:
        """Conta todos os combatentes."""
        return apply_not_deleted(self.db.query(Combatente), Combatente).count()

    def count_by_tipo(self, tipo: str) -> int:
        """Conta combatentes por tipo."""
        return apply_not_deleted(self.db.query(Combatente), Combatente).filter(Combatente.tipo == tipo).count()

    def count_by_owner(self, dono_id: int) -> int:
        """Conta combatentes de um dono."""
        return apply_not_deleted(self.db.query(Combatente), Combatente).filter(Combatente.dono_id == dono_id).count()

    def count_by_owner_and_tipo(self, dono_id: int, tipo: str) -> int:
        """Conta combatentes de um dono filtrando por tipo."""
        return (
            apply_not_deleted(self.db.query(Combatente), Combatente)
            .filter(
                Combatente.dono_id == dono_id,
                Combatente.tipo == tipo,
            )
            .count()
        )

    def get_by_owner_or_campanha_mestre(self, mestre_id: int, skip: int = 0, limit: int = 100) -> List[Combatente]:
        """Busca combatentes do mestre (por dono) ou vinculados às campanhas dele."""
        return (
            apply_not_deleted(self.db.query(Combatente), Combatente)
            .outerjoin(Campanha, Combatente.campanha_id == Campanha.id)
            .filter(
                sa.or_(
                    Combatente.dono_id == mestre_id,
                    Campanha.mestre_id == mestre_id,
                )
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_owner_or_campanha_mestre_and_tipo(
        self,
        mestre_id: int,
        tipo: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Combatente]:
        """Busca combatentes do mestre por tipo (dono ou campanha do mestre)."""
        return (
            apply_not_deleted(self.db.query(Combatente), Combatente)
            .outerjoin(Campanha, Combatente.campanha_id == Campanha.id)
            .filter(
                Combatente.tipo == tipo,
                sa.or_(
                    Combatente.dono_id == mestre_id,
                    Campanha.mestre_id == mestre_id,
                ),
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count_by_owner_or_campanha_mestre(self, mestre_id: int) -> int:
        """Conta combatentes do mestre (dono ou em campanhas do mestre)."""
        return (
            apply_not_deleted(self.db.query(sa.func.count(sa.distinct(Combatente.id))), Combatente)
            .outerjoin(Campanha, Combatente.campanha_id == Campanha.id)
            .filter(
                sa.or_(
                    Combatente.dono_id == mestre_id,
                    Campanha.mestre_id == mestre_id,
                )
            )
            .scalar()
            or 0
        )

    def count_by_owner_or_campanha_mestre_and_tipo(self, mestre_id: int, tipo: str) -> int:
        """Conta combatentes do mestre por tipo (dono ou em campanhas do mestre)."""
        return (
            apply_not_deleted(self.db.query(sa.func.count(sa.distinct(Combatente.id))), Combatente)
            .outerjoin(Campanha, Combatente.campanha_id == Campanha.id)
            .filter(
                Combatente.tipo == tipo,
                sa.or_(
                    Combatente.dono_id == mestre_id,
                    Campanha.mestre_id == mestre_id,
                ),
            )
            .scalar()
            or 0
        )

    def get_by_ids(self, combatente_ids: List[int]) -> List[Combatente]:
        """Busca múltiplos combatentes por lista de IDs."""
        return (
            apply_not_deleted(self.db.query(Combatente), Combatente)
            .filter(Combatente.id.in_(combatente_ids))
            .all()
        )

    def get_vivos_by_ids(self, combatente_ids: List[int]) -> List[Combatente]:
        """
        Busca combatentes vivos de uma lista de IDs.
        D&D 3.5: monstros morrem a 0 HP; jogadores/NPCs morrem a -10 HP.
        """
        return (
            apply_not_deleted(self.db.query(Combatente), Combatente)
            .filter(
                Combatente.id.in_(combatente_ids),
                sa.or_(
                    sa.and_(Combatente.tipo == 'monstro', Combatente.hp_atual > 0),
                    sa.and_(Combatente.tipo.in_(['jogador', 'npc']), Combatente.hp_atual > -10),
                ),
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
        commit_with_rollback(self.db)
        return len(combatentes)