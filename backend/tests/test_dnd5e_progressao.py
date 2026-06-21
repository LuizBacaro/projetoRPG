"""Progressão D&D 5e — HP incremental, marcos feat/ASI, geração de atributos."""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.games.dnd5e.api.v1.personagens import router as dnd5e_personagens_router
from app.games.dnd5e.api.v1.regras import router as dnd5e_regras_router
from app.games.dnd5e.models.personagem import Dnd5ePersonagem
from app.games.dnd5e.rules.progressao import (
    aplicar_marco_na_ficha,
    aplicar_retroativo_con_hp_na_ficha,
    calcular_cura_repouso_longo,
    calcular_hp_max_total,
    gerar_scores_4d6,
    hp_max_nivel_1,
    humano_precisa_feat_nivel_1,
    listar_pendencias,
    matriz_padrao_scores,
    mesclar_feat_escolhas,
    migrar_ficha_para_v2,
    montar_hp_resumo,
    pendencias_feat_escolhas,
    recalcular_ganhos_hp_rolls,
    registrar_hp_roll_na_ficha,
    sincronizar_dados_de_marcos,
    validar_feat_escolhas_ficha,
    validar_marco,
    validar_nivel_vs_experiencia,
    validar_progressao_ficha,
)
from app.repositories.base import commit_with_rollback
from app.shared.core.deps import get_usuario_atual


def test_migrar_ficha_v1_para_v2():
    ficha = {"raca_slug": "humano", "classe_slug": "guerreiro"}
    out = migrar_ficha_para_v2(ficha)
    assert out["v"] == 2
    assert out["metodo_atributos"] == "padrao"
    assert "progressao" in out
    assert out["progressao"]["hp_rolls"] == []


def test_migrar_ficha_legado_raca_classe():
    out = migrar_ficha_para_v2({"raca": "humano", "classe": "guerreiro"})
    assert out["raca_slug"] == "humano"
    assert out["classe_slug"] == "guerreiro"


def test_gerar_scores_4d6_reproduzivel():
    a = gerar_scores_4d6(seed=42)
    b = gerar_scores_4d6(seed=42)
    assert a == b
    assert len(a) == 6


def test_matriz_padrao():
    scores = matriz_padrao_scores()
    assert scores["strength"] == 15
    assert scores["charisma"] == 8


def test_hp_max_total_nivel_3():
    rolls = [
        {"nivel": 2, "roll": 6, "con_mod": 2, "ganho": 8},
        {"nivel": 3, "roll": 5, "con_mod": 2, "ganho": 7},
    ]
    total = calcular_hp_max_total("guerreiro", 2, 3, rolls)
    assert total == 12 + 8 + 7


def test_hp_nivel_1_com_roll_manual():
    rolls = [{"nivel": 1, "roll": 8, "con_mod": 2, "ganho": 10}]
    assert calcular_hp_max_total("guerreiro", 2, 1, rolls) == 10


def test_hp_nivel_1_anao_bonus_por_nivel():
    rolls = [{"nivel": 1, "roll": 8, "con_mod": 2, "ganho": 10}]
    assert calcular_hp_max_total("guerreiro", 2, 1, rolls, raca_slug="anao") == 11


def test_hp_tough_mais_raca_nivel_3():
    rolls = [
        {"nivel": 1, "roll": 10, "con_mod": 2, "ganho": 12},
        {"nivel": 2, "roll": 6, "con_mod": 2, "ganho": 8},
        {"nivel": 3, "roll": 5, "con_mod": 2, "ganho": 7},
    ]
    total = calcular_hp_max_total(
        "guerreiro", 2, 3, rolls, raca_slug="anao", feats=["tough"]
    )
    # nív.1: 12+3, nív.2: 8+3, nív.3: 7+3
    assert total == 15 + 11 + 10


def test_registrar_hp_roll_nivel_1():
    ficha = migrar_ficha_para_v2({"classe_slug": "mago", "raca_slug": "humano"})
    ficha, entrada = registrar_hp_roll_na_ficha(
        ficha, nivel=1, classe_slug="mago", con_mod=-1, roll=4
    )
    assert entrada["ganho"] == 3  # 4 + (-1), mín. 1 -> actually max(1, 4-1)=3
    resumo = montar_hp_resumo("mago", -1, 1, ficha["progressao"]["hp_rolls"])
    assert resumo["total"] == 3


def test_hp_max_nivel_1_maximo_dado():
    assert hp_max_nivel_1("guerreiro", 2) == 12


def test_validar_nivel_vs_xp():
    validar_nivel_vs_experiencia(5, 6500)
    with pytest.raises(ValueError, match="Nível 5"):
        validar_nivel_vs_experiencia(5, 900)


def test_recalcular_ganhos_hp_rolls_con_retroativa():
    rolls = [
        {"nivel": 1, "roll": 10, "con_mod": 1, "ganho": 11},
        {"nivel": 2, "roll": 6, "con_mod": 1, "ganho": 7},
        {"nivel": 3, "roll": 5, "con_mod": 1, "ganho": 6},
    ]
    out = recalcular_ganhos_hp_rolls(rolls, 2, nivel_max=3)
    assert [r["ganho"] for r in out] == [12, 8, 7]
    assert [r["con_mod"] for r in out] == [2, 2, 2]
    total_antes = calcular_hp_max_total("guerreiro", 1, 3, rolls)
    total_depois = calcular_hp_max_total("guerreiro", 2, 3, out)
    assert total_depois - total_antes == 3


def test_aplicar_retroativo_con_hp_na_ficha():
    ficha = migrar_ficha_para_v2(
        {
            "classe_slug": "guerreiro",
            "progressao": {
                "hp_rolls": [
                    {"nivel": 1, "roll": 10, "con_mod": 1, "ganho": 11},
                    {"nivel": 2, "roll": 6, "con_mod": 1, "ganho": 7},
                ],
                "marcos": [],
            },
        }
    )
    out = aplicar_retroativo_con_hp_na_ficha(ficha, con_mod_novo=2, nivel=2)
    rolls = out["progressao"]["hp_rolls"]
    assert rolls[0]["ganho"] == 12
    assert rolls[1]["ganho"] == 8


def test_marco_asi_con_aumenta_hp_retroativo():
    ficha = migrar_ficha_para_v2(
        {
            "raca_slug": "humano",
            "classe_slug": "guerreiro",
            "scores_base": matriz_padrao_scores(),
            "progressao": {
                "hp_rolls": [
                    {"nivel": 1, "roll": 10, "con_mod": 1, "ganho": 11},
                    {"nivel": 2, "roll": 6, "con_mod": 1, "ganho": 7},
                    {"nivel": 3, "roll": 5, "con_mod": 1, "ganho": 6},
                    {"nivel": 4, "roll": 8, "con_mod": 1, "ganho": 9},
                ],
                "marcos": [],
            },
        }
    )
    hp_antes = calcular_hp_max_total("guerreiro", 1, 4, ficha["progressao"]["hp_rolls"])
    ficha = aplicar_marco_na_ficha(
        ficha,
        {"nivel": 4, "tipo": "asi", "distribuicao": {"constitution": 2}},
    )
    ficha = aplicar_retroativo_con_hp_na_ficha(ficha, con_mod_novo=2, nivel=4)
    hp_depois = calcular_hp_max_total(
        "guerreiro",
        2,
        4,
        ficha["progressao"]["hp_rolls"],
    )
    assert hp_depois - hp_antes == 4


def test_calcular_cura_repouso_longo():
    import random

    rng = random.Random(42)
    total, detalhes = calcular_cura_repouso_longo(1, 2, rng=rng)
    assert total == 0
    assert detalhes == []

    rng2 = random.Random(99)
    total3, det3 = calcular_cura_repouso_longo(3, 1, rng=rng2)
    assert len(det3) == 2
    assert det3[0]["nivel"] == 2
    assert det3[1]["nivel"] == 3
    assert all(d["ganho"] >= 1 for d in det3)
    assert total3 == sum(d["ganho"] for d in det3)


def test_aplicar_repouso_longo_service():
    from app.games.dnd5e.repositories.personagem_repository import (
        Dnd5ePersonagemRepository,
    )
    from app.games.dnd5e.services.progressao_service import Dnd5eProgressaoService
    from app.shared.core.database import SessionLocal

    db = SessionLocal()
    try:
        p = Dnd5ePersonagem(
            tipo="jogador",
            nome="Curador",
            nivel=3,
            constitution=14,
            hp_max=30,
            hp_atual=10,
            ficha_json={
                "classe_slug": "guerreiro",
                "raca_slug": "humano",
                "scores_base": matriz_padrao_scores(),
            },
        )
        db.add(p)
        commit_with_rollback(db)
        db.refresh(p)
        svc = Dnd5eProgressaoService(Dnd5ePersonagemRepository(db))
        res = svc.aplicar_repouso_longo(p.id)
        assert res.cura_total >= 2
        assert res.hp_atual > 10
        assert res.hp_atual <= 30
        assert len(res.cura_niveis) == 2
    finally:
        db.close()


def test_registrar_hp_roll_e_marco_feat():
    ficha = migrar_ficha_para_v2(
        {
            "raca_slug": "humano",
            "classe_slug": "guerreiro",
            "scores_base": matriz_padrao_scores(),
        }
    )
    ficha, entrada = registrar_hp_roll_na_ficha(
        ficha,
        nivel=2,
        classe_slug="guerreiro",
        con_mod=2,
        roll=7,
    )
    assert entrada["ganho"] == 9
    ficha = aplicar_marco_na_ficha(
        ficha,
        {"nivel": 4, "tipo": "feat", "slug": "alert"},
    )
    assert "alert" in ficha["feats"]


@pytest.fixture
def client_regras():
    app = FastAPI()
    app.include_router(dnd5e_regras_router, prefix="/api/v1")
    u = SimpleNamespace(id=1, perfil="jogador", email="t@example.com", nome="Teste")
    app.dependency_overrides[get_usuario_atual] = lambda: u
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_post_gerar_atributos_padrao(client_regras):
    r = client_regras.post(
        "/api/v1/dnd5e/regras/gerar-atributos",
        json={"metodo": "padrao"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["metodo"] == "padrao"
    assert data["scores_base"]["strength"] == 15


def test_post_gerar_atributos_4d6(client_regras):
    r = client_regras.post(
        "/api/v1/dnd5e/regras/gerar-atributos",
        json={"metodo": "4d6", "seed": 99},
    )
    assert r.status_code == 200
    assert r.json()["metodo"] == "4d6"


def test_humano_pendencia_feat_nivel_1():
    ficha = migrar_ficha_para_v2({"raca_slug": "humano", "classe_slug": "guerreiro"})
    pend = listar_pendencias(nivel=1, classe_slug="guerreiro", con_mod=2, ficha=ficha)
    assert "feat_nivel_1" in pend
    assert humano_precisa_feat_nivel_1(ficha) is True


def test_humano_marco_feat_nivel_1_remove_pendencia():
    ficha = migrar_ficha_para_v2(
        {
            "raca_slug": "humano",
            "classe_slug": "guerreiro",
            "scores_base": matriz_padrao_scores(),
            "progressao": {"hp_rolls": [], "marcos": []},
        }
    )
    marco = {"nivel": 1, "tipo": "feat", "slug": "alert"}
    validar_marco(marco, ficha=ficha, nivel=1, scores_efetivos=matriz_padrao_scores())
    ficha = aplicar_marco_na_ficha(ficha, marco)
    assert "alert" in ficha["feats"]
    pend = listar_pendencias(nivel=1, classe_slug="guerreiro", con_mod=2, ficha=ficha)
    assert "feat_nivel_1" not in pend


def test_validar_progressao_humano_sem_feat_falha():
    ficha = migrar_ficha_para_v2({"raca_slug": "humano", "classe_slug": "guerreiro"})
    with pytest.raises(ValueError, match="talento no nível 1"):
        validar_progressao_ficha(
            ficha,
            nivel=1,
            classe_slug="guerreiro",
            con_mod=2,
            experiencia=0,
        )


def test_mesclar_feat_escolhas_resilient():
    ficha = migrar_ficha_para_v2({"feats": ["resilient"]})
    out = mesclar_feat_escolhas(ficha, {"resilient": "constitution"})
    assert out["feat_escolhas"]["resilient"] == "constitution"
    validar_feat_escolhas_ficha(out)


def test_resilient_sem_escolha_pendencia():
    ficha = migrar_ficha_para_v2({"feats": ["resilient"]})
    assert "feat_escolha_resilient" in pendencias_feat_escolhas(ficha)
    assert "feat_escolha_resilient" in listar_pendencias(
        nivel=4, classe_slug="guerreiro", con_mod=2, ficha=ficha
    )


def test_marco_resilient_exige_escolha():
    ficha = migrar_ficha_para_v2(
        {
            "raca_slug": "humano",
            "classe_slug": "guerreiro",
            "scores_base": matriz_padrao_scores(),
        }
    )
    marco = {"nivel": 1, "tipo": "feat", "slug": "resilient"}
    with pytest.raises(ValueError, match="Resiliente"):
        validar_marco(
            marco, ficha=ficha, nivel=1, scores_efetivos=matriz_padrao_scores()
        )


def test_aplicar_marco_magic_initiate_com_escolha():
    ficha = migrar_ficha_para_v2(
        {
            "raca_slug": "humano",
            "classe_slug": "guerreiro",
            "scores_base": matriz_padrao_scores(),
        }
    )
    marco = {
        "nivel": 1,
        "tipo": "feat",
        "slug": "magic-initiate",
        "feat_escolhas": {"magic_initiate": "mago"},
    }
    validar_marco(marco, ficha=ficha, nivel=1, scores_efetivos=matriz_padrao_scores())
    out = aplicar_marco_na_ficha(ficha, marco)
    assert out["feat_escolhas"]["magic_initiate"] == "mago"
    assert "feat_escolha_magic_initiate" not in pendencias_feat_escolhas(out)


def test_mesclar_feat_escolhas_skilled():
    ficha = migrar_ficha_para_v2({"feats": ["skilled"]})
    out = mesclar_feat_escolhas(
        ficha,
        {"skilled_pericias": ["furtividade", "percepcao", "investigacao"]},
    )
    assert out["feat_escolhas"]["skilled_pericias"] == [
        "furtividade",
        "percepcao",
        "investigacao",
    ]
    validar_feat_escolhas_ficha(out)


def test_skilled_sem_escolha_pendencia():
    ficha = migrar_ficha_para_v2({"feats": ["skilled"]})
    assert "feat_escolha_skilled" in pendencias_feat_escolhas(ficha)
    assert "feat_escolha_skilled" in listar_pendencias(
        nivel=4, classe_slug="guerreiro", con_mod=2, ficha=ficha
    )


def test_marco_skilled_exige_tres_pericias():
    ficha = migrar_ficha_para_v2(
        {
            "raca_slug": "elfo",
            "classe_slug": "guerreiro",
            "scores_base": matriz_padrao_scores(),
        }
    )
    marco = {
        "nivel": 4,
        "tipo": "feat",
        "slug": "skilled",
        "feat_escolhas": {"skilled_pericias": ["atletismo", "intuicao"]},
    }
    with pytest.raises(ValueError, match="3 perícias"):
        validar_marco(
            marco, ficha=ficha, nivel=4, scores_efetivos=matriz_padrao_scores()
        )


def test_sincronizar_dados_de_marcos_deriva_feats_e_asi():
    ficha = migrar_ficha_para_v2(
        {
            "progressao": {
                "marcos": [
                    {"nivel": 1, "tipo": "feat", "slug": "alert"},
                    {"nivel": 4, "tipo": "asi", "distribuicao": {"wisdom": 2}},
                ],
            },
        }
    )
    out = sincronizar_dados_de_marcos(ficha)
    assert "alert" in out["feats"]
    assert out["bonus_atributo_feat"]["wisdom"] == 2


def test_validar_progressao_nivel5_exige_hp_e_marco4():
    ficha = migrar_ficha_para_v2(
        {
            "raca_slug": "humano",
            "classe_slug": "guerreiro",
            "scores_base": matriz_padrao_scores(),
            "pericia_racial_extra": "percepcao",
            "pericias_classe_escolhidas": ["atletismo", "intuicao"],
            "progressao": {
                "hp_rolls": [
                    {"nivel": 1, "roll": 10, "con_mod": 2, "ganho": 12},
                    {"nivel": 2, "roll": 6, "con_mod": 2, "ganho": 8},
                    {"nivel": 3, "roll": 5, "con_mod": 2, "ganho": 7},
                    {"nivel": 4, "roll": 7, "con_mod": 2, "ganho": 9},
                    {"nivel": 5, "roll": 6, "con_mod": 2, "ganho": 8},
                ],
                "marcos": [
                    {"nivel": 1, "tipo": "feat", "slug": "alert"},
                    {"nivel": 4, "tipo": "asi", "distribuicao": {"constitution": 2}},
                ],
            },
        }
    )
    validar_progressao_ficha(
        ficha,
        nivel=5,
        classe_slug="guerreiro",
        con_mod=2,
        experiencia=6500,
        exigir_hp_nivel_1=True,
    )
    pend = listar_pendencias(nivel=5, classe_slug="guerreiro", con_mod=2, ficha=ficha)
    assert "marco_nivel_4" not in pend
    assert "hp_nivel_2" not in pend
