"""
Injeção de dependências
"""
from fastapi import Depends
from sqlalchemy.orm import Session
from .database import get_db
from ..repositories.combatente_repository import CombatenteRepository
from ..repositories.combate_repository import CombateRepository
from ..services.combatente_service import CombatenteService
from ..services.combate_service import CombateService
from ..services.file_service import FileService
from ..repositories.condicao_repository import CondicaoRepository
from ..repositories.magia_repository import MagiaRepository
from ..repositories.grimorio_repository import GrimorioRepository
from ..services.condicao_service import CondicaoService
from ..services.magia_import_service import MagiaImportService
from ..services.magia_service import MagiaService
from ..services.grimorio_service import GrimorioService

# ==================== REPOSITORIES ====================

def get_combatente_repository(db: Session = Depends(get_db)) -> CombatenteRepository:
    """Factory para CombatenteRepository"""
    return CombatenteRepository(db)


def get_combate_repository(db: Session = Depends(get_db)) -> CombateRepository:
    """Factory para CombateRepository"""
    return CombateRepository(db)


def get_magia_repository(db: Session = Depends(get_db)) -> MagiaRepository:
    """Factory para MagiaRepository"""
    return MagiaRepository(db)


def get_grimorio_repository(db: Session = Depends(get_db)) -> GrimorioRepository:
    """Factory para GrimorioRepository"""
    return GrimorioRepository(db)


# ==================== SERVICES ====================

def get_condicao_repository(db: Session = Depends(get_db)) -> CondicaoRepository:
    """Factory para CondicaoRepository"""
    return CondicaoRepository(db)


def get_combatente_service(
    repository: CombatenteRepository = Depends(get_combatente_repository),
    condicao_repo: CondicaoRepository = Depends(get_condicao_repository),
) -> CombatenteService:
    """Factory para CombatenteService"""
    file_service = FileService()
    return CombatenteService(repository, file_service, condicao_repo)


def get_combate_service(
    combate_repo: CombateRepository = Depends(get_combate_repository),
    combatente_repo: CombatenteRepository = Depends(get_combatente_repository),
) -> CombateService:
    """Factory para CombateService"""
    return CombateService(combate_repo, combatente_repo)


def get_magia_service(
    repository: MagiaRepository = Depends(get_magia_repository),
) -> MagiaService:
    """Factory para MagiaService"""
    return MagiaService(repository)


def get_magia_import_service(
    magia_service: MagiaService = Depends(get_magia_service),
) -> MagiaImportService:
    """Factory para MagiaImportService"""
    return MagiaImportService(magia_service)


def get_grimorio_service(
    grimorio_repository: GrimorioRepository = Depends(get_grimorio_repository),
    magia_repository: MagiaRepository = Depends(get_magia_repository),
) -> GrimorioService:
    """Factory para GrimorioService"""
    return GrimorioService(grimorio_repository, magia_repository)


def get_file_service() -> FileService:
    """Factory para FileService"""
    return FileService()


def get_condicao_service(db: Session = Depends(get_db)) -> CondicaoService:
    condicao_repo   = CondicaoRepository(db)
    combatente_repo = CombatenteRepository(db)
    return CondicaoService(condicao_repo, combatente_repo)