"""[SHIM DE COMPATIBILIDADE] app.services.campanha_service

Este módulo existe apenas para manter os imports legados funcionando
após a migração do domínio "campanha" do D&D 3.5 para a estrutura
modular `app.games.dnd35.*`.

Não adicione lógica nova aqui. Para alterações, edite
`app.games.dnd35.services.campanha_service` diretamente. Quando todos
os call sites estiverem usando o novo path, este shim pode ser
removido.
"""

from app.games.dnd35.services.campanha_service import CampanhaService

__all__ = ["CampanhaService"]
