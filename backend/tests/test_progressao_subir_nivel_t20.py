"""Regras MB — preview subir de nível."""

from app.games.tormenta.rules.progressao_pv_t20 import pv_maximos_v13_multiclasse
from app.games.tormenta.rules.progressao_subir_nivel_t20 import (
    preview_subir_nivel_mb,
    preview_subir_nivel_v13,
)


def test_preview_mago_nivel_2_pv_pm_livro():
    p = preview_subir_nivel_mb(
        nivel_atual=1,
        nivel_alvo=2,
        slug_classe="mago",
        ficha_json={"tormenta_classe_mb_slug": "mago"},
        for_valor=10,
        des_valor=10,
        con_valor=8,
        int_valor=18,
        sab_valor=10,
        car_valor=10,
    )
    assert p["permitido"] is True
    assert p["pv_ganho"] == 1
    assert p["pa_ganho"] == 3
    assert p["magias_livro_ganho"] == 2
    assert "aprende 2 magias" in (p["habilidade_classe"] or "").lower()


def test_preview_rejeita_salto():
    p = preview_subir_nivel_mb(
        nivel_atual=1,
        nivel_alvo=3,
        slug_classe="mago",
        ficha_json={},
        for_valor=10,
        des_valor=10,
        con_valor=10,
        int_valor=10,
        sab_valor=10,
        car_valor=10,
    )
    assert p["permitido"] is False


def test_pv_multiclasse_arcanista3_paladino1_con0():
    """Exemplo livro p.34 — PV multiclasse (CON 0 v1.3)."""
    linhas = [{"slug": "arcanista", "nivel": 3}, {"slug": "paladino", "nivel": 1}]
    pv = pv_maximos_v13_multiclasse(linhas, con_valor=0, slug_primario="arcanista")
    # Arcanista 3: 8+4=12; Paladino 1 (nova): 5; CON×4=0
    assert pv == 17


def test_preview_subir_nivel_v13_nova_classe_paladino():
    p = preview_subir_nivel_v13(
        nivel_personagem=3,
        classe_alvo_slug="paladino",
        ficha_json={
            "regra_versao": "v13",
            "tormenta_classe_mb_slug": "arcanista",
            "multiclasse_v13": [{"slug": "arcanista", "nivel": 3}],
        },
        for_valor=0,
        des_valor=0,
        con_valor=0,
        int_valor=0,
        sab_valor=0,
        car_valor=0,
    )
    assert p["permitido"] is True
    assert p["nivel_atual"] == 3
    assert p["nivel_alvo"] == 4
    assert p["classe_nova_multiclasse"] is True
    assert p["pa_ganho"] == 3
    assert p["pa_max_novo"] == 21
    assert p["pv_ganho"] == 5
    assert p["multiclasse_v13_novo"] == [
        {"slug": "arcanista", "nivel": 3},
        {"slug": "paladino", "nivel": 1},
    ]


def test_preview_subir_nivel_v13_sobe_classe_existente():
    p = preview_subir_nivel_v13(
        nivel_personagem=4,
        classe_alvo_slug="arcanista",
        ficha_json={
            "regra_versao": "v13",
            "tormenta_classe_mb_slug": "arcanista",
            "multiclasse_v13": [
                {"slug": "arcanista", "nivel": 3},
                {"slug": "paladino", "nivel": 1},
            ],
        },
        for_valor=0,
        des_valor=0,
        con_valor=0,
        int_valor=0,
        sab_valor=0,
        car_valor=0,
    )
    assert p["permitido"] is True
    assert p["nivel_alvo"] == 5
    assert p["classe_nova_multiclasse"] is False
    assert p["pa_ganho"] == 6
    assert p["pa_max_novo"] == 27
