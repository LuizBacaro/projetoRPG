"""
api/v1/magias_preparadas.py
SRP: Endpoints para magias preparadas e usadas por conjurador
"""
import re
import unicodedata

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.deps import requer_dono_ou_admin_combatente
from app.models.ataque import MagiaPreparada, MagiaSlot
from app.models.combatente import Combatente
from app.models.magia import Magia
from app.schemas.ataque import (
    MagiaPreparadaResponse,
    MagiaPreparadaCreate,
    DescansoRequest,
)

router = APIRouter(prefix="/magias-preparadas", tags=["Magias Preparadas"])


def _normalizar_classe(valor: str) -> str:
    if not valor:
        return ""
    normalizado = unicodedata.normalize("NFD", str(valor))
    normalizado = "".join(ch for ch in normalizado if unicodedata.category(ch) != "Mn")
    normalizado = normalizado.strip().upper()

    aliases = {
        "FEITICEIRO": "MAGO",
        "PATRULHEIRO": "RANGER",
    }
    return aliases.get(normalizado, normalizado)


def _classes_magia(valor: str) -> set:
    partes = [p.strip() for p in re.split(r"[,/;|]", valor or "") if p.strip()]
    return {_normalizar_classe(parte) for parte in partes}


def _enriquecer(mp: MagiaPreparada) -> dict:
    return {
        "id":            mp.id,
        "combatente_id": mp.combatente_id,
        "magia_id":      mp.magia_id,
        "nivel_slot":    mp.nivel_slot,
        "preparada_em":  mp.preparada_em,
        "usada":         mp.usada,          # ✅ NOVO
        "magia_nome":    mp.magia.nome   if mp.magia else None,
        "magia_escola":  mp.magia.escola if mp.magia else None,
        "magia_nivel":   mp.magia.nivel  if mp.magia else None,
    }


@router.get("/{combatente_id}", response_model=List[MagiaPreparadaResponse])
def listar_preparadas(combatente_id: int, db: Session = Depends(get_db), _: object = Depends(requer_dono_ou_admin_combatente)):
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
    _: object = Depends(requer_dono_ou_admin_combatente),
):
    """
    Marca uma magia como preparada.
    Validações: magia existe + sem duplicata + classe compatível.
    Quantidade de slots é validada no frontend (tabela D&D 3.5).
    """
    combatente = db.query(Combatente).filter(Combatente.id == combatente_id).first()
    if not combatente:
        raise HTTPException(status_code=404, detail="Combatente não encontrado")

    magia = db.query(Magia).filter(Magia.id == payload.magia_id).first()
    if not magia:
        raise HTTPException(status_code=404, detail="Magia não encontrada")

    classe_combatente = _normalizar_classe(combatente.classe)
    classes_permitidas = _classes_magia(magia.classe)

    if classe_combatente not in classes_permitidas:
        classes_legiveis = ", ".join(sorted(classes_permitidas)) or "N/A"
        raise HTTPException(
            status_code=400,
            detail=(
                f"Classe incompatível para preparação: {combatente.classe}. "
                f"Esta magia pertence a: {classes_legiveis}"
            ),
        )

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

    nova = MagiaPreparada(
        combatente_id=combatente_id,
        magia_id=payload.magia_id,
        nivel_slot=payload.nivel_slot,
        usada=False,                         # ✅ NOVO
    )
    db.add(nova)
    db.commit()
    db.refresh(nova)
    nova = db.query(MagiaPreparada).filter(MagiaPreparada.id == nova.id).first()
    return _enriquecer(nova)


@router.patch("/{combatente_id}/{magia_id}/usar", response_model=MagiaPreparadaResponse)
def marcar_usada(
    combatente_id: int,
    magia_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(requer_dono_ou_admin_combatente),
):
    """
    ✅ NOVO: Alterna magia entre usada/não-usada no dia.
    Chamado pelo grimório (checkbox) e pela arena (lançar magia).
    """
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

    registro.usada = not registro.usada
    db.commit()
    db.refresh(registro)
    return _enriquecer(registro)


@router.delete("/{combatente_id}/{magia_id}", status_code=204)
def desmarcar_magia(
    combatente_id: int,
    magia_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(requer_dono_ou_admin_combatente),
):
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
    _: object = Depends(requer_dono_ou_admin_combatente),
):
    """Descanso longo: reseta magias preparadas, usadas e slots."""
    if not payload.confirmar:
        raise HTTPException(status_code=400, detail="Confirmação necessária")

    deletadas = (
        db.query(MagiaPreparada)
        .filter(MagiaPreparada.combatente_id == combatente_id)
        .delete()
    )

    db.query(MagiaSlot).filter(
        MagiaSlot.combatente_id == combatente_id
    ).update({"usados": 0})

    db.commit()

    return {
        "message":              "Descanso longo realizado com sucesso",
        "preparadas_removidas": deletadas,
        "slots_resetados":      True,
    }