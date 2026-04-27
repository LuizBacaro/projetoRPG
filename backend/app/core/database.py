"""[SHIM DE COMPATIBILIDADE] app.core.database

Re-exporta camada canônica de banco de dados de `app.shared.core.database`
durante a consolidação do Auth Hub em `app/shared/`.
"""

from app.shared.core.database import *  # noqa: F401,F403
