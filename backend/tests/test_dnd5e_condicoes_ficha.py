"""Condições de arena persistidas em ficha_json (D&D 5e)."""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.games.dnd5e.api.v1.combate import router as dnd5e_combate_router
from app.games.dnd5e.rules.condicoes_ficha import (
    CHAVE_FICHA_ARENA_CONDICOES,
    DURACAO_PERMANENTE,
    ORIGEM_CONDICAO_HP,
    condicoes_ficha_de_resposta,
    decrementar_condicoes_turno,
    normalizar_condicoes_ficha,
    sincronizar_condicoes_por_hp,
    slugs_de_condicoes,
)
from app.games.dnd5e.rules.ficha import validar_ficha_para_gravacao
from app.shared.core.deps import get_usuario_atual


def test_normalizar_aceita_string_legado() -> None:
    out = normalizar_condicoes_ficha(["cego", "atordoado"])
    assert len(out) == 2
    assert out[0]["slug"] == "atordoado"
    assert out[0]["duracao_turnos"] == DURACAO_PERMANENTE


def test_normalizar_dict_com_duracao() -> None:
    out = normalizar_condicoes_ficha(
        [{"slug": "cego", "duracao_turnos": 2}, {"slug": "invalida", "duracao_turnos": 1}]
    )
    assert len(out) == 1
    assert out[0] == {"slug": "cego", "duracao_turnos": 2}


def test_decrementar_remove_expiradas_mantem_permanente() -> None:
    antes = [
        {"slug": "cego", "duracao_turnos": 1},
        {"slug": "atordoado", "duracao_turnos": -1},
        {"slug": "envenenado", "duracao_turnos": 3},
    ]
    depois = decrementar_condicoes_turno(antes)
    slugs = slugs_de_condicoes(depois)
    assert "cego" not in slugs
    assert "atordoado" in slugs
    assert "envenenado" in slugs
    row = next(x for x in depois if x["slug"] == "envenenado")
    assert row["duracao_turnos"] == 2


def test_ficha_parcial_preserva_arena_condicoes() -> None:
    ficha = validar_ficha_para_gravacao(
        {CHAVE_FICHA_ARENA_CONDICOES: [{"slug": "prostrado", "duracao_turnos": 2}]},
        nivel=1,
    )
    assert ficha[CHAVE_FICHA_ARENA_CONDICOES][0]["slug"] == "prostrado"


def test_condicoes_ficha_de_resposta() -> None:
    assert condicoes_ficha_de_resposta({"arena_condicoes": ["surdo"]}) == [
        {"slug": "surdo", "duracao_turnos": -1}
    ]


@pytest.fixture
def client_condicoes():
    app = FastAPI()
    app.include_router(dnd5e_combate_router, prefix="/api/v1")
    u = SimpleNamespace(id=1, perfil="jogador", email="t@example.com", nome="Teste")
    app.dependency_overrides[get_usuario_atual] = lambda: u
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_sincronizar_hp_zero_adiciona_inconsciente() -> None:
    out = sincronizar_condicoes_por_hp(0, [])
    assert len(out) == 1
    assert out[0]["slug"] == "inconsciente"
    assert out[0]["origem"] == ORIGEM_CONDICAO_HP


def test_sincronizar_hp_positivo_remove_inconsciente_auto() -> None:
    antes = sincronizar_condicoes_por_hp(0, [])
    depois = sincronizar_condicoes_por_hp(5, antes)
    assert slugs_de_condicoes(depois) == []


def test_sincronizar_hp_nao_remove_inconsciente_manual() -> None:
    manual = [{"slug": "inconsciente", "duracao_turnos": 2}]
    depois = sincronizar_condicoes_por_hp(10, manual)
    assert "inconsciente" in slugs_de_condicoes(depois)


def test_post_sincronizar_hp_api(client_condicoes) -> None:
    r = client_condicoes.post(
        "/api/v1/dnd5e/combate/condicoes/sincronizar-hp",
        json={"hp_atual": 0, "condicoes": []},
    )
    assert r.status_code == 200
    assert r.json()["condicoes"][0]["slug"] == "inconsciente"


def test_post_decrementar_turno_api(client_condicoes) -> None:
    r = client_condicoes.post(
        "/api/v1/dnd5e/combate/condicoes/decrementar-turno",
        json={
            "condicoes": [
                {"slug": "cego", "duracao_turnos": 1},
                {"slug": "paralisado", "duracao_turnos": -1},
            ]
        },
    )
    assert r.status_code == 200, r.text
    body = r.json()["condicoes"]
    assert len(body) == 1
    assert body[0]["slug"] == "paralisado"
