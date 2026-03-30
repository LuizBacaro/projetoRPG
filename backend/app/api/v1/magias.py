"""
api/v1/magias.py
SRP: Endpoints para consulta de magias D&D 3.5
SOLID: Single Responsibility — apenas roteamento de magias
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.catalog_cache import catalog_cache, make_cache_key
from app.core.config import settings
from app.core.database import get_db
from app.models.magia import Magia
from app.schemas.magia import MagiaResponse

router = APIRouter(prefix="/magias", tags=["Magias"])


def _serialize_magia(magia: Magia) -> dict:
    return {
        "id": magia.id,
        "nome": magia.nome,
        "nivel": magia.nivel,
        "classe": magia.classe,
        "escola": magia.escola,
        "sub_escola": magia.sub_escola,
        "componentes": magia.componentes,
        "alcance": magia.alcance,
        "area_efeito": magia.area_efeito,
        "duracao": magia.duracao,
        "tempo_conjuracao": magia.tempo_conjuracao,
        "dano": magia.dano,
        "teste_resistencia": magia.teste_resistencia,
        "resistencia_magica": magia.resistencia_magica,
        "descricao": magia.descricao,
        "ativo": magia.ativo,
        "eh_truque": magia.eh_truque,
        "tem_dano": magia.tem_dano,
        "data_criacao": magia.data_criacao,
    }


@router.get("/", response_model=List[MagiaResponse])
def listar_magias(
    classe: Optional[str] = Query(None, description="Filtrar por classe: Mago, Clérigo, Druida, Bardo, Paladino, Ranger"),
    nivel:  Optional[int] = Query(None, ge=0, le=9, description="Filtrar por nível (0-9)"),
    escola: Optional[str] = Query(None, description="Filtrar por escola de magia"),
    nome:   Optional[str] = Query(None, description="Buscar por nome (parcial)"),
    skip:   int = Query(0, ge=0, description="Quantidade de registros para pular"),
    limit:  int = Query(100, ge=1, le=500, description="Quantidade máxima de registros retornados"),
    response: Response = None,
    db:     Session        = Depends(get_db),
):
    """
    Lista magias com filtros opcionais.

    Exemplos:
    - GET /api/v1/magias?classe=Mago&nivel=3
    - GET /api/v1/magias?classe=Clérigo
    - GET /api/v1/magias?nome=bola
    """
    classe_normalizado = None
    if classe:
        classe_normalizado = classe.strip()
        if classe_normalizado.upper() == "FEITICEIRO":
            classe_normalizado = "MAGO"

    cache_key = make_cache_key(
        "magias:list",
        classe=classe_normalizado,
        nivel=nivel,
        escola=escola,
        nome=nome,
        skip=skip,
        limit=limit,
    )

    if settings.CACHE_ENABLED:
        cached = catalog_cache.get(cache_key)
        if cached is not None:
            if response is not None:
                response.headers["X-Total-Count"] = str(cached["total"])
                response.headers["X-Skip"] = str(skip)
                response.headers["X-Limit"] = str(limit)
            return cached["items"]

    query = db.query(Magia).filter(Magia.ativo == True)
    if classe_normalizado:
        query = query.filter(Magia.classe.ilike(classe_normalizado))
    if nivel is not None:
        query = query.filter(Magia.nivel == nivel)
    if escola:
        query = query.filter(Magia.escola.ilike(escola))
    if nome:
        query = query.filter(Magia.nome.ilike(f"%{nome}%"))

    total = query.count()
    items = [_serialize_magia(magia) for magia in query.order_by(Magia.nivel, Magia.nome).offset(skip).limit(limit).all()]

    if settings.CACHE_ENABLED:
        catalog_cache.set(
            cache_key,
            {"total": total, "items": items},
            settings.CACHE_CATALOG_TTL_SECONDS,
        )

    if response is not None:
        response.headers["X-Total-Count"] = str(total)
        response.headers["X-Skip"] = str(skip)
        response.headers["X-Limit"] = str(limit)

    return items


@router.get("/classes", response_model=List[str])
def listar_classes(db: Session = Depends(get_db)):
    """Retorna lista de classes disponíveis."""
    cache_key = "magias:classes"
    if settings.CACHE_ENABLED:
        cached = catalog_cache.get(cache_key)
        if cached is not None:
            return cached

    resultado = db.query(Magia.classe).distinct().order_by(Magia.classe).all()
    classes = [r[0] for r in resultado]
    if settings.CACHE_ENABLED:
        catalog_cache.set(cache_key, classes, settings.CACHE_CATALOG_TTL_SECONDS)
    return classes


@router.get("/{magia_id}", response_model=MagiaResponse)
def obter_magia(magia_id: int, db: Session = Depends(get_db)):
    """Retorna detalhes de uma magia específica."""
    cache_key = make_cache_key("magias:detail", magia_id=magia_id)
    if settings.CACHE_ENABLED:
        cached = catalog_cache.get(cache_key)
        if cached is not None:
            return cached

    magia = db.query(Magia).filter(Magia.id == magia_id).first()
    if not magia:
        raise HTTPException(status_code=404, detail="Magia não encontrada")

    item = _serialize_magia(magia)
    if settings.CACHE_ENABLED:
        catalog_cache.set(cache_key, item, settings.CACHE_CATALOG_TTL_SECONDS)
    return item