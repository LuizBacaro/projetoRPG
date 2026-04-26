"""
Router de Equipamentos (D&D 3.5)
SRP: apenas mapear endpoints HTTP do domínio "equipamentos" do D&D 3.5.

Localização: este router pertence ao pacote `app.games.dnd35.api.v1`
porque os endpoints expõem dados específicos do PHB 3.5 (Tabela 7-5).
Existe um shim em `app.api.v1.equipamentos` que re-exporta este `router`
durante a reorganização multi-jogo, para manter o registro em
`app.main` funcionando sem alteração imediata.

NOTA: ao contrário de outros routers de D&D 3.5, este ainda não usa o
guard `requer_game_dnd35`. A próxima onda de revisão deste domínio deve
avaliar se faz sentido adicioná-lo (impacto: token sem `game_slug`
passaria a receber 409 em strict mode).
"""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.catalog_cache import catalog_cache, make_cache_key
from app.core.config import settings
from app.core.database import get_db
from app.core.deps import (
    get_usuario_atual,
    requer_admin,
    requer_dono_ou_admin_combatente,
)
from app.games.dnd35.schemas.equipamento import (
    EquipamentoCreate,
    EquipamentoJogadorCreate,
    EquipamentoJogadorListResponse,
    EquipamentoResponse,
)
from app.games.dnd35.services.equipamento_service import EquipamentoService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/equipamentos", tags=["Equipamentos"])


def _serialize_equipamento(equipamento) -> dict:
    return {
        "id": equipamento.id,
        "nome": equipamento.nome,
        "descricao": equipamento.descricao,
        "pagina_referencia": equipamento.pagina_referencia,
        "categoria": equipamento.categoria,
        "subcategoria": equipamento.subcategoria,
        "custo": equipamento.custo,
        "dano_pequeno": equipamento.dano_pequeno,
        "dano_medio": equipamento.dano_medio,
        "critico": equipamento.critico,
        "alcance_incremento": equipamento.alcance_incremento,
        "peso": equipamento.peso,
        "tipo_dano": equipamento.tipo_dano,
        "ativo": equipamento.ativo,
        "criado_em": equipamento.criado_em,
    }


def _invalidar_cache_equipamentos() -> None:
    if settings.CACHE_ENABLED:
        catalog_cache.invalidate_prefix("equipamentos:")


# ========== ENDPOINTS DE EQUIPAMENTOS DISPONÍVEIS ==========


@router.post(
    "/", response_model=EquipamentoResponse, status_code=status.HTTP_201_CREATED
)
def criar_equipamento(
    equipamento: EquipamentoCreate,
    db: Session = Depends(get_db),
    _: object = Depends(get_usuario_atual),
):
    """Cria um novo equipamento (Admin only)"""
    try:
        service = EquipamentoService(db)
        equipamento_criado = service.criar_equipamento(equipamento)
        _invalidar_cache_equipamentos()
        return equipamento_criado
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao criar equipamento: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[EquipamentoResponse])
def listar_equipamentos(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: object = Depends(get_usuario_atual),
):
    """Lista todos os equipamentos disponíveis"""
    try:
        cache_key = make_cache_key("equipamentos:list", skip=skip, limit=limit)
        if settings.CACHE_ENABLED:
            cached = catalog_cache.get(cache_key)
            if cached is not None:
                return cached

        service = EquipamentoService(db)
        equipamentos = [
            _serialize_equipamento(eq)
            for eq in service.listar_todos_equipamentos(skip, limit)
        ]
        if settings.CACHE_ENABLED:
            catalog_cache.set(
                cache_key, equipamentos, settings.CACHE_CATALOG_TTL_SECONDS
            )
        return equipamentos
    except Exception as e:
        logger.error(f"Erro ao listar equipamentos: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{equipamento_id}", response_model=EquipamentoResponse)
def obter_equipamento(
    equipamento_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(get_usuario_atual),
):
    """Obtém um equipamento específico"""
    try:
        cache_key = make_cache_key(
            "equipamentos:detail", equipamento_id=equipamento_id
        )
        if settings.CACHE_ENABLED:
            cached = catalog_cache.get(cache_key)
            if cached is not None:
                return cached

        service = EquipamentoService(db)
        equipamento = service.obter_equipamento(equipamento_id)

        if not equipamento:
            raise HTTPException(status_code=404, detail="Equipamento não encontrado")

        equipamento_data = _serialize_equipamento(equipamento)
        if settings.CACHE_ENABLED:
            catalog_cache.set(
                cache_key, equipamento_data, settings.CACHE_CATALOG_TTL_SECONDS
            )
        return equipamento_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter equipamento: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/catalogo/{equipamento_id}", status_code=status.HTTP_204_NO_CONTENT
)
def deletar_equipamento_catalogo(
    equipamento_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(requer_admin),
):
    """
    Remove do catálogo (soft delete) um equipamento por ID.
    Evita ambiguidade com rotas /{combatente_id}/... — use o prefixo /catalogo/.
    """
    try:
        service = EquipamentoService(db)
        if not service.deletar_equipamento(equipamento_id):
            raise HTTPException(status_code=404, detail="Equipamento não encontrado")
        _invalidar_cache_equipamentos()
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao deletar equipamento do catálogo: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ========== ENDPOINTS DE EQUIPAMENTOS DO JOGADOR ==========


@router.post(
    "/{combatente_id}/adicionar",
    response_model=EquipamentoJogadorListResponse,
    status_code=status.HTTP_201_CREATED,
)
def adicionar_equipamento_jogador(
    combatente_id: int,
    equipamento_jogador: EquipamentoJogadorCreate,
    db: Session = Depends(get_db),
    _: object = Depends(requer_dono_ou_admin_combatente),
):
    """Adiciona um equipamento ao combatente"""
    try:
        service = EquipamentoService(db)
        return service.adicionar_equipamento_jogador(
            combatente_id, equipamento_jogador
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao adicionar equipamento: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{combatente_id}/listar",
    response_model=List[EquipamentoJogadorListResponse],
)
def listar_equipamentos_jogador(
    combatente_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(requer_dono_ou_admin_combatente),
):
    """Lista todos os equipamentos de um combatente"""
    try:
        service = EquipamentoService(db)
        return service.obter_equipamentos_jogador(combatente_id)
    except Exception as e:
        logger.error(f"Erro ao listar equipamentos do jogador: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/{combatente_id}/remover/{equipamento_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remover_equipamento_jogador(
    combatente_id: int,
    equipamento_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(requer_dono_ou_admin_combatente),
):
    """Remove um equipamento do combatente"""
    try:
        service = EquipamentoService(db)

        if not service.remover_equipamento_jogador(combatente_id, equipamento_id):
            raise HTTPException(
                status_code=404, detail="Equipamento do jogador não encontrado"
            )

        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao remover equipamento: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{combatente_id}/quantidade/{equipamento_id}")
def atualizar_quantidade_equipamento(
    combatente_id: int,
    equipamento_id: int,
    quantidade: int,
    db: Session = Depends(get_db),
    _: object = Depends(requer_dono_ou_admin_combatente),
):
    """Atualiza a quantidade de um equipamento"""
    try:
        service = EquipamentoService(db)
        result = service.atualizar_quantidade_equipamento(
            combatente_id, equipamento_id, quantidade
        )

        if not result and quantidade > 0:
            raise HTTPException(
                status_code=404, detail="Equipamento do jogador não encontrado"
            )

        return {"mensagem": "Quantidade atualizada com sucesso"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar quantidade: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
