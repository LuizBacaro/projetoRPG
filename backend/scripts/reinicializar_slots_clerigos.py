"""
Recalcula e persiste slots de magia no banco para personagens Clérigo,
usando a mesma lógica de POST /combatentes/{id}/inicializar-slots.

Útil após correção da tabela de domínio (truques sem +1 domínio).
Reseta `usados` de cada slot para 0 (equivalente à rota da API).

Uso:
  cd backend && python scripts/reinicializar_slots_clerigos.py
  cd backend && python scripts/reinicializar_slots_clerigos.py --id 9
"""
from __future__ import annotations

import argparse
import os
import sys

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, backend_dir)

from app.core.database import SessionLocal  # noqa: E402
from app.games.dnd35.models.combatente import Combatente  # noqa: E402
from app.repositories.base import apply_not_deleted  # noqa: E402
from app.games.dnd35.repositories.combatente_repository import CombatenteRepository  # noqa: E402
from app.games.dnd35.repositories.condicao_repository import CondicaoRepository  # noqa: E402
from app.games.dnd35.services.combatente_service import CombatenteService  # noqa: E402
from app.services.file_service import FileService  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Reinicializa slots de magia para Clérigos.")
    parser.add_argument(
        "--id",
        type=int,
        default=None,
        help="Apenas este combatente (deve ser classe Clérigo).",
    )
    args = parser.parse_args()

    db = SessionLocal()
    try:
        repo = CombatenteRepository(db)
        cond_repo = CondicaoRepository(db)
        service = CombatenteService(repo, FileService(), cond_repo)

        q = apply_not_deleted(db.query(Combatente), Combatente).filter(Combatente.classe == "Clérigo")
        if args.id is not None:
            q = q.filter(Combatente.id == args.id)
        clerigos = q.order_by(Combatente.id).all()

        if not clerigos:
            print("Nenhum Clérigo encontrado" + (f" com id={args.id}" if args.id else "") + ".")
            return

        for c in clerigos:
            try:
                r = service.inicializar_slots_magia(c.id)
                print(f"OK id={c.id} nome={c.nome!r} -> {r.get('slots_criados')} slots — {r.get('message')}")
            except Exception as e:
                print(f"ERRO id={c.id} nome={c.nome!r}: {e}")
                raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
