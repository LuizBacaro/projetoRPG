"""Contrato estrutural (Protocol) para campanhas GURPS."""

from __future__ import annotations

from typing import List, Optional, Protocol

from sqlalchemy.orm import Session

from app.games.gurps.models.campanha import GurpsCampanha


class GurpsCampanhaRepositoryProtocol(Protocol):
    """Superfície usada por `GurpsCampanhaService`."""

    db: Session

    def listar_por_mestre(self, mestre_id: int) -> List[GurpsCampanha]: ...

    def obter_por_id_e_mestre(
        self, campanha_id: int, mestre_id: int
    ) -> Optional[GurpsCampanha]: ...

    def create(self, entidade: GurpsCampanha) -> GurpsCampanha: ...

    def update(self, campanha: GurpsCampanha) -> GurpsCampanha: ...

    def delete_hard(self, campanha: GurpsCampanha) -> None: ...
