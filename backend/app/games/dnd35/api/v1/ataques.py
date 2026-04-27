"""
Router de Ataques e Magias
SRP: apenas roteamento HTTP para ataques e slots de magia

Canônico em `app.games.dnd35.api.v1.ataques` (registrado em `app.main`).
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.shared.core.database import get_db
from app.shared.core.deps import (
    requer_dono_ou_admin_combatente,
    requer_dono_ou_admin_slot_magia,
    requer_game_dnd35,
)
from app.shared.exceptions.custom_exceptions import CombatenteNaoEncontrado
from app.games.dnd35.repositories.ataque_repository import AtaqueRepository
from app.games.dnd35.schemas.ataque import (
    AtaqueResponse,
    AtaquesBulkRequest,
    MagiaSlotResponse,
    MagiaSlotUpdate,
    MagiasBulkRequest,
)
from app.games.dnd35.services.ataque_service import AtaqueService
from app.games.dnd35.repositories.combatente_repository import CombatenteRepository

router = APIRouter(
    tags=["Ataques e Magias"],
    dependencies=[Depends(requer_game_dnd35)],
)


def get_ataque_service(db: Session = Depends(get_db)) -> AtaqueService:
    return AtaqueService(
        ataque_repo=AtaqueRepository(db),
        combatente_repo=CombatenteRepository(db),
    )


# ── Ataques


@router.get("/combatentes/{combatente_id}/ataques", response_model=List[AtaqueResponse])
def listar_ataques(
    combatente_id: int,
    service: AtaqueService = Depends(get_ataque_service),
    _: object = Depends(requer_dono_ou_admin_combatente),
):
    try:
        return service.listar_ataques(combatente_id)
    except CombatenteNaoEncontrado as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/combatentes/{combatente_id}/ataques", response_model=List[AtaqueResponse])
def salvar_ataques(
    combatente_id: int,
    payload: AtaquesBulkRequest,
    service: AtaqueService = Depends(get_ataque_service),
    _: object = Depends(requer_dono_ou_admin_combatente),
):
    """Substitui todos os ataques do combatente (bulk replace)."""
    try:
        return service.salvar_ataques(combatente_id, payload.ataques)
    except CombatenteNaoEncontrado as e:
        raise HTTPException(status_code=404, detail=str(e))


# ── Magias


@router.get("/combatentes/{combatente_id}/magias", response_model=List[MagiaSlotResponse])
def listar_magias(
    combatente_id: int,
    service: AtaqueService = Depends(get_ataque_service),
    _: object = Depends(requer_dono_ou_admin_combatente),
):
    try:
        return service.listar_magias(combatente_id)
    except CombatenteNaoEncontrado as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/combatentes/{combatente_id}/magias", response_model=List[MagiaSlotResponse])
def salvar_magias(
    combatente_id: int,
    payload: MagiasBulkRequest,
    service: AtaqueService = Depends(get_ataque_service),
    _: object = Depends(requer_dono_ou_admin_combatente),
):
    """Substitui todos os slots de magia do combatente (bulk replace)."""
    try:
        return service.salvar_magias(combatente_id, payload.slots)
    except CombatenteNaoEncontrado as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/magias_slots/{slot_id}/usados", response_model=MagiaSlotResponse)
def atualizar_usados(
    slot_id: int,
    data: MagiaSlotUpdate,
    service: AtaqueService = Depends(get_ataque_service),
    _: object = Depends(requer_dono_ou_admin_slot_magia),
):
    """Atualiza apenas 'usados' de um slot — chamado na arena."""
    slot = service.atualizar_usados(slot_id, data.usados)
    if not slot:
        raise HTTPException(status_code=404, detail="Slot não encontrado")
    return slot
