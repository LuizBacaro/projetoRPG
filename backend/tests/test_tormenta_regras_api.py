"""Integração HTTP — regras Tormenta (payload estático para a ficha)."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.games.tormenta.api.v1.regras import router as tormenta_regras_router
from app.shared.core.deps import get_usuario_atual
from app.shared.models.usuario import Usuario


@pytest.fixture(scope="function")
def client_regras_tormenta():
    app = FastAPI()
    app.include_router(tormenta_regras_router, prefix="/api/v1")

    u = SimpleNamespace(id=1, perfil="jogador", email="t@example.com", nome="Teste")

    app.dependency_overrides[get_usuario_atual] = lambda: u
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_get_regras_atributos(client_regras_tormenta):
    r = client_regras_tormenta.get("/api/v1/tormenta/regras/atributos")
    assert r.status_code == 200
    body = r.json()
    assert body["pontos_compra_iniciais"] == 20
    assert len(body["custos"]) == 11
    assert body["custos"][0]["valor"] == 8
    assert len(body["pericias"]) == 32
    assert body["pericias"][0]["nome"] == "Acrobacia"
    assert body["pericias"][0]["atributo"] == "des"
    assert body["pericias"][0]["somente_treinado"] is False
    assert body["pericias"][0]["penalidade_armadura"] is True
    assert body["pericias"][1]["nome"] == "Adestramento"
    assert body["pericias"][1]["somente_treinado"] is True
    assert body["pericias"][1]["penalidade_armadura"] is False
    assert body["pericias"][-1]["atributo"] is None
    assert body["pericias"][-1]["somente_treinado"] is False
    assert body["pericias"][-1]["penalidade_armadura"] is False


def test_post_gerar_atributos_4d6(client_regras_tormenta):
    r = client_regras_tormenta.post(
        "/api/v1/tormenta/regras/gerar-atributos",
        json={"metodo": "4d6", "seed": 99},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["metodo"] == "4d6"
    assert set(body["valores"].keys()) == {"for", "des", "con", "int", "sab", "car"}
    assert body["qualidade_4d6_ok"] is True
    for v in body["valores"].values():
        assert 3 <= v <= 18


def test_post_gerar_atributos_compra_pontos(client_regras_tormenta):
    r = client_regras_tormenta.post(
        "/api/v1/tormenta/regras/gerar-atributos",
        json={"metodo": "compra_pontos"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["metodo"] == "compra_pontos"
    assert all(v == 10 for v in body["valores"].values())
    assert body["qualidade_4d6_ok"] is None


def test_get_regras_atributos_inclui_metodos(client_regras_tormenta):
    r = client_regras_tormenta.get("/api/v1/tormenta/regras/atributos")
    assert r.status_code == 200
    assert "4d6" in r.json()["metodos_geracao"]
    assert "compra_pontos" in r.json()["metodos_geracao"]


def test_get_regras_racas(client_regras_tormenta):
    r = client_regras_tormenta.get("/api/v1/tormenta/regras/racas")
    assert r.status_code == 200
    body = r.json()
    assert "racas" in body
    assert len(body["racas"]) >= 11
    assert "idiomas_geral_mb" in body and len(body["idiomas_geral_mb"]) > 50
    assert "idiomas_tabela_mb" in body and len(body["idiomas_tabela_mb"]) >= 10
    slugs = {x["slug"] for x in body["racas"]}
    assert "anao" in slugs and "humano" in slugs
    assert "gnomo" in slugs and "meio_elfo" in slugs and "meio_orc" in slugs
    anao = next(x for x in body["racas"] if x["slug"] == "anao")
    assert anao["ajustes"]["con"] == 4
    assert anao["ajustes"]["des"] == -2
    assert anao.get("idioma_racial_mb") == "Anão"
    hum = next(x for x in body["racas"] if x["slug"] == "humano")
    assert hum.get("idioma_racial_mb") is None


def test_get_regras_classes(client_regras_tormenta):
    r = client_regras_tormenta.get("/api/v1/tormenta/regras/classes")
    assert r.status_code == 200
    body = r.json()
    assert "classes" in body and "beneficios_por_nivel" in body
    assert len(body["classes"]) >= 10
    assert len(body["beneficios_por_nivel"]) == 20
    bar = next(x for x in body["classes"] if x["slug"] == "barbaro")
    assert bar["bba_tipo"] == "plein"
    assert bar["habilidades_por_nivel"]["1"]


def test_get_regras_equipamentos_pagina(client_regras_tormenta):
    r = client_regras_tormenta.get(
        "/api/v1/tormenta/regras/equipamentos",
        params={"q": "espada", "skip": 0, "limit": 5},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert "itens" in body and "total" in body
    assert body["total"] >= 3
    assert len(body["itens"]) <= 5
    assert all("espada" in x["nome"].lower() for x in body["itens"])
    assert r.headers.get("X-Total-Count")


def test_get_regras_talentos_pagina(client_regras_tormenta):
    r = client_regras_tormenta.get(
        "/api/v1/tormenta/regras/talentos",
        params={"q": "usar", "skip": 0, "limit": 10},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["total"] >= 1
    assert len(body["itens"]) >= 1
    assert any("usar" in x["nome"].lower() for x in body["itens"])


def test_get_regras_talentos_busca_por_prerequisito_e_enriquecimento(
    client_regras_tormenta,
):
    r = client_regras_tormenta.get(
        "/api/v1/tormenta/regras/talentos",
        params={"q": "sab 13", "skip": 0, "limit": 20},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["total"] >= 1
    nomes = {x["nome"] for x in body["itens"]}
    assert "Acuidade com Armas" in nomes
    acu = next(x for x in body["itens"] if x["nome"] == "Acuidade com Armas")
    assert acu.get("prerequisitos")
    assert acu.get("descricao_resumo")

    r2 = client_regras_tormenta.get(
        "/api/v1/tormenta/regras/talentos",
        params={"q": "fortitude maior", "skip": 0, "limit": 5},
    )
    assert r2.status_code == 200, r2.text
    body2 = r2.json()
    assert body2["total"] >= 1
    fort = next(
        x
        for x in body2["itens"]
        if str(x.get("nome", "")).startswith("Fortitude Maior")
    )
    assert fort.get("pagina_referencia")


def test_get_regras_identidade_mb(client_regras_tormenta):
    r = client_regras_tormenta.get("/api/v1/tormenta/regras/identidade-mb")
    assert r.status_code == 200, r.text
    body = r.json()
    assert isinstance(body.get("tendencias"), list)
    assert isinstance(body.get("divindades"), list)
    assert len(body["tendencias"]) == 9
    assert len(body["divindades"]) == 20
    assert "Neutro" in body["tendencias"]
    assert any(d.get("slug") == "valkaria" for d in body["divindades"])
    assert any("Valkaria" in d.get("rotulo", "") for d in body["divindades"])


def test_get_regras_armaduras_protecao_pagina(client_regras_tormenta):
    r = client_regras_tormenta.get(
        "/api/v1/tormenta/regras/armaduras-protecao", params={"skip": 0, "limit": 20}
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert "itens" in body and "total" in body
    assert body["total"] == 12
    assert len(body["itens"]) == 12
    assert body["itens"][0]["nome"] == "Armadura de couro"
    assert body["itens"][0]["bonus_ca"] == 2


def test_get_tracos_raciais_preview(client_regras_tormenta):
    r = client_regras_tormenta.get(
        "/api/v1/tormenta/regras/tracos-raciais-preview", params={"slug": "goblin"}
    )
    assert r.status_code == 200
    body = r.json()
    assert body["encontrado"] is True
    assert body["ca_bonus"] == 1


def test_get_regras_pericias_dcs(client_regras_tormenta):
    r = client_regras_tormenta.get("/api/v1/tormenta/regras/pericias")
    assert r.status_code == 200
    body = r.json()
    assert body["bonus_treinado"] == 2
    assert len(body["dificuldades"]) >= 6


def test_post_pericias_rolar(client_regras_tormenta):
    r = client_regras_tormenta.post(
        "/api/v1/tormenta/regras/pericias/rolar",
        json={"bonus": 5, "dc": 15},
    )
    assert r.status_code == 200
    body = r.json()
    assert "d20" in body and "sucesso" in body


def test_get_pv_preview_barbaro(client_regras_tormenta):
    r = client_regras_tormenta.get(
        "/api/v1/tormenta/regras/pv-preview",
        params={"classe_slug": "barbaro", "nivel": 3, "con_valor": 12},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["pv_max"] == 24 + 2 * 6 + 3 * 1


def test_post_pericias_validar_criacao_ok(client_regras_tormenta):
    r = client_regras_tormenta.post(
        "/api/v1/tormenta/regras/pericias/validar-criacao",
        json={
            "nivel": 1,
            "classe_slug": "mago",
            "int_valor": 14,
            "pericias": [
                {"nome": "Conhecimento", "treinado": True, "graduacao": 2},
                {"nome": "Misticismo", "treinado": True, "graduacao": 2},
            ],
        },
    )
    assert r.status_code == 200
    assert r.json()["valido"] is True


def test_get_regras_magias_pagina_e_filtros(client_regras_tormenta):
    r = client_regras_tormenta.get(
        "/api/v1/tormenta/regras/magias", params={"skip": 0, "limit": 20}
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["total"] >= 700
    assert len(body["itens"]) == 20
    assert r.headers.get("X-Total-Count") == str(body["total"])
    assert all("slug" in x and x["circulo"] >= 0 for x in body["itens"])

    r0 = client_regras_tormenta.get(
        "/api/v1/tormenta/regras/magias", params={"circulo": 0}
    )
    assert r0.status_code == 200
    b0 = r0.json()
    assert b0["total"] >= 65

    r_stub = client_regras_tormenta.get(
        "/api/v1/tormenta/regras/magias", params={"q": "stub_truque_arc"}
    )
    assert r_stub.status_code == 200
    assert any(x.get("slug") == "stub_truque_arc" for x in r_stub.json()["itens"])

    r1 = client_regras_tormenta.get(
        "/api/v1/tormenta/regras/magias", params={"circulo": 1}
    )
    assert r1.json()["total"] >= 20

    rdiv = client_regras_tormenta.get(
        "/api/v1/tormenta/regras/magias", params={"tipo": "divina"}
    )
    assert rdiv.json()["total"] >= 300
    assert rdiv.json()["itens"][0]["tipo"] == "divina"

    r_esc = client_regras_tormenta.get(
        "/api/v1/tormenta/regras/magias", params={"escola": "abju"}
    )
    assert r_esc.json()["total"] >= 1
    assert "Abjuração" in (r_esc.json()["itens"][0].get("escola") or "")

    r_page = client_regras_tormenta.get(
        "/api/v1/tormenta/regras/magias",
        params={"q": "[stub]", "skip": 2, "limit": 2},
    )
    assert r_page.json()["total"] == 5
    assert len(r_page.json()["itens"]) == 2


def test_get_regras_magias_catalogo_por_classe_mb_clerigo_nivel_3(
    client_regras_tormenta,
):
    r = client_regras_tormenta.get(
        "/api/v1/tormenta/regras/magias",
        params={
            "catalogo_por_classe_mb": True,
            "classe_mb_slug": "clerigo",
            "nivel_mb": 3,
            "limit": 200,
        },
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["total"] < 400
    for it in body["itens"]:
        assert it["tipo"] == "divina"
        assert it["circulo"] <= 2
    r2 = client_regras_tormenta.get(
        "/api/v1/tormenta/regras/magias", params={"limit": 200}
    )
    assert r2.json()["total"] > body["total"]


def test_get_regras_magias_catalogo_g5_volume_listagem_mb(client_regras_tormenta):
    """G5: listagem pp.307–317 no JSON (≈700 magias arcana+divina)."""
    r = client_regras_tormenta.get(
        "/api/v1/tormenta/regras/magias", params={"limit": 1}
    )
    assert r.status_code == 200, r.text
    total = int(r.json().get("total") or 0)
    assert total >= 700
    r_arc = client_regras_tormenta.get(
        "/api/v1/tormenta/regras/magias",
        params={"tipo": "arcana", "limit": 1},
    )
    r_div = client_regras_tormenta.get(
        "/api/v1/tormenta/regras/magias",
        params={"tipo": "divina", "limit": 1},
    )
    assert int(r_arc.json()["total"]) >= 350
    assert int(r_div.json()["total"]) >= 250


def test_magias_mb_catalogo_g5_escola_completa():
    """G5: enriquecimento MB (pp.150–209) com escola em 100% dos itens reais."""
    catalogo_path = (
        Path(__file__).resolve().parents[1]
        / "app"
        / "games"
        / "tormenta"
        / "data"
        / "magias_mb_catalogo.json"
    )
    data = json.loads(catalogo_path.read_text(encoding="utf-8"))
    itens = data.get("itens") or []
    stubs = sum(
        1
        for row in itens
        if isinstance(row, dict)
        and (
            str(row.get("nome") or "").startswith("[Stub]")
            or str(row.get("slug") or "").startswith("stub_")
        )
    )
    sem_escola = [
        row
        for row in itens
        if isinstance(row, dict)
        and not row.get("escola")
        and not str(row.get("nome") or "").startswith("[Stub]")
    ]
    meta = data.get("meta") or {}
    assert len(itens) >= 700
    assert stubs == 5
    assert (
        not sem_escola
    ), f"magias sem escola: {[r.get('nome') for r in sem_escola[:10]]}"
    assert meta.get("g5_estado") == "enriquecimento_completo"
    assert float(meta.get("g5_escola_cobertura") or 0) >= 1.0


def test_get_regras_magias_item_tem_descricao_longa_reservada(client_regras_tormenta):
    r = client_regras_tormenta.get(
        "/api/v1/tormenta/regras/magias", params={"limit": 1}
    )
    assert r.status_code == 200, r.text
    it = r.json()["itens"][0]
    assert "descricao_longa" in it
    assert it.get("descricao_longa") in (None, "")


def test_get_regras_conjuracao_mb(client_regras_tormenta):
    r = client_regras_tormenta.get("/api/v1/tormenta/regras/conjuracao-mb")
    assert r.status_code == 200, r.text
    body = r.json()
    assert "classes" in body and "custo_pm_circulos" in body
    assert len(body["classes"]) == 7
    slugs = {x["slug"] for x in body["classes"]}
    assert slugs == {
        "bardo",
        "clerigo",
        "druida",
        "feiticeiro",
        "mago",
        "paladino",
        "ranger",
    }
    mago = next(x for x in body["classes"] if x["slug"] == "mago")
    assert (
        mago["habilidade_chave"] == "int"
        and mago["pm_constante"] == 1
        and mago["pm_por_nivel"] == 3
    )
    custos = {x["circulo"]: x["custo_pm"] for x in body["custo_pm_circulos"]}
    assert custos[0] == 0 and custos[1] == 1 and custos[5] == 5
    assert body.get("nota_custo_magia")


def test_get_regras_conjuracao_preview_mago(client_regras_tormenta):
    r = client_regras_tormenta.get(
        "/api/v1/tormenta/regras/conjuracao-preview",
        params={"classe_slug": "mago", "nivel": 1, "int_valor": 14},
    )
    assert r.status_code == 200, r.text
    b = r.json()
    assert b["classe_slug"] == "mago"
    assert b["nivel_conjuracao"] == 1
    assert b["habilidade_chave"] == "int"
    assert b["modificador_conjuracao"] == 2
    assert b["cd_magia"] == 12
    assert b["pontos_mana_maximos"] is not None
    assert b["pontos_magia_maximos"] == b["pontos_mana_maximos"]
    assert b.get("magias_lista_tipo") == "arcana"
    assert b.get("magias_circulo_max") == 1


def test_get_regras_conjuracao_preview_nivel_conjurador_override(
    client_regras_tormenta,
):
    r = client_regras_tormenta.get(
        "/api/v1/tormenta/regras/conjuracao-preview",
        params={
            "classe_slug": "paladino",
            "nivel": 4,
            "nivel_conjurador": 5,
            "sab_valor": 12,
        },
    )
    assert r.status_code == 200, r.text
    b = r.json()
    assert b["nivel_conjuracao"] == 5
    assert b["habilidade_chave"] == "sab"
    assert b["pontos_mana_maximos"] is not None
    assert b["pontos_magia_maximos"] == b["pontos_mana_maximos"]
    assert b.get("magias_lista_tipo") == "divina"
    assert b.get("magias_circulo_max") == 1


def test_get_regras_conjuracao_preview_guerreiro_sem_conjuracao(client_regras_tormenta):
    r = client_regras_tormenta.get(
        "/api/v1/tormenta/regras/conjuracao-preview",
        params={"classe_slug": "guerreiro", "nivel": 5},
    )
    assert r.status_code == 200, r.text
    b = r.json()
    assert b["habilidade_chave"] is None
    assert b["modificador_conjuracao"] is None
    assert b["cd_magia"] is None
    assert b["pontos_mana_maximos"] is None
    assert b.get("pontos_magia_maximos") is None
    assert b.get("magias_lista_tipo") is None
    assert b.get("magias_circulo_max") == 0
