"""Repository para operações de persistência de Magias."""

from __future__ import annotations

from typing import Optional, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from .base import BaseRepository, apply_not_deleted, commit_with_rollback
from ..models.ataque import MagiaPreparada
from ..models.magia import Magia, MagiaClasse


class MagiaRepository(BaseRepository[Magia]):
    def __init__(self, db: Session):
        super().__init__(Magia, db)

    def query_base(self):
        query = self.db.query(Magia)
        if hasattr(query, "options"):
            query = query.options(joinedload(Magia.classes_niveis))
        return apply_not_deleted(query, Magia)

    def get_by_nome(self, nome: str) -> Optional[Magia]:
        return self.query_base().filter(func.lower(Magia.nome) == func.lower(nome.strip())).first()

    def listar_paginado(
        self,
        *,
        classe: Optional[str],
        nivel: Optional[int],
        escola: Optional[str],
        nome: Optional[str],
        componentes: Optional[str],
        dominio: Optional[str],
        ativo: Optional[bool],
        skip: int,
        limit: int,
    ) -> Tuple[int, list[Magia]]:
        query = self.query_base()

        if ativo is not None:
            query = query.filter(Magia.ativo == ativo)
        else:
            query = query.filter(Magia.ativo.is_(True))

        if classe:
            classe_norm = classe.strip().upper()
            query = query.filter(
                (func.upper(Magia.classe).like(f"%{classe_norm}%"))
                | Magia.classes_niveis.any(func.upper(MagiaClasse.classe) == classe_norm)
            )

        if nivel is not None:
            if classe:
                classe_norm = classe.strip().upper()
                query = query.filter(
                    Magia.classes_niveis.any(
                        (func.upper(MagiaClasse.classe) == classe_norm)
                        & (MagiaClasse.nivel == nivel)
                    )
                    | ((Magia.nivel == nivel) & (func.upper(Magia.classe).like(f"%{classe_norm}%")))
                )
            else:
                query = query.filter((Magia.nivel == nivel) | Magia.classes_niveis.any(MagiaClasse.nivel == nivel))

        if escola:
            query = query.filter(Magia.escola.ilike(escola.strip()))

        if nome:
            query = query.filter(Magia.nome.ilike(f"%{nome.strip()}%"))

        if componentes:
            query = query.filter(Magia.componentes.ilike(f"%{componentes.strip()}%"))

        if dominio:
            query = query.filter(Magia.dominios.ilike(f"%{dominio.strip()}%"))

        total = query.count()
        items = query.order_by(Magia.nivel, Magia.nome).offset(skip).limit(limit).all()
        return total, items

    def listar_classes(self) -> list[str]:
        classes_legacy = {
            row[0].strip().upper()
            for row in self.db.query(Magia.classe).filter(Magia.classe.isnot(None)).all()
            if row[0] and row[0].strip()
        }
        classes_rel = {
            row[0].strip().upper()
            for row in self.db.query(MagiaClasse.classe).distinct().all()
            if row[0] and row[0].strip()
        }
        return sorted(classes_legacy | classes_rel)

    def replace_classes(self, magia: Magia, classes_niveis: list[dict]) -> None:
        magia.classes_niveis.clear()
        # Garante que os vínculos antigos sejam removidos antes de inserir novos
        # para evitar conflito de unicidade (magia_id, classe) no mesmo flush.
        self.db.flush()
        for item in classes_niveis:
            magia.classes_niveis.append(
                MagiaClasse(classe=item["classe"].strip().upper(), nivel=item["nivel"])
            )

    def has_dependencias(self, magia_id: int) -> bool:
        return (
            self.db.query(MagiaPreparada.id)
            .filter(MagiaPreparada.magia_id == magia_id)
            .first()
            is not None
        )

    def save(self, magia: Magia) -> Magia:
        commit_with_rollback(self.db)
        self.db.refresh(magia)
        return magia
