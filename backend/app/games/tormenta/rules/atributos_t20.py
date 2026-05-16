"""Regras de atributos Tormenta 20 — modificadores por faixa e custo em compra por pontos."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_COMPRA_JSON = _DATA_DIR / "atributos_compra_pontos.json"
_PERICIAS_JSON = _DATA_DIR / "pericias_atributo_chave.json"

_ATTR_VALIDOS = frozenset({"for", "des", "con", "int", "sab", "car"})


def modificador_atributo_t20(valor: int) -> int:
    """Modificador de habilidade T20 (tabela por faixas, não fórmula d20).

    Faixas 1–25 conforme regra base; acima de 25 aplica-se +1 no modificador a cada +2 no valor.
    """
    v = int(valor)
    if v < 1:
        v = 1

    if v <= 1:
        return -5
    if v <= 3:
        return -4
    if v <= 5:
        return -3
    if v <= 7:
        return -2
    if v <= 9:
        return -1
    if v <= 11:
        return 0
    if v <= 13:
        return 1
    if v <= 15:
        return 2
    if v <= 17:
        return 3
    if v <= 19:
        return 4
    if v <= 21:
        return 5
    if v <= 23:
        return 6
    if v <= 25:
        return 7
    # A cada +2 no valor, +1 no modificador acima da faixa 24–25.
    return 7 + (v - 25 + 1) // 2


@lru_cache(maxsize=1)
def _carregar_compra_pontos() -> Dict[str, Any]:
    raw = _COMPRA_JSON.read_text(encoding="utf-8")
    return json.loads(raw)


def custo_valor_atributo_compra(valor: int) -> Optional[int]:
    """Custo em pontos para um valor na compra por pontos (típico 8–18). None se fora da tabela."""
    data = _carregar_compra_pontos()
    for row in data.get("custos", []):
        if int(row["valor"]) == int(valor):
            return int(row["custo"])
    return None


def pontos_iniciais_compra() -> int:
    data = _carregar_compra_pontos()
    return int(data.get("_meta", {}).get("pontos_iniciais", 20))


def custo_total_compra_seis_atributos(
    forca: int,
    destreza: int,
    constituicao: int,
    inteligencia: int,
    sabedoria: int,
    carisma: int,
) -> Optional[int]:
    """Soma dos custos se todos os seis valores estiverem na tabela; senão None."""
    vals = (forca, destreza, constituicao, inteligencia, sabedoria, carisma)
    total = 0
    for v in vals:
        c = custo_valor_atributo_compra(v)
        if c is None:
            return None
        total += c
    return total


def lista_custos_compra() -> List[Dict[str, int]]:
    """Cópia somente leitura das linhas {valor, custo} para API futura."""
    data = _carregar_compra_pontos()
    return [dict(x) for x in data.get("custos", [])]


@lru_cache(maxsize=1)
def _carregar_pericias_atributo() -> Dict[str, Any]:
    raw = _PERICIAS_JSON.read_text(encoding="utf-8")
    return json.loads(raw)


def lista_pericias_com_atributo() -> List[Dict[str, Any]]:
    """Lista ordenada para a ficha: nome, atributo, somente_treinado, penalidade_armadura."""
    data = _carregar_pericias_atributo()
    out: List[Dict[str, Any]] = []
    for row in data.get("pericias", []):
        nome = str(row.get("nome", ""))
        attr = row.get("atributo")
        if attr is not None:
            attr = str(attr).lower().strip()
            if attr not in _ATTR_VALIDOS:
                raise ValueError(f"atributo invalido em pericia '{nome}': {attr!r}")
        st_raw = row.get("somente_treinado", False)
        somente_treinado = bool(st_raw) if isinstance(st_raw, bool) else False
        pen_raw = row.get("penalidade_armadura", False)
        penalidade_armadura = bool(pen_raw) if isinstance(pen_raw, bool) else False
        out.append(
            {
                "nome": nome,
                "atributo": attr,
                "somente_treinado": somente_treinado,
                "penalidade_armadura": penalidade_armadura,
            }
        )
    return out
