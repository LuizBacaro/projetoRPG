#!/usr/bin/env python3
"""
Aplica no seed_magias.py as correções da lista PHB de magias de Clérigo (níveis 0–1).

Uso:
  python scripts/patch_clerigo_phb_seed.py
  python scripts/patch_clerigo_phb_seed.py --dry-run
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

SEED_FILE = Path(__file__).resolve().parent / "seed_magias.py"

# Novas entradas (nível 1) — componentes V,S para clérigo
NOVAS_NIVEL_1 = [
    (
        "Abençoar Água",
        1,
        "CLÉRIGO",
        "Transmutação",
        "[Bem]",
        "V,S,M",
        "Toque",
        "Frasco água tocado",
        "Inst",
        "1 min",
        "",
        "Não",
        True,
        "Cria água benta",
    ),
    (
        "Amaldiçoar Água",
        1,
        "CLÉRIGO",
        "Necromancia",
        "[Mal]",
        "V,S,M",
        "Toque",
        "Frasco água tocado",
        "Inst",
        "1 min",
        "",
        "Não",
        True,
        "Cria água profana",
    ),
    (
        "Auxílio Divino",
        1,
        "CLÉRIGO",
        "Evocação",
        "",
        "V,S,FD",
        "Pessoal",
        "Você",
        "1 min",
        "1 AP",
        "",
        "Não",
        False,
        "Você recebe +1 de bônus/3 níveis para ataques e dano",
    ),
    (
        "Causar Medo",
        1,
        "CLÉRIGO",
        "Necromancia",
        "",
        "V,S",
        "Curto 7,5m+1,5m/2niv",
        "1 criat 5DV",
        "1d4 rod ou 1rod",
        "1 AP",
        "",
        "Não",
        True,
        "Uma criatura (5 DV ou menos) foge durante 1d4 rodadas",
    ),
    (
        "Divisibilidade Contra Mortos-Vivos",
        1,
        "CLÉRIGO",
        "Abjuração",
        "",
        "V,S,FD",
        "Toque",
        "1 criat toc/niv",
        "10 min/niv(D)",
        "1 AP",
        "",
        "Não",
        True,
        "Mortos-vivos não podem perceber 1 alvo/nível",
    ),
    (
        "Infligir Ferimentos Leves",
        1,
        "CLÉRIGO",
        "Necromancia",
        "",
        "V,S",
        "Toque",
        "Criat. Tocada",
        "Inst",
        "1 AP",
        "",
        "Não",
        True,
        "Ataque de toque, 1d8+1/nível de dano (máx. +5)",
    ),
    (
        "Proteção Contra o Caos / Mal / Bem / Ordem",
        1,
        "CLÉRIGO",
        "Abjuração",
        "",
        "V,S,M/FD",
        "Toque",
        "Criatura tocada",
        "1 min/niv(D)",
        "1 AP",
        "",
        "Não",
        True,
        "+2 na CA e testes de resistência, impede controle mental, isola elementais e seres extra-planares",
    ),
    (
        "Visão da Morte",
        1,
        "CLÉRIGO",
        "Necromancia",
        "",
        "V,S",
        "9m",
        "Emanação em cone",
        "10 min/niv",
        "1 AP",
        "",
        "Não",
        False,
        "Detecta a situação de criaturas a menos de 9 m",
    ),
]

RENOMEAR = {
    "Guia": "Orientação",
    "Mending": None,  # removido (duplicata de Consertar)
    "Névoa Obscurecente": "Névoa Obscurescente",
    "Resistir Elementos": "Suportar Elementos",
}

NOVAS_NIVEL_0 = [
    (
        "Consertar",
        0,
        "CLÉRIGO",
        "Transmutação",
        "",
        "V,S",
        "3m",
        "Objeto 500g",
        "Inst",
        "1 AP",
        "",
        "Não",
        False,
        "Faz pequenos reparos em um objeto",
    ),
    (
        "Criar Água",
        0,
        "CLÉRIGO",
        "Conjuração",
        "",
        "V,S",
        "Curto 7,5m+1,5m/2niv",
        "8 litros/niv",
        "Inst",
        "1 AP",
        "",
        "Não",
        False,
        "Cria 8 litros/nível de água pura",
    ),
    (
        "Infligir Ferimentos Mínimos",
        0,
        "CLÉRIGO",
        "Necromancia",
        "",
        "V,S",
        "Toque",
        "Criatura tocada",
        "Inst",
        "1 AP",
        "",
        "Não",
        True,
        "Ataque de toque, 1 ponto de dano",
    ),
]


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
    return "    (" + ", ".join(parts) + "),"


def _ja_existe(block: str, nome: str) -> bool:
    return bool(re.search(rf"\('{re.escape(nome)}',\s*\d+,\s*'CL", block))


def aplicar_patch(texto: str) -> str:
    m = re.search(r"(MAGIAS_CL[EÉ]RIGO = \[)(.*?)(\]\n\nMAGIAS_DRUIDA)", texto, re.S)
    if not m:
        raise RuntimeError("Bloco MAGIAS_CLÉRIGO não encontrado")

    prefix, block, suffix = m.group(1), m.group(2), m.group(3)

    for antigo, novo in RENOMEAR.items():
        if novo is None:
            block = re.sub(
                rf"\s*\('{re.escape(antigo)}',\s*0,\s*'CL[EÉ]RIGO'.*?\),\n",
                "",
                block,
                count=1,
            )
        else:
            block = block.replace(f"('{antigo}',", f"('{novo}',", 1)

    block = block.replace(
        "Alvo recebe +1 para testes de resistência",
        "O alvo recebe +1 para testes de resistência",
        1,
    )
    if "Resiste a extremos de temperatura" in block:
        block = block.replace(
            "Resiste a extremos de temperatura",
            "Mantém uma criatura confortável dentro de ambientes áridos",
            1,
        )

    for tup in NOVAS_NIVEL_0:
        if not _ja_existe(block, tup[0]):
            insert_after = "    # ── Nível 0 ──\n"
            block = block.replace(
                insert_after,
                insert_after + _format_tuple(tup) + "\n",
                1,
            )

    marker_n1 = "    # ── Nível 1 ──\n"
    novas_linhas = ""
    for tup in NOVAS_NIVEL_1:
        if not _ja_existe(block, tup[0]):
            novas_linhas += _format_tuple(tup) + "\n"
    if novas_linhas:
        block = block.replace(marker_n1, marker_n1 + novas_linhas, 1)

    return texto[: m.start()] + prefix + block + suffix + texto[m.end() :]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    texto = SEED_FILE.read_text(encoding="utf-8")
    novo = aplicar_patch(texto)

    if novo == texto:
        print("Nenhuma alteração necessária.")
        return

    if args.dry_run:
        print("Alterações que seriam aplicadas (dry-run).")
        return

    SEED_FILE.write_text(novo, encoding="utf-8")
    print(f"Patch aplicado em {SEED_FILE}")


if __name__ == "__main__":
    main()
