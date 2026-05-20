"""Factories de injeção — domínio D&D 5e."""

from fastapi import Depends
from sqlalchemy.orm import Session

from app.games.dnd5e.repositories.grimorio_repository import Dnd5eGrimorioRepository
from app.games.dnd5e.repositories.magia_repository import Dnd5eMagiaRepository
from app.games.dnd5e.repositories.personagem_repository import Dnd5ePersonagemRepository
from app.games.dnd5e.services.conjuracao_ficha_service import (
    Dnd5eConjuracaoFichaService,
)
from app.games.dnd5e.services.conjuracao_service import Dnd5eConjuracaoService
from app.games.dnd5e.services.grimorio_service import Dnd5eGrimorioService
from app.games.dnd5e.services.magia_import_service import Dnd5eMagiaImportService
from app.games.dnd5e.services.magia_service import Dnd5eMagiaService
from app.games.dnd5e.services.personagem_service import Dnd5ePersonagemService
from app.shared.core.database import get_db


def get_dnd5e_magia_repository(db: Session = Depends(get_db)) -> Dnd5eMagiaRepository:
    return Dnd5eMagiaRepository(db)


def get_dnd5e_magia_service(
    repository: Dnd5eMagiaRepository = Depends(get_dnd5e_magia_repository),
) -> Dnd5eMagiaService:
    return Dnd5eMagiaService(repository)


def get_dnd5e_magia_import_service(
    repository: Dnd5eMagiaRepository = Depends(get_dnd5e_magia_repository),
) -> Dnd5eMagiaImportService:
    return Dnd5eMagiaImportService(repository)


def get_dnd5e_grimorio_repository(
    db: Session = Depends(get_db),
) -> Dnd5eGrimorioRepository:
    return Dnd5eGrimorioRepository(db)


def get_dnd5e_grimorio_service(
    grimorio_repo: Dnd5eGrimorioRepository = Depends(get_dnd5e_grimorio_repository),
    magia_repo: Dnd5eMagiaRepository = Depends(get_dnd5e_magia_repository),
) -> Dnd5eGrimorioService:
    return Dnd5eGrimorioService(grimorio_repo, magia_repo)


def get_dnd5e_personagem_repository(
    db: Session = Depends(get_db),
) -> Dnd5ePersonagemRepository:
    return Dnd5ePersonagemRepository(db)


def get_dnd5e_personagem_service(
    repository: Dnd5ePersonagemRepository = Depends(get_dnd5e_personagem_repository),
) -> Dnd5ePersonagemService:
    return Dnd5ePersonagemService(repository)


def get_dnd5e_conjuracao_service(
    magia_repo: Dnd5eMagiaRepository = Depends(get_dnd5e_magia_repository),
    grimorio_repo: Dnd5eGrimorioRepository = Depends(get_dnd5e_grimorio_repository),
) -> Dnd5eConjuracaoService:
    return Dnd5eConjuracaoService(magia_repo, grimorio_repo)


def get_dnd5e_conjuracao_ficha_service(
    personagem_repo: Dnd5ePersonagemRepository = Depends(
        get_dnd5e_personagem_repository
    ),
    grimorio_repo: Dnd5eGrimorioRepository = Depends(get_dnd5e_grimorio_repository),
    magia_repo: Dnd5eMagiaRepository = Depends(get_dnd5e_magia_repository),
) -> Dnd5eConjuracaoFichaService:
    return Dnd5eConjuracaoFichaService(personagem_repo, grimorio_repo, magia_repo)
