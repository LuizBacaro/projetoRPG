from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ...core.habilidades_especiais_catalog import (
    get_habilidade_by_slug,
    list_habilidades,
)
from ...schemas.habilidade_especial import (
    HabilidadeEspecialDetalhe,
    HabilidadeEspecialResumo,
)


router = APIRouter(prefix="/habilidades-especiais", tags=["Habilidades Especiais"])


@router.get("", response_model=list[HabilidadeEspecialResumo])
def listar_habilidades_especiais() -> list[HabilidadeEspecialResumo]:
    payload: list[HabilidadeEspecialResumo] = []
    for item in list_habilidades():
        if not isinstance(item, dict):
            continue
        payload.append(
            HabilidadeEspecialResumo(
                slug=str(item.get("slug") or ""),
                titulo=str(item.get("titulo") or ""),
            )
        )
    return payload


@router.get("/{slug}", response_model=HabilidadeEspecialDetalhe)
def obter_habilidade_especial(slug: str) -> HabilidadeEspecialDetalhe:
    found = get_habilidade_by_slug(slug)
    if not found:
        raise HTTPException(status_code=404, detail="Habilidade especial não encontrada")
    return HabilidadeEspecialDetalhe(
        slug=str(found.get("slug") or ""),
        titulo=str(found.get("titulo") or ""),
        descricao=str(found.get("descricao") or ""),
        aliases=list(found.get("aliases") or []),
    )
