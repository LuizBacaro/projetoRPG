"""Perícias Tormenta 20 v1.3 — catálogo, fórmula e orçamento."""

from __future__ import annotations

from app.games.tormenta.rules.atributos_t20 import lista_pericias_com_atributo
from app.games.tormenta.rules.pericias_criacao_t20 import (
    preview_pericias_criacao,
    vagas_pericias_treinadas,
)
from app.games.tormenta.rules.pericias_t20 import (
    bonus_treinamento_por_nivel,
    calcular_bonus_pericia,
    pode_usar_pericia_treinada,
)


def test_lista_pericias_v13_vinte_nove() -> None:
    rows = lista_pericias_com_atributo("v13")
    assert len(rows) == 29
    nomes = {r["nome"] for r in rows}
    assert "Misticismo" in nomes
    assert "Ofício" in nomes
    assert "Atuação" in nomes
    assert all("—" not in n for n in nomes)


def test_atuacao_oficio_somente_treinado_v13() -> None:
    rows = {r["nome"]: r for r in lista_pericias_com_atributo("v13")}
    assert rows["Atuação"]["somente_treinado"] is True
    assert rows["Ofício"]["somente_treinado"] is True
    assert rows["Diplomacia"]["somente_treinado"] is False


def test_bonus_treinamento_patamar_v13() -> None:
    assert bonus_treinamento_por_nivel(3, "v13") == 2
    assert bonus_treinamento_por_nivel(7, "v13") == 4
    assert bonus_treinamento_por_nivel(15, "v13") == 6
    assert bonus_treinamento_por_nivel(7, "mb") == 2


def test_calcular_bonus_acrobacia_nivel_7_v13() -> None:
    """Nível 7, DES 3, treinado → 3 + 3 + 4 = +10."""
    b = calcular_bonus_pericia(
        nivel=7,
        mod_atributo=3,
        treinado=True,
        regra_versao="v13",
    )
    assert b == 10


def test_calcular_bonus_exemplo_livro_nivel_3() -> None:
    """3º nível, FOR 4, treinado Luta → 1 + 4 + 2 = +7."""
    b = calcular_bonus_pericia(
        nivel=3,
        mod_atributo=4,
        treinado=True,
        regra_versao="v13",
    )
    assert b == 7


def test_pode_usar_conhecimento_sem_treino() -> None:
    ok, msg = pode_usar_pericia_treinada("Conhecimento", False, "v13")
    assert ok is False
    assert "treinada" in msg.lower()


def test_vagas_ladino_humano_v13() -> None:
    """Ladino 10 (2 fixas + 8 escolha) + INT 2 + humano 2 = 14."""
    assert vagas_pericias_treinadas("ladino", 2, "humano", "v13") == 14


def test_validar_v13_sem_graduacao() -> None:
    """v1.3 ignora pontos de graduação MB; campo graduacao na ficha não invalida."""
    prev = preview_pericias_criacao(
        nivel=1,
        slug_classe="arcanista",
        int_valor=0,
        slug_raca=None,
        pericias=[
            {"nome": "Misticismo", "treinado": True, "graduacao": 5},
            {"nome": "Vontade", "treinado": True},
            {"nome": "Conhecimento", "treinado": True},
            {"nome": "Investigação", "treinado": True},
        ],
        regra_versao="v13",
    )
    assert prev["valido"] is True
    assert prev["pontos_grad_treinadas"] == 0
