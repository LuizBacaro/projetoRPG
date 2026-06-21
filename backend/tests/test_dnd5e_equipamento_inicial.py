"""Equipamento inicial por classe D&D 5e."""

from app.games.dnd5e.rules.equipamento_inicial import (
    aplicar_equipamento_classe_na_ficha,
)


def test_aplicar_equipamento_guerreiro():
    ficha = {
        "classe_slug": "guerreiro",
        "inventario": {"equipamentos": [], "ouro_po": 0},
    }
    out = aplicar_equipamento_classe_na_ficha(ficha, forcar=True)
    assert out["classe_equip_aplicado"] is True
    assert out["armadura_slug"] == "cota-anéis"
    assert out["escudo_slug"] == "escudo"
    assert out["arma_principal_slug"] == "espada-longa"
    slugs = {i["slug"] for i in out["inventario"]["equipamentos"]}
    assert "mochila" in slugs
    assert "arco-longo" in slugs


def test_trocar_classe_remove_pacote_anterior():
    ficha = aplicar_equipamento_classe_na_ficha(
        {"classe_slug": "guerreiro", "inventario": {"equipamentos": []}},
        forcar=True,
    )
    ficha["classe_slug"] = "mago"
    out = aplicar_equipamento_classe_na_ficha(ficha, forcar=True)
    assert out["classe_equip_slug"] == "mago"
    assert out["arma_principal_slug"] == "adaga"
    assert not any(
        i.get("slug") == "arco-longo"
        for i in out["inventario"]["equipamentos"]
        if i.get("fonte") == "classe"
    )
