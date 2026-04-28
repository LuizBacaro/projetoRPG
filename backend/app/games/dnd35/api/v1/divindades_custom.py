"""
Router de Divindades Customizadas — D&D 3.5
SRP: exposicao HTTP do catalogo customizado criado pelo Mestre.

* GET  /api/v1/divindades/custom          → qualquer usuario autenticado
* POST /api/v1/divindades/custom          → somente Mestre/Administrador
* DELETE /api/v1/divindades/custom/{id}   → somente Mestre/Administrador

Como sao divindades de campanha, qualquer jogador precisa enxergar para
escolher na ficha; apenas a criacao/remocao e restrita.

Canônico em `app.games.dnd35.api.v1.divindades_custom` (registrado em `app.main`).
"""
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...services.divindade_custom_service import (
    DivindadeCustomService,
    build_divindade_custom_service,
)
from ...schemas.divindade_custom import (
    DivindadeCustomCreate,
    DivindadeCustomResponse,
)

# Auth Hub, BD e cache global: `app.shared.core.*` (canónico).
from .....shared.core.catalog_cache import catalog_cache
from .....shared.core.config import settings
from .....shared.core.database import get_db
from .....shared.core.deps import (
    get_usuario_atual,
    requer_mestre_ou_admin,
    requer_game_dnd35,
)
from .....shared.exceptions.custom_exceptions import ArenaBaseException


router = APIRouter(
    prefix="/divindades",
    tags=["Divindades"],
    dependencies=[Depends(requer_game_dnd35)],
)


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
