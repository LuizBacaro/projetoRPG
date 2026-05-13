"""Raças Tormenta 20 (Módulo Básico) — lista e ajustes de habilidades para a ficha."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Tuple

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_RACAS_JSON = _DATA_DIR / "racas_mb.json"


@lru_cache(maxsize=1)
def _carregar_racas() -> Dict[str, Any]:
    raw = _RACAS_JSON.read_text(encoding="utf-8")
    return json.loads(raw)


def idiomas_mb_extras() -> Tuple[str, List[Dict[str, str]]]:
    """Texto geral de idiomas (MB) + tabela Idioma / quem costuma falar."""
    data = _carregar_racas()
    geral = str(data.get("idiomas_geral_mb", "") or "").strip()
    raw_tab = data.get("idiomas_tabela_mb") or []
    tabela: List[Dict[str, str]] = []
    if isinstance(raw_tab, list):
        for it in raw_tab:
            if not isinstance(it, dict):
                continue
            idioma = str(it.get("idioma", "")).strip()
            if not idioma:
                continue
            tabela.append(
                {
                    "idioma": idioma,
                    "falantes": str(it.get("falantes", "") or "").strip(),
                }
            )
    return geral, tabela


def lista_racas_mb() -> List[Dict[str, Any]]:
    """Lista ordenada de raças MB para API/ficha (slug, nome, ajustes, flags, tracos_resumo, idioma_racial_mb)."""
    data = _carregar_racas()
    out: List[Dict[str, Any]] = []
    for row in data.get("racas", []):
        slug = str(row.get("slug", "")).strip()
        nome = str(row.get("nome", "")).strip()
        if not slug or not nome:
            continue
        ajustes = row.get("ajustes") or {}
        if not isinstance(ajustes, dict):
            ajustes = {}
        ajustes_limpo: Dict[str, int] = {}
        for k, v in ajustes.items():
            kk = str(k).lower().strip()
            if kk in ("for", "des", "con", "int", "sab", "car"):
                ajustes_limpo[kk] = int(v)
        ir = row.get("idioma_racial_mb", None)
        idioma_racial: str | None
        if ir is None:
            idioma_racial = None
        else:
            s = str(ir).strip()
            idioma_racial = s if s else None
        excl_raw = row.get("excluir_atributos_mais2") or []
        excluir: List[str] = []
        if isinstance(excl_raw, list):
            for x in excl_raw:
                xx = str(x).lower().strip()
                if xx in ("for", "des", "con", "int", "sab", "car"):
                    excluir.append(xx)
        out.append(
            {
                "slug": slug,
                "nome": nome,
                "ajustes": ajustes_limpo,
                "escolhe_duas_mais2": bool(row.get("escolhe_duas_mais2")),
                "escolhe_um_mais2": bool(row.get("escolhe_um_mais2")),
                "excluir_atributos_mais2": excluir,
                "mod_car_fixo": int(row.get("mod_car_fixo", 0) or 0),
                "tracos_resumo": str(row.get("tracos_resumo", "")).strip(),
                "idioma_racial_mb": idioma_racial,
            }
        )
    return out
