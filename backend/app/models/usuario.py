"""[SHIM DE COMPATIBILIDADE] app.models.usuario

Re-exporta model canônico de `app.shared.models.usuario` durante
a consolidação do Auth Hub em `app/shared/`.
"""

from app.shared.models.usuario import *  # noqa: F401,F403
