"""
Injeção de dependências (barrel de compatibilidade).

A implementação vive em ``app.core.deps`` (ficheiros por domínio).
Importar daqui ou de ``app.core.deps`` é equivalente.
"""

from app.core.deps import *  # noqa: F403

from app.core.deps import __all__ as __all__  # noqa: PLC0414
