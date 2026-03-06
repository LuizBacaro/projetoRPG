"""
Router de Ataques e Magias
SRP: apenas roteamento HTTP para ataques e slots de magia
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ...core.database import get_db
from ...repositories.ataque_repository import AtaqueRepository
from ...repositories.combatente_repository import CombatenteRepository
from ...services.ataque_service import AtaqueService
from ...schemas.ataque import (
    AtaqueResponse, AtaquesBulkRequest,
    MagiaSlotResponse, MagiasBulkRequest, MagiaSlotUpdate
)
from ...exceptions.custom_exceptions import CombatenteNaoEncontrado

router = APIRouter(tags=["Ataques e Magias"])


def get_ataque_service(db: Session = Depends(get_db)) -> AtaqueService:
    return AtaqueService(
        ataque_repo     = AtaqueRepository(db),
        combatente_repo = CombatenteRepository(db)
    )


# ── Ataques 

@router.get("/combatentes/{combatente_id}/ataques",
            response_model=List[AtaqueResponse])
def listar_ataques(combatente_id: int,
                   service: AtaqueService = Depends(get_ataque_service)):
    try:
        return service.listar_ataques(combatente_id)
    except CombatenteNaoEncontrado as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/combatentes/{combatente_id}/ataques",
            response_model=List[AtaqueResponse])
def salvar_ataques(combatente_id: int,
                   payload: AtaquesBulkRequest,
                   service: AtaqueService = Depends(get_ataque_service)):
    """Substitui todos os ataques do combatente (bulk replace)."""
    try:
        return service.salvar_ataques(combatente_id, payload.ataques)
    except CombatenteNaoEncontrado as e:
        raise HTTPException(status_code=404, detail=str(e))


# ── Magias 

@router.get("/combatentes/{combatente_id}/magias",
            response_model=List[MagiaSlotResponse])
def listar_magias(combatente_id: int,
                  service: AtaqueService = Depends(get_ataque_service)):
    try:
        return service.listar_magias(combatente_id)
    except CombatenteNaoEncontrado as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/combatentes/{combatente_id}/magias",
            response_model=List[MagiaSlotResponse])
def salvar_magias(combatente_id: int,
                  payload: MagiasBulkRequest,
                  service: AtaqueService = Depends(get_ataque_service)):
    """Substitui todos os slots de magia do combatente (bulk replace)."""
    try:
        return service.salvar_magias(combatente_id, payload.slots)
    except CombatenteNaoEncontrado as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/magias_slots/{slot_id}/usados",
              response_model=MagiaSlotResponse)
def atualizar_usados(slot_id: int,
                     data: MagiaSlotUpdate,
                     service: AtaqueService = Depends(get_ataque_service)):
    """Atualiza apenas 'usados' de um slot — chamado na arena."""
    slot = service.atualizar_usados(slot_id, data.usados)
    if not slot:
        raise HTTPException(status_code=404, detail="Slot não encontrado")
    return slot