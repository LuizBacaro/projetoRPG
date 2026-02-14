"""
Controller/Router de Combatentes
Princípio SOLID: SRP - Responsável apenas por HTTP routing
"""
from fastapi import APIRouter, Depends, File, UploadFile, Form, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from ...core.database import get_db
from ...core.dependencies import get_combatente_service
from ...services.combatente_service import CombatenteService
from ...schemas.combatente import (
    CombatenteResponse,
    HPUpdateRequest,
    IniciativaUpdateRequest
)
from ...exceptions.custom_exceptions import ArenaBaseException

router = APIRouter(prefix="/combatentes", tags=["Combatentes"])


@router.get("", response_model=List[CombatenteResponse])
def listar_combatentes(
    tipo: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Lista todos os combatentes ou filtra por tipo"""
    service = get_combatente_service(db)
    combatentes = service.listar_todos(tipo)
    return combatentes


@router.get("/{combatente_id}", response_model=CombatenteResponse)
def obter_combatente(
    combatente_id: int,
    db: Session = Depends(get_db)
):
    """Obtém um combatente específico por ID"""
    service = get_combatente_service(db)
    try:
        combatente = service.obter_por_id(combatente_id)
        return combatente
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("", response_model=CombatenteResponse, status_code=201)
async def criar_combatente(
    nome: str = Form(...),
    hp_maximo: int = Form(...),
    iniciativa: int = Form(...),
    tipo: str = Form("jogador"),
    classe: str = Form("Aventureiro"),
    forca: int = Form(10),
    destreza: int = Form(10),
    constituicao: int = Form(10),
    inteligencia: int = Form(10),
    sabedoria: int = Form(10),
    carisma: int = Form(10),
    fortitude: int = Form(0),
    reflexos: int = Form(0),
    vontade: int = Form(0),
    nivel: int = Form(1),
    pontos: int = Form(0),
    foto: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """Cria um novo combatente"""
    service = get_combatente_service(db)
    
    combatente_data = {
        "nome": nome,
        "tipo": tipo,
        "classe": classe,
        "hp_maximo": hp_maximo,
        "iniciativa": iniciativa,
        "forca": forca,
        "destreza": destreza,
        "constituicao": constituicao,
        "inteligencia": inteligencia,
        "sabedoria": sabedoria,
        "carisma": carisma,
        "fortitude": fortitude,
        "reflexos": reflexos,
        "vontade": vontade,
        "nivel": nivel,
        "pontos": pontos
    }
    
    try:
        combatente = service.criar(combatente_data, foto)
        return combatente
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.put("/{combatente_id}", response_model=CombatenteResponse)
async def atualizar_combatente(
    combatente_id: int,
    nome: str = Form(...),
    hp_maximo: int = Form(...),
    iniciativa: int = Form(...),
    tipo: str = Form(...),
    classe: str = Form("Aventureiro"),
    forca: int = Form(10),
    destreza: int = Form(10),
    constituicao: int = Form(10),
    inteligencia: int = Form(10),
    sabedoria: int = Form(10),
    carisma: int = Form(10),
    fortitude: int = Form(0),
    reflexos: int = Form(0),
    vontade: int = Form(0),
    nivel: int = Form(1),
    pontos: int = Form(0),
    foto: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """Atualiza um combatente existente"""
    service = get_combatente_service(db)
    
    combatente_data = {
        "nome": nome,
        "tipo": tipo,
        "classe": classe,
        "hp_maximo": hp_maximo,
        "iniciativa": iniciativa,
        "forca": forca,
        "destreza": destreza,
        "constituicao": constituicao,
        "inteligencia": inteligencia,
        "sabedoria": sabedoria,
        "carisma": carisma,
        "fortitude": fortitude,
        "reflexos": reflexos,
        "vontade": vontade,
        "nivel": nivel,
        "pontos": pontos
    }
    
    try:
        combatente = service.atualizar(combatente_id, combatente_data, foto)
        return combatente
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.patch("/{combatente_id}/hp", response_model=CombatenteResponse)
def atualizar_hp(
    combatente_id: int,
    hp_data: HPUpdateRequest,
    db: Session = Depends(get_db)
):
    """Atualiza apenas o HP atual de um combatente"""
    service = get_combatente_service(db)
    try:
        combatente = service.atualizar_hp(combatente_id, hp_data.hp_atual)
        return combatente
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.patch("/{combatente_id}/iniciativa", response_model=CombatenteResponse)
def atualizar_iniciativa(
    combatente_id: int,
    ini_data: IniciativaUpdateRequest,
    db: Session = Depends(get_db)
):
    """Atualiza apenas a iniciativa de um combatente"""
    service = get_combatente_service(db)
    try:
        combatente = service.atualizar_iniciativa(combatente_id, ini_data.iniciativa)
        return combatente
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.patch("/{combatente_id}", response_model=CombatenteResponse)
def atualizar_parcial(
    combatente_id: int,
    data: dict,
    db: Session = Depends(get_db)
):
    """Atualiza campos específicos de um combatente"""
    service = get_combatente_service(db)
    try:
        combatente = service.atualizar(combatente_id, data)
        return combatente
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.delete("/{combatente_id}")
def deletar_combatente(
    combatente_id: int,
    db: Session = Depends(get_db)
):
    """Deleta um combatente"""
    service = get_combatente_service(db)
    try:
        service.deletar(combatente_id)
        return {"message": "Combatente deletado com sucesso"}
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)