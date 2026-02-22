"""
Injeção de dependências
"""
from typing import Generator
from sqlalchemy.orm import Session
from .database import get_db
from ..repositories.combatente_repository import CombatenteRepository
from ..repositories.combate_repository import CombateRepository
from ..services.combatente_service import CombatenteService
from ..services.combate_service import CombateService
from ..services.file_service import FileService
from ..repositories.condicao_repository import CondicaoRepository
from ..services.condicao_service import CondicaoService

# ==================== REPOSITORIES ====================

def get_combatente_repository(db: Session = None) -> CombatenteRepository:
    """Factory para CombatenteRepository"""
    if db is None:
        db = next(get_db())
    return CombatenteRepository(db)


def get_combate_repository(db: Session = None) -> CombateRepository:
    """Factory para CombateRepository"""
    if db is None:
        db = next(get_db())
    return CombateRepository(db)


# ==================== SERVICES ====================

def get_combatente_service(
    db: Session = None,
    repository: CombatenteRepository = None
) -> CombatenteService:
    """Factory para CombatenteService"""
    if repository is None:
        repository = get_combatente_repository(db)
    file_service = FileService()
    return CombatenteService(repository, file_service)


def get_combate_service(
    db: Session = None,
    combate_repo: CombateRepository = None,
    combatente_repo: CombatenteRepository = None
) -> CombateService:
    """Factory para CombateService"""
    if combate_repo is None:
        combate_repo = get_combate_repository(db)
    if combatente_repo is None:
        combatente_repo = get_combatente_repository(db)
    return CombateService(combate_repo, combatente_repo)


def get_file_service() -> FileService:
    """Factory para FileService"""
    return FileService()


def get_condicao_service(db: Session) -> CondicaoService:
    condicao_repo   = CondicaoRepository(db)
    combatente_repo = CombatenteRepository(db)
    return CondicaoService(condicao_repo, combatente_repo)