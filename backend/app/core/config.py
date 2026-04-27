"""[SHIM DE COMPATIBILIDADE] app.core.config

Re-exporta configuração canônica de `app.shared.core.config` durante a
consolidação do Auth Hub em `app/shared/`.
"""

from app.shared.core.config import *  # noqa: F401,F403
