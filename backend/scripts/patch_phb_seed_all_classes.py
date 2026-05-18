#!/usr/bin/env python3
"""
Correções no seed_magias.py com base no diff PHB × seed (todas as classes).

Uso:
  python scripts/patch_phb_seed_all_classes.py --dry-run
  python scripts/patch_phb_seed_all_classes.py
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

SEED_FILE = Path(__file__).resolve().parent / "seed_magias.py"

# (nome, nível, tag_classe) — remove duplicatas / extras / placeholders
REMOVER: list[tuple[str, int, str]] = [
    ("Favor Divino", 1, "CLÉRIGO"),
    ("Emaranhar", 1, "CLÉRIGO"),
    ("Proibição de Ação", 1, "CLÉRIGO"),
    ("NOME DA MAGIA", 1, "BARDO"),
    ("NOME DA MAGIA", 6, "BARDO"),
    ("NOME DA MAGIA", 5, "DRUIDA"),
    ("NOME DA MAGIA", 1, "MAGO"),
    # Ranger nv.1: não constam na lista PHB (pertencem ao paladino nv.4 no apêndice)
    ("Presa Mágica", 1, "RANGER"),
    ("Resistência a Elementos", 1, "RANGER"),
    ("Retardar Envenenamento", 1, "RANGER"),
    ("Salto", 1, "RANGER"),
    ("Suportar Elementos", 1, "RANGER"),
]

# Remove segunda cópia exata (mantém a primeira)
DEDUPE_CANON: list[tuple[str, int, str]] = [
    ("Consertar", 0, "BARDO"),
    ("Detectar Magia", 0, "BARDO"),
    ("Ler Magias", 0, "BARDO"),
    ("Luz", 0, "BARDO"),
    ("Resistência", 0, "BARDO"),
    ("Causar Medo", 1, "BARDO"),
    ("Compreender Idiomas", 1, "BARDO"),
    ("Curar Ferimentos Leves", 1, "BARDO"),
    ("Invocar Criaturas I", 1, "BARDO"),
    ("Remover Medo", 1, "BARDO"),
]

RENOMEAR: list[tuple[str, str, int, str]] = [
    ("Bane", "Maldição Menor", 1, "CLÉRIGO"),
    ("Invisibilidade Contra Animais", "Divisibilidade Contra Animais", 1, "DRUIDA"),
    ("Dominar Animal", "Dominar Animais", 3, "DRUIDA"),
    ("Controlar a Água", "Controlar Água", 4, "DRUIDA"),
    ("Inverter Gravidade", "Inverter a Gravidade", 8, "DRUIDA"),
    ("Névoa Obscurecente", "Névoa Obscurescente", 1, "BARDO"),
]

# Paladino nv.4 — bloco PHB após quebra de página (faltavam no seed)
NOVAS_PALADINO_4 = [
    (
        "Presa Mágica",
        4,
        "PALADINO",
        "Trans",
        "",
        "V,G,FD",
        "Toque",
        "Criat. Viva tocada",
        "1 hora/niv",
        "1 AP",
        "",
        "Não",
        True,
        "Uma arma natural do alvo recebe +1 de bônus para ataques e dano",
    ),
    (
        "Resistência a Elementos",
        4,
        "PALADINO",
        "Abjur",
        "",
        "V,G,FD",
        "Toque",
        "Criatura tocada",
        "10 min/niv",
        "1 AP",
        "",
        "Não",
        True,
        "Ignora 10 (ou mais) dano/ataque de um tipo de energia",
    ),
    (
        "Retardar Envenenamento",
        4,
        "PALADINO",
        "Conj (cura)",
        "",
        "V,G,FD",
        "Toque",
        "Criatura tocada",
        "1 hora/niv",
        "1 AP",
        "",
        "Não",
        True,
        "Impede que veneno cause dano ao alvo durante 1 hora/nível",
    ),
    (
        "Salto",
        4,
        "PALADINO",
        "Trans",
        "",
        "V,G,M",
        "Toque",
        "Criatura tocada",
        "1 min/niv(D)",
        "1 AP",
        "",
        "Não",
        True,
        "Alvo recebe bônus nos testes de Saltar",
    ),
    (
        "Suportar Elementos",
        4,
        "PALADINO",
        "Abjur",
        "",
        "V,G",
        "Toque",
        "Criatura tocada",
        "24 horas",
        "1 AP",
        "",
        "Não",
        True,
        "Mantém uma criatura confortável dentro de ambientes áridos",
    ),
]


def _tag_pat(classe: str) -> str:
    if "CLERIGO" in classe.upper() or "CLÉRIGO" in classe.upper():
        return "CL[EÉ]RIGO"
    return re.escape(classe)


def _tuple_line_pattern(nome: str, nivel: int, classe: str) -> str:
    esc = re.escape(nome).replace(r"\n", r"\\n")
    return rf"\s*\('{esc}',\s*{nivel},\s*'{_tag_pat(classe)}'.*?\),\n"


def _format_tuple(t: tuple) -> str:
    nome = t[0].replace("'", "\\'")
    if "\n" in nome:
        nome = nome.replace("\n", "\\n")
    parts = [f"'{nome}'", str(t[1]), f"'{t[2]}'"]
    for p in t[3:]:
        if isinstance(p, bool):
            parts.append("True" if p else "False")
        elif p is None or p == "":
            parts.append("''")
        else:
            ps = str(p).replace("'", "\\'").replace("\n", "\\n")
            parts.append(f"'{ps}'")
    return "    (" + ", ".join(parts) + "),\n"


def _ja_existe(texto: str, nome: str, nivel: int, classe: str) -> bool:
    esc = re.escape(nome)
    return bool(
        re.search(rf"\('{esc}',\s*{nivel},\s*'{_tag_pat(classe)}'", texto)
    )


def aplicar(texto: str) -> str:
    for nome, nivel, classe in REMOVER:
        texto = re.sub(_tuple_line_pattern(nome, nivel, classe), "", texto, count=1)

    for nome, nivel, classe in DEDUPE_CANON:
        pat = _tuple_line_pattern(nome, nivel, classe)
        if re.search(pat, texto):
            texto = re.sub(pat, "", texto, count=1)

    for antigo, novo, nivel, classe in RENOMEAR:
        texto = texto.replace(f"('{antigo}', {nivel}, '{classe}'", f"('{novo}', {nivel}, '{classe}'", 1)

    m = re.search(r"(MAGIAS_PALADINO = \[)(.*?)(\]\n\nMAGIAS_RANGER)", texto, re.S)
    if m:
        block = m.group(2)
        novas = ""
        for tup in NOVAS_PALADINO_4:
            if not _ja_existe(block, tup[0], tup[1], tup[2]):
                novas += _format_tuple(tup)
        if novas:
            marker = "    # ── Nível 4 ──\n"
            block = block.replace(marker, marker + novas, 1)
            texto = texto[: m.start()] + m.group(1) + block + m.group(3) + texto[m.end() :]

    return texto


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    texto = SEED_FILE.read_text(encoding="utf-8")
    novo = aplicar(texto)
    if novo == texto:
        print("Nenhuma alteração necessária.")
        return
    if args.dry_run:
        print("Alterações pendentes (dry-run).")
        return
    SEED_FILE.write_text(novo, encoding="utf-8")
    print(f"Patch aplicado em {SEED_FILE}")


if __name__ == "__main__":
    main()
