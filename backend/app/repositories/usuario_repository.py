"""[SHIM DE COMPATIBILIDADE] app.repositories.usuario_repository

Re-exporta repositório canônico de `app.shared.repositories.usuario_repository`
durante a consolidação do Auth Hub em `app/shared/`.
"""

from app.shared.repositories.usuario_repository import *  # noqa: F401,F403
