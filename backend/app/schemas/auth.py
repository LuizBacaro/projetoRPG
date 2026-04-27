"""[SHIM DE COMPATIBILIDADE] app.schemas.auth

Re-exporta schemas canônicos de `app.shared.schemas.auth` durante a
consolidação do Auth Hub em `app/shared/`.
"""

from app.shared.schemas.auth import *  # noqa: F401,F403
