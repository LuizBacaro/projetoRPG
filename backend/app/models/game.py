"""[SHIM DE COMPATIBILIDADE] app.models.game

Re-exporta models canônicos de `app.shared.models.game` durante
a consolidação do Auth Hub em `app/shared/`.
"""

from app.shared.models.game import *  # noqa: F401,F403
