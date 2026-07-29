"""HTTP — regras estáticas D&D 3.5 (bestiário MM)."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response

from app.games.dnd35.rules.bestiario_mm35 import (
    filtrar_bestiario_mm35,
    obter_bestiario_por_slug,
    resumo_bestiario,
)
from app.games.dnd35.schemas.bestiario import (
    DnD35BestiarioDetalhe,
    DnD35BestiarioPagina,
    DnD35BestiarioResumo,
)
from app.shared.core.deps import get_usuario_atual, requer_game_dnd35
from app.shared.models.usuario import Usuario

router = APIRouter(
    prefix="/dnd35/regras",
    tags=["D&D 3.5 — Regras"],
    dependencies=[Depends(requer_game_dnd35)],
)


@router.get("/bestiario", response_model=DnD35BestiarioPagina)
def listar_bestiario(
    q: Optional[str] = Query(None, max_length=80),
    tipo: Optional[str] = Query(None, max_length=40),
    nd_min: Optional[float] = Query(None),
    nd_max: Optional[float] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    response: Response = None,
    _: Usuario = Depends(get_usuario_atual),
):
    itens, total = filtrar_bestiario_mm35(
        q=q, tipo=tipo, nd_min=nd_min, nd_max=nd_max, skip=skip, limit=limit
    )
    if response is not None:
        response.headers["X-Total-Count"] = str(total)
    return DnD35BestiarioPagina(
        itens=[DnD35BestiarioResumo.model_validate(resumo_bestiario(r)) for r in itens],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/bestiario/{slug}", response_model=DnD35BestiarioDetalhe)
def detalhe_bestiario(
    slug: str,
    _: Usuario = Depends(get_usuario_atual),
):
    row = obter_bestiario_por_slug(slug)
    if not row:
        raise HTTPException(
            status_code=404, detail="Criatura não encontrada no bestiário."
        )
    return DnD35BestiarioDetalhe.model_validate(row)
