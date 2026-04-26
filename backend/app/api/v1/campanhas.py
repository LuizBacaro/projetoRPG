"""[SHIM DE COMPATIBILIDADE] app.api.v1.campanhas

Este módulo existe apenas para manter o registro do router em
`app.main` funcionando após a migração do domínio "campanha" do D&D 3.5
para a estrutura modular `app.games.dnd35.*`.

Não adicione lógica nova aqui. Para alterações, edite
`app.games.dnd35.api.v1.campanhas` diretamente. Quando o registro de
routers em `app.main` for atualizado para apontar para o novo path,
este shim pode ser removido.
"""

from app.games.dnd35.api.v1.campanhas import router

__all__ = ["router"]
