"""Contrato estrutural para `DivindadeCustomService`."""

from __future__ import annotations

from typing import List, Optional, Protocol

from app.games.dnd35.models.divindade_custom import DivindadeCustom


class DivindadeCustomRepositoryProtocol(Protocol):
    def listar(self) -> List[DivindadeCustom]:
        ...

    def get_by_nome_case_insensitive(self, nome: str) -> Optional[DivindadeCustom]:
        ...

    def criar(
        self,
        nome: str,
        titulo: str,
        tendencia: str,
        dominios_csv: str,
        descricao: Optional[str],
        criado_por_id: Optional[int],
        commit: bool = True,
    ) -> DivindadeCustom:
        ...

    def deletar(self, divindade_id: int) -> bool:
        ...
