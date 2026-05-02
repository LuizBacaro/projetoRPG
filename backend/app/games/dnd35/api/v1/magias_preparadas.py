"""
Endpoints de magias preparadas (D&D 3.5).

Canônico em `app.games.dnd35.api.v1.magias_preparadas` (registrado em `app.main`).
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.shared.core.database import get_db
from app.shared.core.deps import requer_dono_ou_admin_combatente, requer_game_dnd35
from app.games.dnd35.models.ataque import MagiaPreparada
from app.games.dnd35.models.combatente import Combatente
from app.games.dnd35.models.magia import Magia
from app.games.dnd35.repositories.magia_preparada_repository import MagiaPreparadaRepository
from app.games.dnd35.schemas.ataque import (
    MagiaPreparadaResponse,
    MagiaPreparadaCreate,
    DescansoRequest,
)

from app.games.dnd35.text_utils import (
    classes_magia as _classes_magia,
    normalizar_classe_acesso as _normalizar_classe,
)

router = APIRouter(
    prefix="/magias-preparadas",
    tags=["Magias Preparadas"],
    dependencies=[Depends(requer_game_dnd35)],
)


def _normalizar_quantidade(valor: Optional[int], padrao: int = 1) -> int:
    try:
        quantidade = int(valor if valor is not None else padrao)
    except (TypeError, ValueError):
        quantidade = padrao
    return max(1, quantidade)


def _normalizar_usos(mp: MagiaPreparada) -> int:
    quantidade = _normalizar_quantidade(getattr(mp, "quantidade", 1), 1)
    try:
        usos = int(getattr(mp, "usos_realizados", 0) or 0)
    except (TypeError, ValueError):
        usos = 0
    return max(0, min(quantidade, usos))


def _enriquecer(mp: MagiaPreparada) -> dict:
    quantidade = _normalizar_quantidade(getattr(mp, "quantidade", 1), 1)
    usos_realizados = _normalizar_usos(mp)
    return {
        "id":              mp.id,
        "combatente_id":   mp.combatente_id,
        "magia_id":        mp.magia_id,
        "nivel_slot":      mp.nivel_slot,
        "quantidade":      quantidade,
        "usos_realizados": usos_realizados,
        "preparada_em":    mp.preparada_em,
        "usada":           bool(usos_realizados > 0 or mp.usada),
        "magia_nome":      mp.magia.nome   if mp.magia else None,
        "magia_escola":    mp.magia.escola if mp.magia else None,
        "magia_nivel":     mp.magia.nivel  if mp.magia else None,
    }


@router.get("/{combatente_id}", response_model=List[MagiaPreparadaResponse])
def listar_preparadas(combatente_id: int, db: Session = Depends(get_db), _: object = Depends(requer_dono_ou_admin_combatente)):
    repo = MagiaPreparadaRepository(db)
    registros = repo.listar_por_combatente(combatente_id)
    return [_enriquecer(r) for r in registros]


@router.post("/{combatente_id}", response_model=MagiaPreparadaResponse)
def preparar_magia(
    combatente_id: int,
    payload: MagiaPreparadaCreate,
    db: Session = Depends(get_db),
    _: object = Depends(requer_dono_ou_admin_combatente),
):
    """
    Marca uma magia como preparada para o dia.
    Se a magia já existir, atualiza a quantidade preparada total.
    Quantidade de slots continua validada principalmente no frontend (tabela D&D 3.5).
    """
    repo = MagiaPreparadaRepository(db)
    combatente = db.query(Combatente).filter(Combatente.id == combatente_id).first()
    if not combatente:
        raise HTTPException(status_code=404, detail="Combatente não encontrado")

    magia = db.query(Magia).filter(Magia.id == payload.magia_id).first()
    if not magia:
        raise HTTPException(status_code=404, detail="Magia não encontrada")

    classes_combatente = _classes_magia(combatente.classe)
    if not classes_combatente:
        classe_normalizada = _normalizar_classe(combatente.classe)
        if classe_normalizada:
            classes_combatente = {classe_normalizada}

    classes_permitidas = {
        _normalizar_classe(cn.classe)
        for cn in (getattr(magia, "classes_niveis", None) or [])
        if _normalizar_classe(cn.classe)
    }
    if not classes_permitidas:
        classes_permitidas = _classes_magia(magia.classe)

    classe_solicitada = _normalizar_classe(payload.classe)

    if classe_solicitada:
        if classe_solicitada not in classes_combatente:
            classes_legiveis = ", ".join(sorted(classes_combatente)) or "N/A"
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Classe ativa inválida para este combatente: {payload.classe}. "
                    f"Disponíveis: {classes_legiveis}"
                ),
            )
        classes_validas_para_preparo = {classe_solicitada}
    else:
        classes_validas_para_preparo = classes_combatente

    if not classes_validas_para_preparo.intersection(classes_permitidas):
        classes_legiveis = ", ".join(sorted(classes_permitidas)) or "N/A"
        raise HTTPException(
            status_code=400,
            detail=(
                f"Classe incompatível para preparação: {combatente.classe}. "
                f"Esta magia pertence a: {classes_legiveis}"
            ),
        )

    quantidade_desejada = _normalizar_quantidade(getattr(payload, "quantidade", 1), 1)

    ja_preparada = repo.obter_por_combatente_e_magia(combatente_id, payload.magia_id)
    if ja_preparada:
        ja_preparada.nivel_slot = payload.nivel_slot
        ja_preparada.quantidade = quantidade_desejada
        ja_preparada.usos_realizados = min(_normalizar_usos(ja_preparada), quantidade_desejada)
        ja_preparada.usada = ja_preparada.usos_realizados > 0
        atualizado = repo.commit_refresh(ja_preparada)
        return _enriquecer(atualizado)

    nova = MagiaPreparada(
        combatente_id=combatente_id,
        magia_id=payload.magia_id,
        nivel_slot=payload.nivel_slot,
        quantidade=quantidade_desejada,
        usos_realizados=0,
        usada=False,
    )
    carregada = repo.add_commit_refresh(nova)
    return _enriquecer(carregada)


@router.patch("/{combatente_id}/{magia_id}/usar", response_model=MagiaPreparadaResponse)
def marcar_usada(
    combatente_id: int,
    magia_id: int,
    action: Optional[str] = None,
    db: Session = Depends(get_db),
    _: object = Depends(requer_dono_ou_admin_combatente),
):
    """
    Alterna o consumo/restauração de uma cópia preparada da magia.
    Quando `action=usar`, consome uma cópia; quando `action=restaurar`, devolve uma.
    """
    repo = MagiaPreparadaRepository(db)
    registro = repo.obter_por_combatente_e_magia(combatente_id, magia_id)
    if not registro:
        raise HTTPException(status_code=404, detail="Magia não estava preparada")

    quantidade = _normalizar_quantidade(getattr(registro, "quantidade", 1), 1)
    usos_realizados = _normalizar_usos(registro)
    acao = (action or "").strip().lower()

    if acao == "usar":
        if usos_realizados >= quantidade:
            raise HTTPException(status_code=400, detail="Todas as cópias preparadas desta magia já foram utilizadas hoje")
        usos_realizados += 1
    elif acao == "restaurar":
        if usos_realizados <= 0:
            raise HTTPException(status_code=400, detail="Nenhum uso desta magia foi marcado hoje")
        usos_realizados -= 1
    else:
        usos_realizados = usos_realizados - 1 if usos_realizados > 0 else min(quantidade, usos_realizados + 1)

    registro.usos_realizados = usos_realizados
    registro.usada = usos_realizados > 0
    atualizado = repo.commit_refresh(registro)
    return _enriquecer(atualizado)


@router.delete("/{combatente_id}/{magia_id}", status_code=204)
def desmarcar_magia(
    combatente_id: int,
    magia_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(requer_dono_ou_admin_combatente),
):
    repo = MagiaPreparadaRepository(db)
    registro = repo.obter_por_combatente_e_magia(combatente_id, magia_id)
    if not registro:
        raise HTTPException(status_code=404, detail="Magia não estava preparada")

    repo.delete(registro)


@router.post("/{combatente_id}/descanso", status_code=200)
def descanso_longo(
    combatente_id: int,
    payload: DescansoRequest,
    db: Session = Depends(get_db),
    _: object = Depends(requer_dono_ou_admin_combatente),
):
    """Descanso longo: reseta magias preparadas, usadas e slots."""
    if not payload.confirmar:
        raise HTTPException(status_code=400, detail="Confirmação necessária")

    repo = MagiaPreparadaRepository(db)
    deletadas = repo.delete_all_por_combatente(combatente_id)
    repo.reset_slots_usados(combatente_id)
    repo.commit()

    return {
        "message":              "Descanso longo realizado com sucesso",
        "preparadas_removidas": deletadas,
        "slots_resetados":      True,
    }
