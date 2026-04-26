"""[SHIM DE COMPATIBILIDADE] app.schemas.equipamento

Este módulo existe apenas para manter os imports legados funcionando
após a migração do domínio "equipamento" do D&D 3.5 para a estrutura
modular `app.games.dnd35.*`.

Não adicione lógica nova aqui. Para alterações, edite
`app.games.dnd35.schemas.equipamento` diretamente. Quando todos os
call sites estiverem usando o novo path, este shim pode ser removido.
"""

from app.games.dnd35.schemas.equipamento import (
    EquipamentoBase,
    EquipamentoCreate,
    EquipamentoJogadorBase,
    EquipamentoJogadorCreate,
    EquipamentoJogadorListResponse,
    EquipamentoJogadorResponse,
    EquipamentoResponse,
)

__all__ = [
    "EquipamentoBase",
    "EquipamentoCreate",
    "EquipamentoResponse",
    "EquipamentoJogadorBase",
    "EquipamentoJogadorCreate",
    "EquipamentoJogadorResponse",
    "EquipamentoJogadorListResponse",
]
