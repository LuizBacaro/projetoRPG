"""
Repository de Condição
Princípio SOLID: SRP - Responsável apenas por acesso a dados de Condição
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from ..models.condicao import Condicao
from ..models.combatente_condicao import CombatenteCondicao


class CondicaoRepository:
    """
    Repository para operações de banco de dados de Condição e pivot CombatenteCondicao
    """

    def __init__(self, db: Session):
        self.db = db

    # ── Condições base ─────────────────────────────────────────────────────────

    def get_all(self) -> List[Condicao]:
        """Retorna todas as condições cadastradas"""
        return self.db.query(Condicao).order_by(Condicao.nome).all()

    def get_by_id(self, condicao_id: int) -> Optional[Condicao]:
        """Busca condição por ID"""
        return self.db.query(Condicao).filter(Condicao.id == condicao_id).first()

    def get_by_nome(self, nome: str) -> Optional[Condicao]:
        """Busca condição por nome (case-insensitive)"""
        return (
            self.db.query(Condicao)
            .filter(Condicao.nome.ilike(nome))
            .first()
        )

    def seed(self, condicoes: List[dict]) -> None:
        """
        Insere as condições iniciais caso a tabela esteja vazia.
        Idempotente — seguro de chamar no startup.
        """
        if self.db.query(Condicao).count() > 0:
            return
        for item in condicoes:
            self.db.add(Condicao(**item))
        self.db.commit()

    # ── Pivot CombatenteCondicao ────────────────────────────────────────────────

    def get_condicoes_do_combatente(self, combatente_id: int) -> List[Condicao]:
        """Retorna todas as condições ativas de um combatente"""
        pivots = (
            self.db.query(CombatenteCondicao)
            .filter(CombatenteCondicao.combatente_id == combatente_id)
            .all()
        )
        ids = [p.condicao_id for p in pivots]
        if not ids:
            return []
        return self.db.query(Condicao).filter(Condicao.id.in_(ids)).all()

    def aplicar(self, combatente_id: int, condicao_id: int) -> bool:
        """
        Aplica condição ao combatente.
        Retorna False se já estava aplicada (UniqueConstraint).
        """
        pivot = CombatenteCondicao(
            combatente_id=combatente_id,
            condicao_id=condicao_id
        )
        try:
            self.db.add(pivot)
            self.db.commit()
            return True
        except IntegrityError:
            self.db.rollback()
            return False

    def remover(self, combatente_id: int, condicao_id: int) -> bool:
        """Remove condição de um combatente. Retorna False se não existia."""
        deleted = (
            self.db.query(CombatenteCondicao)
            .filter(
                CombatenteCondicao.combatente_id == combatente_id,
                CombatenteCondicao.condicao_id   == condicao_id,
            )
            .delete()
        )
        self.db.commit()
        return deleted > 0

    def remover_todas(self, combatente_id: int) -> int:
        """Remove todas as condições de um combatente. Retorna quantidade removida."""
        deleted = (
            self.db.query(CombatenteCondicao)
            .filter(CombatenteCondicao.combatente_id == combatente_id)
            .delete()
        )
        self.db.commit()
        return deleted