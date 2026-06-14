#!/usr/bin/env python3
"""
Enriquece `magias_mb_catalogo.json` com metadados MB (pp.150–209, PDF licenciado).

Uso:
  python3 backend/scripts/enrich_magias_mb_catalogo.py \\
      --detalhes backend/app/games/tormenta/data/sources/magias_mb_pp150-209.txt \\
      backend/app/games/tormenta/data/magias_mb_catalogo.json
"""

from __future__ import annotations

import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

_ALIASES_JSON = (
    Path(__file__).resolve().parents[1]
    / "app"
    / "games"
    / "tormenta"
    / "data"
    / "magias_mb_nome_aliases.json"
)

_ESCOLAS_MB = frozenset(
    {
        "abjuracao",
        "adivinhacao",
        "conjuracao",
        "encantamento",
        "evocacao",
        "ilusao",
        "necromancia",
        "transmutacao",
        "cura",
        "universal",
    }
)

_RE_NIVEL_PDF = re.compile(
    r"Nível:\s*(.+?)\s*\(([^)]+)\)",
    re.I,
)
_RE_NIVEL_SEM_ESCOLA = re.compile(
    r"Nível:\s*((?:arcana|divina)\s+\d+(?:\s*,\s*(?:arcana|divina)\s+\d+)*)",
    re.I,
)
_RE_TIPO_CIRC = re.compile(r"(arcana|divina)\s+(\d+)", re.I)
_RE_CAMPO_PDF = re.compile(
    r"(Tempo de Execução|Execução|Execucao|Alcance|Alvo|Área|Area|Efeito|Duração|Duracao|Teste de Resistência|Resistência|Resistencia)\s*:\s*([^;]+)",
    re.I,
)


def _norm_nome(nome: str) -> str:
    s = unicodedata.normalize("NFKD", nome.strip().lower())
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = re.sub(r"\s+", " ", s)
    return s


def _norm_agressivo(nome: str) -> str:
    return re.sub(r"[^a-z0-9]", "", _norm_nome(nome))


def _norm_chaves_lookup(nome: str) -> Set[str]:
    base = _norm_nome(nome)
    keys = {base, _norm_agressivo(nome)}
    keys.add(base.replace("/", " "))
    keys.add(base.replace("/", ""))
    keys.add(re.sub(r"\s*/\s*", " ", base))
    keys.add(re.sub(r"\s+", "", base))
    return {k for k in keys if k}


def _clean_line(raw: str) -> str:
    return raw.replace("\f", "").strip()


def _title_escola_mb(raw: str) -> str:
    s = str(raw or "").strip().lower()
    if not s:
        return ""
    return s[0].upper() + s[1:]


def _is_nivel_line(s: str) -> bool:
    low = s.strip().lower()
    return low.startswith("nível:") or low.startswith("nivel:")


def _looks_like_description(s: str) -> bool:
    if not s:
        return True
    if _is_nivel_line(s):
        return False
    low = s.lower()
    if low.startswith(
        (
            "esta ",
            "este ",
            "estas ",
            "estes ",
            "você ",
            "voce ",
            "como ",
            "uma ",
            "um ",
            "o alvo",
            "a magia",
            "quando ",
            "no início",
            "no inicio",
            "se ",
            "além ",
            "alem ",
            "custo em xp",
            "componente material",
        )
    ):
        return True
    if s.endswith(".") and len(s.split()) > 5:
        return True
    if "(cd " in low or "cd " in low[:12]:
        return True
    return False


def _parse_meta_line(meta_line: str) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    m_nivel = _RE_NIVEL_PDF.search(meta_line)
    tipos_part = ""
    escola_raw = ""
    if m_nivel:
        tipos_part = m_nivel.group(1)
        escola_raw = m_nivel.group(2)
    else:
        m_simple = _RE_NIVEL_SEM_ESCOLA.search(meta_line)
        if not m_simple:
            return {}, []
        tipos_part = m_simple.group(1)
    tipos_circ: List[Dict[str, Any]] = []
    for tm in _RE_TIPO_CIRC.finditer(tipos_part):
        tipos_circ.append(
            {"tipo": tm.group(1).lower(), "circulo": int(tm.group(2))}
        )
    escola = _title_escola_mb(escola_raw) if escola_raw else ""
    meta: Dict[str, Any] = {"escola": escola} if escola else {}
    if tipos_circ:
        meta["variantes_tipo"] = tipos_circ
    for fm in _RE_CAMPO_PDF.finditer(meta_line):
        chave = fm.group(1).lower()
        val = fm.group(2).strip()
        if "execu" in chave or "tempo de execu" in chave:
            meta["execucao"] = val
        elif chave.startswith("alcance"):
            meta["alcance"] = val
        elif chave in ("alvo", "área", "area", "efeito"):
            meta["alvo"] = val
        elif chave.startswith("dura"):
            meta["duracao"] = val
        elif "resist" in chave or "teste de resist" in chave:
            meta["resistencia"] = val
    return meta, tipos_circ


def _nome_variants_for_search(nome: str) -> List[str]:
    n = nome.strip()
    if not n:
        return []
    out = [n]
    if "/" in n:
        parts = [p.strip() for p in n.split("/") if p.strip()]
        if len(parts) == 2:
            out.append(f"{parts[0]}/{parts[1]}")
            out.append(f"{parts[0]} / {parts[1]}")
    return list(dict.fromkeys(out))


def _collect_nivel_meta_after(
    lines: List[str], from_idx: int
) -> Optional[Dict[str, Any]]:
    for j in range(from_idx + 1, min(from_idx + 14, len(lines))):
        if _looks_like_description(lines[j]):
            continue
        if "ível:" not in lines[j].lower() and "ivel:" not in lines[j].lower():
            continue
        chunks: List[str] = []
        for k in range(j, min(j + 10, len(lines))):
            ln = lines[k]
            if k > j and _looks_like_description(ln):
                break
            if k > j and _norm_nome(ln) in _ESCOLAS_MB:
                break
            chunks.append(ln)
            if re.search(r"Resistência:\s*[^;]+", ln, re.I):
                break
        meta, tipos = _parse_meta_line(" ".join(chunks))
        if meta.get("escola") or tipos:
            return meta
    return None


_LINES_CACHE: Optional[List[str]] = None


def _get_lines(text: str) -> List[str]:
    global _LINES_CACHE
    if _LINES_CACHE is None:
        _LINES_CACHE = [_clean_line(ln) for ln in text.replace("\r\n", "\n").split("\n")]
    return _LINES_CACHE


def _find_title_before_nivel(lines: List[str], nivel_idx: int) -> Optional[str]:
    parts: List[str] = []
    for k in range(nivel_idx - 1, max(nivel_idx - 6, -1), -1):
        ln = lines[k]
        if not ln:
            if parts:
                break
            continue
        if _looks_like_description(ln) or "ível:" in ln.lower() or "ivel:" in ln.lower():
            break
        if _norm_nome(ln) in _ESCOLAS_MB:
            break
        if len(ln) > 58 or len(ln.split()) > 9:
            break
        parts.insert(0, ln)
    title = " ".join(parts).strip()
    if not title or _looks_like_description(title):
        return None
    return title


def _is_probable_title_line(s: str) -> bool:
    if not s or len(s) > 58:
        return False
    if _looks_like_description(s):
        return False
    if _norm_nome(s) in _ESCOLAS_MB:
        return False
    if "ível:" in s.lower() or "ivel:" in s.lower() or ";" in s:
        return False
    if not s[0].isupper():
        return False
    if len(s.split()) > 9:
        return False
    return True


def _meta_quality(meta: Dict[str, Any]) -> int:
    q = 0
    if meta.get("escola"):
        q += 20
    variantes = meta.get("variantes_tipo")
    if isinstance(variantes, list):
        q += len(variantes) * 3
    for campo in ("execucao", "alcance", "alvo", "duracao", "resistencia"):
        if meta.get(campo):
            q += 1
    return q


def _store_pdf_meta(
    out: Dict[str, Dict[str, Any]], key: str, meta: Dict[str, Any]
) -> None:
    if not key:
        return
    prev = out.get(key)
    if prev is None or _meta_quality(meta) > _meta_quality(prev):
        out[key] = meta


def build_pdf_index_from_titles(text: str) -> Dict[str, Dict[str, Any]]:
    """Índice por título → metadados (procura Nível: à frente)."""
    lines = _get_lines(text)
    out: Dict[str, Dict[str, Any]] = {}
    for i, line in enumerate(lines):
        candidates: List[Tuple[str, int]] = []
        if _is_probable_title_line(line):
            candidates.append((line, i))
        if i + 1 < len(lines):
            nxt = lines[i + 1]
            if _is_probable_title_line(line) and nxt and _is_probable_title_line(nxt):
                candidates.append((f"{line} {nxt}", i + 1))
        for title, start in candidates:
            meta = _collect_nivel_meta_after(lines, start)
            if not meta:
                continue
            key = _norm_nome(title)
            meta = dict(meta)
            meta["_nome_fonte"] = title
            _store_pdf_meta(out, key, meta)
    return out


def build_pdf_index_from_niveis(text: str) -> Dict[str, Dict[str, Any]]:
    """Índice nome normalizado → metadados (varre Nível: uma vez)."""
    lines = _get_lines(text)
    out: Dict[str, Dict[str, Any]] = {}
    for i, line in enumerate(lines):
        if "ível:" not in line.lower() and "ivel:" not in line.lower():
            continue
        meta = _collect_nivel_meta_after(lines, i)
        if not meta:
            continue
        title = _find_title_before_nivel(lines, i)
        if not title:
            continue
        key = _norm_nome(title)
        if not key or key in _ESCOLAS_MB:
            continue
        meta = dict(meta)
        meta["_nome_fonte"] = title
        _store_pdf_meta(out, key, meta)
    return out


def _lookup_nomes(nome: str, aliases: Dict[str, str]) -> List[str]:
    out: List[str] = []
    seen: Set[str] = set()

    def add(n: str) -> None:
        key = _norm_nome(n)
        if key and key not in seen:
            seen.add(key)
            out.append(n)

    add(nome)
    aliased = aliases.get(_norm_nome(nome))
    if aliased:
        add(aliased)
    return out


def find_meta_for_catalog_name(text: str, nome: str) -> Optional[Dict[str, Any]]:
    """Localiza bloco Nível: após o título da magia no texto pdftotext."""
    lines = _get_lines(text)
    targets = {_norm_nome(v) for v in _nome_variants_for_search(nome)}
    targets.discard("")

    for i, line in enumerate(lines):
        if not line or _looks_like_description(line):
            continue
        if _norm_nome(line) in _ESCOLAS_MB:
            continue
        if _norm_nome(line) in targets:
            meta = _collect_nivel_meta_after(lines, i)
            if meta:
                meta = dict(meta)
                meta["_nome_fonte"] = line
                return meta
        if i + 1 < len(lines):
            nxt = lines[i + 1]
            if nxt and not _looks_like_description(nxt):
                combined = _norm_nome(f"{line} {nxt}")
                if combined in targets:
                    meta = _collect_nivel_meta_after(lines, i + 1)
                    if meta:
                        meta = dict(meta)
                        meta["_nome_fonte"] = f"{line} {nxt}"
                        return meta
        if line.strip().lower() in ("proteção", "protecao") and i + 1 < len(lines):
            nxt = lines[i + 1]
            if nxt and nxt.lower().startswith("contra "):
                combined = _norm_nome(f"{line} {nxt}")
                if combined in targets:
                    meta = _collect_nivel_meta_after(lines, i + 1)
                    if meta:
                        meta = dict(meta)
                        meta["_nome_fonte"] = f"{line} {nxt}"
                        return meta
    return None


def parse_detalhes_mb(text: str) -> Dict[str, Dict[str, Any]]:
    """Índice por títulos imediatamente antes de cada Nível: no PDF."""
    global _LINES_CACHE
    _LINES_CACHE = None
    return build_pdf_index_from_niveis(text)


def build_detalhes_for_catalog(
    catalogo: Dict[str, Any], text: str
) -> Dict[str, Dict[str, Any]]:
    global _LINES_CACHE
    _LINES_CACHE = None
    by_title = build_pdf_index_from_titles(text)
    by_nivel = build_pdf_index_from_niveis(text)
    out: Dict[str, Dict[str, Any]] = dict(by_nivel)
    for k, v in by_title.items():
        out[k] = v
    return out


def _carregar_aliases_json() -> Tuple[Dict[str, str], Dict[str, str]]:
    if not _ALIASES_JSON.is_file():
        return {}, {}
    data = json.loads(_ALIASES_JSON.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return {}, {}

    def _map_str_dict(raw: Any) -> Dict[str, str]:
        if not isinstance(raw, dict):
            return {}
        out: Dict[str, str] = {}
        for k, v in raw.items():
            nk = _norm_nome(str(k))
            nv = _norm_nome(str(v))
            if nk and nv:
                out[nk] = nv
        return out

    return _map_str_dict(data.get("aliases")), _map_str_dict(data.get("escola_fallback"))


def _carregar_aliases() -> Dict[str, str]:
    aliases, _ = _carregar_aliases_json()
    return aliases


def _indice_detalhes(
    detalhes: Dict[str, Dict[str, Any]], aliases: Dict[str, str]
) -> Dict[str, Any]:
    idx: Dict[str, Any] = {}
    agressivo: Dict[str, List[str]] = {}

    def register(chave: str, det: Dict[str, Any]) -> None:
        if not chave or chave == "_agressivo":
            return
        if chave not in idx:
            idx[chave] = det
        ag = _norm_agressivo(chave)
        if ag:
            agressivo.setdefault(ag, []).append(chave)

    for key, det in detalhes.items():
        register(key, det)
        fonte = str(det.get("_nome_fonte") or "")
        for ch in _norm_chaves_lookup(fonte or key):
            register(ch, det)

    for alias_from, alias_to in aliases.items():
        det = idx.get(alias_to) or detalhes.get(alias_to)
        if det:
            for ch in _norm_chaves_lookup(alias_from):
                register(ch, det)

    idx["_agressivo"] = agressivo
    return idx


def _score_detalhe_match(
    det: Dict[str, Any],
    tipo_cat: Optional[str],
    circulo_cat: Optional[int],
) -> int:
    variantes = det.get("variantes_tipo")
    if not variantes or not isinstance(variantes, list):
        return 1
    tipo = str(tipo_cat or "").strip().lower()
    if not tipo:
        return 1
    circ: Optional[int]
    try:
        circ = int(circulo_cat) if circulo_cat is not None else None
    except (TypeError, ValueError):
        circ = None
    best = 0
    for v in variantes:
        if not isinstance(v, dict):
            continue
        vt = str(v.get("tipo", "")).strip().lower()
        if vt != tipo:
            continue
        try:
            vc = int(v.get("circulo"))
        except (TypeError, ValueError):
            vc = None
        if circ is not None and vc is not None:
            if vc == circ:
                best = max(best, 10)
            elif circ == 0 and vc == 1:
                best = max(best, 8)
            elif abs(vc - circ) == 1:
                best = max(best, 5)
            else:
                best = max(best, 3)
        else:
            best = max(best, 4)
    return best


def _candidatos_detalhe(
    nome: str,
    indice: Dict[str, Any],
) -> List[Dict[str, Any]]:
    seen: Set[int] = set()
    out: List[Dict[str, Any]] = []
    for ch in _norm_chaves_lookup(nome):
        det = indice.get(ch)
        if isinstance(det, dict) and id(det) not in seen:
            seen.add(id(det))
            out.append(det)
    ag = _norm_agressivo(nome)
    ag_map = indice.get("_agressivo")
    if isinstance(ag_map, dict) and ag in ag_map:
        for ck in ag_map[ag]:
            det = indice.get(ck)
            if isinstance(det, dict) and id(det) not in seen:
                seen.add(id(det))
                out.append(det)
    return out


def resolver_detalhes_catalogo(
    nome: str,
    *,
    tipo: Optional[str] = None,
    circulo: Optional[int] = None,
    indice: Dict[str, Any],
    detalhes: Dict[str, Dict[str, Any]],
) -> Optional[Dict[str, Any]]:
    candidatos = _candidatos_detalhe(nome, indice)
    if not candidatos:
        return None
    scored = [(det, _score_detalhe_match(det, tipo, circulo)) for det in candidatos]
    scored.sort(key=lambda x: (_meta_quality(x[0]), x[1]), reverse=True)
    best_det, best_score = scored[0]
    if best_score > 0 or not tipo:
        return best_det
    if best_det.get("escola"):
        return best_det
    return None


def _nome_base_em_massa(nome: str) -> Optional[str]:
    n = _norm_nome(nome)
    if " em massa" not in n:
        return None
    return n.replace(" em massa", "").strip()


def _resolver_com_fallbacks(
    nome: str,
    *,
    tipo: Optional[str],
    circulo: Optional[int],
    indice: Dict[str, Any],
    detalhes: Dict[str, Dict[str, Any]],
    aliases: Dict[str, str],
    pdf_text: Optional[str],
) -> Optional[Dict[str, Any]]:
    for try_nome in _lookup_nomes(nome, aliases):
        det = resolver_detalhes_catalogo(
            try_nome,
            tipo=tipo,
            circulo=circulo,
            indice=indice,
            detalhes=detalhes,
        )
        if det:
            return det
        if pdf_text:
            det = find_meta_for_catalog_name(pdf_text, try_nome)
            if det:
                return det
    base = _nome_base_em_massa(nome)
    if base:
        return _resolver_com_fallbacks(
            base,
            tipo=tipo,
            circulo=circulo,
            indice=indice,
            detalhes=detalhes,
            aliases=aliases,
            pdf_text=pdf_text,
        )
    return None


def _herdar_escola_mesmo_nome(itens: List[Any]) -> int:
    by_nome: Dict[str, List[Dict[str, Any]]] = {}
    for row in itens:
        if not isinstance(row, dict):
            continue
        nome = _norm_nome(str(row.get("nome") or ""))
        if nome:
            by_nome.setdefault(nome, []).append(row)
    enriched = 0
    for rows in by_nome.values():
        escola = next((r.get("escola") for r in rows if r.get("escola")), None)
        if not escola:
            continue
        for row in rows:
            if not row.get("escola"):
                row["escola"] = escola
                enriched += 1
    return enriched


def _aplicar_escola_fallback(
    row: Dict[str, Any],
    escola_fallback: Dict[str, str],
) -> bool:
    if row.get("escola"):
        return False
    nome_key = _norm_nome(str(row.get("nome") or ""))
    escola = escola_fallback.get(nome_key)
    if not escola:
        base = _nome_base_em_massa(str(row.get("nome") or ""))
        if base:
            escola = escola_fallback.get(base)
    if not escola:
        return False
    row["escola"] = escola
    return True


def merge_catalogo(
    catalogo: Dict[str, Any],
    detalhes: Dict[str, Dict[str, Any]],
    *,
    aliases: Optional[Dict[str, str]] = None,
    escola_fallback: Optional[Dict[str, str]] = None,
    pdf_text: Optional[str] = None,
) -> Tuple[int, int, int]:
    itens = catalogo.get("itens") or []
    if aliases is None or escola_fallback is None:
        loaded_aliases, loaded_fallback = _carregar_aliases_json()
        aliases = aliases or loaded_aliases
        escola_fallback = escola_fallback or loaded_fallback
    indice = _indice_detalhes(detalhes, aliases)
    matched = 0
    enriched = 0
    stubs = 0
    for row in itens:
        if not isinstance(row, dict):
            continue
        nome = str(row.get("nome") or "")
        slug = str(row.get("slug") or "")
        if nome.startswith("[Stub]") or slug.startswith("stub_"):
            stubs += 1
            if not row.get("escola"):
                row["escola"] = "Geral"
                enriched += 1
            matched += 1
            continue
        tipo = str(row.get("tipo") or "").strip().lower() or None
        circulo = row.get("circulo")
        det = _resolver_com_fallbacks(
            nome,
            tipo=tipo,
            circulo=circulo,
            indice=indice,
            detalhes=detalhes,
            aliases=aliases,
            pdf_text=pdf_text,
        )
        if det:
            matched += 1
            for k, v in det.items():
                if k.startswith("_") or k == "variantes_tipo":
                    continue
                if not v:
                    continue
                if k == "escola" or not row.get(k):
                    if row.get(k) != v:
                        enriched += 1
                    row[k] = v
            if det.get("_nome_fonte"):
                row["pagina_referencia"] = row.get("pagina_referencia") or "MB 150–209"
        if _aplicar_escola_fallback(row, escola_fallback):
            enriched += 1
            if not det:
                matched += 1
    enriched += _herdar_escola_mesmo_nome(itens)
    return matched, enriched, stubs


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    det_path = None
    if "--detalhes" in sys.argv:
        i = sys.argv.index("--detalhes")
        if i + 1 < len(sys.argv):
            det_path = Path(sys.argv[i + 1])
    if not det_path or len(args) < 1:
        print(__doc__, file=sys.stderr)
        sys.exit(1)
    dst = Path(args[-1])
    if not det_path.is_file():
        print(f"AVISO: ficheiro de detalhes não encontrado: {det_path}", file=sys.stderr)
        sys.exit(0)
    if not dst.is_file():
        print(f"ERRO: catálogo não encontrado: {dst}", file=sys.stderr)
        sys.exit(2)
    raw_text = det_path.read_text(encoding="utf-8", errors="replace")
    catalogo = json.loads(dst.read_text(encoding="utf-8"))
    detalhes = build_detalhes_for_catalog(catalogo, raw_text)
    matched, enriched, stubs = merge_catalogo(
        catalogo, detalhes, pdf_text=raw_text
    )
    itens = catalogo.get("itens") or []
    com_escola = sum(
        1 for row in itens if isinstance(row, dict) and row.get("escola")
    )
    meta = catalogo.setdefault("meta", {})
    if isinstance(meta, dict):
        meta["enriquecimento_detalhes"] = str(det_path.name)
        real = max(1, len(itens) - stubs)
        cobertura = com_escola / len(itens)
        meta["g5_escola_cobertura"] = round(cobertura, 4)
        if com_escola >= real:
            meta["g5_estado"] = "enriquecimento_completo"
        else:
            meta["g5_estado"] = "enriquecimento_detalhes"
    dst.write_text(json.dumps(catalogo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        f"OK: {len(detalhes)} nomes únicos no PDF; {matched}/{len(itens)} casadas "
        f"({stubs} stubs); escola {com_escola}/{len(itens)}; "
        f"{enriched} campos preenchidos → {dst}"
    )


if __name__ == "__main__":
    main()
