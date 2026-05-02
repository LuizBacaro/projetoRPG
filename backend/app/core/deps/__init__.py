"""
Injeção de dependências FastAPI, organizada por domínio.

- ``hub`` — plataforma (jogos, memberships)
- ``dnd35`` — D&D 3.5
- ``gurps`` — GURPS
- ``file_storage`` — uploads (partilhado entre jogos)

Rotas e código legado podem continuar a importar de ``app.core.dependencies``.
"""

from .dnd35 import (
    get_campanha_repository,
    get_campanha_service,
    get_combate_repository,
    get_combate_service,
    get_combatente_repository,
    get_combatente_service,
    get_condicao_repository,
    get_condicao_service,
    get_grimorio_repository,
    get_grimorio_service,
    get_magia_import_service,
    get_magia_repository,
    get_magia_service,
    get_sessao_campanha_repository,
    get_sessao_campanha_service,
)
from .file_storage import get_file_service
from .gurps import (
    get_gurps_campanha_repository,
    get_gurps_campanha_service,
    get_gurps_combate_repository,
    get_gurps_combate_service,
    get_gurps_personagem_repository,
    get_gurps_personagem_service,
)
from .hub import (
    get_game_repository,
    get_game_service,
    get_user_game_membership_repository,
)

__all__ = [
    "get_campanha_repository",
    "get_campanha_service",
    "get_combate_repository",
    "get_combate_service",
    "get_combatente_repository",
    "get_combatente_service",
    "get_condicao_repository",
    "get_condicao_service",
    "get_file_service",
    "get_game_repository",
    "get_game_service",
    "get_grimorio_repository",
    "get_grimorio_service",
    "get_gurps_campanha_repository",
    "get_gurps_campanha_service",
    "get_gurps_combate_repository",
    "get_gurps_combate_service",
    "get_gurps_personagem_repository",
    "get_gurps_personagem_service",
    "get_magia_import_service",
    "get_magia_repository",
    "get_magia_service",
    "get_sessao_campanha_repository",
    "get_sessao_campanha_service",
    "get_user_game_membership_repository",
]
