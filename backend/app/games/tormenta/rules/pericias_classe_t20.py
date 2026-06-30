"""Perícias de classe Tormenta 20 v1.3 — fixas, grupos «ou» e lista de escolha."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from app.games.tormenta.rules.classes_t20 import classe_por_slug
from app.games.tormenta.rules.pericias_t20 import meta_pericia_por_nome
from app.games.tormenta.rules.regra_versao_t20 import (
    REGRA_VERSAO_V13,
    normalizar_regra_versao,
)

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_CONFIG_JSON = _DATA_DIR / "pericias_classe_config_v13.json"


@lru_cache(maxsize=1)
def _carregar_config_v13() -> Dict[str, Any]:
    if not _CONFIG_JSON.is_file():
        return {"classes": {}}
    return json.loads(_CONFIG_JSON.read_text(encoding="utf-8"))


def config_pericias_classe_v13(slug_classe: str) -> Optional[Dict[str, Any]]:
    s = str(slug_classe or "").strip().lower()
    if not s:
        return None
    classes = _carregar_config_v13().get("classes") or {}
    row = classes.get(s)
    if not isinstance(row, dict):
        return None
    fixas = [
        str(x).strip().lower()
        for x in (row.get("pericias_fixas") or [])
        if str(x).strip()
    ]
    ou_raw = row.get("pericias_escolha_um_de") or []
    ou: List[List[str]] = []
    if isinstance(ou_raw, list):
        for g in ou_raw:
            if isinstance(g, list):
                opts = [str(x).strip().lower() for x in g if str(x).strip()]
                if opts:
                    ou.append(opts)
    pool = [
        str(x).strip().lower()
        for x in (row.get("pericias_escolha_de") or [])
        if str(x).strip()
    ]
    try:
        qtd = int(row.get("pericias_escolha_qtd", 0) or 0)
    except (TypeError, ValueError):
        qtd = 0
    return {
        "pericias_fixas": fixas,
        "pericias_escolha_um_de": ou,
        "pericias_escolha_qtd": max(0, qtd),
        "pericias_escolha_de": pool,
    }


def _slug_de_linha_pericia(nome: str, regra_versao: Optional[str]) -> Optional[str]:
    meta = meta_pericia_por_nome(nome, regra_versao)
    if not meta:
        return None
    slug = str(meta.get("slug", "")).strip().lower()
    return slug or None


def slugs_pericias_treinadas(
    pericias: List[Dict[str, Any]], regra_versao: Optional[str] = None
) -> Set[str]:
    out: Set[str] = set()
    for p in pericias or []:
        if not isinstance(p, dict) or not p.get("treinado"):
            continue
        slug = p.get("slug")
        if slug:
            out.add(str(slug).strip().lower())
            continue
        nome = str(p.get("nome", "")).strip()
        s = _slug_de_linha_pericia(nome, regra_versao)
        if s:
            out.add(s)
    return out


def universo_pericias_classe(cfg: Dict[str, Any]) -> Set[str]:
    fixas = set(cfg.get("pericias_fixas") or [])
    pool = set(cfg.get("pericias_escolha_de") or [])
    for g in cfg.get("pericias_escolha_um_de") or []:
        pool.update(g)
    return fixas | pool


def vagas_classe_v13(slug_classe: str) -> Optional[int]:
    cfg = config_pericias_classe_v13(slug_classe)
    if not cfg:
        return None
    return (
        len(cfg["pericias_fixas"])
        + len(cfg["pericias_escolha_um_de"])
        + int(cfg["pericias_escolha_qtd"])
    )


def validar_pericias_classe_v13(
    *,
    slug_classe: str,
    pericias: List[Dict[str, Any]],
    int_valor: int,
    slug_raca: Optional[str],
    int_extra: int,
    racial_extra: int,
    origem_extra: int = 0,
) -> Tuple[bool, str, Dict[str, Any]]:
    """Valida fixas, grupos «ou», escolhas da lista e extras INT/racial."""
    cfg = config_pericias_classe_v13(slug_classe)
    if not cfg:
        return True, "", {"ignorado": True}

    rv = REGRA_VERSAO_V13
    treinados = slugs_pericias_treinadas(pericias, rv)
    fixas: List[str] = cfg["pericias_fixas"]
    ou: List[List[str]] = cfg["pericias_escolha_um_de"]
    qtd = int(cfg["pericias_escolha_qtd"])
    universo = universo_pericias_classe(cfg)

    resumo: Dict[str, Any] = {
        "pericias_fixas": fixas,
        "pericias_escolha_um_de": ou,
        "pericias_escolha_qtd": qtd,
        "pericias_escolha_de": cfg["pericias_escolha_de"],
        "vagas_classe": len(fixas) + len(ou) + qtd,
        "int_extra": int_extra,
        "racial_extra": racial_extra,
        "origem_extra": int(origem_extra),
    }

    for f in fixas:
        if f not in treinados:
            return (
                False,
                f"Perícia de classe obrigatória não treinada: {f.replace('_', ' ')}.",
                resumo,
            )

    ou_escolhas: List[str] = []
    for i, grupo in enumerate(ou):
        picks = [g for g in grupo if g in treinados]
        if not picks:
            opts = " ou ".join(g.replace("_", " ") for g in grupo)
            return (
                False,
                f"Escolha uma perícia de classe entre: {opts}.",
                resumo,
            )
        if len(picks) > 1:
            return (
                False,
                f"Grupo de perícias «ou» ({i + 1}): marque apenas uma entre "
                f"{', '.join(grupo)}.",
                resumo,
            )
        ou_escolhas.append(picks[0])

    resumo["pericias_ou_escolhidas"] = ou_escolhas

    min_lista = len(fixas) + len(ou) + qtd
    na_lista = treinados & universo
    if len(na_lista) < min_lista:
        return (
            False,
            f"Perícias da lista de classe: {len(na_lista)} treinadas, "
            f"mínimo {min_lista} (fixas + «ou» + {qtd} à escolha).",
            resumo,
        )

    fora = treinados - universo
    max_fora = max(0, int(int_extra) + int(racial_extra) + int(origem_extra))
    if len(fora) > max_fora:
        return (
            False,
            f"Perícias fora da lista de classe: {len(fora)} treinadas, "
            f"máximo {max_fora} (bônus INT + racial"
            + (" + origem" if origem_extra else "")
            + ").",
            resumo,
        )

    return True, "", resumo


def preview_pericias_classe_v13(slug_classe: str) -> Optional[Dict[str, Any]]:
    cfg = config_pericias_classe_v13(slug_classe)
    if not cfg:
        return None
    row = classe_por_slug(slug_classe, REGRA_VERSAO_V13)
    return {
        "classe_slug": str(slug_classe).strip().lower(),
        "classe_nome": str((row or {}).get("nome", "")),
        **cfg,
        "vagas_classe": vagas_classe_v13(slug_classe),
    }
