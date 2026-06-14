"""Regras MB — preview subir de nível."""

from app.games.tormenta.rules.progressao_subir_nivel_t20 import preview_subir_nivel_mb


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
