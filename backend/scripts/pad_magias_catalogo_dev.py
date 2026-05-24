#!/usr/bin/env python3
"""
Padding opcional do catálogo de magias para dev/QA local.

Insere magias fictícias `[DEV QA] Padding …` (classe DEVQA, nível 0) até atingir
um total próximo de produção (~1061 magias ativas). Isso reproduz localmente o
cenário em que GET /magias?limit=500 sem filtro de classe não cobre todo o
catálogo — bug que afetava o grimório do Mago em produção.

Nunca rode em produção. Remova com --remove.

Uso:
  cd backend && python -m scripts.pad_magias_catalogo_dev
  cd backend && python -m scripts.pad_magias_catalogo_dev --target 1100 --dry-run
  cd backend && python -m scripts.pad_magias_catalogo_dev --remove
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from app.games.dnd35.models.magia import Magia, MagiaClasse  # noqa: E402
from app.shared.core.config import settings  # noqa: E402
from app.shared.core.database import SessionLocal  # noqa: E402

DEV_CLASS = "DEVQA"
DEV_NAME_PREFIX = "[DEV QA] Padding"
DEFAULT_TARGET = 1100


def _is_production_env() -> bool:
    return (settings.ENVIRONMENT or "").strip().lower() == "production"


def _count_padding(db) -> int:
    return (
        db.query(Magia)
        .filter(Magia.ativo.is_(True), Magia.nome.like(f"{DEV_NAME_PREFIX}%"))
        .count()
    )


def _count_ativas(db) -> int:
    return db.query(Magia).filter(Magia.ativo.is_(True)).count()


def pad_catalogo(db, *, target: int, dry_run: bool) -> dict[str, int]:
    total_ativas = _count_ativas(db)
    padding_atual = _count_padding(db)
    faltam = max(0, target - total_ativas)

    stats = {
        "total_antes": total_ativas,
        "padding_antes": padding_atual,
        "inseridas": 0,
        "target": target,
        "faltavam": faltam,
    }

    if faltam == 0:
        print(f"✅ Catálogo já tem {total_ativas} magias ativas (meta {target}). Nada a fazer.")
        return stats

    print(
        f"📦 Inserindo {faltam} magias {DEV_NAME_PREFIX} "
        f"({total_ativas} → {total_ativas + faltam} ativas)…"
    )

    if dry_run:
        print("   (dry-run — nenhuma alteração persistida)")
        return stats

    for i in range(faltam):
        nome = f"{DEV_NAME_PREFIX} {padding_atual + i + 1:04d}"
        magia = Magia(
            nome=nome,
            nivel=0,
            classe=DEV_CLASS,
            escola="Evocacao",
            componentes="V",
            alcance="Pessoal",
            duracao="Instantanea",
            tempo_conjuracao="1 acao",
            descricao="Entrada fictícia para QA local — não usar em mesa. "
            "Remova com: python -m scripts.pad_magias_catalogo_dev --remove",
            ativo=True,
        )
        db.add(magia)
        db.flush()
        db.add(MagiaClasse(magia_id=magia.id, classe=DEV_CLASS, nivel=0))
        stats["inseridas"] += 1

        if stats["inseridas"] % 100 == 0:
            db.commit()
            print(f"   … {stats['inseridas']}/{faltam}")

    db.commit()
    print(
        f"✅ Padding concluído: +{stats['inseridas']} magias | "
        f"total ativas agora {_count_ativas(db)}"
    )
    return stats


def remove_padding(db, *, dry_run: bool) -> int:
    query = db.query(Magia).filter(Magia.nome.like(f"{DEV_NAME_PREFIX}%"))
    total = query.count()
    if total == 0:
        print("Nenhuma magia [DEV QA] encontrada.")
        return 0

    print(f"🗑️  Removendo {total} magias {DEV_NAME_PREFIX}…")
    if dry_run:
        print("   (dry-run — nenhuma alteração persistida)")
        return total

    ids = [row.id for row in query.with_entities(Magia.id).all()]
    db.query(MagiaClasse).filter(MagiaClasse.magia_id.in_(ids)).delete(
        synchronize_session=False
    )
    query.delete(synchronize_session=False)
    db.commit()
    print(f"✅ {total} entradas [DEV QA] removidas.")
    return total


def main() -> int:
    parser = argparse.ArgumentParser(description="Padding de catálogo de magias para dev local.")
    parser.add_argument(
        "--target",
        type=int,
        default=DEFAULT_TARGET,
        help=f"Total desejado de magias ativas (padrão {DEFAULT_TARGET}, próximo de produção).",
    )
    parser.add_argument("--dry-run", action="store_true", help="Simula sem gravar.")
    parser.add_argument(
        "--remove",
        action="store_true",
        help="Remove todas as magias [DEV QA] Padding do banco.",
    )
    args = parser.parse_args()

    if _is_production_env():
        print("❌ Recusado: ENVIRONMENT=production. Este script é só para dev/QA local.", file=sys.stderr)
        return 2

    db = SessionLocal()
    try:
        if args.remove:
            remove_padding(db, dry_run=args.dry_run)
            return 0
        pad_catalogo(db, target=max(1, args.target), dry_run=args.dry_run)
        return 0
    except Exception as exc:
        db.rollback()
        print(f"❌ Erro: {exc}", file=sys.stderr)
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
