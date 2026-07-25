"""Testes — migração magias_texto, concentração ao lançar."""

from __future__ import annotations

import pytest

from app.games.tormenta.rules.catalogo_t20 import resolver_magia_mb_slug_por_texto
from app.games.tormenta.rules.conjuracao_combate_t20 import (
    aplicar_concentracao_ao_lancar,
    limpar_concentracao_mb,
    magia_mb_exige_concentracao,
)


def test_resolver_magia_mb_por_nome():
    """Resolve nome livre em slug do catálogo v1.3 (fonte única, círculos 1–5)."""
    slug = resolver_magia_mb_slug_por_texto("Bola de fogo", tipo_preferido="arcana")
    assert slug == "bola_de_fogo"


def test_resolver_magia_mb_por_nome_legado_retorna_none():
    """Nomes de magias MB removidas em v1.3 (ex.: Mísseis Mágicos) devem retornar None."""
    slug = resolver_magia_mb_slug_por_texto("Mísseis mágicos", tipo_preferido="arcana")
    assert slug is None


def test_magia_exige_concentracao_pela_duracao():
    assert (
        magia_mb_exige_concentracao({"duracao": "concentração, até 1 minuto"}) is True
    )
    assert magia_mb_exige_concentracao({"duracao": "instantânea"}) is False


def test_aplicar_e_limpar_concentracao_ficha_json():
    fj = aplicar_concentracao_ao_lancar(
        {},
        magia_slug="detectar_magia",
        meta={"nome": "Detectar Magia", "duracao": "concentração, até 3 rodadas"},
    )
    sess = fj.get("tormenta_grimorio_sessao_mb") or {}
    assert sess.get("concentracao_magia_slug") == "detectar_magia"
    fj2 = limpar_concentracao_mb(fj)
    assert not (fj2.get("tormenta_grimorio_sessao_mb") or {}).get(
        "concentracao_magia_slug"
    )


@pytest.mark.parametrize("nome", ["missoes", "xyz_inexistente_123"])
def test_resolver_retorna_none_para_desconhecido(nome):
    assert resolver_magia_mb_slug_por_texto(nome) is None
