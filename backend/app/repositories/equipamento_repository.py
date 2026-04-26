"""[SHIM DE COMPATIBILIDADE] app.repositories.equipamento_repository

Este módulo existe apenas para manter os imports legados funcionando
após a migração do domínio "equipamento" do D&D 3.5 para a estrutura
modular `app.games.dnd35.*`.

Não adicione lógica nova aqui. Para alterações, edite
`app.games.dnd35.repositories.equipamento_repository` diretamente.
Quando todos os call sites estiverem usando o novo path, este shim
pode ser removido.
"""

from app.games.dnd35.repositories.equipamento_repository import (
    EquipamentoJogadorRepository,
    EquipamentoRepository,
)

__all__ = ["EquipamentoRepository", "EquipamentoJogadorRepository"]
