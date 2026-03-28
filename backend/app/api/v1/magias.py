"""
api/v1/magias.py
SRP: Endpoints para consulta de magias D&D 3.5
SOLID: Single Responsibility — apenas roteamento de magias
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.models.magia import Magia
from app.schemas.magia import MagiaResponse

router = APIRouter(prefix="/magias", tags=["Magias"])


@router.get("/", response_model=List[MagiaResponse])
def listar_magias(
    classe: Optional[str] = Query(None, description="Filtrar por classe: Mago, Clérigo, Druida, Bardo, Paladino, Ranger"),
    nivel:  Optional[int] = Query(None, ge=0, le=9, description="Filtrar por nível (0-9)"),
    escola: Optional[str] = Query(None, description="Filtrar por escola de magia"),
    nome:   Optional[str] = Query(None, description="Buscar por nome (parcial)"),
    db:     Session        = Depends(get_db),
):
    """
    Lista magias com filtros opcionais.

    Exemplos:
    - GET /api/v1/magias?classe=Mago&nivel=3
    - GET /api/v1/magias?classe=Clérigo
    - GET /api/v1/magias?nome=bola
    """
    query = db.query(Magia).filter(Magia.ativo == True)

    if classe:
        # Mapear Feiticeiro para Mago (mesmas magias)
        classe_normalizado = classe.strip()
        if classe_normalizado.upper() == 'FEITICEIRO':
            classe_normalizado = 'MAGO'
        query = query.filter(Magia.classe.ilike(classe_normalizado))
    if nivel is not None:
        query = query.filter(Magia.nivel == nivel)
    if escola:
        query = query.filter(Magia.escola.ilike(escola))
    if nome:
        query = query.filter(Magia.nome.ilike(f"%{nome}%"))

    return query.order_by(Magia.nivel, Magia.nome).all()


@router.get("/classes", response_model=List[str])
def listar_classes(db: Session = Depends(get_db)):
    """Retorna lista de classes disponíveis."""
    resultado = db.query(Magia.classe).distinct().order_by(Magia.classe).all()
    return [r[0] for r in resultado]


@router.get("/{magia_id}", response_model=MagiaResponse)
def obter_magia(magia_id: int, db: Session = Depends(get_db)):
    """Retorna detalhes de uma magia específica."""
    magia = db.query(Magia).filter(Magia.id == magia_id).first()
    if not magia:
        raise HTTPException(status_code=404, detail="Magia não encontrada")
    return magia