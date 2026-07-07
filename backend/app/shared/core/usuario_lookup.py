"""Consultas em lote para enriquecer respostas com dados do usuário dono."""

from __future__ import annotations

from typing import Any, Dict, Iterable, Optional

from sqlalchemy.orm import Session

from app.shared.models.usuario import Usuario


def mapa_nomes_usuarios_por_ids(
    db: Session, usuario_ids: Iterable[Optional[int]]
) -> Dict[int, str]:
    ids = {int(uid) for uid in usuario_ids if uid is not None}
    if not ids:
        return {}
    rows = db.query(Usuario.id, Usuario.nome).filter(Usuario.id.in_(ids)).all()
    return {uid: (nome or "") for uid, nome in rows}


def enriquecer_dono_nome_em_entidades(
    db: Session,
    entidades: Iterable[Any],
    *,
    campo_dono: str = "dono_id",
    campo_nome: str = "dono_nome",
) -> None:
    entidades_lista = list(entidades)
    if not entidades_lista:
        return
    mapa = mapa_nomes_usuarios_por_ids(
        db, (getattr(ent, campo_dono, None) for ent in entidades_lista)
    )
    for ent in entidades_lista:
        dono_id = getattr(ent, campo_dono, None)
        nome = mapa.get(dono_id, "") if dono_id is not None else ""
        setattr(ent, campo_nome, nome)
