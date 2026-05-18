"""Utilitários compartilhados nos testes D&D 5e."""

from app.games.dnd5e.models.magia import Dnd5eMagia
from app.repositories.base import commit_with_rollback


def get_or_create_magia(db, slug: str, **fields) -> Dnd5eMagia:
    magia = db.query(Dnd5eMagia).filter(Dnd5eMagia.slug == slug).first()
    if magia:
        return magia
    magia = Dnd5eMagia(slug=slug, ativo=True, **fields)
    db.add(magia)
    commit_with_rollback(db)
    db.refresh(magia)
    return magia
