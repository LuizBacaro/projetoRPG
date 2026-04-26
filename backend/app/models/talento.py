"""[SHIM DE COMPATIBILIDADE] app.models.talento

Re-exporta `Talento` e `TalentoJogador` de `app.games.dnd35.models.talento`.
Edite apenas o módulo em `games/dnd35/`; remova este shim quando os
imports legados forem atualizados.
"""

from app.games.dnd35.models.talento import Talento, TalentoJogador

__all__ = ["Talento", "TalentoJogador"]
