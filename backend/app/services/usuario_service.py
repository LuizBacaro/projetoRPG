"""[SHIM DE COMPATIBILIDADE] app.services.usuario_service

Re-exporta service canônico de `app.shared.services.usuario_service`
durante a consolidação do Auth Hub em `app/shared/`.
"""

from app.shared.services.usuario_service import *  # noqa: F401,F403
