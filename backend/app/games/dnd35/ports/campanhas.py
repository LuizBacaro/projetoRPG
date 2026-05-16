"""Contratos estruturais (Protocol) para campanhas e sessões (D&D 3.5)."""

from __future__ import annotations

from typing import List, Optional, Protocol

from sqlalchemy.orm import Session

from app.games.dnd35.models.campanha import Campanha
from app.games.dnd35.models.sessao_campanha import SessaoCampanha


class CampanhaRepositoryProtocol(Protocol):
    """Superfície usada por `CampanhaService` e `SessaoCampanhaService`."""

    db: Session

    def listar_por_mestre(self, mestre_id: int) -> List[Campanha]:
        ...

    def obter_por_id_e_mestre(
        self, campanha_id: int, mestre_id: int
    ) -> Optional[Campanha]:
        ...

    def create(self, entidade: Campanha) -> Campanha:
        ...

    def update(self, campanha: Campanha) -> Campanha:
        ...


class SessaoCampanhaRepositoryProtocol(Protocol):
    """Superfície usada por `SessaoCampanhaService`."""

    def listar_por_mestre(self, mestre_id: int) -> List[SessaoCampanha]:
        ...

    def obter_por_id_e_mestre(
        self, sessao_id: int, mestre_id: int
    ) -> Optional[SessaoCampanha]:
        ...

    def create(self, sessao: SessaoCampanha) -> SessaoCampanha:
        ...

    def update(self, sessao: SessaoCampanha) -> SessaoCampanha:
        ...

    def delete(self, sessao: SessaoCampanha) -> bool:
        ...
