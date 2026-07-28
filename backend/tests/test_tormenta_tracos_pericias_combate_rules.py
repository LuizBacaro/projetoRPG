"""Testes — traços raciais, perícias, combate e grimório MB (regras puras)."""

from __future__ import annotations

from app.games.tormenta.rules.combate_t20 import (
    modificadores_de_condicoes_mb,
    rolar_ataque,
    rolar_iniciativa,
)
from app.games.tormenta.rules.grimorio_conjuracao_t20 import (
    modo_conjuracao_classe_mb,
    validar_papel_magia_para_classe,
)
from app.games.tormenta.rules.pericias_criacao_t20 import (
    preview_pericias_criacao_mb,
    vagas_pericias_treinadas_mb,
)
from app.games.tormenta.rules.pericias_t20 import (
    calcular_bonus_pericia,
    percepcao_passiva_t20,
    rolar_teste_pericia,
)
from app.games.tormenta.rules.progressao_pv_t20 import preview_pv_mb, pv_maximos_mb
from app.games.tormenta.rules.tracos_raciais_t20 import preview_tracos_raciais


def test_preview_tracos_anao():
    p = preview_tracos_raciais("anao")
    assert p["encontrado"] is True
    assert p["fortitude_bonus"] == 4
    assert p["deslocamento_m"] == 6


def test_preview_tracos_goblin_pequeno():
    p = preview_tracos_raciais("goblin")
    assert p["ca_bonus"] == 1
    assert p["furtividade_bonus"] == 4


def test_calcular_bonus_pericia_treinado():
    b = calcular_bonus_pericia(
        nivel=5,
        mod_atributo=3,
        treinado=True,
        graduacao=2,
        outros=0,
    )
    assert b == 3 + 2 + 2 + 2  # mod + meio nv + grad + treinado


def test_calcular_bonus_pericia_bonus_uso_separado_de_outros():
    base = calcular_bonus_pericia(
        nivel=7,
        mod_atributo=3,
        treinado=True,
        outros=1,
        regra_versao="v13",
    )
    com_uso = calcular_bonus_pericia(
        nivel=7,
        mod_atributo=3,
        treinado=True,
        outros=1,
        bonus_uso=2,
        regra_versao="v13",
    )
    assert base == 3 + 3 + 4 + 1  # atr + ½nv + treino + outros
    assert com_uso == base + 2


def test_percepcao_passiva():
    assert percepcao_passiva_t20(7) == 17


def test_rolar_teste_pericia_seed():
    r = rolar_teste_pericia(5, 15, seed=42)
    assert r["d20"] >= 1
    assert r["total"] == r["d20"] + 5


def test_modificadores_condicoes_v13() -> None:
    m = modificadores_de_condicoes_mb(["Desprevenido"])
    assert m["ataque"] == 0
    assert m["ca"] == -5


def test_rolar_iniciativa_seed():
    r = rolar_iniciativa(2, seed=1)
    assert r["total"] == r["d20"] + 2


def test_rolar_ataque_acerto():
    r = rolar_ataque(3, 2, ca_alvo=5, seed=10)
    assert "acertou" in r


def test_modo_conjuracao_feiticeiro_espontaneo():
    assert modo_conjuracao_classe_mb("feiticeiro") == "espontaneo"
    ok, _ = validar_papel_magia_para_classe("feiticeiro", "conhecida")
    assert ok is True
    ok2, msg = validar_papel_magia_para_classe("feiticeiro", "grimorio")
    assert ok2 is False
    assert "grimório" in msg.lower() or "grimorio" in msg.lower()


def test_modo_conjuracao_mago_preparar():
    assert modo_conjuracao_classe_mb("mago") == "preparar"
    ok, msg = validar_papel_magia_para_classe("mago", "conhecida")
    assert ok is False


def test_pv_maximos_barbaro_nivel_5():
    assert pv_maximos_mb("barbaro", 5, 14) == 24 + 4 * 6 + 5 * 2
    p = preview_pv_mb("barbaro", 1, 10)
    assert p["encontrado"] is True
    assert p["pv_max"] == 24


def test_vagas_pericias_humano_ladino():
    assert vagas_pericias_treinadas_mb("ladino", 14, "humano") == 8 + 2 + 2


def test_validar_pericias_excede_treinadas():
    prev = preview_pericias_criacao_mb(
        nivel=1,
        slug_classe="mago",
        int_valor=10,
        pericias=[
            {"nome": "A", "treinado": True, "graduacao": 0},
            {"nome": "B", "treinado": True, "graduacao": 0},
            {"nome": "C", "treinado": True, "graduacao": 0},
        ],
    )
    assert prev["valido"] is False
    assert "treinadas" in prev["motivo"].lower()
