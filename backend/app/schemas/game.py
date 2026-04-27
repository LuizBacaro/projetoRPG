"""[SHIM DE COMPATIBILIDADE] app.schemas.game

Re-exporta schemas canônicos de `app.shared.schemas.game` durante a
consolidação do Auth Hub em `app/shared/`.
"""

from app.shared.schemas.game import *  # noqa: F401,F403
