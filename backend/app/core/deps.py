"""[SHIM DE COMPATIBILIDADE] app.core.deps

Re-exporta dependências canônicas de `app.shared.core.deps` enquanto o hub
é consolidado em `app/shared/`.
"""

from app.shared.core.deps import *  # noqa: F401,F403
