"""[SHIM DE COMPATIBILIDADE] app.api.v1.usuarios

Re-exporta router canônico de `app.shared.api.v1.usuarios` durante a
consolidação do Auth Hub em `app/shared/`.
"""

from app.shared.api.v1.usuarios import *  # noqa: F401,F403
