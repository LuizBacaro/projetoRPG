"""
Importa o catálogo completo de talentos a partir de talentos_importacao_limpo.json
(gerado por processar_talentos_excel.py na raiz do repositório).

Uso (Neon / produção):
  cd backend && DATABASE_URL='postgresql://...' python scripts/importar_talentos_catalogo_json.py

Uso (SQLite local):
  cd backend && python scripts/importar_talentos_catalogo_json.py

Opções:
  --remover-legado  Soft-delete de talentos que não estão no JSON e não estão em uso em fichas.

Faz upsert por `nome`: insere novos e atualiza descricao/prerequisitos/secao dos existentes.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = BACKEND_DIR.parent
DEFAULT_JSON = REPO_ROOT / "talentos_importacao_limpo.json"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.shared.core.database import SessionLocal  # noqa: E402
from app.games.dnd35.catalogs.talentos_catalog_seed import (  # noqa: E402
    aplicar_mapeamento_seed_antigo,
    default_json_path,
    desativar_talentos_fora_do_catalogo,
    load_rows_from_json,
    nomes_catalogo,
    upsert_talentos_from_rows,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Importar catálogo de talentos (JSON → Postgres/SQLite).")
    parser.add_argument(
        "--json",
        type=Path,
        default=None,
        help=f"Caminho do JSON (default: {DEFAULT_JSON})",
    )
    parser.add_argument(
        "--remover-legado",
        action="store_true",
        help="Remove (soft-delete) talentos ativos que não estão no JSON e não têm uso em talentos_jogador.",
    )
    args = parser.parse_args()

    path: Path = args.json or default_json_path()
    if not path.is_file():
        print(f"❌ Arquivo não encontrado: {path}")
        return 1

    rows = load_rows_from_json(path)
    db = SessionLocal()
    try:
        criados, atualizados = upsert_talentos_from_rows(db, rows)
        enriquecidos, avisos_map = aplicar_mapeamento_seed_antigo(db, rows)

        removidos = 0
        avisos_legado: list[str] = []
        if args.remover_legado:
            removidos, avisos_legado = desativar_talentos_fora_do_catalogo(db, nomes_catalogo(rows))

        db.commit()
        print(f"✅ Importação concluída: {criados} criados, {atualizados} atualizados (total JSON: {len(rows)})")
        print(f"✅ Enriquecimento seed→catálogo: {enriquecidos} linhas do seed alinhadas ao JSON por nome equivalente.")
        for msg in avisos_map:
            print(f"⚠️  {msg}")
        if args.remover_legado:
            print(f"✅ Talentos legados removidos (soft-delete): {removidos}")
            for msg in avisos_legado:
                print(f"ℹ️  {msg}")
        return 0
    except Exception as e:
        db.rollback()
        print(f"❌ Erro: {e}")
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
