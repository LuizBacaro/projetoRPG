"""[SHIM DE COMPATIBILIDADE] app.core.habilidades_especiais_catalog

Este módulo existe apenas para manter os imports legados funcionando
após a migração do catálogo "habilidades especiais" do D&D 3.5 para
a estrutura modular `app.games.dnd35.catalogs.*`.

Não adicione lógica nova aqui. Para alterações, edite
`app.games.dnd35.catalogs.habilidades_especiais_catalog` diretamente.
Quando todos os call sites estiverem usando o novo path, este shim
pode ser removido.
"""

from app.games.dnd35.catalogs.habilidades_especiais_catalog import (
    get_habilidade_by_slug,
    list_habilidades,
    load_catalog,
    resolver_por_texto,
)

__all__ = [
    "get_habilidade_by_slug",
    "list_habilidades",
    "load_catalog",
    "resolver_por_texto",
]
