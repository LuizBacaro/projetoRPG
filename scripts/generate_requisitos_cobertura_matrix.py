#!/usr/bin/env python3
"""
Gera docs/requisitos-cobertura-matrix.md a partir de .cursor/requisitos/*.md
e heurísticas de rotas API + testes no repositório.

Uso: python3 scripts/generate_requisitos_cobertura_matrix.py
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
REQ_ROOT = REPO / ".cursor" / "requisitos"
OUT = REPO / "docs" / "requisitos-cobertura-matrix.md"
BACKEND = REPO / "backend"
FRONTEND_GAMES = REPO / "frontend" / "games"

GAME_SLUGS = ("dnd35", "dnd5e", "tormenta", "gurps")


def _read_title(md_path: Path) -> str:
    text = md_path.read_text(encoding="utf-8", errors="replace")
    for line in text.splitlines()[:8]:
        if line.startswith("# "):
            return line[2:].strip()
    return md_path.stem


def _tokens_from_stem(stem: str) -> list[str]:
    base = re.sub(r"^\d+-", "", stem)
    base = base.replace("-dnd35", "").replace("-dnd5e", "").replace("-tormenta", "").replace("-gurps", "")
    parts = re.split(r"[-_]", base)
    return [p for p in parts if len(p) > 2]


def _grep_files(root: Path, pattern: str, glob: str) -> int:
    if not root.is_dir():
        return 0
    count = 0
    rx = re.compile(pattern, re.I)
    for path in root.rglob(glob):
        if "node_modules" in path.parts:
            continue
        try:
            if rx.search(path.read_text(encoding="utf-8", errors="replace")):
                count += 1
        except OSError:
            pass
    return count


def _api_router_files(slug: str) -> list[Path]:
    api_dir = BACKEND / "app" / "games" / slug / "api"
    if not api_dir.is_dir():
        return []
    return sorted(api_dir.rglob("*.py"))


def _score_requisito(slug: str, stem: str) -> tuple[str, str, str]:
    tokens = _tokens_from_stem(stem)
    if not tokens:
        tokens = [stem[:12]]

    api_hits = 0
    for f in _api_router_files(slug):
        blob = f.read_text(encoding="utf-8", errors="replace").lower()
        if any(t in blob or t in f.name.lower() for t in tokens):
            api_hits += 1

    test_dir = BACKEND / "tests"
    test_hits = 0
    for t in tokens:
        test_hits += _grep_files(test_dir, rf"test_.*{re.escape(t)}|{re.escape(t)}", "*.py")

    fe_dir = FRONTEND_GAMES / slug
    fe_hits = 0
    for t in tokens:
        fe_hits += _grep_files(fe_dir, re.escape(t), "*.js")
        fe_hits += _grep_files(fe_dir, re.escape(t), "*.html")

    def band(n: int) -> str:
        if n >= 2:
            return "alto"
        if n == 1:
            return "parcial"
        return "baixo"

    api_b = band(api_hits)
    test_b = band(test_hits)
    fe_b = band(fe_hits)

    if api_b == "alto" and (test_b != "baixo" or fe_b != "baixo"):
        overall = "implementado"
    elif api_b != "baixo" or fe_b != "baixo":
        overall = "parcial"
    else:
        overall = "backlog"

    detail = f"API:{api_hits} · testes:{test_hits} · FE:{fe_hits}"
    return overall, detail, api_b


def main() -> None:
    lines = [
        "# Matriz de cobertura — requisitos × código",
        "",
        f"*Gerado em {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} por "
        "`scripts/generate_requisitos_cobertura_matrix.py`.*",
        "",
        "Legenda heurística (não substitui revisão humana):",
        "",
        "| Sinal | Significado |",
        "|-------|-------------|",
        "| **implementado** | API + (testes ou frontend) com traços no código |",
        "| **parcial** | Alguma camada presente |",
        "| **backlog** | Pouco ou nenhum traço automático |",
        "",
    ]

    for slug in GAME_SLUGS:
        game_dir = REQ_ROOT / slug
        if not game_dir.is_dir():
            continue
        md_files = sorted(game_dir.glob("*.md"))
        md_files = [f for f in md_files if f.name.upper() != "README.MD"]

        lines.append(f"## {slug}")
        lines.append("")
        lines.append("| Requisito | Título | Cobertura | Detalhe |")
        lines.append("|-----------|--------|-----------|---------|")

        for md in md_files:
            stem = md.stem
            title = _read_title(md)
            overall, detail, _api = _score_requisito(slug, stem)
            lines.append(f"| `{stem}` | {title[:60]} | **{overall}** | {detail} |")

        lines.append("")

    lines.append("## Como atualizar")
    lines.append("")
    lines.append("```bash")
    lines.append("python3 scripts/generate_requisitos_cobertura_matrix.py")
    lines.append("```")
    lines.append("")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Escrito: {OUT}")


if __name__ == "__main__":
    main()
