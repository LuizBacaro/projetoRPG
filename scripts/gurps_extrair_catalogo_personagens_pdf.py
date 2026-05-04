#!/usr/bin/env python3
"""
Extrai listas mecânicas (nome + custo ou nome + atributo/dificuldade) do PDF
``GURPS 4E - Módulo Básico - Personagens.pdf`` (Devir) para o catálogo da ficha.

As páginas citadas na “Ficha Aprimorada” costumam espelhar o **mesmo sumário**
deste livro (ex.: cap. Vantagens a partir da p. 32 impressa, Desvantagens ~119,
Perícias ~167). O arquivo ``GURPS 4E - Ficha de Personagem (Aprimorada 1).pdf``
no repositório tem só 3 páginas (formulário); use sempre o **Módulo Personagens**
para extração.

Faixas físicas do PDF (``pdftotext -f/-l``), calibradas na edição em PT-BR:
vantagens 40–117, desvantagens 122–161, perícias 175–228.

Heurística sobre texto nativo (colunas duplas). Depois rode a curadoria:

  python3 scripts/gurps_extrair_catalogo_personagens_pdf.py
  python3 scripts/curar_gurps_personagens_sumario_catalogo.py

Saída: backend/app/games/gurps/catalogs/gurps_personagens_sumario_catalogo.json
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "GURPS 4E - Módulo Básico - Personagens.pdf"
OUT = (
    ROOT
    / "backend"
    / "app"
    / "games"
    / "gurps"
    / "catalogs"
    / "gurps_personagens_sumario_catalogo.json"
)

# Páginas físicas do PDF (ajuste se sua impressão diferir).
PG_VANTAGENS = (40, 117)
PG_DESVANTAGENS = (122, 161)
PG_PERICIAS = (175, 228)

COST_ADV = re.compile(
    r"^("
    r"\d+\s+pontos(?:/nível)?(?:\s*\+\s*[^.\n]{1,40})?|"
    r"\d+\s+pontos/apetrecho|"
    r"\d+\s+ou\s+\d+\s+pontos|"
    r"Variável|variável|"
    r"0\s+ou\s+\d+|"
    r"\d+\s+ou\s+\d+"
    r")",
    re.I,
)
COST_DIS = re.compile(
    r"^("
    r"[–-]\s*\d+\s+pontos(?:/nível)?|"
    r"[–-]\s*Variável|[–-]\s*variável|"
    r"-Variável|-variável|"
    r"Variável|variável"
    r")",
    re.I,
)

SKILL_LINE = re.compile(
    r"^(DX|IQ|HT|ST|Vontade|VONTADE|Per|PER|Will|WILL)\s*/\s*"
    r"(Fácil|Média|Difícil|Muito\s*Difícil|F|M|D|MF|MD|Dif)",
    re.I,
)

SENTENCE_START = re.compile(
    r"^(O|A|Os|As|Um|Uma|Para|Quando|Se|É|E\s|No|Na|Nos|Nas|De|Do|Da|Dos|Das|"
    r"Com|Por|Exemplo|Observe|Algumas|Alguns|Esta|Este|Isto|Assim|Depois|"
    r"Não|Nem|Só|Todos|Todas|Cada|Qualquer|Independente|Nenhum|Nenhuma)\b",
    re.I,
)

SKIP_HEADERS = {
    "Limitações Especiais",
    "Ampliações Especiais",
    "Modificadores",
    "Exemplos de Contatos",
    "Vantagens",
    "Desvantagens",
    "Perícias",
}


def pdf_text(p0: int, p1: int) -> str:
    if not PDF.is_file():
        raise FileNotFoundError(PDF)
    # Sem -layout: colunas duplas ainda aparecem como dois nomes seguidos;
    # o parser abaixo trata “nome + próximo nome” (custo vem depois do 2º).
    r = subprocess.run(
        ["pdftotext", "-f", str(p0), "-l", str(p1), str(PDF), "-"],
        capture_output=True,
        text=True,
        check=True,
    )
    return r.stdout


def is_probably_name(line: str) -> bool:
    s = line.strip()
    if len(s) < 2 or len(s) > 56:
        return False
    if s[0].islower() or s[0].isdigit() or s[0] in "–-—":
        return False
    if s in SKIP_HEADERS:
        return False
    if s.endswith("."):
        return False
    if SENTENCE_START.match(s):
        return False
    if re.search(r"[%•#®]|\bMestre\b|\bquota\b|pontos da", s, re.I):
        return False
    if re.search(r"\d\s*dados|pág\.|página|consulte|teste de", s, re.I):
        return False
    if re.match(r"^[\d\s$/+.\-–—]+$", s):
        return False
    if re.match(r"^\d+\s+pontos", s, re.I):
        return False
    return True


def _linha_custo_limpa(s: str) -> bool:
    if len(s) > 52:
        return False
    if re.search(r"\bpor\b", s.lower()):
        return False
    return True


def _next_nonempty(lines: list[str], start: int) -> int:
    j = start
    while j < len(lines) and not lines[j].strip():
        j += 1
    return j


def parse_vantagens(text: str) -> list[dict]:
    """Só emite pares (nome, custo) válidos; trata coluna dupla (nome1, nome2, custo)."""
    lines = [l.strip() for l in text.splitlines()]
    out: list[dict] = []
    i = 0
    n = len(lines)
    while i < n:
        i = _next_nonempty(lines, i)
        if i >= n:
            break
        a = lines[i]
        if not is_probably_name(a):
            i += 1
            continue
        j = _next_nonempty(lines, i + 1)
        if j >= n:
            break
        b = lines[j]
        if COST_ADV.match(b) and _linha_custo_limpa(b):
            out.append({"nome": a, "custo_texto": b})
            i = j + 1
            continue
        if is_probably_name(b):
            k = _next_nonempty(lines, j + 1)
            if k < n and COST_ADV.match(lines[k]) and _linha_custo_limpa(lines[k]):
                out.append({"nome": b, "custo_texto": lines[k]})
                i = k + 1
            else:
                i = j
            continue
        i += 1
    return out


def parse_desvantagens(text: str) -> list[dict]:
    lines = [l.strip() for l in text.splitlines()]
    out: list[dict] = []
    i = 0
    n = len(lines)
    while i < n:
        i = _next_nonempty(lines, i)
        if i >= n:
            break
        a = lines[i]
        if not is_probably_name(a):
            i += 1
            continue
        j = _next_nonempty(lines, i + 1)
        if j >= n:
            break
        b = lines[j]
        if COST_DIS.match(b) and _linha_custo_limpa(b):
            out.append({"nome": a, "custo_texto": b})
            i = j + 1
            continue
        if is_probably_name(b):
            k = _next_nonempty(lines, j + 1)
            if k < n and COST_DIS.match(lines[k]) and _linha_custo_limpa(lines[k]):
                out.append({"nome": b, "custo_texto": lines[k]})
                i = k + 1
            else:
                i = j
            continue
        i += 1
    return out


def _norm_dif(s: str) -> str:
    t = s.strip().lower()
    if "muito" in t:
        return "VD"
    if t.startswith("d") or t == "dif":
        return "D"
    if t.startswith("m") or t == "média" or t == "media":
        return "M"
    if t.startswith("f"):
        return "F"
    return "M"


def _norm_attr(s: str) -> str:
    t = s.strip().upper()
    if t.startswith("DX"):
        return "dx"
    if t.startswith("IQ"):
        return "iq"
    if t.startswith("HT"):
        return "ht"
    if t.startswith("ST"):
        return "st"
    if "VONT" in t or t.startswith("WILL"):
        return "iq"
    if t.startswith("PER"):
        return "iq"
    return "dx"


def parse_pericias(text: str) -> list[dict]:
    lines = [l.strip() for l in text.splitlines()]
    out: list[dict] = []
    i = 0
    n = len(lines)
    while i < n:
        i = _next_nonempty(lines, i)
        if i >= n:
            break
        a = lines[i]
        if not is_probably_name(a):
            i += 1
            continue
        j = _next_nonempty(lines, i + 1)
        if j >= n:
            break
        b = lines[j]
        if not SKILL_LINE.match(b):
            i += 1
            continue
        m = SKILL_LINE.match(b)
        raw_attr = m.group(1)
        raw_dif = m.group(2)
        out.append(
            {
                "nome": a,
                "atributo_base": _norm_attr(raw_attr),
                "dificuldade": _norm_dif(raw_dif),
                "tipo_linha": f"{_norm_attr(raw_attr).upper()}/{_norm_dif(raw_dif)}",
                "nt": "/nt" in a.lower() or " (nt)" in a.lower(),
            }
        )
        i = j + 1
    return out


def limpar_nome_exibicao(s: str) -> str:
    t = (s or "").strip()
    t = re.sub(r"\s*[\d\*•®/\?¥]+\s*$", "", t)
    t = re.sub(r"\s+(V\?|SPf)\s*$", "", t, flags=re.I)
    return t.strip(" -–/")


def dedupe_key(items: list[dict], key: str = "nome") -> list[dict]:
    seen: set[str] = set()
    out = []
    for it in items:
        if "nome" in it:
            it["nome"] = limpar_nome_exibicao(it["nome"])
        k = (it.get(key) or "").strip()
        if not k or len(k) < 2 or k in seen:
            continue
        if re.search(r"[a-záé]{20,}", k):
            continue
        seen.add(k)
        out.append(it)
    return out


def main() -> None:
    tv = pdf_text(*PG_VANTAGENS)
    td = pdf_text(*PG_DESVANTAGENS)
    tp = pdf_text(*PG_PERICIAS)

    vantagens = dedupe_key(parse_vantagens(tv))
    desvantagens = dedupe_key(parse_desvantagens(td))
    pericias = dedupe_key(parse_pericias(tp))

    payload = {
        "meta": {
            "fonte_pdf": str(PDF.name),
            "paginas_vantagens": list(PG_VANTAGENS),
            "paginas_desvantagens": list(PG_DESVANTAGENS),
            "paginas_pericias": list(PG_PERICIAS),
            "nota": "Extração heurística via pdftotext; revisar nomes duplicados ou ruído.",
        },
        "vantagens": vantagens,
        "desvantagens": desvantagens,
        "pericias": pericias,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        f"Escrito {OUT.relative_to(ROOT)} — "
        f"{len(vantagens)} vantagens, {len(desvantagens)} desvantagens, {len(pericias)} perícias"
    )


if __name__ == "__main__":
    main()
