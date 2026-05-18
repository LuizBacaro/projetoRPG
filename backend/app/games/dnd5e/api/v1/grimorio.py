"""HTTP — grimório D&D 5e (paridade com dnd35, personagem_id no lugar de combatente_id)."""

from __future__ import annotations

import json
from typing import Optional

from fastapi import APIRouter, Depends, Query, Response, status

from app.core.dependencies import get_dnd5e_grimorio_service
from app.games.dnd5e.schemas.grimorio import (
    Dnd5eGrimorioHistoricoTrocaResponse,
    Dnd5eGrimorioMagiaCreate,
    Dnd5eGrimorioMagiaResponse,
    Dnd5eGrimorioMagiaUpdate,
    Dnd5eGrimorioNotificacaoResponse,
    Dnd5eGrimorioNotificacaoUpdate,
    Dnd5eGrimorioTrocaRequest,
    Dnd5eGrimorioTrocaResponse,
)
from app.games.dnd5e.services.grimorio_service import (
    Dnd5eGrimorioService,
    grimorio_item_para_dict,
)
from app.shared.core.deps import (
    requer_dono_ou_admin_dnd5e_personagem,
    requer_game_dnd5e,
)


def _serialize_notificacao(item) -> dict:
    dados = {}
    if item.dados:
        try:
            dados = json.loads(item.dados)
        except json.JSONDecodeError:
            dados = {"raw": item.dados}
    return {
        "id": item.id,
        "personagem_id": item.personagem_id,
        "combatente_id": item.personagem_id,
        "classe": item.classe,
        "tipo": item.tipo,
        "dados": dados,
        "lida": item.lida,
        "criada_em": item.criada_em,
    }


router = APIRouter(
    prefix="/dnd5e/grimorio",
    tags=["D&D 5e — Grimório"],
    dependencies=[Depends(requer_game_dnd5e)],
)


@router.get("/{personagem_id}", response_model=list[Dnd5eGrimorioMagiaResponse])
def listar_grimorio(
    personagem_id: int,
    nome: Optional[str] = Query(default=None),
    nivel: Optional[int] = Query(default=None, ge=0, le=9),
    escola: Optional[str] = Query(default=None),
    classe: Optional[str] = Query(default=None),
    favorita: Optional[bool] = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: Optional[int] = Query(default=None, ge=1, le=200),
    response: Response = None,
    service: Dnd5eGrimorioService = Depends(get_dnd5e_grimorio_service),
    _: object = Depends(requer_dono_ou_admin_dnd5e_personagem),
):
    total, itens = service.listar_paginado(
        personagem_id,
        nome=nome,
        nivel=nivel,
        escola=escola,
        classe=classe,
        favorita=favorita,
        skip=skip,
        limit=limit,
    )
    payload = [grimorio_item_para_dict(item) for item in itens]
    if response is not None:
        response.headers["X-Total-Count"] = str(total)
        response.headers["X-Skip"] = str(skip)
        response.headers["X-Limit"] = str(limit if limit is not None else len(payload))
    return payload


@router.post(
    "/{personagem_id}",
    response_model=Dnd5eGrimorioMagiaResponse,
    status_code=status.HTTP_201_CREATED,
)
def adicionar_magia_grimorio(
    personagem_id: int,
    payload: Dnd5eGrimorioMagiaCreate,
    service: Dnd5eGrimorioService = Depends(get_dnd5e_grimorio_service),
    _: object = Depends(requer_dono_ou_admin_dnd5e_personagem),
):
    item = service.adicionar_magia(
        personagem_id,
        magia_id=payload.magia_id,
        classe=payload.classe,
        origem=payload.origem,
    )
    return grimorio_item_para_dict(item)


@router.patch("/{personagem_id}/{magia_id}", response_model=Dnd5eGrimorioMagiaResponse)
def atualizar_item_grimorio(
    personagem_id: int,
    magia_id: int,
    payload: Dnd5eGrimorioMagiaUpdate,
    classe: str = Query(...),
    service: Dnd5eGrimorioService = Depends(get_dnd5e_grimorio_service),
    _: object = Depends(requer_dono_ou_admin_dnd5e_personagem),
):
    item = service.atualizar_item(
        personagem_id,
        magia_id,
        classe=classe,
        favorita=payload.favorita,
        anotacoes=payload.anotacoes,
    )
    return grimorio_item_para_dict(item)


@router.delete("/{personagem_id}/{magia_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_magia_grimorio(
    personagem_id: int,
    magia_id: int,
    classe: str = Query(...),
    service: Dnd5eGrimorioService = Depends(get_dnd5e_grimorio_service),
    _: object = Depends(requer_dono_ou_admin_dnd5e_personagem),
):
    service.remover_magia(personagem_id, magia_id, classe=classe)
    return None


@router.get(
    "/{personagem_id}/historico",
    response_model=list[Dnd5eGrimorioHistoricoTrocaResponse],
)
@router.get(
    "/{personagem_id}/historico-troca",
    response_model=list[Dnd5eGrimorioHistoricoTrocaResponse],
)
def listar_historico_troca_grimorio(
    personagem_id: int,
    classe: Optional[str] = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    service: Dnd5eGrimorioService = Depends(get_dnd5e_grimorio_service),
    _: object = Depends(requer_dono_ou_admin_dnd5e_personagem),
):
    historico = service.listar_historico_troca(
        personagem_id, classe=classe, limit=limit
    )
    return [
        {
            "id": h.id,
            "personagem_id": h.personagem_id,
            "combatente_id": h.personagem_id,
            "classe": h.classe,
            "magia_removida_id": h.magia_removida_id,
            "magia_adicionada_id": h.magia_adicionada_id,
            "nivel_personagem": h.nivel_personagem,
            "realizada_em": h.realizada_em,
            "magia_removida_nome": h.magia_removida.nome if h.magia_removida else None,
            "magia_adicionada_nome": (
                h.magia_adicionada.nome if h.magia_adicionada else None
            ),
        }
        for h in historico
    ]


@router.post("/{personagem_id}/troca", response_model=Dnd5eGrimorioTrocaResponse)
def trocar_magia_grimorio(
    personagem_id: int,
    payload: Dnd5eGrimorioTrocaRequest,
    service: Dnd5eGrimorioService = Depends(get_dnd5e_grimorio_service),
    _: object = Depends(requer_dono_ou_admin_dnd5e_personagem),
):
    historico = service.trocar_magia(
        personagem_id,
        classe=payload.classe,
        magia_removida_id=payload.magia_removida_id,
        magia_adicionada_id=payload.magia_adicionada_id,
    )
    return {
        "personagem_id": historico.personagem_id,
        "combatente_id": historico.personagem_id,
        "classe": historico.classe,
        "magia_removida_id": historico.magia_removida_id,
        "magia_adicionada_id": historico.magia_adicionada_id,
        "nivel_personagem": historico.nivel_personagem,
        "realizada_em": historico.realizada_em,
    }


@router.get(
    "/{personagem_id}/notificacoes",
    response_model=list[Dnd5eGrimorioNotificacaoResponse],
)
def listar_notificacoes_grimorio(
    personagem_id: int,
    classe: Optional[str] = Query(default=None),
    apenas_nao_lidas: bool = Query(default=False),
    limit: int = Query(default=30, ge=1, le=100),
    force_sync: bool = Query(default=True),
    service: Dnd5eGrimorioService = Depends(get_dnd5e_grimorio_service),
    _: object = Depends(requer_dono_ou_admin_dnd5e_personagem),
):
    itens = service.listar_notificacoes(
        personagem_id,
        classe=classe,
        apenas_nao_lidas=apenas_nao_lidas,
        limit=limit,
        force_sync=force_sync,
    )
    return [_serialize_notificacao(item) for item in itens]


@router.patch(
    "/{personagem_id}/notificacoes/{notificacao_id}",
    response_model=Dnd5eGrimorioNotificacaoResponse,
)
def atualizar_notificacao_grimorio(
    personagem_id: int,
    notificacao_id: int,
    payload: Dnd5eGrimorioNotificacaoUpdate,
    service: Dnd5eGrimorioService = Depends(get_dnd5e_grimorio_service),
    _: object = Depends(requer_dono_ou_admin_dnd5e_personagem),
):
    item = service.marcar_notificacao_lida(
        personagem_id, notificacao_id, lida=payload.lida
    )
    return _serialize_notificacao(item)


@router.delete(
    "/{personagem_id}/notificacoes/{notificacao_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def descartar_notificacao_grimorio(
    personagem_id: int,
    notificacao_id: int,
    service: Dnd5eGrimorioService = Depends(get_dnd5e_grimorio_service),
    _: object = Depends(requer_dono_ou_admin_dnd5e_personagem),
):
    service.descartar_notificacao(personagem_id, notificacao_id)
    return None
