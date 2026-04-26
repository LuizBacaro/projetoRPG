"""[SHIM DE COMPATIBILIDADE] app.schemas.raca

Este módulo existe apenas para manter os imports legados funcionando
após a migração dos schemas de raça do D&D 3.5 para
`app.games.dnd35.schemas.raca`.

Não adicione lógica nova aqui. Para alterações, edite
`app.games.dnd35.schemas.raca` diretamente. Quando todos os call sites
estiverem usando o novo path, este shim pode ser removido.
"""

from app.games.dnd35.schemas.raca import (
    RacaDetalheResponse,
    RacaModificadorAtributo,
    RacaResumoResponse,
)

__all__ = [
    "RacaModificadorAtributo",
    "RacaResumoResponse",
    "RacaDetalheResponse",
]
