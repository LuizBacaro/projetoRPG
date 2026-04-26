"""
Router de Raças (D&D 3.5)
SRP: apenas mapear endpoints HTTP do catálogo de raças.

Canônico em `app.games.dnd35.api.v1.racas` (registrado em `app.main`).

NOTA: este router ainda **não** declara `requer_game_dnd35` (paridade
com o original).
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.games.dnd35.catalogs.racas_catalog import (
    get_raca_by_slug_or_name,
    list_racas,
)
from app.games.dnd35.schemas.raca import RacaDetalheResponse, RacaResumoResponse

router = APIRouter(prefix="/racas", tags=["Raças"])


@router.get("", response_model=list[RacaResumoResponse])
def listar_racas() -> list[RacaResumoResponse]:
    payload = []
    for item in list_racas():
        if not isinstance(item, dict):
            continue
        payload.append(
            RacaResumoResponse(
                slug=str(item.get("slug") or ""),
                nome=str(item.get("nome") or ""),
                tamanho=item.get("tamanho"),
                deslocamento_metros=item.get("deslocamento_metros"),
                classe_favorecida=item.get("classe_favorecida"),
            )
        )
    return payload


@router.get("/{raca_slug}", response_model=RacaDetalheResponse)
def obter_raca(raca_slug: str) -> RacaDetalheResponse:
    found = get_raca_by_slug_or_name(raca_slug)
    if not found:
        raise HTTPException(status_code=404, detail="Raça não encontrada")
    return RacaDetalheResponse(**found)
