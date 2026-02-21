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
    IniciativaUpdateRequest,
    DanoCuraRequest,
    DanoCuraResponse
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
    return service.listar_todos(tipo)


@router.get("/{combatente_id}", response_model=CombatenteResponse)
def obter_combatente(
    combatente_id: int,
    db: Session = Depends(get_db)
):
    """Obtém um combatente específico por ID"""
    service = get_combatente_service(db)
    try:
        return service.obter_por_id(combatente_id)
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("", response_model=CombatenteResponse, status_code=201)
async def criar_combatente(
    nome: str = Form(...),
    hp_maximo: int = Form(...),
    iniciativa: int = Form(...),
    tipo: str = Form("jogador"),
    classe: str = Form("Aventureiro"),
    # Defesa
    ca: int = Form(10),
    toque: int = Form(10),
    surpresa: int = Form(10),
    # Atributos
    forca: int = Form(10),
    destreza: int = Form(10),
    constituicao: int = Form(10),
    inteligencia: int = Form(10),
    sabedoria: int = Form(10),
    carisma: int = Form(10),
    # Resistências
    fortitude: int = Form(0),
    reflexos: int = Form(0),
    vontade: int = Form(0),
    # Progressão
    nivel: int = Form(1),
    pontos: int = Form(0),
    foto: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """Cria um novo combatente"""
    service = get_combatente_service(db)
    combatente_data = {
        "nome": nome, "tipo": tipo, "classe": classe,
        "hp_maximo": hp_maximo, "iniciativa": iniciativa,
        "ca": ca, "toque": toque, "surpresa": surpresa,
        "forca": forca, "destreza": destreza, "constituicao": constituicao,
        "inteligencia": inteligencia, "sabedoria": sabedoria, "carisma": carisma,
        "fortitude": fortitude, "reflexos": reflexos, "vontade": vontade,
        "nivel": nivel, "pontos": pontos
    }
    try:
        return service.criar(combatente_data, foto)
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
    # Defesa
    ca: int = Form(10),
    toque: int = Form(10),
    surpresa: int = Form(10),
    # Atributos
    forca: int = Form(10),
    destreza: int = Form(10),
    constituicao: int = Form(10),
    inteligencia: int = Form(10),
    sabedoria: int = Form(10),
    carisma: int = Form(10),
    # Resistências
    fortitude: int = Form(0),
    reflexos: int = Form(0),
    vontade: int = Form(0),
    # Progressão
    nivel: int = Form(1),
    pontos: int = Form(0),
    foto: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """Atualiza um combatente existente"""
    service = get_combatente_service(db)
    combatente_data = {
        "nome": nome, "tipo": tipo, "classe": classe,
        "hp_maximo": hp_maximo, "iniciativa": iniciativa,
        "ca": ca, "toque": toque, "surpresa": surpresa,
        "forca": forca, "destreza": destreza, "constituicao": constituicao,
        "inteligencia": inteligencia, "sabedoria": sabedoria, "carisma": carisma,
        "fortitude": fortitude, "reflexos": reflexos, "vontade": vontade,
        "nivel": nivel, "pontos": pontos
    }
    try:
        return service.atualizar(combatente_id, combatente_data, foto)
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
        return service.atualizar_hp(combatente_id, hp_data.hp_atual)
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
        return service.atualizar_iniciativa(combatente_id, ini_data.iniciativa)
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/{combatente_id}/dano", response_model=DanoCuraResponse)
def aplicar_dano(
    combatente_id: int,
    dano_data: DanoCuraRequest,
    db: Session = Depends(get_db)
):
    """Aplica dano a um combatente"""
    service = get_combatente_service(db)
    try:
        return service.aplicar_dano(combatente_id, dano_data.valor)
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/{combatente_id}/cura", response_model=DanoCuraResponse)
def aplicar_cura(
    combatente_id: int,
    cura_data: DanoCuraRequest,
    db: Session = Depends(get_db)
):
    """Aplica cura a um combatente"""
    service = get_combatente_service(db)
    try:
        return service.aplicar_cura(combatente_id, cura_data.valor)
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
        return service.atualizar(combatente_id, data)
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