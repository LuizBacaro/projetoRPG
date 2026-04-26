"""
[SHIM DE COMPATIBILIDADE] app.repositories.divindade_custom_repository

O repository real vive em
`app.games.dnd35.repositories.divindade_custom_repository`.
"""
from ..games.dnd35.repositories.divindade_custom_repository import (
    DivindadeCustomRepository,
)

__all__ = ["DivindadeCustomRepository"]
