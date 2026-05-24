#!/usr/bin/env python3
"""
Checagens de paridade do catálogo D&D 3.5 (`magias` / `magias_classes`).

Compara contagens do banco (opcional) com mínimos do seed PHB e, se pedido,
com volume típico de produção (>500 linhas ativas — cenário que expõe bugs de
paginação no grimório do Mago).

Uso:
  cd backend && python -m scripts.check_magias_dnd35_catalogo
  cd backend && python -m scripts.check_magias_dnd35_catalogo --db
  cd backend && python -m scripts.check_magias_dnd35_catalogo --db --production-volume
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from scripts.seed_magias import MAGIAS_MAGO, _norm_nome_magia, _todas_magias  # noqa: E402

# Limites derivados do seed PHB em seed_magias.py (atualize se o seed mudar).
PHB_EXPECTED = {
    "min_magias_ativas": 600,
    "min_vinculos_classe": 990,
    "min_mago_vinculos": 370,
    "min_nomes_unicos_seed": 600,
}

# Produção (Neon) costuma ter ~1061 magias ativas após imports admin.
PRODUCTION_VOLUME = {
    "min_magias_ativas": 1000,
    "min_mago_vinculos": 370,
    "pagination_trap_threshold": 501,
}


def _contagens_seed() -> dict[str, int]:
    todas = _todas_magias()
    nomes = {_norm_nome_magia(t[0]).lower() for t in todas}
    by_classe = Counter(t[2] for t in todas)
    return {
        "vinculos_classe": len(todas),
        "nomes_unicos": len(nomes),
        "mago_vinculos": len(MAGIAS_MAGO),
        "mago_nomes_unicos": len({_norm_nome_magia(t[0]).lower() for t in MAGIAS_MAGO}),
        "by_classe": dict(sorted(by_classe.items())),
    }


def _contagens_db(db) -> dict[str, int]:
    from sqlalchemy import func

    from app.games.dnd35.models.magia import Magia, MagiaClasse
    from app.games.dnd35.text_utils import normalizar_classe

    total_ativas = db.query(Magia).filter(Magia.ativo.is_(True)).count()
    vinculos = db.query(MagiaClasse).count()
    mago_vinculos = (
        db.query(MagiaClasse)
        .filter(func.upper(MagiaClasse.classe).like("%MAGO%"))
        .count()
    )
    mago_norm = sum(
        1
        for mc in db.query(MagiaClasse).all()
        if normalizar_classe(mc.classe or "") == "MAGO"
    )

    dev_padding = (
        db.query(Magia)
        .filter(Magia.ativo.is_(True), Magia.nome.like("[DEV QA]%"))
        .count()
    )

    return {
        "magias_ativas": total_ativas,
        "vinculos_classe": vinculos,
        "mago_vinculos_sql": mago_vinculos,
        "mago_vinculos": mago_norm or mago_vinculos,
        "dev_padding_ativas": dev_padding,
    }


def _simular_armadilha_limit_500() -> dict[str, int]:
    """Quantas magias de Mago ficam fora da 1ª página /magias?limit=500 sem filtro de classe."""
    rows: dict[str, dict] = {}
    for dados in _todas_magias():
        nome = _norm_nome_magia(dados[0])
        nivel = int(dados[1])
        classe = dados[2]
        if nome not in rows:
            rows[nome] = {"nome": nome, "nivel": nivel, "classes": set()}
        rows[nome]["nivel"] = min(rows[nome]["nivel"], nivel)
        rows[nome]["classes"].add(classe)

    ordenado = sorted(rows.values(), key=lambda r: (r["nivel"], r["nome"].lower()))
    primeira_pagina = ordenado[:500]
    mago_total = sum(1 for r in ordenado if "MAGO" in r["classes"])
    mago_na_pagina = sum(1 for r in primeira_pagina if "MAGO" in r["classes"])
    return {
        "magias_unicas_seed": len(ordenado),
        "mago_total_seed": mago_total,
        "mago_na_primeira_500_sem_filtro": mago_na_pagina,
        "mago_fora_da_primeira_500": mago_total - mago_na_pagina,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Verifica paridade do catálogo de magias D&D 3.5.")
    parser.add_argument(
        "--db",
        action="store_true",
        help="Consulta DATABASE_URL e compara com os mínimos esperados.",
    )
    parser.add_argument(
        "--production-volume",
        action="store_true",
        help="Exige volume próximo de produção (>=1000 magias ativas) e avisa sobre armadilha limit=500.",
    )
    args = parser.parse_args()

    erros: list[str] = []
    avisos: list[str] = []

    seed = _contagens_seed()
    sim = _simular_armadilha_limit_500()

    print("=== Catálogo D&D 3.5 — referência seed PHB ===")
    print(f"  Nomes únicos no seed:     {seed['nomes_unicos']}")
    print(f"  Vínculos classe (seed):   {seed['vinculos_classe']}")
    print(f"  Vínculos Mago (seed):     {seed['mago_vinculos']} ({seed['mago_nomes_unicos']} nomes)")
    for classe, qtd in seed["by_classe"].items():
        print(f"    • {classe}: {qtd}")

    print("\n=== Simulação armadilha GET /magias?limit=500 (sem classe) ===")
    print(f"  Magias únicas PHB:        {sim['magias_unicas_seed']}")
    print(f"  Mago no seed:              {sim['mago_total_seed']}")
    print(f"  Mago na 1ª página (500):  {sim['mago_na_primeira_500_sem_filtro']}")
    print(f"  Mago FORA da 1ª página:   {sim['mago_fora_da_primeira_500']}")
    if sim["mago_fora_da_primeira_500"] > 0:
        avisos.append(
            "Com apenas o PHB (~601 nomes), um fallback client-side em /magias?limit=500 "
            f"sem filtro de classe perde {sim['mago_fora_da_primeira_500']} magias de Mago. "
            "Use ?classe=MAGO no backend ou `make pad-magias-dev` para simular produção."
        )

    if args.db:
        from app.shared.core.database import SessionLocal

        db = SessionLocal()
        try:
            db_counts = _contagens_db(db)
        finally:
            db.close()

        print("\n=== Banco (DATABASE_URL) ===")
        print(f"  Magias ativas:            {db_counts['magias_ativas']}")
        print(f"  Vínculos magias_classes:  {db_counts['vinculos_classe']}")
        print(f"  Vínculos Mago:            {db_counts['mago_vinculos']}")
        print(f"  Padding [DEV QA] ativas:  {db_counts['dev_padding_ativas']}")

        if db_counts["magias_ativas"] < PHB_EXPECTED["min_magias_ativas"]:
            erros.append(
                f"Banco com {db_counts['magias_ativas']} magias ativas; "
                f"esperado >= {PHB_EXPECTED['min_magias_ativas']} (seed PHB completo). "
                "Rode: cd backend && python -m scripts.seed_magias"
            )
        if db_counts["mago_vinculos"] < PHB_EXPECTED["min_mago_vinculos"]:
            erros.append(
                f"Apenas {db_counts['mago_vinculos']} vínculos Mago; "
                f"esperado >= {PHB_EXPECTED['min_mago_vinculos']}."
            )

        if args.production_volume:
            if db_counts["magias_ativas"] < PRODUCTION_VOLUME["min_magias_ativas"]:
                erros.append(
                    f"Volume local ({db_counts['magias_ativas']}) abaixo de produção "
                    f"(~{PRODUCTION_VOLUME['min_magias_ativas']}+). "
                    "Rode: make pad-magias-dev"
                )
            elif db_counts["magias_ativas"] >= PRODUCTION_VOLUME["pagination_trap_threshold"]:
                if db_counts["dev_padding_ativas"] == 0:
                    avisos.append(
                        "Catálogo >=501 magias sem padding [DEV QA] — paridade parcial com produção. "
                        "Considere `make pad-magias-dev` para reproduzir o cenário de paginação."
                    )
                else:
                    print(
                        f"\n  ✓ Volume de produção simulado "
                        f"({db_counts['dev_padding_ativas']} entradas [DEV QA])."
                    )

    if args.production_volume and not args.db:
        avisos.append("Use --db junto com --production-volume para validar o banco local.")

    print("\n=== Resumo ===")
    for msg in avisos:
        print(f"  AVISO: {msg}")
    for msg in erros:
        print(f"  ERRO: {msg}")

    if erros:
        print(f"\nFalhou com {len(erros)} erro(s).")
        return 1
    print("\nOK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
