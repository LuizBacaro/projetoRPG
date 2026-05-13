"""Factories de injeção — domínio Tormenta."""

from fastapi import Depends
from sqlalchemy.orm import Session

from app.games.tormenta.repositories.personagem_repository import TormentaPersonagemRepository
from app.games.tormenta.services.personagem_service import TormentaPersonagemService
from app.shared.core.database import get_db


def get_tormenta_personagem_repository(
    db: Session = Depends(get_db),
) -> TormentaPersonagemRepository:
    return TormentaPersonagemRepository(db)


def get_tormenta_personagem_service(
    repository: TormentaPersonagemRepository = Depends(
        get_tormenta_personagem_repository
    ),
) -> TormentaPersonagemService:
    return TormentaPersonagemService(repository)
