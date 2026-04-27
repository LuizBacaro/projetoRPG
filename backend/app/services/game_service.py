"""[SHIM DE COMPATIBILIDADE] app.services.game_service

Re-exporta service canônico de `app.shared.services.game_service`
durante a consolidação do Auth Hub em `app/shared/`.
"""

from app.shared.services.game_service import *  # noqa: F401,F403
