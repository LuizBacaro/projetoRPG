"""
Soft-delete de itens do catálogo de equipamentos por nome exato.

Uso (produção, após conferir nomes):
  cd backend && DATABASE_URL='postgresql://...' python3 scripts/soft_delete_equipamentos_por_nome.py --dry-run
  cd backend && DATABASE_URL='postgresql://...' python3 scripts/soft_delete_equipamentos_por_nome.py

Lista padrão cobre entradas legadas comuns (ajuste ou passe nomes na linha de comando).

Nota: o cache em memória da API não é invalidado por este processo; a lista pode
atualizar após o TTL ou use DELETE /api/v1/equipamentos/catalogo/{id} (admin) por item
para invalidar na hora.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy.orm import Session  # noqa: E402

from app.shared.core.database import SessionLocal  # noqa: E402
from app.games.dnd35.models.equipamento import Equipamento, EquipamentoJogador  # noqa: E402
from app.repositories.base import apply_not_deleted  # noqa: E402
from app.games.dnd35.repositories.equipamento_repository import EquipamentoRepository  # noqa: E402

DEFAULT_NOMES = (
    "Espada Longa",
    "Espada Curta",
    "Machado Grande",
    "Maça",
)


def _equipamento_ativo_por_nome(db: Session, nome: str) -> Equipamento | None:
    return (
        apply_not_deleted(db.query(Equipamento), Equipamento)
        .filter(Equipamento.nome == nome, Equipamento.ativo.is_(True))
        .first()
    )


def _count_uso_jogador(db: Session, equipamento_id: int) -> int:
    return (
        db.query(EquipamentoJogador)
        .filter(EquipamentoJogador.equipamento_id == equipamento_id)
        .count()
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Soft-delete de equipamentos do catálogo por nome.")
    parser.add_argument(
        "nomes",
        nargs="*",
        default=list(DEFAULT_NOMES),
        help=f"Nomes exatos (default: {len(DEFAULT_NOMES)} itens legados comuns)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Apenas mostra o que seria feito.")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Soft-delete mesmo se ainda existir em equipamentos_jogador (use com cuidado).",
    )
    args = parser.parse_args()

    db = SessionLocal()
    try:
        removidos = 0
        for nome in args.nomes:
            eq = _equipamento_ativo_por_nome(db, nome)
            if not eq:
                print(f"⏭️  Não encontrado ou já inativo: {nome!r}")
                continue
            uso = _count_uso_jogador(db, eq.id)
            if uso and not args.force:
                print(f"⚠️  Pulando {nome!r} (id={eq.id}): {uso} uso(s) em fichas — use --force se tiver certeza")
                continue
            if uso and args.force:
                print(f"⚠️  Forçando {nome!r} (id={eq.id}) apesar de {uso} uso(s) em fichas")
            if args.dry_run:
                print(f"[dry-run] removeria {nome!r} (id={eq.id})")
                continue
            if EquipamentoRepository.deletar_equipamento(db, eq.id):
                removidos += 1
                print(f"✅ Soft-delete: {nome!r} (id={eq.id})")
            else:
                print(f"❌ Falha ao remover {nome!r} (id={eq.id})")

        if not args.dry_run:
            db.commit()
            print(f"✅ Concluído. Removidos: {removidos}")
        else:
            print("ℹ️  Dry-run: nenhuma alteração gravada.")
        return 0
    except Exception as e:
        db.rollback()
        print(f"❌ Erro: {e}")
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
