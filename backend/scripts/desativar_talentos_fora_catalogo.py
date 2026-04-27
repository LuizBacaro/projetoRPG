"""
Remove (soft-delete) talentos ativos cujo nome não está em talentos_importacao_limpo.json,
apenas os que nenhuma ficha usa (sem linha em talentos_jogador).

Uso (produção):
  cd backend && DATABASE_URL='postgresql://...' python scripts/desativar_talentos_fora_catalogo.py

Após importar o catálogo com importar_talentos_catalogo_json.py.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.shared.core.database import SessionLocal  # noqa: E402
from app.core.talentos_catalog_seed import (  # noqa: E402
    default_json_path,
    desativar_talentos_fora_do_catalogo,
    load_rows_from_json,
    nomes_catalogo,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", type=Path, default=None, help="JSON do catálogo (default: raiz do repo)")
    args = parser.parse_args()

    path = args.json or default_json_path()
    if not path.is_file():
        print(f"❌ Arquivo não encontrado: {path}")
        return 1

    rows = load_rows_from_json(path)
    nomes = nomes_catalogo(rows)

    db = SessionLocal()
    try:
        removidos, avisos = desativar_talentos_fora_do_catalogo(db, nomes)
        db.commit()
        print(f"✅ Soft-delete de talentos fora do catálogo: {removidos}")
        for a in avisos:
            print(f"ℹ️  {a}")
        return 0
    except Exception as e:
        db.rollback()
        print(f"❌ Erro: {e}")
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
