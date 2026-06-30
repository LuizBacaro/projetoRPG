"""Overlay v1.3 de stats de armas (Tabela 3-3 parcial — kit e origens)."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_ARMAS_JSON = _DATA_DIR / "armas_v13_overlay.json"

_ARMA_FIELDS = (
    "secao",
    "custo",
    "dano_p",
    "dano_m",
    "tipo_dano",
    "critico",
    "alcance",
    "peso",
    "proficiencia",
    "empunhadura",
)


def _norm_nome(texto: str) -> str:
    import unicodedata

    s = unicodedata.normalize("NFKD", str(texto or "").strip().lower())
    return "".join(c for c in s if not unicodedata.combining(c))


@lru_cache(maxsize=1)
def _carregar_armas_overlay() -> List[Dict[str, Any]]:
    if not _ARMAS_JSON.is_file():
        return []
    raw = _ARMAS_JSON.read_text(encoding="utf-8")
    data = json.loads(raw)
    rows = data.get("itens") or data.get("items") or []
    out: List[Dict[str, Any]] = []
    if not isinstance(rows, list):
        return out
    for row in rows:
        if not isinstance(row, dict):
            continue
        nome = str(row.get("nome", "")).strip()
        if not nome:
            continue
        item: Dict[str, Any] = {"nome": nome}
        for key in _ARMA_FIELDS:
            val = row.get(key)
            if val is not None and str(val).strip():
                item[key] = (
                    str(val).strip() if key != "dano_p" and key != "dano_m" else val
                )
        out.append(item)
    return out


# Nomes legacy MB → nome canônico no overlay (stats v1.3)
_ALIASES_ARMA_V13: Dict[str, str] = {
    "mangual pesado": "mangual",
    "katana": "espada samurai (katana)",
}


@lru_cache(maxsize=1)
def mapa_armas_v13_por_nome() -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    for row in _carregar_armas_overlay():
        chave = _norm_nome(str(row.get("nome", "")))
        if chave:
            out[chave] = dict(row)
    for alias_raw, canon_raw in _ALIASES_ARMA_V13.items():
        ak = _norm_nome(alias_raw)
        ck = _norm_nome(canon_raw)
        if ck in out and ak not in out:
            out[ak] = dict(out[ck])
    return out


def lista_armas_v13_overlay() -> List[Dict[str, Any]]:
    return list(_carregar_armas_overlay())
