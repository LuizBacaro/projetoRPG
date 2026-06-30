"""Origens Tormenta 20 v1.3 — Tabela 1-19."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.games.tormenta.rules.atributos_t20 import lista_pericias_com_atributo
from app.games.tormenta.rules.pericias_t20 import (
    _normalizar_nome_pericia,
    meta_pericia_por_nome,
)
from app.games.tormenta.rules.regra_versao_t20 import (
    REGRA_VERSAO_V13,
    regra_versao_de_ficha,
)

_DATA = Path(__file__).resolve().parent.parent / "data" / "origens_v13.json"
_DATA_ITENS = Path(__file__).resolve().parent.parent / "data" / "origens_itens_v13.json"


@lru_cache(maxsize=1)
def _documento_itens() -> Dict[str, Any]:
    if not _DATA_ITENS.is_file():
        return {"itens_por_origem": {}, "escolhas_por_origem": {}}
    return json.loads(_DATA_ITENS.read_text(encoding="utf-8"))


def itens_origem_catalogo_v13(slug: str) -> List[str]:
    s = str(slug or "").strip().lower()
    raw = (_documento_itens().get("itens_por_origem") or {}).get(s) or []
    if not isinstance(raw, list):
        return []
    return [str(x).strip() for x in raw if str(x).strip()]


def escolhas_origem_catalogo_v13(slug: str) -> Optional[Dict[str, Any]]:
    s = str(slug or "").strip().lower()
    cfg = (_documento_itens().get("escolhas_por_origem") or {}).get(s)
    return dict(cfg) if isinstance(cfg, dict) else None


def resolver_itens_origem_v13(
    slug_origem: str, ficha_json: Optional[dict] = None
) -> List[str]:
    """Itens grátis da origem (com escolhas resolvidas)."""
    s = str(slug_origem or "").strip().lower()
    if not s:
        return []
    esc = escolhas_origem_catalogo_v13(s)
    if esc:
        fj = dict(ficha_json or {})
        campo = str(esc.get("campo") or "item")
        opcoes = esc.get("opcoes") or []
        escolha_map = fj.get("origem_itens_escolha") or {}
        pick = ""
        if isinstance(escolha_map, dict):
            pick = (
                str(escolha_map.get(s) or escolha_map.get(campo) or "").strip().lower()
            )
        if not pick:
            pick = str(esc.get("default") or "").strip().lower()
        for op in opcoes:
            if isinstance(op, dict) and str(op.get("slug") or "").lower() == pick:
                return [
                    str(x).strip() for x in (op.get("itens") or []) if str(x).strip()
                ]
        if opcoes and isinstance(opcoes[0], dict):
            return [
                str(x).strip() for x in (opcoes[0].get("itens") or []) if str(x).strip()
            ]
        return []
    return itens_origem_catalogo_v13(s)


@lru_cache(maxsize=1)
def _documento() -> Dict[str, Any]:
    if not _DATA.is_file():
        return {"origens": []}
    return json.loads(_DATA.read_text(encoding="utf-8"))


def lista_origens_v13() -> List[Dict[str, Any]]:
    rows = _documento().get("origens") or []
    out: List[Dict[str, Any]] = []
    if not isinstance(rows, list):
        return out
    for row in rows:
        if not isinstance(row, dict):
            continue
        slug = str(row.get("slug", "")).strip().lower()
        if not slug:
            continue
        out.append(
            {
                "slug": slug,
                "nome": str(row.get("nome", "") or slug).strip(),
                "pagina": int(row.get("pagina", 0) or 0),
                "beneficios_pericias": list(row.get("beneficios_pericias") or []),
                "beneficios_poderes": list(row.get("beneficios_poderes") or []),
                "poder_unico": row.get("poder_unico"),
                "itens": itens_origem_catalogo_v13(slug),
                "itens_escolha": escolhas_origem_catalogo_v13(slug),
            }
        )
    return sorted(out, key=lambda x: x["nome"].lower())


def origem_por_slug(slug: str) -> Optional[Dict[str, Any]]:
    s = str(slug or "").strip().lower()
    if not s:
        return None
    for row in lista_origens_v13():
        if row.get("slug") == s:
            return row
    return None


def validar_beneficios_origem(
    slug_origem: str, beneficios: List[str]
) -> tuple[bool, str]:
    """Valida exatamente 2 benefícios no formato pericia:slug ou poder:slug."""
    orig = origem_por_slug(slug_origem)
    if not orig:
        return False, "Origem desconhecida."
    if len(beneficios) != 2:
        return False, "Escolha exatamente 2 benefícios da origem."
    per_pool = {f"pericia:{p}" for p in orig.get("beneficios_pericias") or []}
    pod_pool = {f"poder:{p}" for p in orig.get("beneficios_poderes") or []}
    pu = orig.get("poder_unico")
    if pu:
        pod_pool.add(f"poder:{pu}")
    pool = per_pool | pod_pool
    for b in beneficios:
        key = str(b or "").strip().lower()
        if key not in pool:
            return False, f"Benefício inválido para a origem: {key}"
    return True, ""


def slugs_pericias_de_beneficios_origem(beneficios: Any) -> List[str]:
    """Extrai slugs de perícia de `origem_beneficios` (`pericia:slug`)."""
    out: List[str] = []
    if not isinstance(beneficios, list):
        return out
    seen: set[str] = set()
    for raw in beneficios:
        key = str(raw or "").strip().lower()
        if not key.startswith("pericia:"):
            continue
        slug = key.split(":", 1)[1].strip().lower()
        if slug and slug not in seen:
            seen.add(slug)
            out.append(slug)
    return out


def contar_vagas_pericias_extra_origem(beneficios: Any) -> int:
    return len(slugs_pericias_de_beneficios_origem(beneficios))


def _linha_pericia_padrao(meta: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "nome": str(meta.get("nome", "") or "").strip(),
        "treinado": False,
        "graduacao": 0,
        "outros": 0,
        "somente_treinado": bool(meta.get("somente_treinado")),
        "penalidade_armadura": bool(meta.get("penalidade_armadura")),
    }


def aplicar_pericias_origem_em_lista(
    pericias: Any,
    beneficios: Any,
    *,
    regra_versao: str = REGRA_VERSAO_V13,
) -> List[Dict[str, Any]]:
    """Marca treinado=true nas perícias escolhidas como benefício de origem v1.3."""
    slugs = slugs_pericias_de_beneficios_origem(beneficios)
    lista: List[Dict[str, Any]] = (
        [dict(p) for p in pericias if isinstance(p, dict)]
        if isinstance(pericias, list)
        else []
    )
    if not slugs:
        return lista

    norm_to_idx: Dict[str, int] = {}
    for i, row in enumerate(lista):
        n = _normalizar_nome_pericia(str(row.get("nome", "")))
        if n:
            norm_to_idx[n] = i

    for slug in slugs:
        meta = meta_pericia_por_nome(slug, regra_versao)
        if not meta:
            for row in lista_pericias_com_atributo(regra_versao):
                if str(row.get("slug", "")).lower() == slug:
                    meta = row
                    break
        if not meta:
            continue
        nome = str(meta.get("nome", "") or "").strip()
        key = _normalizar_nome_pericia(nome)
        if not key:
            continue
        if key in norm_to_idx:
            lista[norm_to_idx[key]]["treinado"] = True
        else:
            row = _linha_pericia_padrao(meta)
            row["treinado"] = True
            lista.append(row)
            norm_to_idx[key] = len(lista) - 1
    return lista


def sincronizar_pericias_origem_ficha_json(
    ficha_json: Dict[str, Any]
) -> Dict[str, Any]:
    """Aplica benefícios de origem v1.3 em `ficha_json.pericias`."""
    fj = dict(ficha_json or {})
    if regra_versao_de_ficha(fj) != REGRA_VERSAO_V13:
        return fj
    beneficios = fj.get("origem_beneficios")
    if not slugs_pericias_de_beneficios_origem(beneficios):
        return fj
    fj["pericias"] = aplicar_pericias_origem_em_lista(
        fj.get("pericias"),
        beneficios,
        regra_versao=REGRA_VERSAO_V13,
    )
    return fj
