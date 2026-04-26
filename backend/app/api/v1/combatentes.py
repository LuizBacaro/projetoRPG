"""
Controller/Router de Combatentes
SRP: Responsável apenas por HTTP routing
"""
from fastapi import APIRouter, Depends, File, UploadFile, Form, HTTPException, Query, Response
from typing import List, Optional
from ...core.deps import get_usuario_atual, requer_dono_ou_admin_combatente
from ...core.dependencies import get_combatente_service
from ...services.combatente_service import CombatenteService
from ...models.usuario import Usuario
from ...schemas.combatente import (
    CombatenteResponse,
    HPUpdateRequest,
    IniciativaUpdateRequest,
    DanoCuraRequest,
    DanoCuraResponse,
    DanoCuraMassaRequest,
    DanoCuraMassaResponse,
)
from ...exceptions.custom_exceptions import ArenaBaseException

router = APIRouter(prefix="/combatentes", tags=["Combatentes"])


@router.get("", response_model=List[CombatenteResponse])
def listar_combatentes(
    tipo: Optional[str] = None,
    meus: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    response: Response = None,
    service: CombatenteService = Depends(get_combatente_service),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    """Lista todos os combatentes ou filtra por tipo"""
    total = service.contar_todos(tipo, usuario=usuario_atual, apenas_meus=meus)
    if response is not None:
        response.headers["X-Total-Count"] = str(total)
        response.headers["X-Skip"] = str(skip)
        response.headers["X-Limit"] = str(limit)
    return service.listar_todos(
        tipo,
        usuario=usuario_atual,
        skip=skip,
        limit=limit,
        apenas_meus=meus,
    )


@router.get("/{combatente_id}", response_model=CombatenteResponse)
def obter_combatente(
    combatente_id: int,
    service: CombatenteService = Depends(get_combatente_service),
    _: Usuario = Depends(requer_dono_ou_admin_combatente),
):
    """Obtém um combatente específico por ID"""
    try:
        return service.obter_por_id(combatente_id)
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("", response_model=CombatenteResponse, status_code=201)
async def criar_combatente(
    nome:       str = Form(..., max_length=100),
    hp_maximo:  int = Form(...),
    iniciativa: int = Form(...),
    tipo:       str = Form("jogador", max_length=20),
    classe:     str = Form("Aventureiro", max_length=50),
    raca:       Optional[str] = Form(None, max_length=50),
    raca_slug:  Optional[str] = Form(None, max_length=80),
    idiomas_customizados: Optional[str] = Form(None, max_length=1200),
    divindade: Optional[str] = Form(None, max_length=80),
    alinhamento: Optional[str] = Form(None, max_length=30),
    dominios: Optional[str] = Form(None, max_length=120),
    campanha_id: Optional[int] = Form(None),
    # ✅ NOVO
    pagina_referencia: Optional[str] = Form(None, max_length=100),
    # Atributos D&D
    forca:        int = Form(10),
    destreza:     int = Form(10),
    constituicao: int = Form(10),
    inteligencia: int = Form(10),
    sabedoria:    int = Form(10),
    carisma:      int = Form(10),
    # Progressão
    nivel:  int = Form(1),
    pontos: int = Form(0),
    # Economia
    pc: int = Form(0),
    pp: int = Form(0),
    po: int = Form(0),
    pl: int = Form(0),
    foto: Optional[UploadFile] = File(None),
    service: CombatenteService = Depends(get_combatente_service),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    """Cria um novo combatente"""
    combatente_data = {
        "nome":               nome,
        "tipo":               tipo,
        "classe":             classe,
        "raca":               raca or "",
        "raca_slug":          raca_slug or "",
        "idiomas_customizados": idiomas_customizados,
        "divindade":          divindade or "",
        "alinhamento":        alinhamento or "",
        "dominios":           dominios or "",
        "campanha_id":        campanha_id,
        "pagina_referencia":  pagina_referencia or "",   # ✅ NOVO
        "hp_maximo":          hp_maximo,
        "iniciativa":         iniciativa,
        "forca":              forca,
        "destreza":           destreza,
        "constituicao":       constituicao,
        "inteligencia":       inteligencia,
        "sabedoria":          sabedoria,
        "carisma":            carisma,
        "nivel":              nivel,
        "pontos":             pontos,
        "pc":                 pc,
        "pp":                 pp,
        "po":                 po,
        "pl":                 pl,
    }
    try:
        return service.criar(combatente_data, foto, dono_id=usuario_atual.id)
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.put("/{combatente_id}", response_model=CombatenteResponse)
async def atualizar_combatente(
    combatente_id: int,
    nome:          str = Form(..., max_length=100),
    hp_maximo:     int = Form(...),
    iniciativa:    int = Form(...),
    tipo:          str = Form(..., max_length=20),
    classe:        str = Form("Aventureiro", max_length=50),
    raca:          Optional[str] = Form(None, max_length=50),
    raca_slug:     Optional[str] = Form(None, max_length=80),
    idiomas_customizados: Optional[str] = Form(None, max_length=1200),
    divindade: Optional[str] = Form(None, max_length=80),
    alinhamento: Optional[str] = Form(None, max_length=30),
    dominios: Optional[str] = Form(None, max_length=120),
    campanha_id: Optional[int] = Form(None),
    # ✅ NOVO
    pagina_referencia: Optional[str] = Form(None, max_length=100),
    # Atributos D&D
    forca:        int = Form(10),
    destreza:     int = Form(10),
    constituicao: int = Form(10),
    inteligencia: int = Form(10),
    sabedoria:    int = Form(10),
    carisma:      int = Form(10),
    # Progressão
    nivel:  int = Form(1),
    pontos: int = Form(0),
    # Economia
    pc: int = Form(0),
    pp: int = Form(0),
    po: int = Form(0),
    pl: int = Form(0),
    foto: Optional[UploadFile] = File(None),
    service: CombatenteService = Depends(get_combatente_service),
    _: Usuario = Depends(requer_dono_ou_admin_combatente),
):
    """Atualiza um combatente existente"""
    combatente_data = {
        "nome":               nome,
        "tipo":               tipo,
        "classe":             classe,
        "raca":               raca or "",
        "raca_slug":          raca_slug or "",
        "idiomas_customizados": idiomas_customizados,
        "divindade":          divindade or "",
        "alinhamento":        alinhamento or "",
        "dominios":           dominios or "",
        "campanha_id":        campanha_id,
        "pagina_referencia":  pagina_referencia or "",   # ✅ NOVO
        "hp_maximo":          hp_maximo,
        "iniciativa":         iniciativa,
        "forca":              forca,
        "destreza":           destreza,
        "constituicao":       constituicao,
        "inteligencia":       inteligencia,
        "sabedoria":          sabedoria,
        "carisma":            carisma,
        "nivel":              nivel,
        "pontos":             pontos,
        "pc":                 pc,
        "pp":                 pp,
        "po":                 po,
        "pl":                 pl,
    }
    try:
        return service.atualizar(combatente_id, combatente_data, foto)
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.patch("/{combatente_id}/hp", response_model=CombatenteResponse)
def atualizar_hp(
    combatente_id: int,
    hp_data: HPUpdateRequest,
    service: CombatenteService = Depends(get_combatente_service),
    _: Usuario = Depends(requer_dono_ou_admin_combatente),
):
    """Atualiza apenas o HP atual de um combatente"""
    try:
        return service.atualizar_hp(combatente_id, hp_data.hp_atual)
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.patch("/{combatente_id}/iniciativa", response_model=CombatenteResponse)
def atualizar_iniciativa(
    combatente_id: int,
    ini_data: IniciativaUpdateRequest,
    service: CombatenteService = Depends(get_combatente_service),
    _: Usuario = Depends(requer_dono_ou_admin_combatente),
):
    """Atualiza apenas a iniciativa de um combatente"""
    try:
        return service.atualizar_iniciativa(combatente_id, ini_data.iniciativa)
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/{combatente_id}/dano", response_model=DanoCuraResponse)
def aplicar_dano(
    combatente_id: int,
    dano_data: DanoCuraRequest,
    service: CombatenteService = Depends(get_combatente_service),
    _: Usuario = Depends(requer_dono_ou_admin_combatente),
):
    """Aplica dano a um combatente"""
    try:
        return service.aplicar_dano(combatente_id, dano_data.valor)
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/{combatente_id}/cura", response_model=DanoCuraResponse)
def aplicar_cura(
    combatente_id: int,
    cura_data: DanoCuraRequest,
    service: CombatenteService = Depends(get_combatente_service),
    _: Usuario = Depends(requer_dono_ou_admin_combatente),
):
    """Aplica cura a um combatente"""
    try:
        return service.aplicar_cura(combatente_id, cura_data.valor)
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/dano/massa", response_model=DanoCuraMassaResponse)
def aplicar_dano_massa(
    dano_data: DanoCuraMassaRequest,
    service: CombatenteService = Depends(get_combatente_service),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    """Aplica dano em lote para múltiplos combatentes."""
    try:
        return service.aplicar_dano_massa(
            dano_data.combatente_ids,
            dano_data.valor,
            usuario_atual,
        )
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/cura/massa", response_model=DanoCuraMassaResponse)
def aplicar_cura_massa(
    cura_data: DanoCuraMassaRequest,
    service: CombatenteService = Depends(get_combatente_service),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    """Aplica cura em lote para múltiplos combatentes."""
    try:
        return service.aplicar_cura_massa(
            cura_data.combatente_ids,
            cura_data.valor,
            usuario_atual,
        )
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.patch("/{combatente_id}", response_model=CombatenteResponse)
def atualizar_parcial(
    combatente_id: int,
    data: dict,
    service: CombatenteService = Depends(get_combatente_service),
    _: Usuario = Depends(requer_dono_ou_admin_combatente),
):
    """Atualiza campos específicos de um combatente"""
    try:
        return service.atualizar(combatente_id, data)
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.delete("/{combatente_id}")
def deletar_combatente(
    combatente_id: int,
    service: CombatenteService = Depends(get_combatente_service),
    _: Usuario = Depends(requer_dono_ou_admin_combatente),
):
    """Deleta um combatente"""
    try:
        service.deletar(combatente_id)
        return {"message": "Combatente deletado com sucesso"}
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/{combatente_id}/inicializar-slots", status_code=200)
def inicializar_slots(
    combatente_id: int,
    service: CombatenteService = Depends(get_combatente_service),
    _: Usuario = Depends(requer_dono_ou_admin_combatente),
):
    """Inicializa slots de magia para um combatente"""
    try:
        return service.inicializar_slots_magia(combatente_id)
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)