"""[SHIM DE COMPATIBILIDADE] app.core.racas_catalog

Este módulo existe apenas para manter os imports legados funcionando
após a migração do catálogo de raças do D&D 3.5 para
`app.games.dnd35.catalogs.racas_catalog`.

Não adicione lógica nova aqui. Para alterações, edite
`app.games.dnd35.catalogs.racas_catalog` diretamente. Quando todos os
call sites estiverem usando o novo path, este shim pode ser removido.
"""

from app.games.dnd35.catalogs.racas_catalog import (
    get_raca_by_slug_or_name,
    list_racas,
    load_racas_catalog,
)

__all__ = [
    "load_racas_catalog",
    "list_racas",
    "get_raca_by_slug_or_name",
]
