"""Versão das regras Tormenta 20 expostas ao motor (MB legado vs Edição Jogo do Ano v1.3)."""

from __future__ import annotations

from typing import Any, Mapping, Optional

REGRA_VERSAO_MB = "mb"
REGRA_VERSAO_V13 = "v13"
REGRA_VERSOES_VALIDAS = frozenset({REGRA_VERSAO_MB, REGRA_VERSAO_V13})
REGRA_VERSAO_PADRAO = REGRA_VERSAO_MB

# Suplemento: Heróis de Arton v1.1
SUPLEMENTO_HEROIS_ARTON = "herois_arton"
SUPLEMENTOS_VALIDOS = frozenset({SUPLEMENTO_HEROIS_ARTON})


def normalizar_regra_versao(valor: Optional[str]) -> str:
    """Normaliza alias de versão; padrão MB para compatibilidade com fichas existentes."""
    if valor is None:
        return REGRA_VERSAO_PADRAO
    v = str(valor).strip().lower()
    if v in ("v13", "ve", "jogo_do_ano", "jda"):
        return REGRA_VERSAO_V13
    if v == REGRA_VERSAO_MB:
        return REGRA_VERSAO_MB
    return REGRA_VERSAO_PADRAO


def regra_versao_de_ficha(ficha_json: Optional[Mapping[str, Any]]) -> str:
    if not ficha_json:
        return REGRA_VERSAO_PADRAO
    return normalizar_regra_versao(ficha_json.get("regra_versao"))


def game_suplemento_de_ficha(ficha_json: Optional[Mapping[str, Any]]) -> Optional[str]:
    if not ficha_json:
        return None
    raw = ficha_json.get("game_suplemento")
    if raw is None or str(raw).strip() == "":
        return None
    s = str(raw).strip().lower()
    return s if s in SUPLEMENTOS_VALIDOS else None
