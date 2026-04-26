"""
Teste do enriquecimento de habilidades especiais do combatente.

Cobre:
- Formato JSON agrupado por nível → retorno enriquecido com descrição do catálogo.
- Formato legado `a | b` → retorno agrupado em único nível com fallback.
- Tokens não reconhecidos pelo catálogo → slug/descricao vazios, raw preservado.
"""
from __future__ import annotations

import json
from unittest.mock import Mock

from app.games.dnd35.services.combatente_service import CombatenteService
from app.games.dnd35.models.combatente import Combatente


def _service_com_mocks() -> CombatenteService:
    return CombatenteService(repository=Mock(), file_service=Mock())


def test_enriquecer_habilidades_com_json_agrupado_resolve_descricao():
    svc = _service_com_mocks()
    c = Combatente(
        id=1,
        nome="Ragar",
        tipo="jogador",
        classe="Bárbaro",
        nivel=3,
        hp_maximo=30,
        hp_atual=30,
        iniciativa=2,
    )
    c.habilidades_especiais = json.dumps(
        [{"nivel": 1, "habilidades": ["Fúria (1/dia)"]}]
    )

    svc._enriquecer_habilidades_especiais_em_memoria([c])

    detalhadas = getattr(c, "habilidades_especiais_detalhadas", [])
    assert len(detalhadas) == 1
    grupo = detalhadas[0]
    assert grupo["nivel"] == 1
    assert len(grupo["habilidades"]) == 1
    habilidade = grupo["habilidades"][0]
    assert habilidade["raw"] == "Fúria (1/dia)"
    assert habilidade["slug"] == "furia"
    assert "Fúria" in habilidade["titulo"] or "Furia" in habilidade["titulo"]
    assert habilidade["descricao"]  # veio do catálogo canônico


def test_enriquecer_habilidades_legado_separado_por_pipe():
    svc = _service_com_mocks()
    c = Combatente(
        id=2,
        nome="Kira",
        tipo="jogador",
        classe="Ladino",
        nivel=4,
        hp_maximo=24,
        hp_atual=24,
        iniciativa=4,
    )
    c.habilidades_especiais = "Esquiva sobrenatural | Sentir armadilhas"

    svc._enriquecer_habilidades_especiais_em_memoria([c])

    detalhadas = getattr(c, "habilidades_especiais_detalhadas", [])
    assert len(detalhadas) == 1
    assert detalhadas[0]["nivel"] == 4  # vem do atributo `nivel`
    raws = [h["raw"] for h in detalhadas[0]["habilidades"]]
    assert raws == ["Esquiva sobrenatural", "Sentir armadilhas"]
    slugs = [h["slug"] for h in detalhadas[0]["habilidades"]]
    # Pelo menos a primeira deve ser resolvida no catálogo canônico.
    assert "esquiva-sobrenatural" in slugs


def test_enriquecer_mantem_raw_quando_nao_resolve():
    svc = _service_com_mocks()
    c = Combatente(
        id=3,
        nome="Test",
        tipo="jogador",
        classe="Guerreiro",
        nivel=1,
        hp_maximo=10,
        hp_atual=10,
        iniciativa=0,
    )
    c.habilidades_especiais = json.dumps(
        [{"nivel": 1, "habilidades": ["Habilidade inédita só pra teste"]}]
    )

    svc._enriquecer_habilidades_especiais_em_memoria([c])

    detalhadas = getattr(c, "habilidades_especiais_detalhadas", [])
    item = detalhadas[0]["habilidades"][0]
    assert item["raw"] == "Habilidade inédita só pra teste"
    assert item["slug"] == ""
    assert item["descricao"] == ""


def test_enriquecer_sem_habilidades_define_lista_vazia():
    svc = _service_com_mocks()
    c = Combatente(
        id=4,
        nome="Vazio",
        tipo="jogador",
        classe="Comum",
        nivel=1,
        hp_maximo=5,
        hp_atual=5,
        iniciativa=0,
    )
    c.habilidades_especiais = ""

    svc._enriquecer_habilidades_especiais_em_memoria([c])
    assert getattr(c, "habilidades_especiais_detalhadas", None) == []
