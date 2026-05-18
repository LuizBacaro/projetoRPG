"""Parser de descrições PT do Foundry."""

from app.games.dnd5e.data.foundry_spells import (
    html_para_texto,
    separar_descricao_foundry,
)


def test_separar_descricao_bola_de_fogo():
    html = (
        "<p>Um rastro brilhante lampeja do seu dedo.</p>"
        "<p><strong>Em Círculos Superiores.</strong> O dano aumenta em 1d6.</p>"
    )
    principal, superior = separar_descricao_foundry(html)
    assert "lampeja" in principal
    assert superior is not None
    assert "Círculos Superiores" in superior


def test_html_para_texto_remove_tags():
    assert "dano" in html_para_texto("<p>8d6 de <strong>dano</strong></p>")
