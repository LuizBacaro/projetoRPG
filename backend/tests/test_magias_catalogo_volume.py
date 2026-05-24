"""
Regressão: catálogo grande (>500 magias) e filtro por classe Mago.

Reproduz o cenário de produção em que um fallback client-side em
GET /magias?limit=500 (sem ?classe=) não cobre todas as magias de Mago,
enquanto a API paginada com filtro de classe continua correta.
"""

from __future__ import annotations

from fastapi import Response

from app.games.dnd35.api.v1.magias import listar_magias
from app.games.dnd35.models.magia import Magia, MagiaClasse


def _criar_mago(db, nome: str, nivel: int = 1) -> Magia:
    magia = Magia(nome=nome, nivel=nivel, classe="MAGO", escola="Evocacao", ativo=True)
    db.add(magia)
    db.flush()
    db.add(MagiaClasse(magia_id=magia.id, classe="MAGO", nivel=nivel))
    return magia


def _criar_filler(db, nome: str) -> Magia:
    magia = Magia(
        nome=nome,
        nivel=0,
        classe="CLERIGO",
        escola="Abjuracao",
        ativo=True,
    )
    db.add(magia)
    db.flush()
    db.add(MagiaClasse(magia_id=magia.id, classe="CLERIGO", nivel=0))
    return magia


def test_listar_mago_completo_com_catalogo_acima_de_500(test_db):
    """Com >500 magias ativas, ?classe=MAGO deve retornar todas as do Mago."""
    for i in range(520):
        _criar_filler(test_db, f"AAA Filler Clerigo {i:04d}")
    magos = [
        _criar_mago(test_db, "Misseis Magicos QA"),
        _criar_mago(test_db, "Bola de Fogo QA"),
        _criar_mago(test_db, "Teletransporte QA", nivel=5),
    ]
    test_db.commit()

    response = Response()
    resultado = listar_magias(
        classe="MAGO",
        nivel=None,
        escola=None,
        nome=None,
        componentes=None,
        dominio=None,
        ativo=None,
        sort_by=None,
        sort_dir="asc",
        skip=0,
        limit=500,
        response=response,
        db=test_db,
    )

    assert response.headers["x-total-count"] == str(len(magos))
    nomes = {
        item["nome"] if isinstance(item, dict) else item.nome for item in resultado
    }
    assert nomes == {m.nome for m in magos}


def test_limit_500_sem_classe_nao_cobre_todo_mago(test_db):
    """
    Documenta a armadilha: sem filtro de classe, a 1ª página de 500 registros
    pode omitir magias de Mago quando o catálogo total é grande.
    """
    for i in range(520):
        _criar_filler(test_db, f"AAA Filler Clerigo {i:04d}")
    magos = [_criar_mago(test_db, f"Mago QA Spell {i}") for i in range(8)]
    test_db.commit()

    response = Response()
    pagina = listar_magias(
        classe=None,
        nivel=None,
        escola=None,
        nome=None,
        componentes=None,
        dominio=None,
        ativo=None,
        sort_by=None,
        sort_dir="asc",
        skip=0,
        limit=500,
        response=response,
        db=test_db,
    )

    assert int(response.headers["x-total-count"]) > 500
    ids_pagina = {item["id"] if isinstance(item, dict) else item.id for item in pagina}
    mago_ids = {m.id for m in magos}
    # Fillers AAA ocupam a 1ª página; magias de Mago (nome começa com M) ficam de fora.
    assert not mago_ids.intersection(ids_pagina)
