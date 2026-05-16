"""Factories de injeção — domínio D&D 5e."""

from fastapi import Depends
from sqlalchemy.orm import Session

from app.games.dnd5e.repositories.personagem_repository import Dnd5ePersonagemRepository
from app.games.dnd5e.services.personagem_service import Dnd5ePersonagemService
from app.shared.core.database import get_db


def get_dnd5e_personagem_repository(
    db: Session = Depends(get_db),
) -> Dnd5ePersonagemRepository:
    return Dnd5ePersonagemRepository(db)


def get_dnd5e_personagem_service(
    repository: Dnd5ePersonagemRepository = Depends(get_dnd5e_personagem_repository),
) -> Dnd5ePersonagemService:
    return Dnd5ePersonagemService(repository)
