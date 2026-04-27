"""[SHIM DE COMPATIBILIDADE] app.repositories.game_repository

Re-exporta repositórios canônicos de `app.shared.repositories.game_repository`
durante a consolidação do Auth Hub em `app/shared/`.
"""

from app.shared.repositories.game_repository import *  # noqa: F401,F403
