"""Poderes do suplemento Heróis de Arton v1.1 — catálogo e elegibilidade na ficha."""

from __future__ import annotations

import json
import re
import unicodedata
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.games.tormenta.rules.regra_versao_t20 import (
    SUPLEMENTO_HEROIS_ARTON,
    game_suplemento_de_ficha,
)

_DATA_JSON = (
    Path(__file__).resolve().parent.parent / "data" / "poderes_herois_arton.json"
)


def normalizar_slug_poder_ha(texto: str) -> str:
    s = unicodedata.normalize("NFKD", str(texto or ""))
    s = s.encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "_", s).strip("_")


@lru_cache(maxsize=1)
def _documento_poderes_ha() -> Dict[str, Any]:
    if not _DATA_JSON.is_file():
        return {"poderes": []}
    return json.loads(_DATA_JSON.read_text(encoding="utf-8"))


def lista_poderes_herois_arton() -> List[Dict[str, Any]]:
    """Todos os poderes do suplemento Heróis de Arton (estrutura do JSON)."""
    rows = _documento_poderes_ha().get("poderes") or []
    out: List[Dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        slug = normalizar_slug_poder_ha(str(row.get("slug") or ""))
        if not slug:
            continue
        nome = str(row.get("nome") or slug).strip()
        item: Dict[str, Any] = {
            "slug": slug,
            "nome": nome,
            "fonte_catalogo": str(row.get("fonte_catalogo") or SUPLEMENTO_HEROIS_ARTON),
            "categoria_v13": str(row.get("categoria_v13") or "geral").strip().lower(),
            "custo_pm": int(row.get("custo_pm") or 0),
        }
        for opt in (
            "classe_exigida",
            "raca_exigida",
            "descricao_resumo",
            "pagina_referencia",
            "prerequisitos",
        ):
            raw = row.get(opt)
            if raw is not None and str(raw).strip():
                item[opt] = str(raw).strip()
        if item.get("classe_exigida"):
            item["classe_exigida"] = normalizar_slug_poder_ha(item["classe_exigida"])
        if item.get("raca_exigida"):
            item["raca_exigida"] = normalizar_slug_poder_ha(item["raca_exigida"])
        out.append(item)
    return sorted(out, key=lambda x: x["nome"].lower())


def poder_por_slug(slug: str) -> Optional[Dict[str, Any]]:
    """Retorna metadados de um poder HA ou None."""
    s = normalizar_slug_poder_ha(slug)
    if not s:
        return None
    for row in lista_poderes_herois_arton():
        if row.get("slug") == s:
            return dict(row)
    return None


def _raca_slug_de_ficha(ficha_json: Optional[dict]) -> Optional[str]:
    fj = dict(ficha_json or {})
    raw = str(fj.get("raca_tormenta_slug") or fj.get("raca") or "").strip().lower()
    if not raw or raw == "__livre__":
        return None
    return normalizar_slug_poder_ha(raw)


def _classes_slugs_de_ficha(ficha_json: Optional[dict]) -> set[str]:
    fj = dict(ficha_json or {})
    slugs: set[str] = set()
    try:
        nv = int(fj.get("nivel") or fj.get("tormenta_nivel_mb") or 1)
    except (TypeError, ValueError):
        nv = 1
    from app.games.tormenta.rules.progressao_pv_t20 import (
        niveis_multiclasse_v13_de_ficha,
    )

    for row in niveis_multiclasse_v13_de_ficha(fj, nv):
        cs = str(row.get("slug") or "").strip()
        if cs:
            slugs.add(normalizar_slug_poder_ha(cs))
    arr = fj.get("tormenta_niveis_classe_mb")
    if isinstance(arr, list):
        for row in arr:
            if isinstance(row, dict):
                cs = normalizar_slug_poder_ha(
                    str(row.get("classe_slug") or row.get("slug") or "")
                )
                if cs:
                    slugs.add(cs)
    legacy = str(fj.get("tormenta_classe_mb_slug") or "").strip()
    if legacy:
        slugs.add(normalizar_slug_poder_ha(legacy))
    return slugs


def classe_atende_exigencia(classe_exigida: str, classes_ficha: set[str]) -> bool:
    """
    ``classe_exigida=treinador`` vale para slug ``treinador`` e prefixo ``treinador_*``
    (variantes futuras ou mesa).
    """
    req = normalizar_slug_poder_ha(classe_exigida)
    if not req:
        return True
    for cs in classes_ficha:
        c = normalizar_slug_poder_ha(cs)
        if not c:
            continue
        if c == req:
            return True
        if req == "treinador" and (c == "treinador" or c.startswith("treinador_")):
            return True
    return False


def _poder_elegivel_ficha(row: Dict[str, Any], ficha_json: Optional[dict]) -> bool:
    raca_req = str(row.get("raca_exigida") or "").strip()
    if raca_req:
        raca_ficha = _raca_slug_de_ficha(ficha_json)
        if not raca_ficha or raca_ficha != normalizar_slug_poder_ha(raca_req):
            return False
    classe_req = str(row.get("classe_exigida") or "").strip()
    if classe_req:
        classes = _classes_slugs_de_ficha(ficha_json)
        if not classe_atende_exigencia(classe_req, classes):
            return False
    return True


def poderes_disponiveis_ficha(ficha_json: Optional[dict]) -> List[Dict[str, Any]]:
    """
    Poderes HA elegíveis para a ficha (requer ``game_suplemento=herois_arton``).
    Filtra por ``raca_exigida`` e ``classe_exigida`` quando presentes.
    """
    if game_suplemento_de_ficha(ficha_json) != SUPLEMENTO_HEROIS_ARTON:
        return []
    return [
        dict(row)
        for row in lista_poderes_herois_arton()
        if _poder_elegivel_ficha(row, ficha_json)
    ]
