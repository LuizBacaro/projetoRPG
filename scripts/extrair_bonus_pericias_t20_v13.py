#!/usr/bin/env python3
"""Extrai bônus/penalidades de perícias do Tormenta20 v1.3 (Cap. 2/3/8 + raças/origens).

Uso local (PDF em ``livros/``, não versionado):

  python3 scripts/extrair_bonus_pericias_t20_v13.py \\
    --pdf livros/Tormenta20-Edicao-Jogo-do-Ano-v1.3.pdf \\
    --out backend/app/games/tormenta/data/bonus_pericias_fontes_v13.json

Gera catálogo mecânico + remissão de página; revisão humana antes de auto-aplicar.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import unicodedata
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Neste PDF: índice 1-based ≈ página impressa + 6
PDF_OFFSET = 6

# (fonte_tipo, pdf_ini, pdf_fim) — páginas PDF inclusivas
FAIXAS = [
    ("raca", 24, 39),
    ("classe_poder", 48, 90),
    ("origem", 91, 111),
    ("poder_geral", 128, 145),
    ("equipamento", 146, 175),
    ("item_magico", 330, 358),
]

PERICIAS: Dict[str, str] = {
    "acrobacia": "acrobacia",
    "adestramento": "adestramento",
    "atletismo": "atletismo",
    "atuacao": "atuacao",
    "atuação": "atuacao",
    "cavalgar": "cavalgar",
    "conhecimento": "conhecimento",
    "cura": "cura",
    "diplomacia": "diplomacia",
    "enganacao": "enganacao",
    "enganação": "enganacao",
    "fortitude": "fortitude",
    "furtividade": "furtividade",
    "guerra": "guerra",
    "iniciativa": "iniciativa",
    "intimidacao": "intimidacao",
    "intimidação": "intimidacao",
    "intuicao": "intuicao",
    "intuição": "intuicao",
    "investigacao": "investigacao",
    "investigação": "investigacao",
    "jogatina": "jogatina",
    "ladinagem": "ladinagem",
    "luta": "luta",
    "misticismo": "misticismo",
    "nobreza": "nobreza",
    "oficio": "oficio",
    "ofício": "oficio",
    "percepcao": "percepcao",
    "percepção": "percepcao",
    "pilotagem": "pilotagem",
    "pontaria": "pontaria",
    "reflexos": "reflexos",
    "religiao": "religiao",
    "religião": "religiao",
    "sobrevivencia": "sobrevivencia",
    "sobrevivência": "sobrevivencia",
    "vontade": "vontade",
}

# Padrões de uso (Cap. 2) — substring → (pericia_slug, uso_id)
USOS_HINTS: List[Tuple[str, str, str]] = [
    ("natação", "atletismo", "natacao"),
    ("natacao", "atletismo", "natacao"),
    ("nadar", "atletismo", "natacao"),
    ("escalar", "atletismo", "escalar"),
    ("saltar", "atletismo", "saltar"),
    ("corrida", "atletismo", "corrida"),
    ("disfarce", "enganacao", "disfarce"),
    ("mentir", "enganacao", "mentir"),
    ("fintar", "enganacao", "fintar"),
    ("falsificação", "enganacao", "falsificacao"),
    ("falsificacao", "enganacao", "falsificacao"),
    ("ocultar", "ladinagem", "ocultar"),
    ("ocultá", "ladinagem", "ocultar"),
    ("ocultad", "ladinagem", "ocultar"),
    ("punga", "ladinagem", "punga"),
    ("fechadura", "ladinagem", "abrir_fechadura"),
    ("sabotar", "ladinagem", "sabotar"),
    ("rastrear", "sobrevivencia", "rastrear"),
    ("observar", "percepcao", "observar"),
    ("ouvir", "percepcao", "ouvir"),
]

# Não-perícia (descartar se for o único alvo)
NAO_PERICIA = {
    "ataque",
    "ataques",
    "dano",
    "defesa",
    "ca",
    "pv",
    "pm",
    "deslocamento",
    "força",
    "forca",
    "destreza",
    "constituição",
    "constituicao",
    "inteligência",
    "inteligencia",
    "sabedoria",
    "carisma",
    "mana",
    "pontos de vida",
    "pontos de mana",
}


def slugify(nome: str) -> str:
    s = unicodedata.normalize("NFKD", nome)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-") or "fonte"


def norm_key(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s.lower().strip()


def impressa(pdf_page: int) -> int:
    return pdf_page - PDF_OFFSET


def pdftotext_range(pdf: Path, ini: int, fim: int) -> str:
    out = subprocess.check_output(
        ["pdftotext", "-layout", "-f", str(ini), "-l", str(fim), str(pdf), "-"],
        text=True,
        errors="replace",
    )
    return out


def split_pages(text: str, ini: int, fim: int) -> Dict[int, str]:
    """pdftotext junta páginas com form feed \\x0c."""
    parts = text.split("\x0c")
    pages: Dict[int, str] = {}
    for i, chunk in enumerate(parts):
        p = ini + i
        if p > fim:
            break
        if chunk.strip():
            pages[p] = chunk
    if not pages and text.strip():
        pages[ini] = text
    return pages


PERICIA_ALT = "|".join(
    sorted(
        {
            "Acrobacia",
            "Adestramento",
            "Atletismo",
            "Atuação",
            "Atuacao",
            "Cavalgar",
            "Conhecimento",
            "Cura",
            "Diplomacia",
            "Enganação",
            "Enganacao",
            "Fortitude",
            "Furtividade",
            "Guerra",
            "Iniciativa",
            "Intimidação",
            "Intimidacao",
            "Intuição",
            "Intuicao",
            "Investigação",
            "Investigacao",
            "Jogatina",
            "Ladinagem",
            "Luta",
            "Misticismo",
            "Nobreza",
            "Ofício",
            "Oficio",
            "Percepção",
            "Percepcao",
            "Pilotagem",
            "Pontaria",
            "Reflexos",
            "Religião",
            "Religiao",
            "Sobrevivência",
            "Sobrevivencia",
            "Vontade",
        },
        key=len,
        reverse=True,
    )
)

# +2 em Diplomacia | +2 em testes de Enganação para mentir
RE_BONUS = re.compile(
    rf"(?P<sinal>[+\-])\s*(?P<valor>\d+)\s*"
    rf"(?:em\s+)?(?:testes?\s+de\s+)?"
    rf"(?P<alvo>{PERICIA_ALT})"
    rf"(?:\s+para\s+(?P<contexto>[^.;\n]{{3,80}}))?",
    re.IGNORECASE,
)

RE_RECEBE = re.compile(
    rf"(?:você\s+recebe|fornece|recebe|concede)\s+"
    rf"(?P<sinal>[+\-])?\s*(?P<valor>\d+)\s*"
    rf"(?:em\s+)?(?:testes?\s+de\s+)?"
    rf"(?P<alvo>{PERICIA_ALT})"
    rf"(?:\s+para\s+(?P<contexto>[^.;\n]{{3,80}}))?",
    re.IGNORECASE,
)

RE_PENALIDADE = re.compile(
    rf"penalidade\s+de\s+(?P<sinal>[+\-])?\s*(?P<valor>\d+)\s*"
    rf"(?:em\s+)?(?:testes?\s+de\s+)?"
    rf"(?P<alvo>{PERICIA_ALT})",
    re.IGNORECASE,
)


def flatten_layout(text: str) -> str:
    """Junta palavras partidas por fim de linha (Ladina-\\ngem → Ladinagem)."""
    t = text.replace("−", "-").replace("–", "-")
    t = re.sub(r"-\n\s*", "", t)
    t = re.sub(r"\n+", " ", t)
    t = re.sub(r"\s+", " ", t)
    return t


def resolve_pericia(alvo: str) -> Optional[str]:
    a = norm_key(alvo)
    a = re.sub(r"\s+", " ", a).strip(" .,;:")
    for sep in (" e ", " ou ", ",", "/"):
        if sep in a:
            a = a.split(sep)[0].strip()
    if a in NAO_PERICIA:
        return None
    if a in PERICIAS:
        return PERICIAS[a]
    for nome, slug in PERICIAS.items():
        if a == nome:
            return slug
    return None


def resolve_uso(contexto: Optional[str], pericia: Optional[str], snippet: str = "") -> Tuple[Optional[str], str]:
    """Retorna (uso_id, escopo)."""
    blob = " ".join(x for x in (contexto or "", snippet or "") if x)
    c = norm_key(blob)
    for hint, pslug, uid in USOS_HINTS:
        if hint in c:
            if pericia is None or pericia == pslug:
                return uid, "uso"
            return uid, "contexto_prosa"
    if contexto and len(norm_key(contexto)) > 3:
        return None, "contexto_prosa"
    return None, "pericia"


def guess_fonte_nome(page_text_raw: str, approx_pos: int) -> str:
    """Heurística sobre texto com quebras originais."""
    before = page_text_raw[: max(0, min(approx_pos, len(page_text_raw)))]
    lines = [ln.strip() for ln in before.splitlines() if ln.strip()]
    for ln in reversed(lines[-16:]):
        if 2 <= len(ln) <= 70 and not ln.endswith("."):
            if re.fullmatch(r"\d+", ln):
                continue
            if re.match(r"^(Capítulo|Tabela|Cap\.|Capítulo)", ln, re.I):
                continue
            if ln[0].isupper() or ln.isupper():
                # títulos tipo "Banhado a ouro." 
                clean = re.sub(r"\s+", " ", ln).strip(" .")
                if len(clean) >= 3:
                    return clean[:80]
    return ""


def extract_from_page(
    fonte_tipo: str,
    pdf_page: int,
    page_text: str,
) -> List[Dict[str, Any]]:
    hits: List[Dict[str, Any]] = []
    flat = flatten_layout(page_text)

    patterns = [
        ("bonus", RE_BONUS),
        ("recebe", RE_RECEBE),
        ("penalidade", RE_PENALIDADE),
    ]

    seen_local: set = set()

    for kind, cre in patterns:
        for m in cre.finditer(flat):
            gd = m.groupdict()
            alvo = (gd.get("alvo") or "").strip()
            if not alvo:
                continue

            pericia = resolve_pericia(alvo)
            if pericia is None:
                continue

            sinal_raw = (gd.get("sinal") or "+").strip()
            if sinal_raw == "-" or kind == "penalidade":
                sinal = -1
            else:
                sinal = 1
            try:
                valor = int(gd["valor"])
            except (KeyError, ValueError):
                continue
            if valor <= 0 or valor > 20:
                continue

            contexto = (gd.get("contexto") or "").strip() or None
            snippet = re.sub(r"\s+", " ", m.group(0))[:180]
            uso_id, escopo = resolve_uso(contexto, pericia, snippet)

            # Itens mágicos: +N em Luta/Pontaria sem "testes de" costuma ser ataque —
            # mantém com confiança baixa se não houver "testes".
            conf = "alta"
            if pericia in ("luta", "pontaria") and "testes" not in snippet.lower():
                conf = "baixa"
            if escopo == "contexto_prosa":
                conf = "media"

            key = (pericia, uso_id, sinal * valor, snippet[:50])
            if key in seen_local:
                continue
            seen_local.add(key)

            # posição aproximada no texto original para título
            nome = guess_fonte_nome(page_text, int(len(page_text) * 0.5))
            # tentar achar nome pelo snippet no texto original
            idx = page_text.lower().find(alvo.lower()[:8])
            if idx >= 0:
                nome = guess_fonte_nome(page_text, idx) or nome

            hits.append(
                {
                    "fonte_tipo": fonte_tipo,
                    "nome_fonte": nome or f"(trecho p.{impressa(pdf_page)})",
                    "pagina": impressa(pdf_page),
                    "pagina_pdf": pdf_page,
                    "pericia_slug": pericia,
                    "uso_id": uso_id,
                    "valor": sinal * valor,
                    "sinal": "bonus" if sinal > 0 else "penalidade",
                    "escopo": escopo,
                    "contexto": contexto,
                    "snippet": snippet,
                    "confianca": conf,
                    "extrator": kind,
                }
            )
    return hits


def load_codigo_refs(repo: Path) -> Dict[str, Any]:
    """Índices do que já está no código para ja_no_codigo."""
    out: Dict[str, Any] = {
        "racial": {},  # pericia_nome -> [(raca, bonus)]
        "itens_superiores_mods": {},  # key -> slug melhoria
    }
    tracos = repo / "backend/app/games/tormenta/data/tracos_mecanicos_v13.json"
    if tracos.is_file():
        data = json.loads(tracos.read_text(encoding="utf-8"))
        for raca, row in (data.get("racas") or {}).items():
            pb = row.get("pericias_bonus") or {}
            for nome, val in pb.items():
                slug = resolve_pericia(str(nome)) or norm_key(str(nome))
                out["racial"].setdefault(slug, []).append(
                    {"raca": raca, "valor": int(val)}
                )

    its = repo / "backend/app/games/tormenta/data/itens_superiores_v13.json"
    if its.is_file():
        data = json.loads(its.read_text(encoding="utf-8"))
        for mel in data.get("melhorias") or []:
            mods = mel.get("mods") or {}
            slug_m = mel.get("slug") or ""
            for k, v in mods.items():
                if k in (
                    "ataque",
                    "dano",
                    "ca",
                    "defesa",
                    "critico",
                    "deslocamento",
                ):
                    continue
                # pericia genérica ou slug
                out["itens_superiores_mods"][f"{k}:{v}"] = slug_m
                out["itens_superiores_mods"][k] = slug_m
    return out


def mark_ja_no_codigo(entry: Dict[str, Any], refs: Dict[str, Any]) -> str:
    ft = entry["fonte_tipo"]
    slug = entry["pericia_slug"]
    uso = entry.get("uso_id")
    valor = entry["valor"]

    if ft == "raca":
        racial = refs.get("racial") or {}
        for item in racial.get(slug) or []:
            if item["valor"] == abs(valor) or item["valor"] == valor:
                return "true"
        return "parcial" if racial.get(slug) else "false"

    if ft in ("equipamento", "item_magico"):
        mods = refs.get("itens_superiores_mods") or {}
        if uso and f"{uso}:{valor}" in mods:
            return "true"
        if uso and uso in mods:
            return "parcial"
        if f"{slug}:{valor}" in mods:
            return "true"
        if f"{slug}:{abs(valor)}" in mods:
            return "true"
        if slug in mods:
            return "parcial"
        if "pericia" in mods and abs(valor) == 1:
            return "parcial"
        return "false"

    return "false"


# Entradas canônicas revisadas (melhorias TS já no JSON de código + encantamentos chave).
CURATED_EXTRA: List[Dict[str, Any]] = [
    {
        "fonte_tipo": "equipamento",
        "nome_fonte": "Banhado a ouro (melhoria)",
        "pagina": 164,
        "pericia_slug": "diplomacia",
        "uso_id": None,
        "valor": 2,
        "sinal": "bonus",
        "escopo": "pericia",
        "contexto": None,
        "snippet": "Banhado a ouro: +2 em Diplomacia",
        "confianca": "alta",
        "extrator": "curated",
        "ja_no_codigo": "true",
    },
    {
        "fonte_tipo": "equipamento",
        "nome_fonte": "Cravejado de gemas (melhoria)",
        "pagina": 164,
        "pericia_slug": "enganacao",
        "uso_id": None,
        "valor": 2,
        "sinal": "bonus",
        "escopo": "pericia",
        "contexto": None,
        "snippet": "Cravejado de gemas: +2 em Enganação",
        "confianca": "alta",
        "extrator": "curated",
        "ja_no_codigo": "true",
    },
    {
        "fonte_tipo": "equipamento",
        "nome_fonte": "Discreto (melhoria)",
        "pagina": 164,
        "pericia_slug": "ladinagem",
        "uso_id": "ocultar",
        "valor": 5,
        "sinal": "bonus",
        "escopo": "uso",
        "contexto": "ocultar o item",
        "snippet": "Discreto: +5 em testes de Ladinagem para ser ocultado",
        "confianca": "alta",
        "extrator": "curated",
        "ja_no_codigo": "true",
    },
    {
        "fonte_tipo": "equipamento",
        "nome_fonte": "Macabro (melhoria)",
        "pagina": 164,
        "pericia_slug": "intimidacao",
        "uso_id": None,
        "valor": 2,
        "sinal": "bonus",
        "escopo": "pericia",
        "contexto": None,
        "snippet": "Macabro: +2 em Intimidação",
        "confianca": "alta",
        "extrator": "curated",
        "ja_no_codigo": "true",
    },
    {
        "fonte_tipo": "equipamento",
        "nome_fonte": "Macabro (melhoria)",
        "pagina": 164,
        "pericia_slug": "diplomacia",
        "uso_id": None,
        "valor": -2,
        "sinal": "penalidade",
        "escopo": "pericia",
        "contexto": None,
        "snippet": "Macabro: penalidade de −2 em Diplomacia",
        "confianca": "alta",
        "extrator": "curated",
        "ja_no_codigo": "true",
    },
    {
        "fonte_tipo": "item_magico",
        "nome_fonte": "Encantamento Acrobático",
        "pagina": 338,
        "pericia_slug": "acrobacia",
        "uso_id": None,
        "valor": 5,
        "sinal": "bonus",
        "escopo": "pericia",
        "contexto": None,
        "snippet": "Acrobático: +5 em Acrobacia",
        "confianca": "alta",
        "extrator": "curated",
        "ja_no_codigo": "false",
    },
    {
        "fonte_tipo": "item_magico",
        "nome_fonte": "Encantamento Sombrio",
        "pagina": 339,
        "pericia_slug": "furtividade",
        "uso_id": None,
        "valor": 5,
        "sinal": "bonus",
        "escopo": "pericia",
        "contexto": None,
        "snippet": "Sombrio: +5 em Furtividade (e ignora pen. armadura nesta perícia)",
        "confianca": "alta",
        "extrator": "curated",
        "ja_no_codigo": "false",
    },
]


def merge_curated(entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out = list(entries)
    for c in CURATED_EXTRA:
        key = (
            c["fonte_tipo"],
            norm_key(c["nome_fonte"]),
            c["pericia_slug"],
            c.get("uso_id"),
            c["valor"],
            c["pagina"],
        )
        exists = False
        for e in out:
            ek = (
                e["fonte_tipo"],
                norm_key(e.get("nome_fonte") or ""),
                e["pericia_slug"],
                e.get("uso_id"),
                e["valor"],
                e["pagina"],
            )
            # match frouxo por pericia+valor+pagina+uso
            if (
                e["pericia_slug"] == c["pericia_slug"]
                and e["valor"] == c["valor"]
                and e["pagina"] == c["pagina"]
                and e.get("uso_id") == c.get("uso_id")
            ):
                e["ja_no_codigo"] = c.get("ja_no_codigo", e.get("ja_no_codigo"))
                e["confianca"] = "alta"
                e["escopo"] = c["escopo"]
                if c.get("uso_id"):
                    e["uso_id"] = c["uso_id"]
                if c.get("nome_fonte") and (
                    e.get("nome_fonte", "").startswith("(trecho")
                    or "melhoria" in c["nome_fonte"].lower()
                    or "encantamento" in c["nome_fonte"].lower()
                ):
                    e["nome_fonte"] = c["nome_fonte"]
                exists = True
                break
        if not exists:
            row = dict(c)
            row["pagina_pdf"] = c["pagina"] + PDF_OFFSET
            out.append(row)
    return out


def dedupe(entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    best: Dict[Tuple, Dict[str, Any]] = {}
    for e in entries:
        key = (
            e["fonte_tipo"],
            norm_key(e.get("nome_fonte") or ""),
            e["pericia_slug"],
            e.get("uso_id"),
            e["valor"],
            e["pagina"],
        )
        prev = best.get(key)
        if prev is None or len(e.get("snippet") or "") > len(prev.get("snippet") or ""):
            best[key] = e
    return sorted(best.values(), key=lambda x: (x["pagina"], x["fonte_tipo"], x["pericia_slug"]))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--pdf",
        type=Path,
        default=Path("livros/Tormenta20-Edicao-Jogo-do-Ano-v1.3.pdf"),
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=Path("backend/app/games/tormenta/data/bonus_pericias_fontes_v13.json"),
    )
    ap.add_argument("--repo", type=Path, default=Path("."))
    args = ap.parse_args()

    if not args.pdf.is_file():
        raise SystemExit(f"PDF não encontrado: {args.pdf}")

    refs = load_codigo_refs(args.repo.resolve())
    all_hits: List[Dict[str, Any]] = []

    for fonte_tipo, ini, fim in FAIXAS:
        print(f"… {fonte_tipo} PDF {ini}–{fim}")
        raw = pdftotext_range(args.pdf, ini, fim)
        pages = split_pages(raw, ini, fim)
        for pdf_page, text in pages.items():
            all_hits.extend(extract_from_page(fonte_tipo, pdf_page, text))

    entries = dedupe(all_hits)
    for e in entries:
        e["ja_no_codigo"] = mark_ja_no_codigo(e, refs)
        if e.get("confianca") == "alta" and e["escopo"] == "contexto_prosa":
            e["confianca"] = "media"
        elif e["escopo"] == "pericia" and not e.get("contexto") and e.get("confianca") != "baixa":
            e["confianca"] = "alta"
        elif e["escopo"] == "uso":
            e["confianca"] = "alta"

    entries = merge_curated(entries)
    entries = dedupe(entries)
    # reassign ids after merge
    for i, e in enumerate(sorted(entries, key=lambda x: (x["pagina"], x["fonte_tipo"], x["pericia_slug"])), start=1):
        e["id"] = f"bpf-{i:04d}"
    entries = sorted(entries, key=lambda x: (x["pagina"], x["fonte_tipo"], x["pericia_slug"], x["id"]))

    # estatísticas
    by_tipo: Dict[str, int] = defaultdict(int)
    by_codigo: Dict[str, int] = defaultdict(int)
    by_escopo: Dict[str, int] = defaultdict(int)
    for e in entries:
        by_tipo[e["fonte_tipo"]] += 1
        by_codigo[str(e.get("ja_no_codigo", "false"))] += 1
        by_escopo[e["escopo"]] += 1

    catalog = {
        "_meta": {
            "fonte": "Tormenta20-Edicao-Jogo-do-Ano-v1.3.pdf — Cap. 2/3/8 + raças/origens",
            "offset_pdf": "pagina_pdf = pagina_impressa + 6",
            "nota": (
                "Extração heurística por regex + CURATED_EXTRA; não substitui o livro. "
                "Usos (subperícias) são raros; maioria é perícia inteira ou contexto_prosa. "
                "Não auto-aplica na ficha — ver RF-T14."
            ),
            "total": len(entries),
            "por_fonte_tipo": dict(by_tipo),
            "por_ja_no_codigo": dict(by_codigo),
            "por_escopo": dict(by_escopo),
            "script": "scripts/extrair_bonus_pericias_t20_v13.py",
            "gaps_prioritarios_auto_apply": [
                "Vestuário Cap.3 (Andrajos, Enfeite de Elmo, etc.) → outros",
                "Encantamentos Acrobático/Sombrio Cap.8 → outros",
                "Discreto → pericias_usos_bonus.ladinagem.ocultar (mods já no itens_superiores)",
                "Poderes gerais/classe com +N em perícia → efeitos estruturados",
            ],
        },
        "entradas": entries,
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"OK → {args.out} ({len(entries)} entradas)")
    print("por_fonte_tipo:", dict(by_tipo))
    print("por_ja_no_codigo:", dict(by_codigo))
    print("por_escopo:", dict(by_escopo))


if __name__ == "__main__":
    main()
