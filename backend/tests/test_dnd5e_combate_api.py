"""API de combate D&D 5e."""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.games.dnd5e.api.v1.combate import router as dnd5e_combate_router
from app.shared.core.deps import get_usuario_atual


@pytest.fixture
def client_combate():
    app = FastAPI()
    app.include_router(dnd5e_combate_router, prefix="/api/v1")
    u = SimpleNamespace(id=1, perfil="jogador", email="t@example.com", nome="Teste")
    app.dependency_overrides[get_usuario_atual] = lambda: u
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_post_iniciativa(client_combate):
    r = client_combate.post(
        "/api/v1/dnd5e/combate/iniciativa",
        json={
            "combatentes": [
                {"id": "1", "nome": "A", "dex_mod": 2},
                {"id": "2", "nome": "B", "dex_mod": 0},
            ]
        },
    )
    assert r.status_code == 200, r.text
    ordem = r.json()["ordem"]
    assert len(ordem) == 2
    assert ordem[0]["iniciativa"] >= ordem[1]["iniciativa"]


def test_post_ataque(client_combate):
    r = client_combate.post(
        "/api/v1/dnd5e/combate/ataque",
        json={
            "mod_atributo": 3,
            "bonus_proficiencia": 2,
            "ac_alvo": 15,
            "rolagem_d20": 12,
        },
    )
    assert r.status_code == 200
    assert r.json()["acerto"] is True


def test_post_ataque_com_condicoes_alvo(client_combate):
    r = client_combate.post(
        "/api/v1/dnd5e/combate/ataque",
        json={
            "mod_atributo": 0,
            "bonus_proficiencia": 2,
            "ac_alvo": 25,
            "rolagem_d20": 5,
            "condicoes_alvo": ["incapacitado"],
            "corpo_a_corpo": True,
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["acerto"] is True
    assert body["acerto_automatico"] is True


def test_post_ataque_nat_20_critico(client_combate):
    r = client_combate.post(
        "/api/v1/dnd5e/combate/ataque",
        json={
            "mod_atributo": 0,
            "bonus_proficiencia": 2,
            "ac_alvo": 30,
            "rolagem_d20": 20,
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["is_critico"] is True
    assert body["acerto"] is True


def test_post_death_save(client_combate):
    r = client_combate.post(
        "/api/v1/dnd5e/combate/death-save",
        json={
            "hp_atual": 0,
            "death_failures": 0,
            "death_successes": 0,
            "rolagem_d20": 15,
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["death_successes"] == 1
    assert body["status_vida"] == "inconsciente"


def test_post_iniciativa_empate_des(client_combate):
    r = client_combate.post(
        "/api/v1/dnd5e/combate/iniciativa",
        json={
            "combatentes": [
                {"id": "a", "nome": "Alpha", "dex_mod": 3},
                {"id": "b", "nome": "Beta", "dex_mod": 1},
            ]
        },
    )
    assert r.status_code == 200
    ordem = r.json()["ordem"]
    if ordem[0]["iniciativa"] == ordem[1]["iniciativa"]:
        assert ordem[0]["dex_mod"] >= ordem[1]["dex_mod"]


def test_post_economia_turno(client_combate):
    r = client_combate.post(
        "/api/v1/dnd5e/combate/turno/economia",
        json={"tipo": "acao", "economia": {}},
    )
    assert r.status_code == 200
    assert r.json()["economia"]["acao_usada"] is True


def test_post_death_save_nat_20_recupera_pv(client_combate):
    r = client_combate.post(
        "/api/v1/dnd5e/combate/death-save",
        json={
            "hp_atual": 0,
            "death_failures": 1,
            "death_successes": 0,
            "rolagem_d20": 20,
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["hp_atual"] == 1
    assert body["status_vida"] == "vivo"


def test_post_dano_hp_morte_instantanea(client_combate):
    r = client_combate.post(
        "/api/v1/dnd5e/combate/dano-hp",
        json={
            "hp_atual": 8,
            "hp_max": 8,
            "dano": 20,
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["morte_instantanea"] is True
    assert body["status_vida"] == "morto"


def test_post_dano_hp_em_zero_falha(client_combate):
    r = client_combate.post(
        "/api/v1/dnd5e/combate/dano-hp",
        json={
            "hp_atual": 0,
            "hp_max": 30,
            "dano": 4,
            "status_vida": "inconsciente",
        },
    )
    assert r.status_code == 200
    assert r.json()["death_failures"] == 1


def test_post_salvamento_elfo_vantagem(client_combate):
    r = client_combate.post(
        "/api/v1/dnd5e/combate/salvamento",
        json={
            "mod_atributo": 3,
            "bonus_proficiencia": 2,
            "cd": 15,
            "proficiente": True,
            "raca_slug": "elfo",
            "categoria": "encantamento",
            "rolagem_d20": 10,
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 15
    assert body["sucesso"] is True


def test_post_dano_hp_anao_resistencia_veneno(client_combate):
    r = client_combate.post(
        "/api/v1/dnd5e/combate/dano-hp",
        json={
            "hp_atual": 20,
            "hp_max": 30,
            "dano": 10,
            "raca_slug": "anao",
            "tipo_dano": "veneno",
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["dano_aplicado"] == 5
    assert body["hp_atual"] == 15
    assert "veneno" in body["mensagem_racial"].lower()


def test_post_estabilizar_medicina(client_combate):
    r = client_combate.post(
        "/api/v1/dnd5e/combate/estabilizar",
        json={
            "hp_atual": 0,
            "metodo": "medicina",
            "rolagem_d20": 15,
            "mod_medicina": 2,
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["sucesso"] is True
    assert body["status_vida"] == "estabilizado"


def test_post_iniciativa_com_alert(client_combate):
    r = client_combate.post(
        "/api/v1/dnd5e/combate/iniciativa",
        json={
            "combatentes": [
                {"id": "1", "nome": "Alert", "dex_mod": 0, "feats": ["alert"]},
            ]
        },
    )
    assert r.status_code == 200
    row = r.json()["ordem"][0]
    assert row["iniciativa"] == row["rolagem"] + 5


def test_post_economia_dash(client_combate):
    r = client_combate.post(
        "/api/v1/dnd5e/combate/turno/economia",
        json={"tipo": "dash", "economia": {"velocidade_metros": 9}},
    )
    assert r.status_code == 200
    eco = r.json()["economia"]
    assert eco["acao_usada"] is True
    assert eco["velocidade_metros"] == 18.0


def test_post_oportunidade(client_combate):
    r = client_combate.post(
        "/api/v1/dnd5e/combate/oportunidade",
        json={
            "str_mod": 3,
            "dex_mod": 1,
            "bonus_proficiencia": 2,
            "ac_alvo": 12,
            "rolagem_d20": 10,
            "economia_atacante": {},
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["acerto"] is True
    assert body["economia_atacante"]["reacao_usada"] is True


def test_post_oportunidade_desengajado(client_combate):
    r = client_combate.post(
        "/api/v1/dnd5e/combate/oportunidade",
        json={
            "str_mod": 3,
            "dex_mod": 1,
            "bonus_proficiencia": 2,
            "ac_alvo": 12,
            "alvo_desengajado": True,
        },
    )
    assert r.status_code == 422


def test_post_salvamento_resilient(client_combate):
    r = client_combate.post(
        "/api/v1/dnd5e/combate/salvamento",
        json={
            "mod_atributo": 2,
            "bonus_proficiencia": 2,
            "cd": 12,
            "proficiente": False,
            "feats": ["resilient"],
            "feat_escolhas": {"resilient": "constitution"},
            "save_tipo": "fortitude",
            "rolagem_d20": 8,
            "aplicar_sorte_halfling": False,
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["proficiente_resilient"] is True
    assert body["sucesso"] is True
