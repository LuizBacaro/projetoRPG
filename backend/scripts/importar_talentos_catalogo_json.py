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

# Nomes do seed em `init_db.inicializar_talentos` → nome exato no JSON (talentos_importacao_limpo.json).
# Só entram pares com correspondência razoável no LdJ; nomes sem entrada ficam só com o upsert geral por nome igual.
MAPEAMENTO_SEED_PARA_JSON: dict[str, str | None] = {
    "Golpe Poderoso": "Ataque Poderoso¹",
    "Ataque Especial": None,  # não há entrada clara no JSON (nome genérico do seed)
    "Arma Focada": "Foco em Arma¹²",
    "Especialização de Arma": "Especialização em Arma¹²",
    "Lidar com Corda": "Mãos Leves",  # aproximação: bônus em Usar Cordas no mesmo bloco de perícias
    "Vitalidade Aumentada": "Vitalidade³",
    "Reflexos Rápidos": "Reflexos Rápidos",
    "Golpe Girante": "Ataque Giratório¹",
    "Salto Acrobático": "Acrobático",
    "Esquiva Extraordinária": "Mobilidade¹",
    "Defesa Aprimorada": "Esquiva¹",
    "Conjuração Rápida": "Acelerar Magia",
    "Magia Silenciosa": "Magia Silenciosa",
    "Magia Imóvel": "Magia Sem Gestos",
    "Golpe Certeiro": "Acuidade com Arma¹²",
}


def _trunc(s: str | None, max_len: int) -> str | None:
    if s is None:
        return None
    s = str(s).strip()
    if len(s) <= max_len:
        return s
    return s[: max_len - 1] + "…"


def _indice_por_nome_json(rows: list[dict]) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for row in rows:
        n = row.get("nome")
        if isinstance(n, str) and n.strip():
            out[n.strip()] = row
    return out


def _aplicar_mapeamento_seed(
    db,
    rows: list[dict],
) -> tuple[int, list[str]]:
    """Copia benefício/pré-requisitos/seção do JSON para linhas criadas pelo seed (nome diferente)."""
    idx = _indice_por_nome_json(rows)
    atualizados = 0
    avisos: list[str] = []

    for seed_nome, json_nome in MAPEAMENTO_SEED_PARA_JSON.items():
        if not json_nome:
            continue
        if json_nome not in idx:
            avisos.append(f"Nome JSON não encontrado no arquivo: {json_nome!r} (seed {seed_nome!r})")
            continue

        talento = (
            db.query(Talento)
            .filter(Talento.nome == seed_nome, Talento.deleted_at.is_(None))
            .first()
        )
        if not talento:
            avisos.append(f"Seed não encontrado no banco: {seed_nome!r}")
            continue

        src = idx[json_nome]
        talento.descricao = _trunc(src.get("beneficios") or src.get("descricao"), 1000)
        talento.prerequisitos = _trunc(src.get("prerequisitos"), 500)
        talento.secao = _trunc(src.get("secao"), 200)
        talento.pagina_referencia = _trunc(src.get("pagina_referencia"), 50) or talento.pagina_referencia
        talento.ativo = True
        atualizados += 1

    return atualizados, avisos


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

        enriquecidos, avisos_map = _aplicar_mapeamento_seed(db, rows)

        db.commit()
        print(f"✅ Importação concluída: {criados} criados, {atualizados} atualizados (total JSON: {len(rows)})")
        print(f"✅ Enriquecimento seed→catálogo: {enriquecidos} linhas do seed alinhadas ao JSON por nome equivalente.")
        for msg in avisos_map:
            print(f"⚠️  {msg}")
        return 0
    except Exception as e:
        db.rollback()
        print(f"❌ Erro: {e}")
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
