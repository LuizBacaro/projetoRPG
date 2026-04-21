"""Testes para utilidades compartilhadas entre os pipelines de catálogo."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest


_REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_from_path(alias: str, relative_path: str) -> ModuleType:
    """Carrega módulo por caminho, registrando-o em sys.modules.

    Usamos esse utilitário porque `backend/scripts/` mascara o pacote
    top-level `scripts/` do repositório durante a execução dos testes.
    """
    abs_path = _REPO_ROOT / relative_path
    spec = importlib.util.spec_from_file_location(alias, abs_path)
    assert spec and spec.loader, f"Não foi possível criar spec para {abs_path}"
    module = importlib.util.module_from_spec(spec)
    sys.modules[alias] = module
    spec.loader.exec_module(module)
    return module


_common = _load_from_path("_catalog_common", "scripts/catalog_common.py")

sem_acentos = _common.sem_acentos
slug = _common.slug
texto_limpo = _common.texto_limpo
split_tokens = _common.split_tokens
build_envelope = _common.build_envelope


class TestNormalizacaoTextual:
    def test_sem_acentos_preserva_letras_base(self) -> None:
        assert sem_acentos("Ação") == "Acao"
        assert sem_acentos("Élfico") == "Elfico"

    def test_slug_usa_hifen_e_minusculas(self) -> None:
        assert slug("Meio-Elfo") == "meio-elfo"
        assert slug("Fúria Total!") == "furia-total"
        assert slug("   ") == ""

    def test_texto_limpo_remove_placeholders(self) -> None:
        assert texto_limpo(" nan ") == ""
        assert texto_limpo(None) == ""
        assert texto_limpo("  Anão  ") == "Anão"


class TestSplitTokens:
    @pytest.mark.parametrize(
        "entrada,esperado",
        [
            ("+2 FOR; -2 CAR", ["+2 FOR", "-2 CAR"]),
            ("+2 FOR, -2 CAR", ["+2 FOR", "-2 CAR"]),
            ("+2 FOR\n-2 CAR", ["+2 FOR", "-2 CAR"]),
            ("", []),
            (None, []),
        ],
    )
    def test_delimitadores_default(
        self, entrada: object, esperado: list[str]
    ) -> None:
        assert split_tokens(entrada) == esperado

    def test_delimitador_customizado(self) -> None:
        assert split_tokens("a|b|c", delimitadores="|") == ["a", "b", "c"]


class TestBuildEnvelope:
    def test_estrutura_canonica(self) -> None:
        envelope = build_envelope(
            source_path="arquivo.xlsx",
            items_key="racas",
            items=[{"slug": "humano"}],
        )
        assert envelope["source"] == "arquivo.xlsx"
        assert envelope["total_racas"] == 1
        assert envelope["racas"] == [{"slug": "humano"}]
        assert "generated_at" in envelope

    def test_nao_permite_sobrescrever_chaves_reservadas(self) -> None:
        envelope = build_envelope(
            source_path="x.xlsx",
            items_key="itens",
            items=[],
            extras={"total_itens": 999, "extra_meta": "ok"},
        )
        assert envelope["total_itens"] == 0
        assert envelope["extra_meta"] == "ok"
