"""[SHIM DE COMPATIBILIDADE] app.models.mixins

`SoftDeleteMixin` foi movido para `app.core.mixins` para evitar import
circular com `app.models` ao carregar modelos em `app.games.dnd35.models`.
"""

from app.core.mixins import SoftDeleteMixin

__all__ = ["SoftDeleteMixin"]
