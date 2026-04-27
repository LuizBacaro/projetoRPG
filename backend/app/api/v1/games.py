"""[SHIM DE COMPATIBILIDADE] app.api.v1.games

Re-exporta router canônico de `app.shared.api.v1.games` durante a
consolidação do Auth Hub em `app/shared/`.
"""

from app.shared.api.v1.games import *  # noqa: F401,F403
