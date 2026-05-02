"""
Injeção de dependências (barrel de compatibilidade).

A implementação vive em ``app.core.deps`` (módulos por domínio: hub, dnd35, gurps, file_storage).
"""

from app.core.deps import *  # noqa: F403
from app.core.deps import __all__  # noqa: F401
