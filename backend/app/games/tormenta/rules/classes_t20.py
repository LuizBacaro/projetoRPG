"""Classes Tormenta 20 (MB) — benefícios por nível, BBA por tipo de classe."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_BEN_JSON = _DATA_DIR / "beneficios_nivel_mb.json"
_CLASS_JSON = _DATA_DIR / "classes_mb.json"


@lru_cache(maxsize=1)
def _carregar_beneficios() -> List[Dict[str, Any]]:
    raw = _BEN_JSON.read_text(encoding="utf-8")
    data = json.loads(raw)
    rows = data.get("niveis") or []
    return rows if isinstance(rows, list) else []


@lru_cache(maxsize=1)
def _carregar_classes_raw() -> Dict[str, Any]:
    raw = _CLASS_JSON.read_text(encoding="utf-8")
    return json.loads(raw)


def lista_beneficios_por_nivel_mb() -> List[Dict[str, Any]]:
    """20 linhas da tabela «Benefícios por Nível de Personagem» (MB)."""
    out: List[Dict[str, Any]] = []
    for row in _carregar_beneficios():
        if not isinstance(row, dict):
            continue
        try:
            n = int(row.get("nivel", 0))
        except (TypeError, ValueError):
            continue
        if n < 1 or n > 40:
            continue
        out.append(
            {
                "nivel": n,
                "xp_total": int(row.get("xp_total", 0) or 0),
                "graduacao_pericias": str(row.get("graduacao_pericias", "") or "").strip(),
                "talentos_totais": int(row.get("talentos_totais", 0) or 0),
                "pontos_habilidade_acumulados": int(row.get("pontos_habilidade_acumulados", 0) or 0),
                "bonus_meio_nivel": int(row.get("bonus_meio_nivel", 0) or 0),
            }
        )
    return sorted(out, key=lambda x: x["nivel"])


def lista_classes_mb() -> List[Dict[str, Any]]:
    """Classes do MB com PV, perícias e mapa opcional habilidades por nível."""
    data = _carregar_classes_raw()
    rows = data.get("classes") or []
    out: List[Dict[str, Any]] = []
    if not isinstance(rows, list):
        return out
    for row in rows:
        if not isinstance(row, dict):
            continue
        slug = str(row.get("slug", "")).strip()
        nome = str(row.get("nome", "")).strip()
        if not slug or not nome:
            continue
        bba_tipo = str(row.get("bba_tipo", "plein")).strip()
        if bba_tipo not in ("plein", "tres_quartos", "meio"):
            bba_tipo = "plein"
        hab = row.get("habilidades_por_nivel") or {}
        hab_limpo: Dict[str, str] = {}
        if isinstance(hab, dict):
            for k, v in hab.items():
                kk = str(k).strip()
                if kk.isdigit() and 1 <= int(kk) <= 40:
                    hab_limpo[kk] = str(v or "").strip()
        out.append(
            {
                "slug": slug,
                "nome": nome,
                "abreviatura": str(row.get("abreviatura", "") or "").strip(),
                "bba_tipo": bba_tipo,
                "pv_inicial": int(row.get("pv_inicial", 8) or 8),
                "pv_por_nivel": int(row.get("pv_por_nivel", 2) or 0),
                "pericias_treinadas": str(row.get("pericias_treinadas", "") or "").strip(),
                "pericias_classe": str(row.get("pericias_classe", "") or "").strip(),
                "talentos_adicionais": str(row.get("talentos_adicionais", "") or "").strip(),
                "habilidades_por_nivel": hab_limpo,
            }
        )
    return out


def bba_por_nivel_classe(nivel_classe: int, bba_tipo: str) -> int:
    """Bônus base de ataque para um único nível na classe (1..20)."""
    n = max(0, min(20, int(nivel_classe)))
    if n <= 0:
        return 0
    t = (bba_tipo or "plein").strip()
    if t == "meio":
        return n // 2
    if t == "tres_quartos":
        return (n * 3) // 4
    return n
