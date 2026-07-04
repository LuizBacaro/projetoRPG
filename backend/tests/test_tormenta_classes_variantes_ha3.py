"""HA-3 — Classes variantes e origens Heróis de Arton."""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.games.tormenta.api.v1.regras import router as tormenta_regras_router
from app.games.tormenta.rules.classes_t20 import (
    lista_classes_herois_arton,
    validar_classe_variante,
    validar_compatibilidade_classes_v13,
)
from app.games.tormenta.rules.origens_t20 import (
    lista_origens_com_suplemento,
    lista_origens_herois_arton,
    origem_por_slug,
    validar_beneficios_origem,
)
from app.games.tormenta.rules.regra_versao_t20 import SUPLEMENTO_HEROIS_ARTON
from app.shared.core.deps import get_usuario_atual
from tests.test_tormenta_personagens_api import (
    _build_client,
    _t20_post_jogador_v13_json,
    _usuario,
)

pytest_plugins = ("tests.test_tormenta_personagens_api",)


@pytest.fixture(scope="function")
def client_regras_tormenta():
    app = FastAPI()
    app.include_router(tormenta_regras_router, prefix="/api/v1")
    u = SimpleNamespace(id=1, perfil="jogador", email="t@example.com", nome="Teste")
    app.dependency_overrides[get_usuario_atual] = lambda: u
    yield TestClient(app)
    app.dependency_overrides.clear()


_FICHA_V13_BASE = {
    "origem_slug": "acolito",
    "origem_beneficios": ["pericia:cura", "poder:medicina"],
    "game_suplemento": SUPLEMENTO_HEROIS_ARTON,
    "cadastro_dashboard": True,
}


def test_quatorze_classes_variantes() -> None:
    rows = lista_classes_herois_arton()
    variantes = [r for r in rows if r["slug"] != "treinador"]
    assert len(variantes) == 14
    com_base = [r for r in variantes if r.get("classe_variante_base")]
    assert len(com_base) == 13
    duelista = next(r for r in variantes if r["slug"] == "duelista")
    assert duelista.get("classe_variante_base") is None


def test_validar_classe_variante_alquimista_vs_inventor() -> None:
    err = validar_classe_variante("alquimista", ["inventor"])
    assert err is not None
    assert "incompatível" in err.lower() or "incompat" in err.lower()


def test_validar_classe_variante_ok_sem_conflito() -> None:
    assert validar_classe_variante("alquimista", ["guerreiro"]) is None
    assert validar_classe_variante("guerreiro", ["alquimista"]) is None


def test_validar_compatibilidade_ficha_multiclasse() -> None:
    ficha_ok = {
        "regra_versao": "v13",
        "tormenta_classe_mb_slug": "alquimista",
        "multiclasse_v13": [{"slug": "alquimista", "nivel": 3}],
    }
    assert validar_compatibilidade_classes_v13(ficha_ok, 3) is None

    ficha_bad = {
        "regra_versao": "v13",
        "tormenta_classe_mb_slug": "inventor",
        "multiclasse_v13": [
            {"slug": "inventor", "nivel": 2},
            {"slug": "alquimista", "nivel": 1},
        ],
    }
    err = validar_compatibilidade_classes_v13(ficha_bad, 3)
    assert err is not None


def test_origens_herois_arton_quatorze() -> None:
    rows = lista_origens_herois_arton()
    assert len(rows) == 14
    assert all(r["fonte_catalogo"] == SUPLEMENTO_HEROIS_ARTON for r in rows)


def test_origens_com_suplemento_mescla() -> None:
    core = lista_origens_com_suplemento()
    ha = lista_origens_com_suplemento(SUPLEMENTO_HEROIS_ARTON)
    assert len(ha) == len(core) + 14


def test_origem_por_slug_bacharel() -> None:
    row = origem_por_slug("bacharel")
    assert row is not None
    assert row["nome"] == "Bacharel"
    assert row.get("troca_pericia_treinada") is True


def test_validar_beneficios_origem_herois() -> None:
    ok, _ = validar_beneficios_origem(
        "bacharel",
        ["pericia:conhecimento", "poder:retórica"],
    )
    assert ok is True


def test_get_regras_classes_ha_campos_variante(client_regras_tormenta) -> None:
    r = client_regras_tormenta.get(
        "/api/v1/tormenta/regras/classes",
        params={"regra_versao": "v13", "suplemento": SUPLEMENTO_HEROIS_ARTON},
    )
    assert r.status_code == 200, r.text
    alq = next(c for c in r.json()["classes"] if c["slug"] == "alquimista")
    assert alq["classe_variante_base"] == "inventor"
    assert "inventor" in alq["exclusivo_com"]
    assert alq["fonte_catalogo"] == SUPLEMENTO_HEROIS_ARTON
    duel = next(c for c in r.json()["classes"] if c["slug"] == "duelista")
    assert duel.get("classe_variante_base") is None


def test_post_personagem_ha_alquimista_sozinho_ok(tormenta_personagens_db) -> None:
    SessionLocal, u1, *_ = tormenta_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))
    r = client.post(
        "/api/v1/tormenta/personagens",
        json=_t20_post_jogador_v13_json(
            nome="Alq HA",
            nivel=1,
            pv_max=10,
            pv_atual=10,
            ficha_json={
                **_FICHA_V13_BASE,
                "tormenta_classe_mb_slug": "alquimista",
            },
        ),
    )
    assert r.status_code == 201, r.text
    assert r.json()["ficha_json"]["tormenta_classe_mb_slug"] == "alquimista"


def test_post_personagem_ha_multiclasse_inventor_alquimista_rejeita(
    tormenta_personagens_db,
) -> None:
    SessionLocal, u1, *_ = tormenta_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))
    r = client.post(
        "/api/v1/tormenta/personagens",
        json=_t20_post_jogador_v13_json(
            nome="Inv+Alq",
            nivel=3,
            pv_max=18,
            pv_atual=18,
            ficha_json={
                **_FICHA_V13_BASE,
                "tormenta_classe_mb_slug": "inventor",
                "multiclasse_v13": [
                    {"slug": "inventor", "nivel": 2},
                    {"slug": "alquimista", "nivel": 1},
                ],
            },
        ),
    )
    assert r.status_code == 422, r.text
    detail = r.json()["detail"].lower()
    assert "incompat" in detail


def test_put_personagem_ha_multiclasse_conflito_rejeita(
    tormenta_personagens_db,
) -> None:
    SessionLocal, u1, *_ = tormenta_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))
    criado = client.post(
        "/api/v1/tormenta/personagens",
        json=_t20_post_jogador_v13_json(
            nome="Alq Upd",
            nivel=2,
            pv_max=14,
            pv_atual=14,
            ficha_json={
                **_FICHA_V13_BASE,
                "tormenta_classe_mb_slug": "alquimista",
                "multiclasse_v13": [{"slug": "alquimista", "nivel": 2}],
            },
        ),
    )
    assert criado.status_code == 201, criado.text
    rid = criado.json()["id"]
    r2 = client.patch(
        f"/api/v1/tormenta/personagens/{rid}",
        json={
            "ficha_json": {
                "multiclasse_v13": [
                    {"slug": "alquimista", "nivel": 2},
                    {"slug": "inventor", "nivel": 1},
                ],
            },
        },
    )
    assert r2.status_code == 422, r2.text
    assert "incompat" in r2.json()["detail"].lower()
