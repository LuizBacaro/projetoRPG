"""
Testes do pipeline de catálogo de raças.

Executa a leitura real das planilhas `Características especiais.xlsx` e
`Características especiais_v2.xlsx` quando disponíveis, valida o contrato
canônico e confere que o normalizador é tolerante a variações de delimitação
(`;`, `,`, quebras de linha) sem perder modificadores silenciosamente.

Notas de import:
- O pytest deste projeto adiciona `backend/` ao `sys.path` (ver `pytest.ini`).
- Como existe `backend/scripts/` como package regular, `import scripts.*` seria
  resolvido para esse pacote e não para o da raiz do repositório.
- Por isso carregamos os módulos diretamente pelo caminho de arquivo com
  `importlib`, sob nomes privados, sem alterar configuração global do projeto.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
PLANILHA_V1 = _REPO_ROOT / "Características especiais.xlsx"
PLANILHA_V2 = _REPO_ROOT / "Características especiais_v2.xlsx"


def _load_from_path(alias: str, relative_path: str) -> ModuleType:
    abs_path = _REPO_ROOT / relative_path
    spec = importlib.util.spec_from_file_location(alias, abs_path)
    assert spec and spec.loader, f"Não foi possível criar spec para {abs_path}"
    module = importlib.util.module_from_spec(spec)
    sys.modules[alias] = module
    spec.loader.exec_module(module)
    return module


_pipeline_mod = _load_from_path(
    "_racas_catalog_pipeline", "scripts/racas_catalog_pipeline.py"
)
_validator_mod = _load_from_path(
    "_racas_catalog_validator", "scripts/racas_catalog_validator.py"
)

ParseWarning = _pipeline_mod.ParseWarning
RacasCatalogPipeline = _pipeline_mod.RacasCatalogPipeline
RacasNormalizer = _pipeline_mod.RacasNormalizer
RacasWorkbookReader = _pipeline_mod.RacasWorkbookReader
_parse_modificadores_habilidade = _pipeline_mod._parse_modificadores_habilidade

validate_records = _validator_mod.validate_records


# ─── Parsing de modificadores ────────────────────────────────────────────


def test_parse_modificadores_aceita_ponto_e_virgula():
    mods, warnings = _parse_modificadores_habilidade(
        "+2 CONSTITUIÇÃO; -2 CARISMA", "Anões"
    )
    assert warnings == []
    assert mods == [
        {"atributo": "constituicao", "valor": 2},
        {"atributo": "carisma", "valor": -2},
    ]


def test_parse_modificadores_aceita_quebra_de_linha():
    mods, warnings = _parse_modificadores_habilidade(
        "+2 CONSTITUIÇÃO\n-2 CARISMA", "Anões"
    )
    assert warnings == []
    assert mods == [
        {"atributo": "constituicao", "valor": 2},
        {"atributo": "carisma", "valor": -2},
    ]


def test_parse_modificadores_aceita_mistura_de_delimitadores():
    mods, _ = _parse_modificadores_habilidade(
        "+2 FORÇA, -2 INTELIGÊNCIA; -2 CARISMA", "Meio-orcs"
    )
    assert mods == [
        {"atributo": "forca", "valor": 2},
        {"atributo": "inteligencia", "valor": -2},
        {"atributo": "carisma", "valor": -2},
    ]


def test_parse_modificadores_emite_warning_para_token_invalido():
    mods, warnings = _parse_modificadores_habilidade("+2 FOO, +2 FORÇA", "Teste")
    assert mods == [{"atributo": "forca", "valor": 2}]
    assert len(warnings) == 1
    assert warnings[0].campo == "modificadores_habilidade"
    assert warnings[0].token == "+2 FOO"


def test_parse_modificadores_ignora_traço():
    mods, warnings = _parse_modificadores_habilidade("-", "Humanos")
    assert mods == []
    assert warnings == []


# ─── Workbooks reais ─────────────────────────────────────────────────────


@pytest.mark.skipif(not PLANILHA_V1.exists(), reason="planilha v1 ausente")
def test_pipeline_le_planilha_v1_sem_warnings_de_parser():
    pipeline = RacasCatalogPipeline(
        reader=RacasWorkbookReader(PLANILHA_V1),
        normalizer=RacasNormalizer(),
    )
    resultado = pipeline.run()

    slugs = {r["slug"] for r in resultado.racas}
    assert {
        "humanos",
        "anoes",
        "elfos",
        "gnomos",
        "meio-elfos",
        "meio-orcs",
        "halfling",
    } <= slugs

    warnings_mods = [
        w for w in resultado.warnings if w.campo == "modificadores_habilidade"
    ]
    assert warnings_mods == [], (
        "Parser não deveria perder modificadores na planilha v1: " f"{warnings_mods}"
    )


@pytest.mark.skipif(not PLANILHA_V2.exists(), reason="planilha v2 ausente")
def test_pipeline_le_planilha_v2_sem_perder_modificadores():
    pipeline = RacasCatalogPipeline(
        reader=RacasWorkbookReader(PLANILHA_V2),
        normalizer=RacasNormalizer(),
    )
    resultado = pipeline.run()

    racas_por_slug = {r["slug"]: r for r in resultado.racas}

    anoes = racas_por_slug["anoes"]
    assert {"atributo": "constituicao", "valor": 2} in anoes["modificadores_habilidade"]
    assert {"atributo": "carisma", "valor": -2} in anoes["modificadores_habilidade"]

    meio_orcs = racas_por_slug["meio-orcs"]
    atributos = {m["atributo"] for m in meio_orcs["modificadores_habilidade"]}
    assert {"forca", "inteligencia", "carisma"} <= atributos

    warnings_mods = [
        w for w in resultado.warnings if w.campo == "modificadores_habilidade"
    ]
    assert warnings_mods == [], (
        "Parser v2 não deveria perder modificadores: " f"{warnings_mods}"
    )


@pytest.mark.skipif(not PLANILHA_V1.exists(), reason="planilha v1 ausente")
def test_validacao_catalogo_gerado_nao_tem_erros():
    pipeline = RacasCatalogPipeline(
        reader=RacasWorkbookReader(PLANILHA_V1),
        normalizer=RacasNormalizer(),
    )
    resultado = pipeline.run()
    issues = validate_records(resultado.racas)
    erros = [i for i in issues if i.level == "error"]
    assert erros == [], f"Validação retornou erros: {erros}"


# ─── Erros de input ───────────────────────────────────────────────────────


def test_reader_falha_para_arquivo_inexistente(tmp_path: Path):
    reader = RacasWorkbookReader(tmp_path / "inexistente.xlsx")
    with pytest.raises(FileNotFoundError):
        reader.read()


def test_parse_warning_to_dict_serializavel():
    w = ParseWarning(raca="X", campo="c", mensagem="m", token="t")
    assert w.to_dict() == {"raca": "X", "campo": "c", "mensagem": "m", "token": "t"}
