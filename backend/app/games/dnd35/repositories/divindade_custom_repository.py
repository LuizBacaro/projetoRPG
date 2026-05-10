"""
DivindadeCustomRepository (D&D 3.5)
SRP: persistencia das divindades customizadas (por campanha/mestre).
"""

from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

# `commit_with_rollback` continua no Auth Hub (utilitário compartilhado de
# persistência) durante a reorganização.
from ....repositories.base import commit_with_rollback
from ..models.divindade_custom import DivindadeCustom


class DivindadeCustomRepository:
    def __init__(self, db: Session):
        self.db = db

    # ─── Leitura ────────────────────────────────────────────────────────────

    def listar(self) -> List[DivindadeCustom]:
        return (
            self.db.query(DivindadeCustom)
            .order_by(func.lower(DivindadeCustom.nome))
            .all()
        )

    def get_by_id(self, divindade_id: int) -> Optional[DivindadeCustom]:
        return (
            self.db.query(DivindadeCustom)
            .filter(DivindadeCustom.id == divindade_id)
            .first()
        )

    def get_by_nome_case_insensitive(self, nome: str) -> Optional[DivindadeCustom]:
        if not nome:
            return None
        return (
            self.db.query(DivindadeCustom)
            .filter(func.lower(DivindadeCustom.nome) == nome.strip().lower())
            .first()
        )

    # ─── Escrita ────────────────────────────────────────────────────────────

    def criar(
        self,
        nome: str,
        titulo: str,
        tendencia: str,
        dominios_csv: str,
        descricao: Optional[str],
        criado_por_id: Optional[int],
        commit: bool = True,
    ) -> DivindadeCustom:
        entidade = DivindadeCustom(
            nome=nome,
            titulo=titulo or "",
            tendencia=tendencia,
            dominios=dominios_csv or "",
            descricao=(descricao or None),
            criado_por_id=criado_por_id,
        )
        self.db.add(entidade)
        if commit:
            commit_with_rollback(self.db)
            self.db.refresh(entidade)
        return entidade

    def deletar(self, divindade_id: int, commit: bool = True) -> bool:
        entidade = self.get_by_id(divindade_id)
        if not entidade:
            return False
        self.db.delete(entidade)
        if commit:
            commit_with_rollback(self.db)
        return True
