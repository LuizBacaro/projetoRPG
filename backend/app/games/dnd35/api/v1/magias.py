"""
Endpoints do catálogo de magias (D&D 3.5).

Localização: `app.games.dnd35.api.v1.magias`. Shim em `app.api.v1.magias`
durante a reorganização multi-jogo.
"""

from io import BytesIO

from fastapi import APIRouter, Depends, File, HTTPException, Query, Response, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.catalog_cache import catalog_cache, make_cache_key
from app.core.config import settings
from app.core.text_utils import normalizar_classe_acesso
from app.core.dependencies import get_magia_import_service, get_magia_service
from app.core.database import get_db
from app.core.deps import requer_mestre_ou_admin
from app.games.dnd35.models.magia import Magia
from app.games.dnd35.repositories.magia_repository import MagiaRepository
from app.games.dnd35.schemas.magia import (
    MagiaCreate,
    MagiaImportConfirmRequest,
    MagiaImportConfirmResponse,
    MagiaHistoricoResponse,
    MagiaImportPreviewResponse,
    MagiaResponse,
    MagiaUpdate,
)
from app.games.dnd35.services.magia_import_service import MagiaImportService
from app.games.dnd35.services.magia_service import MagiaService
from app.services.divindade_custom_service import build_divindade_custom_service

router = APIRouter(prefix="/magias", tags=["Magias"])


def _serialize_magia(magia: Magia) -> dict:
    return {
        "id": getattr(magia, "id", None),
        "nome": getattr(magia, "nome", None),
        "nome_en": getattr(magia, "nome_en", None),
        "nivel": getattr(magia, "nivel", None),
        "classe": getattr(magia, "classe", None),
        "escola": getattr(magia, "escola", None),
        "sub_escola": getattr(magia, "sub_escola", None),
        "descritor": getattr(magia, "descritor", None),
        "componentes": getattr(magia, "componentes", None),
        "componente_extra": getattr(magia, "componente_extra", None),
        "alcance": getattr(magia, "alcance", None),
        "area_efeito": getattr(magia, "area_efeito", None),
        "duracao": getattr(magia, "duracao", None),
        "tempo_conjuracao": getattr(magia, "tempo_conjuracao", None),
        "dano": getattr(magia, "dano", None),
        "teste_resistencia": getattr(magia, "teste_resistencia", None),
        "resistencia_magica": getattr(magia, "resistencia_magica", False),
        "resistencia_magia_texto": getattr(magia, "resistencia_magia_texto", None),
        "descricao": getattr(magia, "descricao", None),
        "descricao_en": getattr(magia, "descricao_en", None),
        "ativo": getattr(magia, "ativo", True),
        "e_magia_dominio": getattr(magia, "e_magia_dominio", False),
        "dominios": getattr(magia, "dominios", None),
        "pagina_referencia": getattr(magia, "pagina_referencia", None),
        "eh_truque": getattr(magia, "eh_truque", False),
        "tem_dano": getattr(magia, "tem_dano", False),
        "classes_niveis": [
            {"id": cn.id, "classe": cn.classe, "nivel": cn.nivel}
            for cn in (getattr(magia, "classes_niveis", []) or [])
        ],
        "data_criacao": getattr(magia, "data_criacao", None),
    }


def _resolve_service(service: Optional[MagiaService], db: Session) -> MagiaService:
    if isinstance(service, MagiaService):
        return service
    return MagiaService(MagiaRepository(db))


def _sanitize_query_value(value):
    return None if hasattr(value, "default") else value


@router.get("/", response_model=List[MagiaResponse])
def listar_magias(
    classe: Optional[str] = Query(None, description="Filtrar por classe: Mago, Clérigo, Druida, Bardo, Paladino, Ranger"),
    nivel:  Optional[int] = Query(None, ge=0, le=9, description="Filtrar por nível (0-9)"),
    escola: Optional[str] = Query(None, description="Filtrar por escola de magia"),
    nome:   Optional[str] = Query(None, description="Buscar por nome (parcial)"),
    componentes: Optional[str] = Query(None, description="Filtrar por componentes (ex: V,S)"),
    dominio: Optional[str] = Query(None, description="Filtrar por domínio"),
    ativo: Optional[bool] = Query(None, description="Filtrar por status ativa/inativa"),
    sort_by: Optional[str] = Query(None, description="Ordenacao por campo: nome, escola, nivel"),
    sort_dir: Optional[str] = Query("asc", description="Direcao da ordenacao: asc ou desc"),
    skip:   int = Query(0, ge=0, description="Quantidade de registros para pular"),
    limit:  int = Query(100, ge=1, le=500, description="Quantidade máxima de registros retornados"),
    response: Response = None,
    db:     Session        = Depends(get_db),
    service: Optional[MagiaService] = Depends(get_magia_service),
):
    """
    Lista magias com filtros opcionais.

    Exemplos:
    - GET /api/v1/magias?classe=Mago&nivel=3
    - GET /api/v1/magias?classe=Clérigo
    - GET /api/v1/magias?nome=bola
    """
    classe = _sanitize_query_value(classe)
    nivel = _sanitize_query_value(nivel)
    escola = _sanitize_query_value(escola)
    nome = _sanitize_query_value(nome)
    componentes = _sanitize_query_value(componentes)
    dominio = _sanitize_query_value(dominio)
    ativo = _sanitize_query_value(ativo)
    sort_by = _sanitize_query_value(sort_by)
    sort_dir = _sanitize_query_value(sort_dir)

    # Mesma normalização do repositório (acentos, maiúsculas, Feiticeiro→Mago, Patrulheiro→Ranger)
    classe_normalizado = None
    if classe and str(classe).strip():
        token = normalizar_classe_acesso(str(classe).strip())
        classe_normalizado = token or None

    cache_key = make_cache_key(
        "magias:list",
        classe=classe_normalizado,
        nivel=nivel,
        escola=escola,
        nome=nome,
        componentes=componentes,
        dominio=dominio,
        ativo=ativo,
        sort_by=sort_by,
        sort_dir=sort_dir,
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

    srv = _resolve_service(service, db)
    total, rows = srv.listar_magias(
        classe=classe_normalizado,
        nivel=nivel,
        escola=escola,
        nome=nome,
        componentes=componentes,
        dominio=dominio,
        ativo=ativo,
        sort_by=sort_by,
        sort_dir=sort_dir,
        skip=skip,
        limit=limit,
    )
    items = [_serialize_magia(magia) for magia in rows]

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
def listar_classes(
    db: Session = Depends(get_db),
    service: Optional[MagiaService] = Depends(get_magia_service),
):
    """Retorna lista de classes disponíveis."""
    cache_key = "magias:classes"
    if settings.CACHE_ENABLED:
        cached = catalog_cache.get(cache_key)
        if cached is not None:
            return cached

    srv = _resolve_service(service, db)
    classes = srv.listar_classes()
    if settings.CACHE_ENABLED:
        catalog_cache.set(cache_key, classes, settings.CACHE_CATALOG_TTL_SECONDS)
    return classes


@router.get("/dominios", response_model=List[str])
def listar_dominios(
    db: Session = Depends(get_db),
    service: Optional[MagiaService] = Depends(get_magia_service),
):
    cache_key = "magias:dominios"
    if settings.CACHE_ENABLED:
        cached = catalog_cache.get(cache_key)
        if cached is not None:
            return cached

    srv = _resolve_service(service, db)
    dominios = srv.listar_dominios()
    if settings.CACHE_ENABLED:
        catalog_cache.set(cache_key, dominios, settings.CACHE_CATALOG_TTL_SECONDS)
    return dominios


@router.get("/divindades", response_model=List[str])
def listar_divindades_sugeridas(
    db: Session = Depends(get_db),
    service: Optional[MagiaService] = Depends(get_magia_service),
):
    """Lista apenas os nomes canonicos (oficial + customizadas).
    Retrocompatibilidade — o endpoint novo e `/magias/divindades/catalogo`."""
    cache_key = "magias:divindades"
    if settings.CACHE_ENABLED:
        cached = catalog_cache.get(cache_key)
        if cached is not None:
            return cached

    unificado = build_divindade_custom_service(db).listar_catalogo_unificado()
    nomes = [item["nome"] for item in unificado]
    if settings.CACHE_ENABLED:
        catalog_cache.set(cache_key, nomes, settings.CACHE_CATALOG_TTL_SECONDS)
    return nomes


@router.get("/divindades/catalogo")
def listar_divindades_catalogo(
    db: Session = Depends(get_db),
    service: Optional[MagiaService] = Depends(get_magia_service),
):
    """Catalogo rico de divindades: oficial (Tabela 3-7) + customizadas da
    campanha. Cada item traz: nome, titulo, label ('Nome, Titulo'), tendencia,
    dominios (lista canonica), descricao curta e `origem` ('oficial' | 'custom').
    """
    cache_key = "magias:divindades:catalogo"
    if settings.CACHE_ENABLED:
        cached = catalog_cache.get(cache_key)
        if cached is not None:
            return cached

    # Nota: listar_divindades_catalogo() retorna apenas o catalogo oficial.
    # O endpoint unifica com as customizadas para que o frontend nao precise
    # fazer duas chamadas (oficial + /divindades/custom).
    unificado = build_divindade_custom_service(db).listar_catalogo_unificado()
    if settings.CACHE_ENABLED:
        catalog_cache.set(cache_key, unificado, settings.CACHE_CATALOG_TTL_SECONDS)
    return unificado


@router.get("/importacao/modelo")
def baixar_modelo_importacao(
    service: MagiaImportService = Depends(get_magia_import_service),
    _: object = Depends(requer_mestre_ou_admin),
):
    content = service.gerar_modelo()
    filename = "modelo_importacao_magias.xlsx"
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return StreamingResponse(
        BytesIO(content),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )


@router.post("/importacao/preview", response_model=MagiaImportPreviewResponse)
async def preview_importacao_magias(
    arquivo: UploadFile = File(...),
    service: MagiaImportService = Depends(get_magia_import_service),
    _: object = Depends(requer_mestre_ou_admin),
):
    return await service.criar_preview(arquivo)


@router.post("/importacao/confirmar", response_model=MagiaImportConfirmResponse)
def confirmar_importacao_magias(
    payload: MagiaImportConfirmRequest,
    service: MagiaImportService = Depends(get_magia_import_service),
    _: object = Depends(requer_mestre_ou_admin),
):
    result = service.confirmar_importacao(payload.import_id)
    if settings.CACHE_ENABLED and result.get("importadas", 0) > 0:
        catalog_cache.invalidate_prefix("magias:")
    return result


@router.get("/{magia_id}", response_model=MagiaResponse)
def obter_magia(
    magia_id: int,
    db: Session = Depends(get_db),
    service: Optional[MagiaService] = Depends(get_magia_service),
):
    """Retorna detalhes de uma magia específica."""
    cache_key = make_cache_key("magias:detail", magia_id=magia_id)
    if settings.CACHE_ENABLED:
        cached = catalog_cache.get(cache_key)
        if cached is not None:
            return cached

    srv = _resolve_service(service, db)
    magia = srv.obter_por_id(magia_id)

    item = _serialize_magia(magia)
    if settings.CACHE_ENABLED:
        catalog_cache.set(cache_key, item, settings.CACHE_CATALOG_TTL_SECONDS)
    return item


@router.post("/", response_model=MagiaResponse, status_code=status.HTTP_201_CREATED)
def criar_magia(
    payload: MagiaCreate,
    db: Session = Depends(get_db),
    service: Optional[MagiaService] = Depends(get_magia_service),
    usuario=Depends(requer_mestre_ou_admin),
):
    magia = _resolve_service(service, db).criar(payload, usuario_id=getattr(usuario, "id", None))
    if settings.CACHE_ENABLED:
        catalog_cache.invalidate_prefix("magias:")
    return _serialize_magia(magia)


@router.put("/{magia_id}", response_model=MagiaResponse)
def atualizar_magia(
    magia_id: int,
    payload: MagiaUpdate,
    db: Session = Depends(get_db),
    service: Optional[MagiaService] = Depends(get_magia_service),
    usuario=Depends(requer_mestre_ou_admin),
):
    magia = _resolve_service(service, db).atualizar(
        magia_id,
        payload,
        usuario_id=getattr(usuario, "id", None),
    )
    if settings.CACHE_ENABLED:
        catalog_cache.invalidate_prefix("magias:")
    return _serialize_magia(magia)


@router.patch("/{magia_id}/desativar", response_model=MagiaResponse)
def desativar_magia(
    magia_id: int,
    db: Session = Depends(get_db),
    service: Optional[MagiaService] = Depends(get_magia_service),
    usuario=Depends(requer_mestre_ou_admin),
):
    magia = _resolve_service(service, db).desativar(magia_id, usuario_id=getattr(usuario, "id", None))
    if settings.CACHE_ENABLED:
        catalog_cache.invalidate_prefix("magias:")
    return _serialize_magia(magia)


@router.patch("/{magia_id}/reativar", response_model=MagiaResponse)
def reativar_magia(
    magia_id: int,
    db: Session = Depends(get_db),
    service: Optional[MagiaService] = Depends(get_magia_service),
    usuario=Depends(requer_mestre_ou_admin),
):
    magia = _resolve_service(service, db).reativar(magia_id, usuario_id=getattr(usuario, "id", None))
    if settings.CACHE_ENABLED:
        catalog_cache.invalidate_prefix("magias:")
    return _serialize_magia(magia)


@router.delete("/{magia_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_magia(
    magia_id: int,
    db: Session = Depends(get_db),
    service: Optional[MagiaService] = Depends(get_magia_service),
    usuario=Depends(requer_mestre_ou_admin),
):
    _resolve_service(service, db).deletar_fisico(magia_id, usuario_id=getattr(usuario, "id", None))
    if settings.CACHE_ENABLED:
        catalog_cache.invalidate_prefix("magias:")
    return None


@router.get("/{magia_id}/historico", response_model=List[MagiaHistoricoResponse])
def listar_historico_magia(
    magia_id: int,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    service: Optional[MagiaService] = Depends(get_magia_service),
    _: object = Depends(requer_mestre_ou_admin),
):
    return _resolve_service(service, db).listar_historico(magia_id, limit=limit)

