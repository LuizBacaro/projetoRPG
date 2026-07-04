"""HA-4 — poderes Heróis de Arton (catálogo, API e ficha)."""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.games.tormenta.api.v1.regras import router as tormenta_regras_router
from app.games.tormenta.rules.poderes_ficha_v13_t20 import nome_poder_por_slug_v13
from app.games.tormenta.rules.poderes_herois_arton_t20 import (
    lista_poderes_herois_arton,
    poder_por_slug,
    poderes_disponiveis_ficha,
)
from app.shared.core.deps import get_usuario_atual


@pytest.fixture(scope="function")
def client_regras_tormenta():
    app = FastAPI()
    app.include_router(tormenta_regras_router, prefix="/api/v1")
    u = SimpleNamespace(id=1, perfil="jogador", email="t@example.com", nome="Teste")
    app.dependency_overrides[get_usuario_atual] = lambda: u
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_lista_poderes_herois_arton_minimo_viavel() -> None:
    rows = lista_poderes_herois_arton()
    slugs = {r["slug"] for r in rows}
    treinador = [r for r in rows if r.get("categoria_v13") == "treinador"]
    assert len(rows) >= 25
    assert len(treinador) >= 20
    assert "amigo_divino" in slugs
    assert "aumento_de_atributo" in slugs
    assert "coracao_grande" in slugs
    assert "eco_arcano" in slugs
    assert "chuva_de_golpes" in slugs


def test_poder_por_slug_amigo_divino() -> None:
    row = poder_por_slug("amigo_divino")
    assert row is not None
    assert row["nome"] == "Amigo Divino"
    assert row["categoria_v13"] == "treinador"
    assert row["classe_exigida"] == "treinador"


def test_nome_poder_por_slug_v13_ha() -> None:
    assert nome_poder_por_slug_v13("amigo_divino") == "Amigo Divino"


def test_get_poderes_treinador_com_suplemento(client_regras_tormenta) -> None:
    r = client_regras_tormenta.get(
        "/api/v1/tormenta/regras/poderes",
        params={
            "suplemento": "herois_arton",
            "categoria_v13": "treinador",
            "limit": 50,
        },
    )
    assert r.status_code == 200, r.text
    slugs = {it.get("slug") for it in r.json()["itens"]}
    assert "amigo_divino" in slugs
    assert "bom_garoto" in slugs
    for it in r.json()["itens"]:
        assert it.get("categoria_v13") == "treinador"
        assert it.get("fonte_catalogo") == "herois_arton"


def test_get_poderes_sem_suplemento_nao_inclui_ha(client_regras_tormenta) -> None:
    r = client_regras_tormenta.get(
        "/api/v1/tormenta/regras/poderes",
        params={"limit": 200},
    )
    assert r.status_code == 200, r.text
    slugs = {it.get("slug") for it in r.json()["itens"]}
    assert "amigo_divino" not in slugs
    assert "eco_arcano" not in slugs


def test_get_poderes_raca_eiradaan(client_regras_tormenta) -> None:
    r = client_regras_tormenta.get(
        "/api/v1/tormenta/regras/poderes",
        params={
            "suplemento": "herois_arton",
            "categoria_v13": "raca",
            "raca": "eiradaan",
            "limit": 20,
        },
    )
    assert r.status_code == 200, r.text
    itens = r.json()["itens"]
    assert len(itens) >= 1
    assert all(it.get("raca_exigida") == "eiradaan" for it in itens)
    assert any(it.get("slug") == "eco_arcano" for it in itens)


def test_poderes_disponiveis_ficha_filtra_raca() -> None:
    ficha_ha = {
        "regra_versao": "v13",
        "game_suplemento": "herois_arton",
        "raca_tormenta_slug": "eiradaan",
        "tormenta_niveis_classe_mb": [{"classe_slug": "arcanista", "nivel": 1}],
    }
    slugs = {r["slug"] for r in poderes_disponiveis_ficha(ficha_ha)}
    assert "eco_arcano" in slugs
    assert "forca_titanica" not in slugs

    ficha_core = {
        "regra_versao": "v13",
        "raca_tormenta_slug": "eiradaan",
    }
    assert poderes_disponiveis_ficha(ficha_core) == []


def test_poderes_disponiveis_ficha_filtra_classe_treinador() -> None:
    ficha = {
        "regra_versao": "v13",
        "game_suplemento": "herois_arton",
        "tormenta_niveis_classe_mb": [{"classe_slug": "treinador", "nivel": 2}],
    }
    slugs = {r["slug"] for r in poderes_disponiveis_ficha(ficha)}
    assert "amigo_divino" in slugs
    assert "chuva_de_golpes" not in slugs


def test_poderes_disponiveis_variante_treinador_prefixo() -> None:
    ficha = {
        "regra_versao": "v13",
        "game_suplemento": "herois_arton",
        "tormenta_classe_mb_slug": "treinador_guerreiro",
        "nivel": 3,
    }
    slugs = {r["slug"] for r in poderes_disponiveis_ficha(ficha)}
    assert "amigo_divino" in slugs
    assert "aumento_de_atributo" in slugs


def test_poderes_disponiveis_multiclasse_v13_treinador() -> None:
    ficha = {
        "regra_versao": "v13",
        "game_suplemento": "herois_arton",
        "multiclasse_v13": [{"slug": "treinador", "nivel": 2}],
    }
    slugs = {r["slug"] for r in poderes_disponiveis_ficha(ficha)}
    assert "bom_garoto" in slugs
    assert "eco_arcano" not in slugs


def test_validar_vinculo_poder_ha_exige_suplemento() -> None:
    from app.games.tormenta.rules.poderes_herois_arton_t20 import (
        validar_vinculo_poder_ha,
    )
    from app.shared.exceptions.custom_exceptions import DadosInvalidos

    with pytest.raises(DadosInvalidos, match="Heróis de Arton"):
        validar_vinculo_poder_ha(
            "Eco Arcano",
            {"regra_versao": "v13", "raca_tormenta_slug": "eiradaan"},
        )


def test_validar_vinculo_poder_ha_bloqueia_raca_errada() -> None:
    from app.games.tormenta.rules.poderes_herois_arton_t20 import (
        validar_vinculo_poder_ha,
    )
    from app.shared.exceptions.custom_exceptions import DadosInvalidos

    ficha = {
        "regra_versao": "v13",
        "game_suplemento": "herois_arton",
        "raca_tormenta_slug": "galokk",
    }
    with pytest.raises(DadosInvalidos, match="elegível"):
        validar_vinculo_poder_ha("Eco Arcano", ficha)


def test_validar_vinculo_poder_ha_ok_eiradaan() -> None:
    from app.games.tormenta.rules.poderes_herois_arton_t20 import (
        validar_vinculo_poder_ha,
    )

    ficha = {
        "regra_versao": "v13",
        "game_suplemento": "herois_arton",
        "raca_tormenta_slug": "eiradaan",
    }
    validar_vinculo_poder_ha("Eco Arcano", ficha)


def test_pm_bonus_meio_elfo_ha_ficha() -> None:
    from app.games.tormenta.rules.progressao_pv_t20 import (
        pm_bonus_racial_ha_de_ficha,
        preview_pm_multiclasse_v13,
    )

    fj = {
        "game_suplemento": "herois_arton",
        "raca_tormenta_slug": "meio_elfo",
    }
    assert pm_bonus_racial_ha_de_ficha(fj, 1) == 1
    assert pm_bonus_racial_ha_de_ficha(fj, 3) == 2
    assert pm_bonus_racial_ha_de_ficha({"raca_tormenta_slug": "meio_elfo"}, 1) == 0
    prev = preview_pm_multiclasse_v13(
        [{"slug": "guerreiro", "nivel": 1}],
        ficha_json=fj,
        nivel_personagem=1,
    )
    assert prev["pm_max"] == 4  # 3 + 1 racial


def test_conjuracao_eiradaan_magia_instintiva() -> None:
    from app.games.tormenta.rules.conjuracao_t20 import (
        habilidade_chave_conjuracao_efetiva,
        modificador_conjuracao_efetivo,
    )

    hk = habilidade_chave_conjuracao_efetiva("arcanista", "v13", None, "eiradaan")
    assert hk == "sab"
    mod = modificador_conjuracao_efetivo(
        "arcanista", 0, 0, 0, 2, 4, 0, "v13", None, "eiradaan"
    )
    assert mod == 4


def test_classe_atende_exigencia_treinador_variante() -> None:
    from app.games.tormenta.rules.poderes_herois_arton_t20 import (
        classe_atende_exigencia,
    )

    assert classe_atende_exigencia("treinador", {"treinador_guerreiro"})
    assert classe_atende_exigencia("treinador", {"treinador"})
    assert not classe_atende_exigencia("treinador", {"guerreiro"})
    assert classe_atende_exigencia("guerreiro", {"guerreiro", "treinador"})
