#!/usr/bin/env python3
"""
Pós-processamento do ``gurps_personagens_sumario_catalogo.json``:
remove ruído óbvio, corrige marcas de rodapé/OCR conhecidos e deduplica.

  python3 scripts/curar_gurps_personagens_sumario_catalogo.py
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = (
    ROOT
    / "backend"
    / "app"
    / "games"
    / "gurps"
    / "catalogs"
    / "gurps_personagens_sumario_catalogo.json"
)

RENOMEAR_EXATO = {
    "Arremedo": "Apetrechos",
    "Metabolismo": "Controle do Metabolismo",
}

REMOVER_NOME_EXATO = {
    "Vf",
    "Líquidos",
    "? Lenta V",
    "Vício «?/**>",
}

REMOVER_PREFIXO = (
    "Modificadores ",
    "Limitações ",
    "Ampliações ",
)

# Fragmentos de coluna / lixo (não são entradas de lista).
REMOVER_NOME_REGEX = (
    re.compile(r"^♦"),
    re.compile(r"♦>"),
    re.compile(r"\?\s*/\s*\*"),
)


def limpar_nome_bruto(nome: str) -> str:
    s = (nome or "").strip()
    s = RENOMEAR_EXATO.get(s, s)
    # Sufixos de nota / símbolos do PDF (várias passadas)
    for _ in range(6):
        t = re.sub(
            r"(\s*[\^$#®*?¥♦«»/]+|\s*\$/?\*?|♦>|\s+SP\$|\s+S\?\$?|\s+Sr\*\$?|\s+[fFW]\b)+\s*$",
            "",
            s,
            flags=re.I,
        )
        t = t.strip(" -–/")
        if t == s:
            break
        s = t
    s = re.sub(r"\s+f\s+t\s*$", "", s, flags=re.I)
    s = re.sub(r"\s+t\s*$", "", s, flags=re.I)
    s = re.sub(r"\s+\^?\s*P\s*$", "", s)
    s = re.sub(r"\s+\^?\s*t\s*$", "", s, flags=re.I)
    s = re.sub(r"\s+S\^f\s*$", "", s, flags=re.I)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def ajustar_vantagem_pos_limpar(nome: str, custo_texto: str | None) -> str:
    ct = (custo_texto or "").strip()
    if "Sobrenatural" in nome and "^" in nome and "150" in ct:
        return "Durabilidade Sobrenatural"
    return nome


def manter_vantagem(nome: str) -> bool:
    if nome in REMOVER_NOME_EXATO:
        return False
    if len(nome) < 2:
        return False
    if nome[0] in "?¿0123456789":
        return False
    if any(nome.startswith(p) for p in REMOVER_PREFIXO):
        return False
    for rx in REMOVER_NOME_REGEX:
        if rx.search(nome):
            return False
    return True


def manter_desvantagem(nome: str) -> bool:
    if nome in REMOVER_NOME_EXATO:
        return False
    if len(nome) < 2:
        return False
    if nome[0] in "?¿":
        return False
    for rx in REMOVER_NOME_REGEX:
        if rx.search(nome):
            return False
    return True


def manter_pericia(nome: str) -> bool:
    if len(nome) < 2:
        return False
    if nome[0] in "?¿0123456789":
        return False
    return True


def dedup(seq: list[dict], key: str = "nome") -> list[dict]:
    seen: set[str] = set()
    out: list[dict] = []
    for it in seq:
        k = (it.get(key) or "").strip().casefold()
        if not k or k in seen:
            continue
        seen.add(k)
        out.append(it)
    return out


def main() -> None:
    data = json.loads(PATH.read_text(encoding="utf-8"))
    meta = data.setdefault("meta", {})

    va: list[dict] = []
    for it in data.get("vantagens", []):
        ct = it.get("custo_texto")
        nome = limpar_nome_bruto(it.get("nome", ""))
        nome = ajustar_vantagem_pos_limpar(nome, ct)
        if not manter_vantagem(nome):
            continue
        va.append({"nome": nome, "custo_texto": ct})

    de: list[dict] = []
    for it in data.get("desvantagens", []):
        nome = limpar_nome_bruto(it.get("nome", ""))
        if not manter_desvantagem(nome):
            continue
        de.append({"nome": nome, "custo_texto": it.get("custo_texto")})

    pe: list[dict] = []
    for it in data.get("pericias", []):
        nome = limpar_nome_bruto(it.get("nome", ""))
        if not manter_pericia(nome):
            continue
        pe.append(
            {
                "nome": nome,
                "atributo_base": it.get("atributo_base", "dx"),
                "dificuldade": it.get("dificuldade", "M"),
                "nt": bool(it.get("nt")),
            }
        )

    data["vantagens"] = dedup(va)
    data["desvantagens"] = dedup(de)
    data["pericias"] = dedup(pe)
    meta["nota"] = (
        "Extração heurística (pdftotext) + curadoria automática "
        "(símbolos de rodapé, OCR pontual, dedupe)."
    )

    PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        f"Atualizado {PATH.relative_to(ROOT)}: "
        f"{len(data['vantagens'])} vantagens, "
        f"{len(data['desvantagens'])} desvantagens, "
        f"{len(data['pericias'])} perícias"
    )


if __name__ == "__main__":
    main()
