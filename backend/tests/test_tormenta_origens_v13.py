"""Regras de origens v1.3 — validação de benefícios e sync de perícias."""

from app.games.tormenta.rules.origens_t20 import (
    aplicar_pericias_origem_em_lista,
    lista_origens_v13,
    origem_por_slug,
    sincronizar_pericias_origem_ficha_json,
    slugs_pericias_de_beneficios_origem,
    validar_beneficios_origem,
)
from app.games.tormenta.rules.pericias_criacao_t20 import validar_pericias_ficha


def test_lista_origens_v13_tem_35():
    assert len(lista_origens_v13()) == 35


def test_origem_por_slug_acolito():
    row = origem_por_slug("acolito")
    assert row is not None
    assert row["nome"] == "Acólito"


def test_validar_beneficios_origem_ok():
    ok, msg = validar_beneficios_origem("acolito", ["pericia:cura", "poder:medicina"])
    assert ok is True
    assert msg == ""


def test_validar_beneficios_origem_rejeita_quantidade():
    ok, msg = validar_beneficios_origem("acolito", ["pericia:cura"])
    assert ok is False
    assert "2" in msg


def test_validar_beneficios_origem_rejeita_beneficio_invalido():
    ok, msg = validar_beneficios_origem(
        "acolito", ["pericia:acrobacia", "poder:medicina"]
    )
    assert ok is False
    assert "inválido" in msg.lower()


def test_slugs_pericias_de_beneficios_origem():
    assert slugs_pericias_de_beneficios_origem(["pericia:cura", "poder:medicina"]) == [
        "cura"
    ]


def test_aplicar_pericias_origem_marca_treinado():
    per = aplicar_pericias_origem_em_lista(
        [{"nome": "Luta", "treinado": False}],
        ["pericia:cura", "poder:medicina"],
        regra_versao="v13",
    )
    cura = next(p for p in per if p["nome"] == "Cura")
    assert cura["treinado"] is True
    assert next(p for p in per if p["nome"] == "Luta")["treinado"] is False


def test_sincronizar_pericias_origem_ficha_json():
    fj = sincronizar_pericias_origem_ficha_json(
        {
            "regra_versao": "v13",
            "origem_beneficios": ["pericia:religiao", "poder:medicina"],
            "pericias": [{"nome": "Fortitude", "treinado": True}],
        }
    )
    rel = next(p for p in fj["pericias"] if p["nome"] == "Religião")
    assert rel["treinado"] is True


def test_validar_pericias_com_extra_origem_acolito():
    """Barbaro 6 treinos + 1 perícia de origem entra no orçamento extra."""
    per = [
        {"nome": "Fortitude", "treinado": True},
        {"nome": "Luta", "treinado": True},
        {"nome": "Atletismo", "treinado": True},
        {"nome": "Cavalgar", "treinado": True},
        {"nome": "Iniciativa", "treinado": True},
        {"nome": "Intimidação", "treinado": True},
        {"nome": "Cura", "treinado": True},
    ]
    ok, _, res = validar_pericias_ficha(
        nivel=1,
        slug_classe="barbaro",
        int_valor=0,
        slug_raca=None,
        pericias=per,
        regra_versao="v13",
        origem_beneficios=["pericia:cura", "poder:medicina"],
    )
    assert ok is True
    assert res["pericias_treinadas_extra_origem"] == 1
    assert res["vagas_treinadas"] == 7


def test_validar_origem_v13_obrigatoria_na_criacao() -> None:
    import pytest

    from app.games.tormenta.services.personagem_service import TormentaPersonagemService
    from app.shared.exceptions.custom_exceptions import DadosInvalidos

    svc = TormentaPersonagemService(None)  # type: ignore[arg-type]
    with pytest.raises(DadosInvalidos, match="origem obrigatoria"):
        svc._validar_origem_v13(
            "jogador",
            {"regra_versao": "v13", "tormenta_classe_mb_slug": "guerreiro"},
            criacao=True,
        )


def test_validar_origem_v13_criacao_com_beneficios_ok() -> None:
    from app.games.tormenta.services.personagem_service import TormentaPersonagemService

    svc = TormentaPersonagemService(None)  # type: ignore[arg-type]
    svc._validar_origem_v13(
        "jogador",
        {
            "regra_versao": "v13",
            "origem_slug": "acolito",
            "origem_beneficios": ["pericia:cura", "poder:medicina"],
        },
        criacao=True,
    )


def test_validar_origem_v13_nao_exige_em_mb() -> None:
    from app.games.tormenta.services.personagem_service import TormentaPersonagemService

    svc = TormentaPersonagemService(None)  # type: ignore[arg-type]
    svc._validar_origem_v13("jogador", {"regra_versao": "mb"}, criacao=True)


def test_validar_origem_v13_update_sem_slug_nao_exige() -> None:
    from app.games.tormenta.services.personagem_service import TormentaPersonagemService

    svc = TormentaPersonagemService(None)  # type: ignore[arg-type]
    svc._validar_origem_v13(
        "jogador",
        {"regra_versao": "v13", "tormenta_classe_mb_slug": "guerreiro"},
        criacao=False,
    )
