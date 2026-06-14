#!/usr/bin/env python3
"""
Monta `magias_mb_catalogo.json` a partir do texto extraído do MB (pp. 307–317),
geralmente via:

  pdftotext -f 307 -l 317 tormenta-rpg-modulo-basico.pdf listagem_magias_mb_pp307-317.txt

Metadados estruturados (escola, execução, etc.) podem ser fundidos depois com
`enrich_magias_mb_catalogo.py` a partir de pp.150–209 (PDF licenciado).

Uso:
  python3 backend/scripts/build_magias_mb_catalogo_from_listagem_txt.py \\
      backend/app/games/tormenta/data/sources/listagem_magias_mb_pp307-317.txt \\
      backend/app/games/tormenta/data/magias_mb_catalogo.json
"""

from __future__ import annotations

import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def _slug_base(nome: str) -> str:
    s = unicodedata.normalize("NFKD", nome.strip())
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s[:80] or "magia"


def _unique_slug(base: str, used: set[str]) -> str:
    b = base[:70]
    if b not in used:
        used.add(b)
        return b
    n = 2
    while True:
        cand = f"{b}_{n}"[:80]
        if cand not in used:
            used.add(cand)
            return cand
        n += 1


_RE_NIVEL0 = re.compile(r"^\s*Nível\s*0\s*$", re.I)
_RE_MAGIAS_NIVEL0 = re.compile(r"^\s*Magias\s+de\s+n[ií]vel\s+0\s*$", re.I)
_RE_MAGIAS_NIVEL = re.compile(
    r"^\s*Magias\s+de\s+(\d+)\s*(?:º|o)\s*n[ií]vel\s*$",
    re.I,
)
_RE_SKIP_LINE = re.compile(
    r"^\s*(Magias arcanas|Magias divinas|Lista de magias|A seguir estão)\b",
    re.I,
)


def _parse_level_line(line: str) -> Optional[int]:
    t = line.strip()
    if _RE_NIVEL0.match(t) or _RE_MAGIAS_NIVEL0.match(t):
        return 0
    m = _RE_MAGIAS_NIVEL.match(t)
    if m:
        try:
            return int(m.group(1))
        except ValueError:
            return None
    return None


def _is_spell_start(line: str) -> Optional[Tuple[str, str]]:
    """Retorna (nome, resto) se a linha inicia uma entrada Nome: descrição…"""
    t = line.strip().lstrip("\f").strip()
    if not t:
        return None
    if _RE_SKIP_LINE.match(t):
        return None
    if _parse_level_line(line) is not None:
        return None
    if ":" not in t:
        return None
    nome, _, rest = t.partition(":")
    nome = nome.strip()
    rest = rest.strip()
    if len(nome) < 2 or len(nome) > 120:
        return None
    if nome.lower().startswith("magias "):
        return None
    if nome.lower().startswith("nível ") or nome.lower().startswith("nivel "):
        return None
    # Evita linhas de rodapé só com número
    if nome.isdigit():
        return None
    return nome, rest


def _alloc_slug(nome: str, tipo: str, used: set[str]) -> str:
    base = _slug_base(nome)
    if base not in used:
        used.add(base)
        return base
    suf = "arc" if tipo == "arcana" else "div"
    cand = f"{base}_{suf}"[:80]
    if cand not in used:
        used.add(cand)
        return cand
    return _unique_slug(f"{base}_{suf}", used)


def parse_listagem(text: str) -> List[Dict[str, Any]]:
    lines = text.replace("\r\n", "\n").split("\n")
    modo: Optional[str] = None  # "arcana" | "divina"
    circulo = 0
    itens: List[Dict[str, Any]] = []
    cur_nome: Optional[str] = None
    cur_desc: List[str] = []
    cur_circ: int = 0
    cur_tipo: str = "arcana"

    used_slugs: set[str] = set()

    def flush() -> None:
        nonlocal cur_nome, cur_desc, cur_circ, cur_tipo
        if not cur_nome:
            return
        desc = " ".join(x.strip() for x in cur_desc if x.strip()).strip()
        if len(desc) > 500:
            desc = desc[:497] + "…"
        base = _slug_base(cur_nome)
        slug = _alloc_slug(cur_nome.strip(), cur_tipo, used_slugs)
        itens.append(
            {
                "slug": slug,
                "nome": cur_nome.strip(),
                "circulo": int(cur_circ),
                "tipo": cur_tipo,
                "descricao_curta": desc or None,
                "pagina_referencia": "MB 307–317",
            }
        )
        cur_nome = None
        cur_desc = []

    for raw in lines:
        line = raw.rstrip()
        ln = line.lstrip("\f").strip()
        if ln.startswith("Magias arcanas"):
            flush()
            modo = "arcana"
            continue
        if ln.startswith("Magias divinas"):
            flush()
            modo = "divina"
            continue
        if modo is None:
            continue

        nv = _parse_level_line(line)
        if nv is not None:
            flush()
            circulo = nv
            continue

        sp = _is_spell_start(line)
        if sp:
            flush()
            cur_nome, first = sp
            cur_circ = circulo
            cur_tipo = modo
            cur_desc = [first] if first else []
            continue

        if cur_nome:
            t = line.strip()
            if not t or re.match(r"^\d+$", t):
                continue
            if t.startswith("\f"):
                t = t.lstrip("\f").strip()
            if t:
                cur_desc.append(t)

    flush()
    return itens


def load_stubs(path: Path) -> List[Dict[str, Any]]:
    if not path.is_file():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    stubs = []
    for r in data.get("itens") or []:
        if str(r.get("slug", "")).startswith("stub_"):
            stubs.append(dict(r))
    return stubs


def main() -> None:
    if len(sys.argv) < 3:
        print(__doc__, file=sys.stderr)
        sys.exit(1)
    src = Path(sys.argv[1])
    dst = Path(sys.argv[2])
    text = src.read_text(encoding="utf-8", errors="replace")
    parsed = parse_listagem(text)
    stubs = load_stubs(dst)
    stub_slugs = {s["slug"] for s in stubs}
    merged = [r for r in parsed if r.get("slug") not in stub_slugs] + stubs
    merged.sort(key=lambda x: (str(x.get("tipo", "")), int(x.get("circulo", 0)), str(x.get("nome", "")).lower()))
    out = {
        "meta": {
            "nota": "Listagem MB pp.307–317 (nomes + resumo do efeito). Entradas [Stub] preservam testes de API. Re gere com build_magias_mb_catalogo_from_listagem_txt.py.",
            "fonte_listagem": str(src.name),
        },
        "itens": merged,
    }
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"OK: {len(parsed)} magias parseadas + {len(stubs)} stubs → {len(merged)} itens em {dst}")


if __name__ == "__main__":
    main()
