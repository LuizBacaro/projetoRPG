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
from ..services.condicao_service import CondicaoService

# ==================== REPOSITORIES ====================

def get_combatente_repository(db: Session = Depends(get_db)) -> CombatenteRepository:
    """Factory para CombatenteRepository"""
    return CombatenteRepository(db)


def get_combate_repository(db: Session = Depends(get_db)) -> CombateRepository:
    """Factory para CombateRepository"""
    return CombateRepository(db)


# ==================== SERVICES ====================

def get_combatente_service(
    repository: CombatenteRepository = Depends(get_combatente_repository),
) -> CombatenteService:
    """Factory para CombatenteService"""
    file_service = FileService()
    return CombatenteService(repository, file_service)


def get_combate_service(
    combate_repo: CombateRepository = Depends(get_combate_repository),
    combatente_repo: CombatenteRepository = Depends(get_combatente_repository),
) -> CombateService:
    """Factory para CombateService"""
    return CombateService(combate_repo, combatente_repo)


def get_file_service() -> FileService:
    """Factory para FileService"""
    return FileService()


def get_condicao_service(db: Session = Depends(get_db)) -> CondicaoService:
    condicao_repo   = CondicaoRepository(db)
    combatente_repo = CombatenteRepository(db)
    return CondicaoService(condicao_repo, combatente_repo)