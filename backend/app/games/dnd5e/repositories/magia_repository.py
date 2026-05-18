"""Repository — catálogo `dnd5e_magias`."""

from __future__ import annotations

from typing import Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app.games.dnd5e.models.magia import Dnd5eMagia, Dnd5eMagiaClasse


class Dnd5eMagiaRepository:
    def __init__(self, db: Session):
        self.db = db

    def obter(self, magia_id: int) -> Optional[Dnd5eMagia]:
        return (
            self.db.query(Dnd5eMagia)
            .options(joinedload(Dnd5eMagia.classes_niveis))
            .filter(Dnd5eMagia.id == magia_id, Dnd5eMagia.ativo.is_(True))
            .first()
        )

    def obter_por_slug(self, slug: str) -> Optional[Dnd5eMagia]:
        return (
            self.db.query(Dnd5eMagia)
            .options(joinedload(Dnd5eMagia.classes_niveis))
            .filter(Dnd5eMagia.slug == slug)
            .first()
        )

    def listar_paginado(
        self,
        *,
        nome: Optional[str] = None,
        nivel: Optional[int] = None,
        escola: Optional[str] = None,
        classe_slug: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[int, list[Dnd5eMagia]]:
        query = (
            self.db.query(Dnd5eMagia)
            .options(joinedload(Dnd5eMagia.classes_niveis))
            .filter(Dnd5eMagia.ativo.is_(True))
        )

        if classe_slug:
            slug = classe_slug.strip().lower()
            query = query.join(Dnd5eMagiaClasse).filter(
                Dnd5eMagiaClasse.classe_slug == slug
            )

        if nome:
            termo = f"%{nome.strip()}%"
            query = query.filter(
                or_(
                    Dnd5eMagia.nome.ilike(termo),
                    Dnd5eMagia.descricao.ilike(termo),
                    Dnd5eMagia.slug.ilike(termo),
                )
            )

        if nivel is not None:
            query = query.filter(Dnd5eMagia.nivel == nivel)

        if escola:
            query = query.filter(Dnd5eMagia.escola.ilike(escola.strip()))

        rows = query.order_by(Dnd5eMagia.nivel, Dnd5eMagia.nome).all()
        total = len(rows)
        if skip or limit < len(rows):
            rows = rows[skip : skip + limit]
        return total, rows

    def criar(self, magia: Dnd5eMagia) -> Dnd5eMagia:
        self.db.add(magia)
        self.db.flush()
        return magia
