"""Endpoints do Grimório (D&D 3.5) — canônico em `app.games.dnd35.api.v1.grimorio` (registrado em `app.main`)."""

from __future__ import annotations

import json
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from app.core.dependencies import get_grimorio_service
from app.games.dnd35.schemas.grimorio import (
    GrimorioDiagnosticoResponse,
    GrimorioHistoricoTrocaResponse,
    GrimorioMagiaCreate,
    GrimorioMagiaResponse,
    GrimorioMagiaUpdate,
    GrimorioNotificacaoResponse,
    GrimorioNotificacaoUpdate,
    GrimorioTrocaRequest,
    GrimorioTrocaResponse,
)
from app.games.dnd35.services.grimorio_service import (
    GrimorioService,
    _nivel_por_classe,
    _normalizar as _normalizar_classe_grimorio,
)
from app.shared.core.database import get_db
from app.shared.core.deps import requer_dono_ou_admin_combatente, requer_game_dnd35

router = APIRouter(
    prefix="/grimorio",
    tags=["Grimório"],
    dependencies=[Depends(requer_game_dnd35)],
)


def _parse_magia_ids(values: Optional[list[str]]) -> Optional[list[int]]:
    if not values:
        return None

    tokens: list[str] = []
    for value in values:
        for token in str(value or "").split(","):
            token = token.strip()
            if token:
                tokens.append(token)

    if not tokens:
        return None

    try:
        return list(dict.fromkeys(int(token) for token in tokens))
    except ValueError as exc:
        raise HTTPException(
            status_code=422, detail="magia_ids deve conter apenas inteiros"
        ) from exc


def _serialize(item) -> dict:
    magia = item.magia
    classe_norm = _normalizar_classe_grimorio(item.classe) if item.classe else None
    magia_nivel = None
    if magia:
        magia_nivel = (
            _nivel_por_classe(magia, classe_norm) if classe_norm else magia.nivel
        )
    return {
        "id": item.id,
        "combatente_id": item.combatente_id,
        "magia_id": item.magia_id,
        "classe": item.classe,
        "favorita": item.favorita,
        "anotacoes": item.anotacoes,
        "origem": item.origem,
        "adicionada_em": item.adicionada_em,
        "magia_nome": magia.nome if magia else None,
        "magia_escola": magia.escola if magia else None,
        "magia_nivel": magia_nivel,
        "magia_componentes": magia.componentes if magia else None,
        "magia_e_magia_dominio": bool(magia.e_magia_dominio) if magia else False,
        "magia_dominios": magia.dominios if magia else None,
        "descricao": magia.descricao if magia else None,
        "sub_escola": magia.sub_escola if magia else None,
        "area_efeito": magia.area_efeito if magia else None,
        "resistencia_magia": magia.resistencia_magia_texto if magia else None,
    }


def _serialize_notificacao(item) -> dict:
    dados = {}
    if item.dados:
        try:
            dados = json.loads(item.dados)
        except Exception:
            dados = {}

    return {
        "id": item.id,
        "combatente_id": item.combatente_id,
        "classe": item.classe,
        "tipo": item.tipo,
        "dados": dados,
        "lida": bool(item.lida),
        "criada_em": item.criada_em,
    }


@router.get("/{combatente_id}", response_model=list[GrimorioMagiaResponse])
def listar_grimorio(
    combatente_id: int,
    nome: Optional[str] = Query(default=None),
    nivel: Optional[int] = Query(default=None, ge=0, le=9),
    escola: Optional[str] = Query(default=None),
    componentes: Optional[str] = Query(default=None),
    magia_ids: Optional[list[str]] = Query(default=None),
    classe: Optional[str] = Query(default=None),
    favorita: Optional[bool] = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: Optional[int] = Query(default=None, ge=1, le=200),
    response: Response = None,
    service: GrimorioService = Depends(get_grimorio_service),
    _: object = Depends(requer_dono_ou_admin_combatente),
):
    magia_ids_parseados = _parse_magia_ids(magia_ids)
    total, itens = service.listar_paginado(
        combatente_id,
        nome=nome,
        nivel=nivel,
        escola=escola,
        componentes=componentes,
        magia_ids=magia_ids_parseados,
        classe=classe,
        favorita=favorita,
        skip=skip,
        limit=limit,
    )
    payload = [_serialize(item) for item in itens]
    if response is not None:
        response.headers["X-Total-Count"] = str(total)
        response.headers["X-Skip"] = str(skip)
        response.headers["X-Limit"] = str(limit if limit is not None else len(payload))
    return payload


@router.get("/{combatente_id}/diagnostico", response_model=GrimorioDiagnosticoResponse)
def diagnosticar_regras_grimorio(
    combatente_id: int,
    classe: Optional[str] = Query(default=None),
    service: GrimorioService = Depends(get_grimorio_service),
    _: object = Depends(requer_dono_ou_admin_combatente),
):
    return service.diagnosticar_regras_divinas(combatente_id, classe=classe)


@router.post(
    "/{combatente_id}",
    response_model=GrimorioMagiaResponse,
    status_code=status.HTTP_201_CREATED,
)
def adicionar_magia_grimorio(
    combatente_id: int,
    payload: GrimorioMagiaCreate,
    service: GrimorioService = Depends(get_grimorio_service),
    _: object = Depends(requer_dono_ou_admin_combatente),
):
    item = service.adicionar_magia(
        combatente_id,
        magia_id=payload.magia_id,
        classe=payload.classe,
        origem=payload.origem,
    )
    return _serialize(item)


@router.patch("/{combatente_id}/{magia_id}", response_model=GrimorioMagiaResponse)
def atualizar_item_grimorio(
    combatente_id: int,
    magia_id: int,
    payload: GrimorioMagiaUpdate,
    classe: str = Query(...),
    service: GrimorioService = Depends(get_grimorio_service),
    _: object = Depends(requer_dono_ou_admin_combatente),
):
    item = service.atualizar_item(
        combatente_id,
        magia_id,
        classe=classe,
        favorita=payload.favorita,
        anotacoes=payload.anotacoes,
    )
    return _serialize(item)


@router.delete("/{combatente_id}/{magia_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_magia_grimorio(
    combatente_id: int,
    magia_id: int,
    classe: str = Query(...),
    service: GrimorioService = Depends(get_grimorio_service),
    _: object = Depends(requer_dono_ou_admin_combatente),
):
    service.remover_magia(combatente_id, magia_id, classe=classe)
    return None


@router.get(
    "/{combatente_id}/historico", response_model=list[GrimorioHistoricoTrocaResponse]
)
def listar_historico_troca(
    combatente_id: int,
    classe: Optional[str] = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    service: GrimorioService = Depends(get_grimorio_service),
    _: object = Depends(requer_dono_ou_admin_combatente),
):
    historico = service.listar_historico_troca(
        combatente_id, classe=classe, limit=limit
    )
    return [
        {
            "id": item.id,
            "combatente_id": item.combatente_id,
            "classe": item.classe,
            "magia_removida_id": item.magia_removida_id,
            "magia_adicionada_id": item.magia_adicionada_id,
            "nivel_personagem": item.nivel_personagem,
            "realizada_em": item.realizada_em,
            "magia_removida_nome": (
                item.magia_removida.nome if item.magia_removida else None
            ),
            "magia_adicionada_nome": (
                item.magia_adicionada.nome if item.magia_adicionada else None
            ),
        }
        for item in historico
    ]


@router.post("/{combatente_id}/troca", response_model=GrimorioTrocaResponse)
def trocar_magia_grimorio(
    combatente_id: int,
    payload: GrimorioTrocaRequest,
    service: GrimorioService = Depends(get_grimorio_service),
    _: object = Depends(requer_dono_ou_admin_combatente),
):
    historico = service.trocar_magia(
        combatente_id,
        classe=payload.classe,
        magia_removida_id=payload.magia_removida_id,
        magia_adicionada_id=payload.magia_adicionada_id,
    )
    return {
        "combatente_id": historico.combatente_id,
        "classe": historico.classe,
        "magia_removida_id": historico.magia_removida_id,
        "magia_adicionada_id": historico.magia_adicionada_id,
        "nivel_personagem": historico.nivel_personagem,
        "realizada_em": historico.realizada_em,
    }


@router.get(
    "/{combatente_id}/notificacoes", response_model=list[GrimorioNotificacaoResponse]
)
def listar_notificacoes_grimorio(
    combatente_id: int,
    classe: Optional[str] = Query(default=None),
    apenas_nao_lidas: bool = Query(default=False),
    limit: int = Query(default=30, ge=1, le=100),
    force_sync: bool = Query(
        default=True,
        description="Passa false para polling leve sem sincronização automática",
    ),
    service: GrimorioService = Depends(get_grimorio_service),
    _: object = Depends(requer_dono_ou_admin_combatente),
):
    itens = service.listar_notificacoes(
        combatente_id,
        classe=classe,
        apenas_nao_lidas=apenas_nao_lidas,
        limit=limit,
        force_sync=force_sync,
    )
    return [_serialize_notificacao(item) for item in itens]


@router.patch(
    "/{combatente_id}/notificacoes/{notificacao_id}",
    response_model=GrimorioNotificacaoResponse,
)
def atualizar_notificacao_grimorio(
    combatente_id: int,
    notificacao_id: int,
    payload: GrimorioNotificacaoUpdate,
    service: GrimorioService = Depends(get_grimorio_service),
    _: object = Depends(requer_dono_ou_admin_combatente),
):
    item = service.marcar_notificacao_lida(
        combatente_id, notificacao_id, lida=payload.lida
    )
    return _serialize_notificacao(item)


@router.delete(
    "/{combatente_id}/notificacoes/{notificacao_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def descartar_notificacao_grimorio(
    combatente_id: int,
    notificacao_id: int,
    service: GrimorioService = Depends(get_grimorio_service),
    _: object = Depends(requer_dono_ou_admin_combatente),
):
    service.descartar_notificacao(combatente_id, notificacao_id)
    return None
