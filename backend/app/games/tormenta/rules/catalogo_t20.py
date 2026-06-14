"""Catálogos MB (equipamento, talentos) para autocomplete na ficha."""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_EQUIP_JSON = _DATA_DIR / "equipamentos_mb_catalogo.json"
_TALENT_JSON = _DATA_DIR / "talentos_mb_catalogo.json"
_MAGIAS_JSON = _DATA_DIR / "magias_mb_catalogo.json"

_MAGIA_FIELD_LIMITS: Dict[str, int] = {
    "slug": 80,
    "nome": 200,
    "escola": 80,
    "resistencia": 120,
    "execucao": 120,
    "alcance": 120,
    "alvo": 200,
    "duracao": 120,
    "descricao_curta": 500,
    "pagina_referencia": 80,
}
_MAGIA_STRING_FIELDS: Tuple[str, ...] = tuple(_MAGIA_FIELD_LIMITS)

_TALENT_FIELD_LIMITS: Dict[str, int] = {
    "secao": 200,
    "categoria": 80,
    "prerequisitos": 500,
    "descricao_resumo": 2000,
    "pagina_referencia": 80,
}
_TALENT_EXTRA_FIELDS: Tuple[str, ...] = tuple(_TALENT_FIELD_LIMITS)


@lru_cache(maxsize=1)
def _carregar_equipamentos() -> List[Dict[str, Any]]:
    if not _EQUIP_JSON.is_file():
        return []
    raw = _EQUIP_JSON.read_text(encoding="utf-8")
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
        cat = str(row.get("categoria", "") or "").strip() or None

        def _s(key: str, mx: int) -> str | None:
            v = row.get(key)
            if v is None:
                return None
            t = str(v).strip()
            if not t:
                return None
            return t[:mx]

        out.append(
            {
                "nome": nome,
                "categoria": cat,
                "secao": _s("secao", 200),
                "custo": _s("custo", 80),
                "dano_p": _s("dano_p", 40),
                "dano_m": _s("dano_m", 40),
                "tipo_dano": _s("tipo_dano", 120),
                "critico": _s("critico", 80),
                "alcance": _s("alcance", 80),
                "peso": _s("peso", 80),
            }
        )
    return out


@lru_cache(maxsize=1)
def _carregar_talentos_mb_catalogo_json() -> List[Dict[str, Any]]:
    if not _TALENT_JSON.is_file():
        return []
    raw = _TALENT_JSON.read_text(encoding="utf-8")
    data = json.loads(raw)
    rows = data.get("itens") or data.get("items") or []
    out: List[Dict[str, Any]] = []
    if not isinstance(rows, list):
        return out

    def _trim(key: str, row: Dict[str, Any]) -> str | None:
        v = row.get(key)
        if v is None:
            return None
        t = str(v).strip()
        if not t:
            return None
        mx = _TALENT_FIELD_LIMITS.get(key, 500)
        return t[:mx]

    for row in rows:
        if not isinstance(row, dict):
            continue
        nome = str(row.get("nome", "")).strip()
        if not nome:
            continue
        item: Dict[str, Any] = {"nome": nome}
        for key in _TALENT_EXTRA_FIELDS:
            tv = _trim(key, row)
            if tv:
                item[key] = tv
        out.append(item)
    return out


def lista_equipamentos_mb_catalogo() -> List[Dict[str, Any]]:
    """Lista completa de itens de equipamento (MB) para filtro/paginação."""
    return list(_carregar_equipamentos())


def filtrar_equipamentos_mb(
    q: str | None, skip: int, limit: int
) -> Tuple[List[Dict[str, Any]], int]:
    rows = [dict(r) for r in lista_equipamentos_mb_catalogo()]
    qn = (q or "").strip().lower()
    if qn:
        rows = [r for r in rows if qn in str(r.get("nome", "")).lower()]
    for i, item in enumerate(rows, start=1):
        item["id"] = i
    total = len(rows)
    s = max(0, int(skip))
    lim = max(1, min(200, int(limit)))
    return rows[s : s + lim], total


def _split_talentos_texto(texto: str) -> List[str]:
    """Separa nomes de talentos (vírgulas, ponto-e-vírgula, quebras de linha)."""
    if not texto or not str(texto).strip():
        return []
    partes = re.split(r"[,;\n]+", str(texto))
    return [p.strip() for p in partes if p and len(p.strip()) >= 2]


def lista_talentos_mb_catalogo() -> List[Dict[str, Any]]:
    """Talentos das classes MB + enriquecimento opcional (`talentos_mb_catalogo.json`)."""
    from app.games.tormenta.rules.classes_t20 import lista_classes_mb

    json_rows = _carregar_talentos_mb_catalogo_json()
    meta_by_lower: Dict[str, Dict[str, Any]] = {}
    for r in json_rows:
        nk = str(r.get("nome", "")).strip().lower()
        if nk:
            meta_by_lower[nk] = r

    seen: set[str] = set()
    out: List[Dict[str, Any]] = []
    for row in lista_classes_mb():
        raw = row.get("talentos_adicionais") or ""
        for nome in _split_talentos_texto(str(raw)):
            key = nome.lower()
            if key in seen:
                continue
            seen.add(key)
            item: Dict[str, Any] = {"nome": nome.strip()}
            meta = meta_by_lower.get(key)
            if meta:
                for fld in _TALENT_EXTRA_FIELDS:
                    if meta.get(fld):
                        item[fld] = meta[fld]
            if "secao" not in item:
                item["secao"] = "Talentos das classes (MB)"
            if "categoria" not in item:
                item["categoria"] = "Classe"
            out.append(item)

    for r in json_rows:
        nk = str(r.get("nome", "")).strip().lower()
        if not nk or nk in seen:
            continue
        seen.add(nk)
        item = {"nome": str(r["nome"]).strip()}
        for fld in _TALENT_EXTRA_FIELDS:
            if r.get(fld):
                item[fld] = r[fld]
        if "secao" not in item:
            item["secao"] = "Catálogo MB"
        if "categoria" not in item:
            item["categoria"] = "Talento"
        out.append(item)

    out.sort(key=lambda x: str(x["nome"]).lower())
    return out


def _haystack_talento_mb(r: Dict[str, Any]) -> str:
    parts: List[str] = []
    for k in (
        "nome",
        "secao",
        "categoria",
        "prerequisitos",
        "descricao_resumo",
        "pagina_referencia",
    ):
        v = r.get(k)
        if v is not None and str(v).strip():
            parts.append(str(v).lower())
    return " ".join(parts)


def filtrar_talentos_mb(
    q: str | None, skip: int, limit: int
) -> Tuple[List[Dict[str, Any]], int]:
    rows = [dict(r) for r in lista_talentos_mb_catalogo()]
    qn = (q or "").strip().lower()
    if qn:
        rows = [r for r in rows if qn in _haystack_talento_mb(r)]
    for i, item in enumerate(rows, start=1):
        item["id"] = i
    total = len(rows)
    s = max(0, int(skip))
    lim = max(1, min(200, int(limit)))
    return rows[s : s + lim], total


def _trim_magia_field(key: str, row: Dict[str, Any]) -> str | None:
    v = row.get(key)
    if v is None:
        return None
    t = str(v).strip()
    if not t:
        return None
    mx = _MAGIA_FIELD_LIMITS.get(key, 200)
    return t[:mx]


@lru_cache(maxsize=1)
def _carregar_magias_mb_catalogo_json() -> List[Dict[str, Any]]:
    """Magias MB (metadados) — ficheiro versionado; pode ser preenchido por seed privado."""
    if not _MAGIAS_JSON.is_file():
        return []
    raw = _MAGIAS_JSON.read_text(encoding="utf-8")
    data = json.loads(raw)
    rows = data.get("itens") or data.get("items") or []
    out: List[Dict[str, Any]] = []
    if not isinstance(rows, list):
        return out
    for row in rows:
        if not isinstance(row, dict):
            continue
        slug = _trim_magia_field("slug", row)
        nome = _trim_magia_field("nome", row)
        if not slug or not nome:
            continue
        try:
            circulo = int(row.get("circulo", 0))
        except (TypeError, ValueError):
            continue
        if circulo < 0 or circulo > 20:
            continue
        tipo_raw = str(row.get("tipo", "")).strip().lower()
        if tipo_raw not in ("arcana", "divina"):
            continue
        tipo = "arcana" if tipo_raw == "arcana" else "divina"
        item: Dict[str, Any] = {
            "slug": slug,
            "nome": nome,
            "circulo": circulo,
            "tipo": tipo,
        }
        for key in _MAGIA_STRING_FIELDS:
            if key in ("slug", "nome"):
                continue
            tv = _trim_magia_field(key, row)
            if tv:
                item[key] = tv
        out.append(item)
    out.sort(key=lambda x: (x["circulo"], str(x["nome"]).lower()))
    return out


def lista_magias_mb_catalogo() -> List[Dict[str, Any]]:
    """Lista completa de magias (MB / stub) para filtro e paginação."""
    return list(_carregar_magias_mb_catalogo_json())


def magia_mb_slug_no_catalogo(slug: str) -> bool:
    """True se o slug existe no catálogo `magias_mb_catalogo.json` (validação de vínculos)."""
    s = str(slug or "").strip().lower()
    if not s:
        return False
    return any(
        str(r.get("slug", "")).strip().lower() == s for r in lista_magias_mb_catalogo()
    )


def metadados_magia_mb_por_slug(slug: str) -> Dict[str, Any] | None:
    """Metadados do catálogo para um slug, ou None."""
    s = str(slug or "").strip().lower()
    if not s:
        return None
    for r in lista_magias_mb_catalogo():
        if str(r.get("slug", "")).strip().lower() == s:
            return dict(r)
    return None


def _norm_nome_magia_mb(texto: str) -> str:
    import unicodedata

    s = unicodedata.normalize("NFKD", str(texto or "").strip().lower())
    return "".join(ch for ch in s if not unicodedata.combining(ch))


def resolver_magia_mb_slug_por_texto(
    texto: str,
    *,
    tipo_preferido: Optional[str] = None,
) -> Optional[str]:
    """Resolve nome livre ou slug para slug do catálogo MB."""
    raw = str(texto or "").strip()
    if not raw:
        return None
    slug_try = raw.lower().replace(" ", "-")[:80]
    if magia_mb_slug_no_catalogo(slug_try):
        return slug_try
    if magia_mb_slug_no_catalogo(raw.lower()[:80]):
        return raw.lower()[:80]
    alvo = _norm_nome_magia_mb(raw)
    if not alvo:
        return None
    tipo = str(tipo_preferido or "").strip().lower() or None
    candidatos: list[Dict[str, Any]] = []
    for r in lista_magias_mb_catalogo():
        nome = _norm_nome_magia_mb(str(r.get("nome") or ""))
        if nome == alvo or alvo in nome or nome in alvo:
            candidatos.append(r)
    if not candidatos:
        return None
    if tipo:
        por_tipo = [r for r in candidatos if str(r.get("tipo") or "").lower() == tipo]
        if len(por_tipo) == 1:
            return str(por_tipo[0].get("slug") or "").strip().lower()
        if len(por_tipo) > 1:
            candidatos = por_tipo
    if len(candidatos) == 1:
        return str(candidatos[0].get("slug") or "").strip().lower()
    return None


def papel_padrao_migracao_magias_mb(slug_classe: str) -> str:
    from app.games.tormenta.rules.grimorio_conjuracao_t20 import (
        modo_conjuracao_classe_mb,
    )
    from app.games.tormenta.rules.magias_grimorio_aprendizado_t20 import (
        classe_usa_limite_grimorio_mb,
    )

    if modo_conjuracao_classe_mb(slug_classe) == "espontaneo":
        return "conhecida"
    if classe_usa_limite_grimorio_mb(slug_classe):
        return "grimorio"
    return "conhecida"


def _haystack_magia_mb(r: Dict[str, Any]) -> str:
    parts: List[str] = []
    for k in (
        "slug",
        "nome",
        "escola",
        "tipo",
        "resistencia",
        "execucao",
        "alcance",
        "alvo",
        "duracao",
        "descricao_curta",
        "pagina_referencia",
    ):
        v = r.get(k)
        if v is not None and str(v).strip():
            parts.append(str(v).lower())
    return " ".join(parts)


def filtrar_magias_mb(
    q: str | None,
    circulo: int | None,
    tipo: str | None,
    escola: str | None,
    circulo_max: int | None,
    skip: int,
    limit: int,
) -> Tuple[List[Dict[str, Any]], int]:
    rows = [dict(r) for r in lista_magias_mb_catalogo()]
    qn = (q or "").strip().lower()
    if qn:
        rows = [r for r in rows if qn in _haystack_magia_mb(r)]
    if circulo is not None:
        rows = [r for r in rows if int(r.get("circulo", -1)) == int(circulo)]
    if circulo_max is not None:
        try:
            cmax = int(circulo_max)
        except (TypeError, ValueError):
            cmax = None
        if cmax is not None and cmax >= 0:
            rows = [r for r in rows if int(r.get("circulo", -1)) <= cmax]
    if tipo is not None and str(tipo).strip():
        tn = str(tipo).strip().lower()
        if tn in ("arcana", "divina"):
            rows = [r for r in rows if str(r.get("tipo", "")).lower() == tn]
    if escola is not None and str(escola).strip():
        en = str(escola).strip().lower()
        rows = [r for r in rows if en in str(r.get("escola") or "").lower()]
    for i, item in enumerate(rows, start=1):
        item["id"] = i
    total = len(rows)
    s = max(0, int(skip))
    lim = max(1, min(200, int(limit)))
    return rows[s : s + lim], total
