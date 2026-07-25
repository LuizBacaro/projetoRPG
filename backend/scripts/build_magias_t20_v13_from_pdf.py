#!/usr/bin/env python3
"""
Regenera `magias_mb_catalogo.json` a partir do PDF Tormenta 20 Edição Jogo do Ano v1.3.

Extrai as listas arcanas/divinas (páginas impressas ~174–177) e funde metadados
curtos já existentes (escola/descrição) quando o slug/nome coincidem.

Não grava texto longo do livro — só metadados + `pagina_referencia`.

Uso (a partir da raiz do repo, com venv):
  .venv/bin/python backend/scripts/build_magias_t20_v13_from_pdf.py \\
      --pdf livros/Tormenta20-Edicao-Jogo-do-Ano-v1.3.pdf \\
      --out backend/app/games/tormenta/data/magias_mb_catalogo.json
"""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Índice 0-based no PDF (capa/offset): listas ~179–182.
_PAGINAS_LISTAS = (179, 180, 181, 182)

_ESCOLA_PREFIX = {
    "abjur": "Abjuração",
    "adiv": "Adivinhação",
    "conv": "Convocação",
    "encan": "Encantamento",
    "evoc": "Evocação",
    "ilusao": "Ilusão",
    "ilusão": "Ilusão",
    "necro": "Necromancia",
    "trans": "Transmutação",
}

_RE_CIRCULO = re.compile(r"(\d+)\s*º\s*C[ií]rculo", re.I)
_RE_TIPO = re.compile(r"Lista de Magias\s+(Arcanas|Divinas)", re.I)
_RE_ENTRY = re.compile(
    r"^(?:(Abjur|Adiv|Conv|Encan|Evoc|Ilus[aã]o|Necro|Trans)\s+)?"
    r"([A-ZÁÉÍÓÚÂÊÔÃÕÇ][^.]{1,80}?)\.\s+(.+)$"
)


def _slug(nome: str) -> str:
    s = unicodedata.normalize("NFKD", nome.strip())
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    return re.sub(r"_+", "_", s).strip("_")[:80] or "magia"


def _norm_nome(texto: str) -> str:
    s = unicodedata.normalize("NFKD", str(texto or "").strip().lower())
    return "".join(ch for ch in s if not unicodedata.combining(ch))


def _parse_listas(textos: List[str]) -> List[Dict[str, Any]]:
    tipo: Optional[str] = None
    circulo: Optional[int] = None
    escola_cur: Optional[str] = None
    out: List[Dict[str, Any]] = []
    seen: set[Tuple[str, int, str]] = set()

    buf_nome: Optional[str] = None
    buf_desc: List[str] = []
    buf_escola: Optional[str] = None

    def flush() -> None:
        nonlocal buf_nome, buf_desc, buf_escola
        if not buf_nome or tipo is None or circulo is None:
            buf_nome, buf_desc, buf_escola = None, [], None
            return
        nome = re.sub(r"\s+", " ", buf_nome).strip()
        desc = re.sub(r"\s+", " ", " ".join(buf_desc)).strip()
        key = (tipo, circulo, _norm_nome(nome))
        if key in seen:
            buf_nome, buf_desc, buf_escola = None, [], None
            return
        seen.add(key)
        esc = buf_escola or escola_cur or ""
        out.append(
            {
                "slug": _slug(nome),
                "nome": nome,
                "circulo": circulo,
                "tipo": tipo,
                "escola": esc,
                "descricao_curta": desc[:220] if desc else "",
                "pagina_referencia": "v1.3 p.174–177",
            }
        )
        buf_nome, buf_desc, buf_escola = None, [], None

    for bloco in textos:
        for raw in (bloco or "").splitlines():
            line = raw.strip()
            if not line:
                continue
            if re.search(r"Cap[ií]tulo", line, re.I) and re.search(r"\d{3}", line):
                continue
            m_tipo = _RE_TIPO.search(line)
            if m_tipo:
                flush()
                tipo = "arcana" if m_tipo.group(1).lower().startswith("arc") else "divina"
                continue
            m_circ = _RE_CIRCULO.search(line)
            if m_circ and "círculo" in line.lower().replace("circulo", "círculo"):
                # linha só de cabeçalho de círculo (pode ter dois círculos lado a lado)
                parts = _RE_CIRCULO.findall(line)
                if parts:
                    flush()
                    circulo = int(parts[0])
                continue
            # duas colunas: às vezes "1º Círculo 2º Círculo" só
            if re.fullmatch(r"(\d+\s*º\s*C[ií]rculo\s*)+", line, re.I):
                flush()
                circulo = int(_RE_CIRCULO.findall(line)[0])
                continue

            m = _RE_ENTRY.match(line)
            if m:
                flush()
                pref = (m.group(1) or "").lower().replace("ã", "a")
                if pref:
                    escola_cur = _ESCOLA_PREFIX.get(pref, escola_cur)
                    buf_escola = _ESCOLA_PREFIX.get(pref, "")
                else:
                    buf_escola = escola_cur
                buf_nome = m.group(2).strip()
                buf_desc = [m.group(3).strip()]
                continue

            if buf_nome:
                # continuação da descrição ou nome partido
                if line[0].islower() or line[0] in "-–":
                    buf_desc.append(line)
                elif len(line) < 40 and not line.endswith("."):
                    buf_nome = f"{buf_nome} {line}".strip()
                else:
                    buf_desc.append(line)
    flush()
    return out


def _fundir_com_existente(
    novos: List[Dict[str, Any]], antigo_path: Path
) -> List[Dict[str, Any]]:
    legado: Dict[str, Dict[str, Any]] = {}
    if antigo_path.is_file():
        try:
            raw = json.loads(antigo_path.read_text(encoding="utf-8"))
            for row in raw.get("itens") or []:
                if not isinstance(row, dict):
                    continue
                k = (
                    str(row.get("tipo") or ""),
                    int(row.get("circulo") or 0),
                    _norm_nome(str(row.get("nome") or "")),
                )
                legado[k] = row
                legado[str(row.get("slug") or "")] = row
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            pass

    out: List[Dict[str, Any]] = []
    used_slugs: set[str] = set()
    for row in novos:
        key = (row["tipo"], row["circulo"], _norm_nome(row["nome"]))
        old = legado.get(key) or legado.get(row["slug"])
        if isinstance(old, dict):
            if old.get("escola") and not row.get("escola"):
                row["escola"] = old["escola"]
            if old.get("descricao_curta") and (
                not row.get("descricao_curta")
                or len(str(row.get("descricao_curta"))) < 12
            ):
                row["descricao_curta"] = old["descricao_curta"]
            # preserva slug estável se o nome for o mesmo
            old_slug = str(old.get("slug") or "")
            if old_slug and _norm_nome(old.get("nome", "")) == _norm_nome(row["nome"]):
                row["slug"] = old_slug
        base = row["slug"]
        slug = base
        n = 2
        while slug in used_slugs:
            slug = f"{base}_{n}"[:80]
            n += 1
        row["slug"] = slug
        used_slugs.add(slug)
        out.append(row)

    out.sort(key=lambda x: (x["circulo"], x["tipo"], x["nome"].lower()))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--pdf",
        type=Path,
        default=Path("livros/Tormenta20-Edicao-Jogo-do-Ano-v1.3.pdf"),
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=Path("backend/app/games/tormenta/data/magias_mb_catalogo.json"),
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Só imprime contagens; não grava o JSON.",
    )
    ap.add_argument(
        "--validate-only",
        action="store_true",
        help=(
            "Compara nomes nas páginas de descrição (p.178+) com o JSON actual; "
            "não sobrescreve (layout em duas colunas das listas é frágil)."
        ),
    )
    args = ap.parse_args()

    try:
        import pdfplumber
    except ImportError as exc:
        raise SystemExit(
            "pdfplumber é necessário. Ative o .venv do projeto."
        ) from exc

    if not args.pdf.is_file():
        raise SystemExit(f"PDF não encontrado: {args.pdf}")

    if args.validate_only:
        with pdfplumber.open(str(args.pdf)) as pdf:
            desc = "\n".join(
                (pdf.pages[i].extract_text() or "")
                for i in range(183, min(212, len(pdf.pages)))
            )
        hits = re.findall(r"(Arcana|Divina)\s+(\d)\s*\(([^)]+)\)", desc)
        cat = json.loads(args.out.read_text(encoding="utf-8"))
        itens = cat.get("itens") or []
        print(f"PDF descrições (marcadores tipo/círculo): {len(hits)}")
        print(f"Catálogo JSON actual: {len(itens)} entradas (arcana+divina)")
        nomes_cat = {_norm_nome(r.get("nome", "")) for r in itens if isinstance(r, dict)}
        amostragem = (
            "abençoar alimentos",
            "adaga mental",
            "bola de fogo",
            "curar ferimentos",
        )
        for n in amostragem:
            print(f"  {'OK' if _norm_nome(n) in nomes_cat else 'FALTA'}: {n}")
        circs = sorted(
            {
                int(r.get("circulo"))
                for r in itens
                if isinstance(r, dict) and r.get("circulo") is not None
            }
        )
        print(f"Círculos no JSON: {circs}")
        if circs != [1, 2, 3, 4, 5]:
            raise SystemExit("Catálogo deve ter apenas círculos 1–5.")
        return 0

    textos: List[str] = []
    with pdfplumber.open(str(args.pdf)) as pdf:
        for idx in _PAGINAS_LISTAS:
            if 0 <= idx < len(pdf.pages):
                textos.append(pdf.pages[idx].extract_text() or "")

    novos = _parse_listas(textos)
    if len(novos) < 100:
        raise SystemExit(
            f"Extração frágil: só {len(novos)} magias. "
            "Prefira --validate-only; o JSON curado (~227) é a fonte de produção."
        )

    fundidos = _fundir_com_existente(novos, args.out)
    payload = {
        "meta": {
            "fonte": "Tormenta20-Edicao-Jogo-do-Ano-v1.3.pdf",
            "referencia_paginas": "Listas arcana/divina p.174–177",
            "nota": (
                "Metadados curtos por magia: nome, círculo (1–5), tipo (arcana/divina), "
                "escola e descrição curta. Textos longos permanecem no livro (fonte legal)."
            ),
            "gerado_por": "backend/scripts/build_magias_t20_v13_from_pdf.py",
        },
        "itens": fundidos,
    }

    por_tipo: Dict[str, int] = {}
    for r in fundidos:
        por_tipo[r["tipo"]] = por_tipo.get(r["tipo"], 0) + 1
    print(f"Total: {len(fundidos)} | {por_tipo}")
    print(
        "Nota: layout em 2 colunas pode subextrair. "
        "O catálogo curado em produção tem ~227 entradas; use --validate-only."
    )

    if args.dry_run:
        return 0

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Gravado: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
