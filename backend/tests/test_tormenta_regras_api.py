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
    assert len(body["pericias"]) == 30
    assert body["pericias"][0]["nome"] == "Acrobacia"
    assert body["pericias"][0]["atributo"] == "des"
    assert body["pericias"][0]["somente_treinado"] is False
    assert body["pericias"][0]["penalidade_armadura"] is True
    assert body["pericias"][1]["nome"] == "Adestramento"
    assert body["pericias"][1]["somente_treinado"] is True
    assert body["pericias"][1]["penalidade_armadura"] is False
    assert body["pericias"][-1]["nome"] == "Vontade"
    assert body["pericias"][-1]["atributo"] == "sab"


def test_get_regras_atributos_v13(client_regras_tormenta):
    r = client_regras_tormenta.get(
        "/api/v1/tormenta/regras/atributos", params={"regra_versao": "v13"}
    )
    assert r.status_code == 200
    body = r.json()
    assert body["regra_versao"] == "v13"
    assert body["pontos_compra_iniciais"] == 10
    assert len(body["pericias"]) == 29
    nomes = {p["nome"] for p in body["pericias"]}
    assert "Misticismo" in nomes
    assert "Atuação" in nomes
    atuacao = next(p for p in body["pericias"] if p["nome"] == "Atuação")
    assert atuacao["somente_treinado"] is True


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


def test_post_gerar_atributos_compra_pontos_v13(client_regras_tormenta):
    r = client_regras_tormenta.post(
        "/api/v1/tormenta/regras/gerar-atributos",
        json={"metodo": "compra_pontos", "regra_versao": "v13"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["regra_versao"] == "v13"
    assert all(v == 0 for v in body["valores"].values())
    assert body["soma_modificadores"] == 0


def test_post_gerar_atributos_4d6_v13(client_regras_tormenta):
    r = client_regras_tormenta.post(
        "/api/v1/tormenta/regras/gerar-atributos",
        json={"metodo": "4d6", "seed": 42, "regra_versao": "v13"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["regra_versao"] == "v13"
    assert body["qualidade_4d6_ok"] is True
    vals = list(body["valores"].values())
    assert all(-2 <= v <= 4 for v in vals)
    assert sum(vals) >= 6


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


def test_get_regras_racas_v13(client_regras_tormenta):
    r = client_regras_tormenta.get(
        "/api/v1/tormenta/regras/racas", params={"regra_versao": "v13"}
    )
    assert r.status_code == 200
    body = r.json()
    assert body["regra_versao"] == "v13"
    assert len(body["racas"]) == 17
    slugs = {x["slug"] for x in body["racas"]}
    assert "hynne" in slugs and "dahllan" in slugs
    assert "gnomo" not in slugs
    assert "eiradaan" not in slugs
    assert all(x.get("fonte_catalogo") == "core" for x in body["racas"])
    hum = next(x for x in body["racas"] if x["slug"] == "humano")
    assert hum["escolhe_tres_mais1"] is True
    lef = next(x for x in body["racas"] if x["slug"] == "lefou")
    assert lef["escolhe_lefou_deformidade"] is True


def test_get_regras_racas_v13_herois_arton(client_regras_tormenta):
    r = client_regras_tormenta.get(
        "/api/v1/tormenta/regras/racas",
        params={"regra_versao": "v13", "suplemento": "herois_arton"},
    )
    assert r.status_code == 200
    body = r.json()
    assert len(body["racas"]) == 21  # 17 core + 4 suplemento (sem Duende)
    eir = next(x for x in body["racas"] if x["slug"] == "eiradaan")
    assert eir["fonte_catalogo"] == "herois_arton"


def test_get_regras_escolhas_raciais_lefou(client_regras_tormenta):
    r = client_regras_tormenta.get(
        "/api/v1/tormenta/regras/escolhas-raciais",
        params={"slug": "lefou", "regra_versao": "v13"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["regra_versao"] == "v13"
    assert body["raca"]["slug"] == "lefou"
    assert body["raca"]["tipo"] == "deformidade"
    assert len(body["raca"]["modos"]) == 2


def test_get_regras_escolhas_raciais_golem(client_regras_tormenta):
    r = client_regras_tormenta.get(
        "/api/v1/tormenta/regras/escolhas-raciais",
        params={"slug": "golem", "regra_versao": "v13"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["raca"]["tipo"] == "fonte_elemental_poder"
    assert len(body["raca"]["fontes"]) == 4


def test_get_tracos_raciais_lefou_deformidade(client_regras_tormenta):
    r = client_regras_tormenta.get(
        "/api/v1/tormenta/regras/tracos-raciais-preview",
        params={
            "slug": "lefou",
            "regra_versao": "v13",
            "lefou_deformidade_modo": "duas_pericias",
            "lefou_deformidade_pericias": "Acrobacia,Percepção",
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["pericias_bonus"]["Acrobacia"] == 2
    assert body["pericias_bonus"]["Percepção"] == 2


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
    nv1 = next(x for x in body["beneficios_por_nivel"] if x["nivel"] == 1)
    assert nv1["graduacao_pericias"] == "+4/+0"


def test_get_regras_classes_v13_beneficios(client_regras_tormenta):
    r = client_regras_tormenta.get(
        "/api/v1/tormenta/regras/classes",
        params={"regra_versao": "v13"},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["regra_versao"] == "v13"
    assert len(body["classes"]) == 14
    slugs = {x["slug"] for x in body["classes"]}
    assert "arcanista" in slugs
    assert "mago" not in slugs
    assert "ranger" not in slugs
    bar = next(x for x in body["classes"] if x["slug"] == "barbaro")
    assert bar["pv_inicial"] == 24
    assert bar["pv_por_nivel"] == 6
    assert bar["pm_por_nivel"] == 3
    arc = next(x for x in body["classes"] if x["slug"] == "arcanista")
    assert arc["pm_por_nivel"] == 6
    assert arc.get("atributo_principal")
    assert len(body["beneficios_por_nivel"]) == 20
    nv1 = next(x for x in body["beneficios_por_nivel"] if x["nivel"] == 1)
    assert nv1["graduacao_pericias"] == "+2/+0"
    assert nv1.get("poderes_gerais_totais") == 1
    nv7 = next(x for x in body["beneficios_por_nivel"] if x["nivel"] == 7)
    assert nv7["graduacao_pericias"] == "+7/+3"
    nv20 = next(x for x in body["beneficios_por_nivel"] if x["nivel"] == 20)
    assert nv20["xp_total"] == 190000


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


def test_get_regras_equipamentos_armadura_v13(client_regras_tormenta):
    r = client_regras_tormenta.get(
        "/api/v1/tormenta/regras/equipamentos",
        params={"q": "Armadura de couro", "limit": 1},
    )
    assert r.status_code == 200
    itens = r.json()["itens"]
    assert len(itens) == 1
    row = itens[0]
    assert row["tipo"] == "leve"
    assert row["bonus_ca"] == 2
    assert row["espacos"] == 2


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
    valk = next(d for d in body["divindades"] if d["slug"] == "valkaria")
    assert valk.get("energia")
    assert len(valk.get("poderes_concedidos") or []) == 4
    ali = next(d for d in body["divindades"] if d["slug"] == "allihanna")
    assert ali.get("pagina") == 97
    flags = ali.get("obrigacoes_flags") or []
    assert any(f.get("slug") == "nao_usar_armadura_metal" for f in flags)
    nimb = next(d for d in body["divindades"] if d["slug"] == "nimb")
    assert nimb.get("sem_penalidade_obrigacao") is True


def test_get_regras_origens_v13(client_regras_tormenta):
    r = client_regras_tormenta.get(
        "/api/v1/tormenta/regras/origens", params={"regra_versao": "v13"}
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["regra_versao"] == "v13"
    assert len(body["origens"]) == 35
    acolito = next(o for o in body["origens"] if o["slug"] == "acolito")
    assert acolito["nome"] == "Acólito"
    assert "cura" in acolito["beneficios_pericias"]
    assert "medicina" in acolito["beneficios_poderes"]


def test_get_regras_classes_herois_arton(client_regras_tormenta):
    r = client_regras_tormenta.get(
        "/api/v1/tormenta/regras/classes",
        params={"regra_versao": "v13", "suplemento": "herois_arton"},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert len(body["classes"]) == 29  # 14 core + 15 suplemento
    tre = next(c for c in body["classes"] if c["slug"] == "treinador")
    assert tre["fonte_catalogo"] == "herois_arton"
    assert tre["pm_por_nivel"] == 4


def test_get_regras_origens_herois_arton(client_regras_tormenta):
    r = client_regras_tormenta.get(
        "/api/v1/tormenta/regras/origens",
        params={"regra_versao": "v13", "suplemento": "herois_arton"},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert len(body["origens"]) == 49  # 35 core + 14 suplemento
    bacharel = next(o for o in body["origens"] if o["slug"] == "bacharel")
    assert bacharel["fonte_catalogo"] == "herois_arton"
    assert bacharel["troca_pericia_treinada"] is True


def test_get_truques_melhor_amigo(client_regras_tormenta):
    r = client_regras_tormenta.get(
        "/api/v1/tormenta/regras/truques-melhor-amigo",
        params={"nivel_treinador": 5},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["nivel_treinador"] == 5
    assert body["qtd_maxima_truques"] == 3
    assert len(body["truques"]) >= 8


def test_get_tipos_melhor_amigo(client_regras_tormenta):
    r = client_regras_tormenta.get("/api/v1/tormenta/regras/tipos-melhor-amigo")
    assert r.status_code == 200, r.text
    body = r.json()
    assert len(body["tipos"]) == 5


def test_get_regras_armaduras_protecao_pagina(client_regras_tormenta):
    r = client_regras_tormenta.get(
        "/api/v1/tormenta/regras/armaduras-protecao", params={"skip": 0, "limit": 20}
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert "itens" in body and "total" in body
    assert body["total"] == 13
    assert len(body["itens"]) == 13
    assert body["itens"][0]["nome"] == "Armadura de couro"
    assert body["itens"][0]["bonus_ca"] == 2


def test_get_regras_condicoes_v13(client_regras_tormenta):
    r = client_regras_tormenta.get("/api/v1/tormenta/regras/condicoes")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["total"] >= 30
    slugs = {c["slug"] for c in body["condicoes"]}
    assert "desprevenido" in slugs
    assert "vulneravel" in slugs
    assert len(body["situacoes_especiais"]) >= 3


def test_get_tracos_raciais_preview(client_regras_tormenta):
    r = client_regras_tormenta.get(
        "/api/v1/tormenta/regras/tracos-raciais-preview", params={"slug": "goblin"}
    )
    assert r.status_code == 200
    body = r.json()
    assert body["encontrado"] is True
    assert body["ca_bonus"] == 1


def test_get_tracos_raciais_preview_v13(client_regras_tormenta):
    r = client_regras_tormenta.get(
        "/api/v1/tormenta/regras/tracos-raciais-preview",
        params={"slug": "goblin", "regra_versao": "v13"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["regra_versao"] == "v13"
    assert body["furtividade_bonus"] == 2
    assert body["fortitude_bonus"] == 2


def test_get_regras_pericias_dcs(client_regras_tormenta):
    r = client_regras_tormenta.get("/api/v1/tormenta/regras/pericias")
    assert r.status_code == 200
    body = r.json()
    assert body["bonus_treinado"] == 2
    assert len(body["dificuldades"]) >= 6


def test_get_regras_pericias_v13(client_regras_tormenta):
    r = client_regras_tormenta.get(
        "/api/v1/tormenta/regras/pericias", params={"regra_versao": "v13"}
    )
    assert r.status_code == 200
    body = r.json()
    assert body["regra_versao"] == "v13"
    assert body["bonus_treinamento_niveis"] is not None
    assert len(body["bonus_treinamento_niveis"]) == 3


def test_post_pericias_calcular_bonus_v13(client_regras_tormenta):
    r = client_regras_tormenta.post(
        "/api/v1/tormenta/regras/pericias/calcular-bonus",
        json={
            "nivel": 7,
            "mod_atributo": 3,
            "treinado": True,
            "regra_versao": "v13",
            "nome_pericia": "Acrobacia",
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["bonus_total"] == 10
    assert body["bonus_treinamento"] == 4
    assert body["penalidade_armadura_aplicada"] == 0


def test_post_pericias_calcular_bonus_acrobacia_com_armadura(client_regras_tormenta):
    r = client_regras_tormenta.post(
        "/api/v1/tormenta/regras/pericias/calcular-bonus",
        json={
            "nivel": 7,
            "mod_atributo": 3,
            "treinado": True,
            "regra_versao": "v13",
            "nome_pericia": "Acrobacia",
            "itens_protecao": [
                {"nome": "Cota de malha", "tipo": "media", "penalidade": -2},
                {"nome": "Escudo leve", "tipo": "escudo", "penalidade": -1},
            ],
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["penalidade_armadura_aplicada"] == 3
    assert body["bonus_total"] == 7


def test_post_pericias_calcular_bonus_percepcao_passiva(client_regras_tormenta):
    r = client_regras_tormenta.post(
        "/api/v1/tormenta/regras/pericias/calcular-bonus",
        json={
            "nivel": 3,
            "mod_atributo": 4,
            "treinado": True,
            "regra_versao": "v13",
            "nome_pericia": "Percepção",
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["bonus_total"] == 7
    assert body["percepcao_passiva"] == 17


def test_post_pericias_calcular_bonus_diplomacia_ignora_armadura(
    client_regras_tormenta,
):
    r = client_regras_tormenta.post(
        "/api/v1/tormenta/regras/pericias/calcular-bonus",
        json={
            "nivel": 3,
            "mod_atributo": 2,
            "treinado": False,
            "regra_versao": "v13",
            "nome_pericia": "Diplomacia",
            "itens_protecao": [{"nome": "Placas", "tipo": "pesada", "penalidade": -5}],
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["penalidade_armadura_aplicada"] == 0
    assert body["bonus_total"] == 3


def test_post_pericias_calcular_bonus_luta_arcanista_sem_proficiencia(
    client_regras_tormenta,
):
    r = client_regras_tormenta.post(
        "/api/v1/tormenta/regras/pericias/calcular-bonus",
        json={
            "nivel": 5,
            "mod_atributo": 3,
            "treinado": False,
            "regra_versao": "v13",
            "nome_pericia": "Luta",
            "tormenta_classe_mb_slug": "arcanista",
            "itens_protecao": [{"nome": "Placas", "tipo": "pesada", "penalidade": -5}],
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["penalidade_armadura_aplicada"] == 5
    assert body["bonus_total"] == 0


def test_post_ataque_ajustar_bonus_arcanista_marcial(client_regras_tormenta):
    r = client_regras_tormenta.post(
        "/api/v1/tormenta/regras/ataque/ajustar-bonus",
        json={
            "bonus_base": 6,
            "nome_arma": "Espada longa",
            "tormenta_classe_mb_slug": "arcanista",
        },
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["bonus_efetivo"] == 1
    assert body["penalidade_nao_proficiente"] == 5
    assert body["proficiente"] is False


def test_post_carga_preview_v13(client_regras_tormenta):
    r = client_regras_tormenta.post(
        "/api/v1/tormenta/regras/carga-preview",
        json={
            "for_valor": 2,
            "itens": [
                {"nome": "Mochila", "quantidade": 1},
                {"nome": "Armadura de couro", "tipo": "leve", "quantidade": 1},
            ],
            "moedas_total": 1500,
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["limite"] == 14
    assert body["espacos_moedas"] == 1
    assert body["estado"] == "normal"


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


def test_get_pv_preview_barbaro_v13_pm(client_regras_tormenta):
    r = client_regras_tormenta.get(
        "/api/v1/tormenta/regras/pv-preview",
        params={
            "classe_slug": "barbaro",
            "nivel": 1,
            "con_valor": 2,
            "regra_versao": "v13",
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["regra_versao"] == "v13"
    assert body["pv_max"] == 26
    assert body["pm_por_nivel"] == 3
    assert body["pm_max"] == 3


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


def test_get_regras_conjuracao_mb_v13(client_regras_tormenta):
    r = client_regras_tormenta.get(
        "/api/v1/tormenta/regras/conjuracao-mb",
        params={"regra_versao": "v13"},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["regra_versao"] == "v13"
    assert "classes" in body and "custo_pm_circulos" in body
    assert any(x["slug"] == "arcanista" for x in body["classes"])
    arcanista = next(x for x in body["classes"] if x["slug"] == "arcanista")
    assert arcanista["modo_conjuracao"] == "caminho"
    custos = {x["circulo"]: x["custo_pm"] for x in body["custo_pm_circulos"]}
    assert custos[0] == 0 and custos[1] == 1 and custos[5] == 15
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


def test_post_pm_preview_multiclasse_v13(client_regras_tormenta):
    r = client_regras_tormenta.post(
        "/api/v1/tormenta/regras/pm-preview-multiclasse",
        json={
            "classes": [
                {"slug": "arcanista", "nivel": 3},
                {"slug": "paladino", "nivel": 1},
            ],
            "regra_versao": "v13",
        },
    )
    assert r.status_code == 200, r.text
    b = r.json()
    assert b["pm_max"] == 21
    assert len(b["breakdown"]) == 2


def test_get_dinheiro_inicial_v13(client_regras_tormenta):
    r = client_regras_tormenta.get(
        "/api/v1/tormenta/regras/dinheiro-inicial",
        params={"nivel": 5, "regra_versao": "v13"},
    )
    assert r.status_code == 200, r.text
    b = r.json()
    assert b["tipo"] == "fixo"
    assert b["valor"] == 2000


def test_get_poderes_categoria_filtro_v13(client_regras_tormenta):
    r = client_regras_tormenta.get(
        "/api/v1/tormenta/regras/poderes",
        params={"categoria_v13": "combate", "limit": 5},
    )
    assert r.status_code == 200, r.text
    for it in r.json()["itens"]:
        assert it.get("categoria_v13") == "combate"


def test_get_conjuracao_preview_v13_cd_atributo_valor(client_regras_tormenta):
    r = client_regras_tormenta.get(
        "/api/v1/tormenta/regras/conjuracao-preview",
        params={
            "classe_slug": "clerigo",
            "nivel": 8,
            "sab_valor": 5,
            "regra_versao": "v13",
        },
    )
    assert r.status_code == 200, r.text
    b = r.json()
    assert b["modificador_conjuracao"] == 5
    assert b["cd_magia"] == 19


def test_post_poderes_validar_pre_requisitos_v13(client_regras_tormenta):
    r = client_regras_tormenta.post(
        "/api/v1/tormenta/regras/poderes/validar-pre-requisitos",
        json={
            "nome_poder": "Ataque Poderoso",
            "regra_versao": "v13",
            "for_valor": 0,
        },
    )
    assert r.status_code == 200, r.text
    assert r.json()["valido"] is False
    assert r.json()["faltando"]

    r_ok = client_regras_tormenta.post(
        "/api/v1/tormenta/regras/poderes/validar-pre-requisitos",
        json={
            "nome_poder": "Ataque Poderoso",
            "regra_versao": "v13",
            "for_valor": 2,
        },
    )
    assert r_ok.status_code == 200
    assert r_ok.json()["valido"] is True
