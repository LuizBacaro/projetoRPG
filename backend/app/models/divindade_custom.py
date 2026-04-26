"""
[SHIM DE COMPATIBILIDADE] app.models.divindade_custom

O model real foi movido para `app.games.dnd35.models.divindade_custom`
como parte da reorganização multi-jogo (ver
`docs/arquitetura-multi-jogo.md`, Fase 5).

Este módulo apenas re-exporta `DivindadeCustom` para preservar imports
legados como:

    from app.models.divindade_custom import DivindadeCustom
    from ..models.divindade_custom import DivindadeCustom

Quando todos os call sites apontarem direto para `app.games.dnd35.models`,
este arquivo pode ser removido.
"""
from ..games.dnd35.models.divindade_custom import DivindadeCustom

__all__ = ["DivindadeCustom"]
