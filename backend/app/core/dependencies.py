"""
Injeção de dependências
"""
from fastapi import Depends
from sqlalchemy.orm import Session
from ..shared.core.database import get_db
from ..games.dnd35.repositories.combatente_repository import CombatenteRepository
from ..games.dnd35.repositories.combate_repository import CombateRepository
from ..games.dnd35.services.combatente_service import CombatenteService
from ..games.dnd35.services.combate_service import CombateService
from ..services.file_service import FileService
from ..games.dnd35.repositories.condicao_repository import CondicaoRepository
from ..games.dnd35.repositories.magia_repository import MagiaRepository
from ..games.dnd35.repositories.grimorio_repository import GrimorioRepository
from ..games.dnd35.repositories.campanha_repository import CampanhaRepository
from ..games.dnd35.repositories.sessao_campanha_repository import (
    SessaoCampanhaRepository,
)
from ..games.gurps.repositories.campanha_repository import GurpsCampanhaRepository
from ..games.gurps.repositories.combate_repository import GurpsCombateRepository
from ..games.gurps.repositories.personagem_repository import GurpsPersonagemRepository
from ..games.gurps.services.campanha_service import GurpsCampanhaService
from ..games.gurps.services.combate_service import GurpsCombateService
from ..games.gurps.services.personagem_service import GurpsPersonagemService
from ..shared.repositories.game_repository import (
    GameRepository,
    UserGameMembershipRepository,
)
from ..games.dnd35.services.condicao_service import CondicaoService
from ..games.dnd35.services.magia_import_service import MagiaImportService
from ..games.dnd35.services.magia_service import MagiaService
from ..games.dnd35.services.grimorio_service import GrimorioService
from ..games.dnd35.services.campanha_service import CampanhaService
from ..games.dnd35.services.sessao_campanha_service import SessaoCampanhaService
from ..shared.services.game_service import GameService

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


def get_campanha_repository(db: Session = Depends(get_db)) -> CampanhaRepository:
    """Factory para CampanhaRepository"""
    return CampanhaRepository(db)

def get_sessao_campanha_repository(db: Session = Depends(get_db)) -> SessaoCampanhaRepository:
    """Factory para SessaoCampanhaRepository"""
    return SessaoCampanhaRepository(db)


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


def get_campanha_service(
    campanha_repository: CampanhaRepository = Depends(get_campanha_repository),
    combatente_repository: CombatenteRepository = Depends(get_combatente_repository),
) -> CampanhaService:
    """Factory para CampanhaService"""
    return CampanhaService(campanha_repository, combatente_repository)


def get_sessao_campanha_service(
    sessao_repository: SessaoCampanhaRepository = Depends(get_sessao_campanha_repository),
    campanha_repository: CampanhaRepository = Depends(get_campanha_repository),
) -> SessaoCampanhaService:
    """Factory para SessaoCampanhaService"""
    return SessaoCampanhaService(sessao_repository, campanha_repository)


def get_file_service() -> FileService:
    """Factory para FileService"""
    return FileService()


def get_condicao_service(db: Session = Depends(get_db)) -> CondicaoService:
    condicao_repo   = CondicaoRepository(db)
    combatente_repo = CombatenteRepository(db)
    return CondicaoService(condicao_repo, combatente_repo)


# ==================== GAMES (Auth Hub multi-jogo) ====================

def get_game_repository(db: Session = Depends(get_db)) -> GameRepository:
    return GameRepository(db)


def get_user_game_membership_repository(
    db: Session = Depends(get_db),
) -> UserGameMembershipRepository:
    return UserGameMembershipRepository(db)


def get_game_service(
    games: GameRepository = Depends(get_game_repository),
    memberships: UserGameMembershipRepository = Depends(
        get_user_game_membership_repository
    ),
) -> GameService:
    return GameService(games, memberships)


# ==================== GURPS ====================


def get_gurps_personagem_repository(
    db: Session = Depends(get_db),
) -> GurpsPersonagemRepository:
    return GurpsPersonagemRepository(db)


def get_gurps_campanha_repository(
    db: Session = Depends(get_db),
) -> GurpsCampanhaRepository:
    return GurpsCampanhaRepository(db)


def get_gurps_combate_repository(
    db: Session = Depends(get_db),
) -> GurpsCombateRepository:
    return GurpsCombateRepository(db)


def get_gurps_personagem_service(
    repository: GurpsPersonagemRepository = Depends(get_gurps_personagem_repository),
) -> GurpsPersonagemService:
    return GurpsPersonagemService(repository)


def get_gurps_campanha_service(
    campanha_repository: GurpsCampanhaRepository = Depends(get_gurps_campanha_repository),
    personagem_repository: GurpsPersonagemRepository = Depends(get_gurps_personagem_repository),
) -> GurpsCampanhaService:
    return GurpsCampanhaService(campanha_repository, personagem_repository)


def get_gurps_combate_service(
    combate_repo: GurpsCombateRepository = Depends(get_gurps_combate_repository),
    personagem_repo: GurpsPersonagemRepository = Depends(get_gurps_personagem_repository),
) -> GurpsCombateService:
    return GurpsCombateService(combate_repo, personagem_repo)
