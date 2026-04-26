"""[SHIM DE COMPATIBILIDADE] app.schemas.habilidade_especial

Este módulo existe apenas para manter os imports legados funcionando
após a migração do domínio "habilidade especial" do D&D 3.5 para a
estrutura modular `app.games.dnd35.*`.

Não adicione lógica nova aqui. Para alterações, edite
`app.games.dnd35.schemas.habilidade_especial` diretamente. Quando
todos os call sites estiverem usando o novo path, este shim pode ser
removido.
"""

from app.games.dnd35.schemas.habilidade_especial import (
    HabilidadeEspecialDetalhe,
    HabilidadeEspecialResumo,
)

__all__ = [
    "HabilidadeEspecialResumo",
    "HabilidadeEspecialDetalhe",
]
