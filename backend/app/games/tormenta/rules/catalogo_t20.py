"""Catálogos MB (equipamento, talentos) para autocomplete na ficha."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_EQUIP_JSON = _DATA_DIR / "equipamentos_mb_catalogo.json"
_EQUIP_HA_JSON = _DATA_DIR / "equipamentos_herois_arton.json"
_TALENT_JSON = _DATA_DIR / "talentos_mb_catalogo.json"
_MAGIAS_JSON = _DATA_DIR / "magias_mb_catalogo.json"
_MAGIAS_ALIASES_MB_V13 = _DATA_DIR / "magias_mb_v13_slug_aliases.json"
_BESTIARIO_JSON = _DATA_DIR / "bestiario_v13.json"
_BESTIARIO_DDA_JSON = _DATA_DIR / "bestiario_dda_v11.json"
_BESTIARIO_STUB_JSON = _DATA_DIR / "bestiario_mb_stub.json"

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
    "categoria_v13": 40,
    "prerequisitos": 500,
    "descricao_resumo": 2000,
    "pagina_referencia": 80,
    "custo_pm": 4,
}
_TALENT_EXTRA_FIELDS: Tuple[str, ...] = tuple(_TALENT_FIELD_LIMITS) + (
    "pre_requisitos_v13",
)


def _norm_nome_catalogo(texto: str) -> str:
    import unicodedata

    s = unicodedata.normalize("NFKD", str(texto or "").strip().lower())
    return "".join(c for c in s if not unicodedata.combining(c))


@lru_cache(maxsize=1)
def _mapa_armaduras_por_nome() -> Dict[str, Dict[str, Any]]:
    from app.games.tormenta.rules.catalogo_armaduras_t20 import (
        lista_armaduras_protecao_catalogo,
    )

    out: Dict[str, Dict[str, Any]] = {}
    for row in lista_armaduras_protecao_catalogo():
        chave = _norm_nome_catalogo(str(row.get("nome", "")))
        if chave:
            out[chave] = dict(row)
    return out


_ARMA_OVERLAY_KEYS = (
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


@lru_cache(maxsize=1)
def _mapa_armas_v13_por_nome() -> Dict[str, Dict[str, Any]]:
    from app.games.tormenta.rules.catalogo_armas_v13_t20 import mapa_armas_v13_por_nome

    return mapa_armas_v13_por_nome()


def _score_busca_equipamento(qn: str, nome: str) -> tuple[int, str]:
    """Prioriza match exato, depois prefixo, depois substring (nome mais curto)."""
    nl = str(nome or "").lower()
    if nl == qn:
        return (0, nl)
    if nl.startswith(qn):
        return (1, nl)
    if qn in nl:
        return (2, nl)
    return (99, nl)


def _enriquecer_equipamento_v13(item: Dict[str, Any]) -> Dict[str, Any]:
    """Mescla metadados v1.3 de armaduras/armas e calcula espacos de carga."""
    from app.games.tormenta.rules.carga_t20 import espacos_por_item

    out = dict(item)
    chave = _norm_nome_catalogo(out.get("nome", ""))
    arm = _mapa_armaduras_por_nome().get(chave)
    if arm:
        out["tipo"] = str(arm.get("tipo", "") or "").strip() or out.get("tipo")
        out["bonus_ca"] = int(arm.get("bonus_ca", 0) or 0)
        out["penalidade"] = int(arm.get("penalidade", 0) or 0)
        if arm.get("peso") and not out.get("peso"):
            out["peso"] = str(arm.get("peso"))
        out["regra_versao"] = "v13"
    arma = _mapa_armas_v13_por_nome().get(chave)
    if arma:
        for key in _ARMA_OVERLAY_KEYS:
            if out.get(key) is None and arma.get(key) is not None:
                out[key] = arma[key]
        out["regra_versao"] = "v13"
    esp = espacos_por_item(
        {
            "nome": out.get("nome"),
            "categoria": out.get("categoria"),
            "tipo": out.get("tipo"),
            "espacos": out.get("espacos"),
        }
    )
    out["espacos"] = esp
    if out.get("regra_versao") is None and (
        out.get("bonus_ca") is not None or out.get("espacos") is not None
    ):
        out["regra_versao"] = "v13"
    return out


@lru_cache(maxsize=1)
def _carregar_equipamentos_ha() -> List[Dict[str, Any]]:
    if not _EQUIP_HA_JSON.is_file():
        return []
    data = json.loads(_EQUIP_HA_JSON.read_text(encoding="utf-8"))
    rows = data.get("itens") or []
    out: List[Dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        nome = str(row.get("nome", "")).strip()
        if not nome:
            continue
        item = dict(row)
        item["nome"] = nome
        item.setdefault("fonte_catalogo", "herois_arton")
        out.append(_enriquecer_equipamento_v13(item))
    return out


def lista_equipamentos_com_suplemento(
    suplemento: Optional[str] = None,
) -> List[Dict[str, Any]]:
    from app.games.tormenta.rules.regra_versao_t20 import SUPLEMENTO_HEROIS_ARTON

    rows = lista_equipamentos_mb_catalogo()
    if suplemento and str(suplemento).strip().lower() == SUPLEMENTO_HEROIS_ARTON:
        seen = {_norm_nome_catalogo(r.get("nome", "")) for r in rows}
        for ha in _carregar_equipamentos_ha():
            ch = _norm_nome_catalogo(ha.get("nome", ""))
            if ch and ch not in seen:
                rows.append(ha)
                seen.add(ch)
    return rows


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

        item: Dict[str, Any] = {
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
        for opt in (
            "tipo",
            "espacos",
            "bonus_ca",
            "penalidade",
            "proficiencia",
            "empunhadura",
        ):
            if row.get(opt) is not None:
                item[opt] = row.get(opt)
        out.append(_enriquecer_equipamento_v13(item))
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
    q: str | None, skip: int, limit: int, suplemento: str | None = None
) -> Tuple[List[Dict[str, Any]], int]:
    rows = [dict(r) for r in lista_equipamentos_com_suplemento(suplemento)]
    qn = (q or "").strip().lower()
    if qn:
        filtrados = [r for r in rows if qn in str(r.get("nome", "")).lower()]
        filtrados.sort(
            key=lambda r: _score_busca_equipamento(qn, str(r.get("nome", "")))
        )
        rows = filtrados
    for i, item in enumerate(rows, start=1):
        item["id"] = i
    total = len(rows)
    s = max(0, int(skip))
    lim = max(1, min(200, int(limit)))
    return rows[s : s + lim], total


def lista_talentos_mb_catalogo() -> List[Dict[str, Any]]:
    """Catálogo canónico de poderes Cap. 2 v1.3 (`talentos_mb_catalogo.json`).

    Não mistura ``talentos_adicionais`` das classes (proficiências / textos de
    ficha) — o split por vírgula gerava fragmentos falsos (ex.: ``adaga``).
    """
    json_rows = _carregar_talentos_mb_catalogo_json()
    out: List[Dict[str, Any]] = []
    for r in json_rows:
        nome = str(r.get("nome", "")).strip()
        if not nome:
            continue
        item: Dict[str, Any] = {"nome": nome}
        for fld in _TALENT_EXTRA_FIELDS:
            if r.get(fld):
                item[fld] = r[fld]
        if "secao" not in item:
            item["secao"] = "Catálogo MB"
        if "categoria" not in item:
            item["categoria"] = "Talento"
        out.append(item)

    out.sort(key=lambda x: str(x["nome"]).lower())
    from app.games.tormenta.rules.poderes_catalogo_v13_t20 import (
        enriquecer_item_catalogo_poder,
    )

    return [enriquecer_item_catalogo_poder(r) for r in out]


def _poder_ha_para_catalogo(row: Dict[str, Any]) -> Dict[str, Any]:
    from app.games.tormenta.rules.poderes_catalogo_v13_t20 import (
        enriquecer_item_catalogo_poder,
    )

    slug = str(row.get("slug") or "").strip().lower()
    nome = str(row.get("nome") or slug).strip()
    item: Dict[str, Any] = {
        "slug": slug,
        "nome": nome,
        "fonte_catalogo": str(row.get("fonte_catalogo") or "herois_arton"),
        "categoria_v13": str(row.get("categoria_v13") or "geral").strip().lower(),
        "secao": "Heróis de Arton",
        "categoria": str(row.get("categoria_v13") or "Geral").replace("_", " ").title(),
    }
    for opt in (
        "classe_exigida",
        "raca_exigida",
        "descricao_resumo",
        "pagina_referencia",
        "prerequisitos",
        "custo_pm",
    ):
        if row.get(opt) is not None:
            item[opt] = row[opt]
    return enriquecer_item_catalogo_poder(item)


def lista_poderes_catalogo_v13(
    suplemento: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Catálogo MB + suplemento Heróis de Arton quando ``suplemento='herois_arton'``."""
    from app.games.tormenta.rules.poderes_herois_arton_t20 import (
        lista_poderes_herois_arton,
    )
    from app.games.tormenta.rules.regra_versao_t20 import SUPLEMENTO_HEROIS_ARTON

    out = lista_talentos_mb_catalogo()
    if not suplemento or str(suplemento).strip().lower() != SUPLEMENTO_HEROIS_ARTON:
        return out
    seen = {
        str(r.get("slug") or _norm_nome_catalogo(str(r.get("nome", ""))))
        .strip()
        .lower()
        for r in out
        if r.get("slug") or r.get("nome")
    }
    for row in lista_poderes_herois_arton():
        slug = str(row.get("slug") or "").strip().lower()
        if not slug or slug in seen:
            continue
        seen.add(slug)
        out.append(_poder_ha_para_catalogo(row))
    out.sort(key=lambda x: str(x["nome"]).lower())
    return out


def _haystack_talento_mb(r: Dict[str, Any]) -> str:
    parts: List[str] = []
    for k in (
        "slug",
        "nome",
        "secao",
        "categoria",
        "categoria_v13",
        "prerequisitos",
        "descricao_resumo",
        "pagina_referencia",
        "raca_exigida",
        "classe_exigida",
        "fonte_catalogo",
    ):
        v = r.get(k)
        if v is not None and str(v).strip():
            parts.append(str(v).lower())
    return " ".join(parts)


def filtrar_talentos_mb(
    q: str | None,
    skip: int,
    limit: int,
    *,
    categoria_v13: str | None = None,
    suplemento: str | None = None,
    raca: str | None = None,
    classe_exigida: str | None = None,
) -> Tuple[List[Dict[str, Any]], int]:
    rows = [dict(r) for r in lista_poderes_catalogo_v13(suplemento)]
    qn = (q or "").strip().lower()
    if qn:
        rows = [r for r in rows if qn in _haystack_talento_mb(r)]
    cat_f = str(categoria_v13 or "").strip().lower()
    if cat_f:
        if cat_f == "geral":
            # Poderes Gerais do livro = combate + destino + magia (não há slug «geral»).
            _gerais = {"combate", "destino", "magia"}
            rows = [
                r
                for r in rows
                if str(r.get("categoria_v13") or "").strip().lower() in _gerais
            ]
        else:
            rows = [r for r in rows if str(r.get("categoria_v13") or "") == cat_f]
    raca_f = str(raca or "").strip().lower()
    if raca_f:
        rows = [
            r
            for r in rows
            if str(r.get("raca_exigida") or "").strip().lower() == raca_f
        ]
    classe_f = str(classe_exigida or "").strip().lower()
    if classe_f:
        rows = [
            r
            for r in rows
            if str(r.get("classe_exigida") or "").strip().lower() == classe_f
        ]
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


@lru_cache(maxsize=1)
def _mapa_aliases_mb_para_v13() -> Dict[str, str]:
    """Mapa slug MB antigo → slug v1.3 no catálogo atual.

    Usado para preservar compatibilidade com vínculos gravados em
    `tormenta_magias_personagem` antes da migração para o catálogo Jogo do Ano
    v1.3 (magias de círculos 0 e 6–9 do MB tornam-se órfãs).
    """
    if not _MAGIAS_ALIASES_MB_V13.is_file():
        return {}
    try:
        raw = json.loads(_MAGIAS_ALIASES_MB_V13.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    aliases = raw.get("aliases") if isinstance(raw, dict) else None
    if not isinstance(aliases, dict):
        return {}
    return {
        str(k).strip().lower(): str(v).strip().lower()
        for k, v in aliases.items()
        if isinstance(k, str) and isinstance(v, str) and k.strip() and v.strip()
    }


def resolver_slug_mb_para_v13(slug: str) -> str:
    """Retorna slug v1.3 se `slug` (MB antigo) estiver mapeado; senão o próprio slug."""
    s = str(slug or "").strip().lower()
    if not s:
        return s
    return _mapa_aliases_mb_para_v13().get(s, s)


def magia_mb_slug_no_catalogo(slug: str) -> bool:
    """True se o slug (ou seu alias MB→v1.3) existe no catálogo atual."""
    s = str(slug or "").strip().lower()
    if not s:
        return False
    v13 = resolver_slug_mb_para_v13(s)
    return any(
        str(r.get("slug", "")).strip().lower() == v13
        for r in lista_magias_mb_catalogo()
    )


def metadados_magia_mb_por_slug(slug: str) -> Dict[str, Any] | None:
    """Metadados do catálogo para um slug (ou alias MB→v1.3), ou None."""
    s = str(slug or "").strip().lower()
    if not s:
        return None
    v13 = resolver_slug_mb_para_v13(s)
    for r in lista_magias_mb_catalogo():
        if str(r.get("slug", "")).strip().lower() == v13:
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


def _nd_numerico(raw: Any) -> Optional[float]:
    if raw is None or raw == "":
        return None
    if isinstance(raw, (int, float)):
        return float(raw)
    s = str(raw).strip().replace(",", ".")
    if "/" in s:
        parts = s.split("/", 1)
        try:
            a, b = float(parts[0]), float(parts[1])
            if b:
                return a / b
        except (TypeError, ValueError):
            return None
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def _nd_rotulo_de_row(row: Dict[str, Any]) -> Optional[str]:
    rot = str(row.get("nd_rotulo") or "").strip()
    if rot:
        return rot
    nd = _nd_numerico(row.get("nd"))
    if nd is None:
        return None
    if abs(nd - 0.25) < 1e-9:
        return "1/4"
    if abs(nd - 0.5) < 1e-9:
        return "1/2"
    if nd == int(nd):
        return str(int(nd))
    return str(nd).rstrip("0").rstrip(".")


@lru_cache(maxsize=1)
def _carregar_bestiario_mb() -> List[Dict[str, Any]]:
    """Catálogo unificado: T20 v1.3 + Deuses de Arton Cap.4 (se presentes)."""
    paths: List[Path] = []
    if _BESTIARIO_JSON.is_file():
        paths.append(_BESTIARIO_JSON)
    elif _BESTIARIO_STUB_JSON.is_file():
        paths.append(_BESTIARIO_STUB_JSON)
    if _BESTIARIO_DDA_JSON.is_file():
        paths.append(_BESTIARIO_DDA_JSON)
    if not paths:
        return []

    out: List[Dict[str, Any]] = []
    seen_slugs: set[str] = set()
    for path in paths:
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        rows = raw.get("criaturas") if isinstance(raw, dict) else raw
        if not isinstance(rows, list):
            continue
        fonte_arquivo = (
            str(raw.get("fonte") or "").strip() if isinstance(raw, dict) else ""
        )
        for row in rows:
            if not isinstance(row, dict):
                continue
            slug = str(row.get("slug") or "").strip()
            nome = str(row.get("nome") or "").strip()
            if not slug or not nome:
                continue
            slug_l = slug.lower()
            if slug_l in seen_slugs:
                # Preferir primeira fonte (v13); DdA com colisão seria -dda
                continue
            seen_slugs.add(slug_l)
            item = dict(row)
            item["slug"] = slug
            item["nome"] = nome
            if not item.get("fonte") and fonte_arquivo:
                item["fonte"] = fonte_arquivo
            nd_num = _nd_numerico(item.get("nd"))
            if nd_num is not None:
                item["nd"] = nd_num
            elif item.get("nd") is not None and str(item.get("nd")).strip() == "":
                item["nd"] = None
            item["nd_rotulo"] = _nd_rotulo_de_row(item)
            out.append(item)
    return out


def lista_bestiario_mb_catalogo() -> List[Dict[str, Any]]:
    """Lista completa do bestiário Tormenta (v1.3 + DdA Cap.4, ou stub legado)."""
    return [dict(r) for r in _carregar_bestiario_mb()]


def obter_bestiario_mb_por_slug(slug: str) -> Optional[Dict[str, Any]]:
    s = str(slug or "").strip().lower()
    if not s:
        return None
    for row in _carregar_bestiario_mb():
        if str(row.get("slug", "")).strip().lower() == s:
            return dict(row)
        aliases = row.get("aliases")
        if isinstance(aliases, list):
            for alias in aliases:
                if str(alias or "").strip().lower() == s:
                    return dict(row)
    return None


def _score_busca_bestiario(qn: str, row: Dict[str, Any]) -> tuple[int, str]:
    nome = str(row.get("nome", "")).lower()
    slug = str(row.get("slug", "")).lower()
    tipo = str(row.get("tipo_criatura", "")).lower()
    grupo = str(row.get("grupo", "")).lower()
    if nome == qn or slug == qn:
        return (0, nome)
    if nome.startswith(qn) or slug.startswith(qn):
        return (1, nome)
    if qn in nome or qn in slug or qn in tipo or qn in grupo:
        return (2, nome)
    return (99, nome)


def filtrar_bestiario_mb(
    q: str | None,
    skip: int,
    limit: int,
    *,
    tipo: str | None = None,
    nd_min: float | None = None,
    nd_max: float | None = None,
) -> Tuple[List[Dict[str, Any]], int]:
    rows = [dict(r) for r in lista_bestiario_mb_catalogo()]
    qn = (q or "").strip().lower()
    tipo_n = (tipo or "").strip().lower()
    if tipo_n:
        rows = [
            r
            for r in rows
            if tipo_n in str(r.get("tipo_criatura") or "").lower()
            or tipo_n in str(r.get("grupo") or "").lower()
        ]
    if nd_min is not None:
        rows = [
            r
            for r in rows
            if (nd := _nd_numerico(r.get("nd"))) is not None and nd >= float(nd_min)
        ]
    if nd_max is not None:
        rows = [
            r
            for r in rows
            if (nd := _nd_numerico(r.get("nd"))) is not None and nd <= float(nd_max)
        ]
    if qn:
        filtrados = [r for r in rows if _score_busca_bestiario(qn, r)[0] < 99]
        filtrados.sort(key=lambda r: _score_busca_bestiario(qn, r))
        rows = filtrados
    else:
        rows.sort(
            key=lambda r: (
                (
                    _nd_numerico(r.get("nd"))
                    if _nd_numerico(r.get("nd")) is not None
                    else 999.0
                ),
                str(r.get("nome") or "").lower(),
            )
        )
    for i, item in enumerate(rows, start=1):
        item["id"] = i
    total = len(rows)
    s = max(0, int(skip))
    lim = max(1, min(200, int(limit)))
    return rows[s : s + lim], total
