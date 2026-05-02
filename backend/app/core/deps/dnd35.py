"""Factories de injeção — domínio D&D 3.5."""

from fastapi import Depends
from sqlalchemy.orm import Session

from app.games.dnd35.repositories.campanha_repository import CampanhaRepository
from app.games.dnd35.repositories.combate_repository import CombateRepository
from app.games.dnd35.repositories.combatente_repository import CombatenteRepository
from app.games.dnd35.repositories.condicao_repository import CondicaoRepository
from app.games.dnd35.repositories.grimorio_repository import GrimorioRepository
from app.games.dnd35.repositories.magia_repository import MagiaRepository
from app.games.dnd35.repositories.sessao_campanha_repository import (
    SessaoCampanhaRepository,
)
from app.games.dnd35.services.campanha_service import CampanhaService
from app.games.dnd35.services.combate_service import CombateService
from app.games.dnd35.services.combatente_service import CombatenteService
from app.games.dnd35.services.condicao_service import CondicaoService
from app.games.dnd35.services.grimorio_service import GrimorioService
from app.games.dnd35.services.magia_import_service import MagiaImportService
from app.games.dnd35.services.magia_service import MagiaService
from app.games.dnd35.services.sessao_campanha_service import SessaoCampanhaService
from app.shared.core.database import get_db

from .file_storage import get_file_service


def get_combatente_repository(db: Session = Depends(get_db)) -> CombatenteRepository:
    return CombatenteRepository(db)


def get_combate_repository(db: Session = Depends(get_db)) -> CombateRepository:
    return CombateRepository(db)


def get_magia_repository(db: Session = Depends(get_db)) -> MagiaRepository:
    return MagiaRepository(db)


def get_grimorio_repository(db: Session = Depends(get_db)) -> GrimorioRepository:
    return GrimorioRepository(db)


def get_campanha_repository(db: Session = Depends(get_db)) -> CampanhaRepository:
    return CampanhaRepository(db)


def get_sessao_campanha_repository(
    db: Session = Depends(get_db),
) -> SessaoCampanhaRepository:
    return SessaoCampanhaRepository(db)


def get_condicao_repository(db: Session = Depends(get_db)) -> CondicaoRepository:
    return CondicaoRepository(db)


def get_combatente_service(
    repository: CombatenteRepository = Depends(get_combatente_repository),
    condicao_repo: CondicaoRepository = Depends(get_condicao_repository),
) -> CombatenteService:
    file_service = get_file_service()
    return CombatenteService(repository, file_service, condicao_repo)


def get_combate_service(
    combate_repo: CombateRepository = Depends(get_combate_repository),
    combatente_repo: CombatenteRepository = Depends(get_combatente_repository),
) -> CombateService:
    return CombateService(combate_repo, combatente_repo)


def get_magia_service(
    repository: MagiaRepository = Depends(get_magia_repository),
) -> MagiaService:
    return MagiaService(repository)


def get_magia_import_service(
    magia_service: MagiaService = Depends(get_magia_service),
) -> MagiaImportService:
    return MagiaImportService(magia_service)


def get_grimorio_service(
    grimorio_repository: GrimorioRepository = Depends(get_grimorio_repository),
    magia_repository: MagiaRepository = Depends(get_magia_repository),
) -> GrimorioService:
    return GrimorioService(grimorio_repository, magia_repository)


def get_campanha_service(
    campanha_repository: CampanhaRepository = Depends(get_campanha_repository),
    combatente_repository: CombatenteRepository = Depends(get_combatente_repository),
) -> CampanhaService:
    return CampanhaService(campanha_repository, combatente_repository)


def get_sessao_campanha_service(
    sessao_repository: SessaoCampanhaRepository = Depends(
        get_sessao_campanha_repository
    ),
    campanha_repository: CampanhaRepository = Depends(get_campanha_repository),
) -> SessaoCampanhaService:
    return SessaoCampanhaService(sessao_repository, campanha_repository)


def get_condicao_service(db: Session = Depends(get_db)) -> CondicaoService:
    condicao_repo = CondicaoRepository(db)
    combatente_repo = CombatenteRepository(db)
    return CondicaoService(condicao_repo, combatente_repo)
