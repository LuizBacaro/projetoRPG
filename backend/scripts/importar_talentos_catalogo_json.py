"""
Importa o catálogo completo de talentos a partir de talentos_importacao_limpo.json
(gerado por processar_talentos_excel.py na raiz do repositório).

Uso (Neon / produção):
  cd backend && DATABASE_URL='postgresql://...' python scripts/importar_talentos_catalogo_json.py

Uso (SQLite local):
  cd backend && python scripts/importar_talentos_catalogo_json.py

Faz upsert por `nome`: insere novos e atualiza descricao/prerequisitos/secao dos existentes.
Não remove talentos que só existem no banco (ex.: seed mínimo antigo).
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = BACKEND_DIR.parent
DEFAULT_JSON = REPO_ROOT / "talentos_importacao_limpo.json"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.database import SessionLocal  # noqa: E402
from app.models.talento import Talento  # noqa: E402


def _trunc(s: str | None, max_len: int) -> str | None:
    if s is None:
        return None
    s = str(s).strip()
    if len(s) <= max_len:
        return s
    return s[: max_len - 1] + "…"


def main() -> int:
    parser = argparse.ArgumentParser(description="Importar catálogo de talentos (JSON → Postgres/SQLite).")
    parser.add_argument(
        "--json",
        type=Path,
        default=DEFAULT_JSON,
        help=f"Caminho do JSON (default: {DEFAULT_JSON})",
    )
    args = parser.parse_args()

    path: Path = args.json
    if not path.is_file():
        print(f"❌ Arquivo não encontrado: {path}")
        return 1

    with path.open(encoding="utf-8") as f:
        rows: list[dict] = json.load(f)

    db = SessionLocal()
    criados = 0
    atualizados = 0
    try:
        for row in rows:
            nome = _trunc(row.get("nome"), 100)
            if not nome:
                continue

            descricao = _trunc(row.get("beneficios") or row.get("descricao"), 1000)
            prerequisitos = _trunc(row.get("prerequisitos"), 500)
            secao = _trunc(row.get("secao"), 200)
            pagina = _trunc(row.get("pagina_referencia"), 50)

            q = db.query(Talento).filter(Talento.nome == nome, Talento.deleted_at.is_(None))
            existing = q.first()

            if existing:
                existing.descricao = descricao
                existing.prerequisitos = prerequisitos or existing.prerequisitos
                existing.secao = secao or existing.secao
                existing.pagina_referencia = pagina or existing.pagina_referencia
                existing.ativo = True
                atualizados += 1
            else:
                db.add(
                    Talento(
                        nome=nome,
                        descricao=descricao,
                        prerequisitos=prerequisitos,
                        secao=secao,
                        pagina_referencia=pagina or None,
                        ativo=True,
                        criado_em=datetime.now(timezone.utc),
                    )
                )
                criados += 1

        db.commit()
        print(f"✅ Importação concluída: {criados} criados, {atualizados} atualizados (total JSON: {len(rows)})")
        return 0
    except Exception as e:
        db.rollback()
        print(f"❌ Erro: {e}")
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
