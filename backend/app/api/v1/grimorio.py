"""Endpoints do módulo Grimório."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from typing import Optional
import json

from app.core.database import get_db
from app.core.dependencies import get_grimorio_service
from app.core.deps import requer_dono_ou_admin_combatente
from app.schemas.grimorio import (
    GrimorioHistoricoTrocaResponse,
    GrimorioMagiaCreate,
    GrimorioMagiaResponse,
    GrimorioMagiaUpdate,
    GrimorioNotificacaoResponse,
    GrimorioNotificacaoUpdate,
    GrimorioTrocaRequest,
    GrimorioTrocaResponse,
)
from app.services.grimorio_service import GrimorioService

router = APIRouter(prefix="/grimorio", tags=["Grimório"])


def _serialize(item) -> dict:
    magia = item.magia
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
        "magia_nivel": magia.nivel if magia else None,
        "magia_componentes": magia.componentes if magia else None,
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
    classe: Optional[str] = Query(default=None),
    favorita: Optional[bool] = Query(default=None),
    service: GrimorioService = Depends(get_grimorio_service),
    _: object = Depends(requer_dono_ou_admin_combatente),
):
    itens = service.listar(combatente_id, classe=classe, favorita=favorita)
    return [_serialize(item) for item in itens]


@router.post("/{combatente_id}", response_model=GrimorioMagiaResponse, status_code=status.HTTP_201_CREATED)
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


@router.get("/{combatente_id}/historico", response_model=list[GrimorioHistoricoTrocaResponse])
def listar_historico_troca(
    combatente_id: int,
    classe: Optional[str] = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    service: GrimorioService = Depends(get_grimorio_service),
    _: object = Depends(requer_dono_ou_admin_combatente),
):
    historico = service.listar_historico_troca(combatente_id, classe=classe, limit=limit)
    return [
        {
            "id": item.id,
            "combatente_id": item.combatente_id,
            "classe": item.classe,
            "magia_removida_id": item.magia_removida_id,
            "magia_adicionada_id": item.magia_adicionada_id,
            "nivel_personagem": item.nivel_personagem,
            "realizada_em": item.realizada_em,
            "magia_removida_nome": item.magia_removida.nome if item.magia_removida else None,
            "magia_adicionada_nome": item.magia_adicionada.nome if item.magia_adicionada else None,
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


@router.get("/{combatente_id}/notificacoes", response_model=list[GrimorioNotificacaoResponse])
def listar_notificacoes_grimorio(
    combatente_id: int,
    classe: Optional[str] = Query(default=None),
    apenas_nao_lidas: bool = Query(default=False),
    limit: int = Query(default=30, ge=1, le=100),
    service: GrimorioService = Depends(get_grimorio_service),
    _: object = Depends(requer_dono_ou_admin_combatente),
):
    itens = service.listar_notificacoes(
        combatente_id,
        classe=classe,
        apenas_nao_lidas=apenas_nao_lidas,
        limit=limit,
    )
    return [_serialize_notificacao(item) for item in itens]


@router.patch("/{combatente_id}/notificacoes/{notificacao_id}", response_model=GrimorioNotificacaoResponse)
def atualizar_notificacao_grimorio(
    combatente_id: int,
    notificacao_id: int,
    payload: GrimorioNotificacaoUpdate,
    service: GrimorioService = Depends(get_grimorio_service),
    _: object = Depends(requer_dono_ou_admin_combatente),
):
    item = service.marcar_notificacao_lida(combatente_id, notificacao_id, lida=payload.lida)
    return _serialize_notificacao(item)


@router.delete("/{combatente_id}/notificacoes/{notificacao_id}", status_code=status.HTTP_204_NO_CONTENT)
def descartar_notificacao_grimorio(
    combatente_id: int,
    notificacao_id: int,
    service: GrimorioService = Depends(get_grimorio_service),
    _: object = Depends(requer_dono_ou_admin_combatente),
):
    service.descartar_notificacao(combatente_id, notificacao_id)
    return None
