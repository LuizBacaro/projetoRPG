"""Regras D&D 5E — feats."""

from app.games.dnd5e.rules.habilidades import AbilityScores, PersonagemHabilidades
from app.games.dnd5e.rules.talentos import (
    Feat,
    PersonagemFeats,
    adicionar_feat,
    calcular_ganhos_feats,
    feat_do_catalogo,
    listar_feats_por_categoria,
    niveis_com_ganho_feat,
    validar_feat,
)


def test_niveis_ganho_feat() -> None:
    assert niveis_com_ganho_feat() == (4, 8, 12, 16, 19)
    assert calcular_ganhos_feats(4) == 1
    assert calcular_ganhos_feats(8) == 2
    assert calcular_ganhos_feats(19) == 5
    assert calcular_ganhos_feats(1, raca_slug="humano") == 1
    assert calcular_ganhos_feats(1, raca_slug="elfo") == 0


def test_catalogo_tem_cerca_de_50_feats() -> None:
    assert len(listar_feats_por_categoria()) >= 45


def test_pre_requisitos_validam() -> None:
    p = PersonagemFeats(
        habilidades=PersonagemHabilidades(
            abilities=AbilityScores(dexterity=14),
            nivel=5,
        ),
        spellcasting=True,
    )
    feat = feat_do_catalogo("defensive-duelist")
    assert feat is not None
    assert validar_feat(feat, p) is True
    p.habilidades.abilities = AbilityScores(dexterity=10)
    assert validar_feat(feat, p) is False


def test_adicionar_feat_asi() -> None:
    p = PersonagemFeats(
        habilidades=PersonagemHabilidades(nivel=4),
    )
    asi = Feat(
        slug="asi-custom",
        nome="ASI",
        tipo_bonus="Atributo",
        bonus_especial={"strength": 2},
        requisito_nivel=4,
    )
    adicionar_feat(p, asi)
    assert "asi-custom" in p.feats
    assert p.bonus_atributo_feat.get("strength") == 2
