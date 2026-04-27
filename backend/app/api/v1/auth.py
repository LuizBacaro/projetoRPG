"""[SHIM DE COMPATIBILIDADE] app.api.v1.auth

Re-exporta router canônico de `app.shared.api.v1.auth` durante a
consolidação do Auth Hub em `app/shared/`.
"""

from app.shared.api.v1.auth import *  # noqa: F401,F403
