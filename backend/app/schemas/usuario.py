"""[SHIM DE COMPATIBILIDADE] app.schemas.usuario

Re-exporta schemas canônicos de `app.shared.schemas.usuario` durante a
consolidação do Auth Hub em `app/shared/`.
"""

from app.shared.schemas.usuario import *  # noqa: F401,F403
