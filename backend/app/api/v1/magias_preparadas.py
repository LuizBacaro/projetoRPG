"""
api/v1/magias_preparadas.py
SRP: Endpoints para magias preparadas por conjurador
SOLID: SRP — apenas gerenciar preparação diária de magias

DECISÃO DE DESIGN:
  A validação de QUANTIDADE de slots por nível é responsabilidade do frontend,
  pois a fonte de verdade é a tabela D&D 3.5 (nível + atributo + classe).
  O backend valida apenas: magia existe, magia não duplicada.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.ataque import MagiaPreparada, MagiaSlot
from app.models.magia import Magia
from app.schemas.ataque import (
    MagiaPreparadaResponse,
    MagiaPreparadaCreate,
    DescansoRequest,
)

router = APIRouter(prefix="/magias-preparadas", tags=["Magias Preparadas"])


def _enriquecer(mp: MagiaPreparada) -> dict:
    """
    Adiciona dados da magia ao response.
    SRP: apenas serialização enriquecida.
    """
    return {
        "id":            mp.id,
        "combatente_id": mp.combatente_id,
        "magia_id":      mp.magia_id,
        "nivel_slot":    mp.nivel_slot,
        "preparada_em":  mp.preparada_em,
        "magia_nome":    mp.magia.nome   if mp.magia else None,
        "magia_escola":  mp.magia.escola if mp.magia else None,
        "magia_nivel":   mp.magia.nivel  if mp.magia else None,
    }


@router.get("/{combatente_id}", response_model=List[MagiaPreparadaResponse])
def listar_preparadas(combatente_id: int, db: Session = Depends(get_db)):
    """Lista todas as magias preparadas do conjurador hoje."""
    registros = (
        db.query(MagiaPreparada)
        .filter(MagiaPreparada.combatente_id == combatente_id)
        .all()
    )
    return [_enriquecer(r) for r in registros]


@router.post("/{combatente_id}", response_model=MagiaPreparadaResponse)
def preparar_magia(
    combatente_id: int,
    payload: MagiaPreparadaCreate,
    db: Session = Depends(get_db),
):
    """
    Marca uma magia como preparada.

    Validações:
      1. Magia existe no banco
      2. Magia não está duplicada para este combatente

    NÃO valida quantidade de slots — responsabilidade do frontend
    (fonte de verdade: tabela D&D 3.5 por nível/classe/atributo).
    """
    # 1. Verificar se a magia existe
    magia = db.query(Magia).filter(Magia.id == payload.magia_id).first()
    if not magia:
        raise HTTPException(status_code=404, detail="Magia não encontrada")

    # 2. Verificar duplicata
    ja_preparada = (
        db.query(MagiaPreparada)
        .filter(
            MagiaPreparada.combatente_id == combatente_id,
            MagiaPreparada.magia_id      == payload.magia_id,
        )
        .first()
    )
    if ja_preparada:
        raise HTTPException(status_code=400, detail="Magia já está preparada")

    # 3. Persistir
    nova = MagiaPreparada(
        combatente_id=combatente_id,
        magia_id=payload.magia_id,
        nivel_slot=payload.nivel_slot,
    )
    db.add(nova)
    db.commit()
    db.refresh(nova)

    # Recarregar com relacionamento para enriquecer o response
    nova = db.query(MagiaPreparada).filter(MagiaPreparada.id == nova.id).first()
    return _enriquecer(nova)


@router.delete("/{combatente_id}/{magia_id}", status_code=204)
def desmarcar_magia(
    combatente_id: int,
    magia_id: int,
    db: Session = Depends(get_db),
):
    """Remove uma magia da lista de preparadas."""
    registro = (
        db.query(MagiaPreparada)
        .filter(
            MagiaPreparada.combatente_id == combatente_id,
            MagiaPreparada.magia_id      == magia_id,
        )
        .first()
    )
    if not registro:
        raise HTTPException(status_code=404, detail="Magia não estava preparada")

    db.delete(registro)
    db.commit()


@router.post("/{combatente_id}/descanso", status_code=200)
def descanso_longo(
    combatente_id: int,
    payload: DescansoRequest,
    db: Session = Depends(get_db),
):
    """
    Descanso longo: reseta magias preparadas e slots usados.
    Equivale a uma nova manhã de preparação de magias.
    """
    if not payload.confirmar:
        raise HTTPException(status_code=400, detail="Confirmação necessária")

    # 1. Deletar todas as magias preparadas do combatente
    deletadas = (
        db.query(MagiaPreparada)
        .filter(MagiaPreparada.combatente_id == combatente_id)
        .delete()
    )

    # 2. Resetar slots usados para 0 (arena de combate usa este campo)
    db.query(MagiaSlot).filter(
        MagiaSlot.combatente_id == combatente_id
    ).update({"usados": 0})

    db.commit()

    return {
        "message":              "Descanso longo realizado com sucesso",
        "preparadas_removidas": deletadas,
        "slots_resetados":      True,
    }