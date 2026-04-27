"""
Router de Perícias (D&D 3.5)

Canônico em `app.games.dnd35.api.v1.pericias` (registrado em `app.main`).

NOTA: ainda **não** declara `requer_game_dnd35` (paridade com o original).
"""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.shared.core.catalog_cache import catalog_cache, make_cache_key
from app.core.config import settings
from app.core.database import get_db
from app.shared.core.deps import get_usuario_atual, requer_dono_ou_admin_combatente
from app.games.dnd35.schemas.pericia import (
    PericiaCreate,
    PericiaJogadorCreate,
    PericiaJogadorListResponse,
    PericiaJogadorResponse,
    PericiaJogadorUpdate,
    PericiaResponse,
    PericiaUpdate,
)
from app.games.dnd35.services.pericia_service import PericiaService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/pericias", tags=["Perícias"])


def _serialize_pericia(pericia, custo_para_classe=None) -> dict:
    atributo_normalizado = (
        (pericia.atributo or "").upper() if pericia.atributo else pericia.atributo
    )
    return {
        "id": pericia.id,
        "nome": pericia.nome,
        "descricao": pericia.descricao,
        "atributo": atributo_normalizado,
        "tipo": pericia.tipo,
        "requer_treinamento": pericia.requer_treinamento,
        "especialidade": pericia.especialidade,
        "pode_usar_sem_treinamento": pericia.pode_usar_sem_treinamento,
        "sofre_penalidade_armadura": pericia.sofre_penalidade_armadura,
        "pagina_livro": pericia.pagina_livro,
        "custo_para_classe": custo_para_classe,
    }


def _invalidar_cache_pericias() -> None:
    if settings.CACHE_ENABLED:
        catalog_cache.invalidate_prefix("pericias:")


# ========== ENDPOINTS DE PERÍCIAS DISPONÍVEIS ==========


@router.post(
    "/", response_model=PericiaResponse, status_code=status.HTTP_201_CREATED
)
def criar_pericia(
    pericia: PericiaCreate,
    db: Session = Depends(get_db),
    _: object = Depends(get_usuario_atual),
):
    """Cria uma nova perícia (Admin only)"""
    try:
        service = PericiaService(db)
        pericia_criada = service.criar_pericia(pericia)
        _invalidar_cache_pericias()
        return pericia_criada
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao criar perícia: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[PericiaResponse])
def listar_pericias(
    skip: int = 0,
    limit: int = 100,
    atributo: str = Query(None),
    classe: str = Query(None),
    db: Session = Depends(get_db),
    _: object = Depends(get_usuario_atual),
):
    """Lista todas as perícias disponíveis com custo baseado em classe"""
    try:
        cache_key = make_cache_key(
            "pericias:list",
            skip=skip,
            limit=limit,
            atributo=atributo,
            classe=classe,
        )
        if settings.CACHE_ENABLED:
            cached = catalog_cache.get(cache_key)
            if cached is not None:
                return cached

        service = PericiaService(db)

        if atributo:
            pericias = service.listar_pericias_por_atributo(atributo)
        else:
            pericias = service.listar_todas_pericias(skip, limit)

        if classe:
            custos_por_pericia = service.obter_custos_pericias(
                [pericia.id for pericia in pericias],
                classe,
            )
            pericias_com_custo = []
            for pericia in pericias:
                pericias_com_custo.append(
                    _serialize_pericia(
                        pericia, custos_por_pericia.get(pericia.id, 2)
                    )
                )
            if settings.CACHE_ENABLED:
                catalog_cache.set(
                    cache_key,
                    pericias_com_custo,
                    settings.CACHE_CATALOG_TTL_SECONDS,
                )
            return pericias_com_custo

        pericias_serializadas = [
            _serialize_pericia(pericia) for pericia in pericias
        ]
        if settings.CACHE_ENABLED:
            catalog_cache.set(
                cache_key,
                pericias_serializadas,
                settings.CACHE_CATALOG_TTL_SECONDS,
            )
        return pericias_serializadas
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao listar perícias: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{pericia_id}", response_model=PericiaResponse)
def obter_pericia(
    pericia_id: int,
    classe: str = Query(None),
    db: Session = Depends(get_db),
    _: object = Depends(get_usuario_atual),
):
    """Obtém uma perícia por ID com custo baseado em classe se fornecido"""
    try:
        cache_key = make_cache_key(
            "pericias:detail",
            pericia_id=pericia_id,
            classe=classe,
        )
        if settings.CACHE_ENABLED:
            cached = catalog_cache.get(cache_key)
            if cached is not None:
                return cached

        service = PericiaService(db)
        pericia = service.obter_pericia(pericia_id)

        if not pericia:
            raise HTTPException(status_code=404, detail="Perícia não encontrada")

        if classe:
            custo = service.calcular_custo_pericia(pericia_id, classe)
            pericia_dict = _serialize_pericia(pericia, custo)
            if settings.CACHE_ENABLED:
                catalog_cache.set(
                    cache_key, pericia_dict, settings.CACHE_CATALOG_TTL_SECONDS
                )
            return pericia_dict

        pericia_dict = _serialize_pericia(pericia)
        if settings.CACHE_ENABLED:
            catalog_cache.set(
                cache_key, pericia_dict, settings.CACHE_CATALOG_TTL_SECONDS
            )
        return pericia_dict
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter perícia: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{pericia_id}", response_model=PericiaResponse)
def atualizar_pericia(
    pericia_id: int,
    pericia: PericiaUpdate,
    db: Session = Depends(get_db),
    _: object = Depends(get_usuario_atual),
):
    """Atualiza uma perícia (Admin only)"""
    try:
        service = PericiaService(db)
        pericia_atualizada = service.atualizar_pericia(pericia_id, pericia)

        if not pericia_atualizada:
            raise HTTPException(status_code=404, detail="Perícia não encontrada")

        _invalidar_cache_pericias()
        return pericia_atualizada
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar perícia: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/classe/{classe_nome}", response_model=List[PericiaResponse])
def listar_pericias_classe(
    classe_nome: str,
    db: Session = Depends(get_db),
    _: object = Depends(get_usuario_atual),
):
    """Lista perícias padrão de uma classe com seus custos"""
    try:
        cache_key = make_cache_key("pericias:classe", classe_nome=classe_nome)
        if settings.CACHE_ENABLED:
            cached = catalog_cache.get(cache_key)
            if cached is not None:
                return cached

        service = PericiaService(db)
        pericias = service.listar_pericias_por_classe(classe_nome)
        custos_por_pericia = service.obter_custos_pericias(
            [pericia.id for pericia in pericias],
            classe_nome,
        )

        pericias_com_custo = []
        for pericia in pericias:
            pericias_com_custo.append(
                _serialize_pericia(pericia, custos_por_pericia.get(pericia.id, 2))
            )

        if settings.CACHE_ENABLED:
            catalog_cache.set(
                cache_key,
                pericias_com_custo,
                settings.CACHE_CATALOG_TTL_SECONDS,
            )
        return pericias_com_custo
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao listar perícias da classe: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{pericia_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_pericia(
    pericia_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(get_usuario_atual),
):
    """Deleta uma perícia (Admin only)"""
    try:
        service = PericiaService(db)

        if not service.deletar_pericia(pericia_id):
            raise HTTPException(status_code=404, detail="Perícia não encontrada")
        _invalidar_cache_pericias()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao deletar perícia: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ========== ENDPOINTS DE PERÍCIAS DO JOGADOR ==========


@router.post(
    "/{combatente_id}/adicionar",
    response_model=PericiaJogadorResponse,
    status_code=status.HTTP_201_CREATED,
)
def adicionar_pericia_jogador(
    combatente_id: int,
    pericia: PericiaJogadorCreate,
    classe: str = Query(None),
    db: Session = Depends(get_db),
    _: object = Depends(requer_dono_ou_admin_combatente),
):
    """Adiciona uma perícia ao jogador com validação de custo"""
    try:
        service = PericiaService(db)

        if classe:
            custo_total = service.calcular_custo_total_graduacao(
                pericia.pericia_id,
                classe,
                pericia.graduacao,
            )

            from app.games.dnd35.models.combatente import Combatente

            combatente = (
                db.query(Combatente).filter(Combatente.id == combatente_id).first()
            )
            if not combatente:
                raise ValueError(f"Combatente {combatente_id} não encontrado")

            pontos_disponiveis = combatente.pontos
            if custo_total > pontos_disponiveis:
                raise ValueError(
                    f"Pontos insuficientes. Necessário: {custo_total}, "
                    f"Disponível: {pontos_disponiveis}"
                )

        return service.adicionar_pericia_jogador(combatente_id, pericia)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao adicionar perícia: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{combatente_id}/listar", response_model=PericiaJogadorListResponse
)
def listar_pericias_jogador(
    combatente_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(requer_dono_ou_admin_combatente),
):
    """Lista todas as perícias de um combatente"""
    try:
        service = PericiaService(db)
        stats = service.obter_estatisticas_pericias(combatente_id)

        return PericiaJogadorListResponse(
            pericias=stats["pericias"],
            total_pontos_gastos=stats["pontos_gastos_total"],
            pontos_disponiveis=stats["pontos_disponiveis"],
        )
    except Exception as e:
        logger.error(f"Erro ao listar perícias do jogador: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put(
    "/{combatente_id}/pericia/{pericia_jogador_id}",
    response_model=PericiaJogadorResponse,
)
def atualizar_pericia_jogador(
    combatente_id: int,
    pericia_jogador_id: int,
    pericia: PericiaJogadorUpdate,
    db: Session = Depends(get_db),
    _: object = Depends(requer_dono_ou_admin_combatente),
):
    """Atualiza uma perícia do jogador"""
    try:
        service = PericiaService(db)
        pericia_atualizada = service.atualizar_pericia_jogador(
            pericia_jogador_id, pericia
        )

        if not pericia_atualizada:
            raise HTTPException(
                status_code=404, detail="Perícia do jogador não encontrada"
            )

        return pericia_atualizada
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar perícia do jogador: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/{combatente_id}/pericia/{pericia_jogador_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def deletar_pericia_jogador(
    combatente_id: int,
    pericia_jogador_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(requer_dono_ou_admin_combatente),
):
    """Deleta uma perícia do jogador"""
    try:
        service = PericiaService(db)

        if not service.deletar_pericia_jogador(pericia_jogador_id):
            raise HTTPException(
                status_code=404, detail="Perícia do jogador não encontrada"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao deletar perícia do jogador: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{combatente_id}/estatisticas")
def obter_estatisticas_pericias(
    combatente_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(requer_dono_ou_admin_combatente),
):
    """Obtém estatísticas de perícias do combatente"""
    try:
        service = PericiaService(db)
        return service.obter_estatisticas_pericias(combatente_id)
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
