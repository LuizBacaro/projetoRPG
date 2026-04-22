"""
Router de Divindades Customizadas
SRP: exposicao HTTP do catalogo customizado criado pelo Mestre.

* GET  /api/v1/divindades/custom          → qualquer usuario autenticado
* POST /api/v1/divindades/custom          → somente Mestre/Administrador
* DELETE /api/v1/divindades/custom/{id}   → somente Mestre/Administrador

Como sao divindades de campanha, qualquer jogador precisa enxergar para
escolher na ficha; apenas a criacao/remocao e restrita.
"""
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...core.catalog_cache import catalog_cache
from ...core.config import settings
from ...core.database import get_db
from ...core.deps import get_usuario_atual, requer_mestre_ou_admin
from ...exceptions.custom_exceptions import ArenaBaseException
from ...schemas.divindade_custom import (
    DivindadeCustomCreate,
    DivindadeCustomResponse,
)
from ...services.divindade_custom_service import (
    DivindadeCustomService,
    build_divindade_custom_service,
)

router = APIRouter(prefix="/divindades", tags=["Divindades"])


def get_service(db: Session = Depends(get_db)) -> DivindadeCustomService:
    return build_divindade_custom_service(db)


def _invalidar_caches() -> None:
    """Invalida caches do catalogo de divindades para refletir mudancas."""
    if settings.CACHE_ENABLED:
        catalog_cache.invalidate_prefix("magias:divindades")


@router.get("/custom", response_model=List[DivindadeCustomResponse])
def listar_divindades_custom(
    service: DivindadeCustomService = Depends(get_service),
    _: object = Depends(get_usuario_atual),
):
    """Lista as divindades customizadas da campanha (visiveis para todos)."""
    return [service.serializar(item) for item in service.listar()]


@router.post(
    "/custom",
    response_model=DivindadeCustomResponse,
    status_code=status.HTTP_201_CREATED,
)
def criar_divindade_custom(
    payload: DivindadeCustomCreate,
    service: DivindadeCustomService = Depends(get_service),
    usuario=Depends(requer_mestre_ou_admin),
):
    """Cria uma divindade customizada (restrito a Mestre/Administrador)."""
    try:
        entidade = service.criar(payload.model_dump(), usuario_id=getattr(usuario, "id", None))
    except ArenaBaseException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)
    _invalidar_caches()
    return service.serializar(entidade)


@router.delete(
    "/custom/{divindade_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def deletar_divindade_custom(
    divindade_id: int,
    service: DivindadeCustomService = Depends(get_service),
    _=Depends(requer_mestre_ou_admin),
):
    """Remove uma divindade customizada (restrito a Mestre/Administrador)."""
    try:
        service.deletar(divindade_id)
    except ArenaBaseException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)
    _invalidar_caches()
    return None


@router.get("/catalogo", response_model=List[Dict[str, Any]])
def catalogo_unificado(
    service: DivindadeCustomService = Depends(get_service),
    _: object = Depends(get_usuario_atual),
):
    """Catalogo oficial (Tabela 3-7) + customizadas, cada item com `origem`.

    Mesma forma do endpoint /magias/divindades/catalogo, porem com campo
    `origem` ('oficial' | 'custom') para que o frontend possa marcar quais
    entradas sao deletaveis pelo Mestre.
    """
    return service.listar_catalogo_unificado()
