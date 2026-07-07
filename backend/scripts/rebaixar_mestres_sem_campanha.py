"""
Rebaixa usuários com perfil global `mestre` que não são mestre de nenhuma campanha.

Uso:
  python backend/scripts/rebaixar_mestres_sem_campanha.py
  python backend/scripts/rebaixar_mestres_sem_campanha.py --aplicar
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import app.models  # noqa: F401 — registra todos os mappers antes das queries

from sqlalchemy.orm import Session

from app.games.dnd35.models.campanha import Campanha
from app.games.gurps.models.campanha import GurpsCampanha
from app.games.tormenta.models.campanha import TormentaCampanha
from app.shared.core.database import SessionLocal
from app.shared.models.usuario import PerfilUsuario, Usuario


@dataclass
class CandidatoRebaixamento:
    usuario_id: int
    email: str
    nome: str


def usuario_tem_campanha_como_mestre_em_algum_jogo(
    db: Session, usuario_id: int
) -> bool:
    for model in (Campanha, TormentaCampanha, GurpsCampanha):
        row = (
            db.query(model.id)
            .filter(model.mestre_id == usuario_id)
            .limit(1)
            .scalar()
        )
        if isinstance(row, int):
            return True
    return False


def listar_mestres_sem_campanha(db: Session) -> list[CandidatoRebaixamento]:
    mestres = (
        db.query(Usuario)
        .filter(Usuario.perfil == PerfilUsuario.MESTRE)
        .order_by(Usuario.id.asc())
        .all()
    )
    candidatos: list[CandidatoRebaixamento] = []
    for usuario in mestres:
        if usuario_tem_campanha_como_mestre_em_algum_jogo(db, usuario.id):
            continue
        candidatos.append(
            CandidatoRebaixamento(
                usuario_id=usuario.id,
                email=usuario.email,
                nome=usuario.nome,
            )
        )
    return candidatos


def rebaixar_mestres_sem_campanha(*, aplicar: bool = False) -> tuple[list[CandidatoRebaixamento], int]:
    db = SessionLocal()
    try:
        candidatos = listar_mestres_sem_campanha(db)
        alterados = 0
        if aplicar and candidatos:
            for item in candidatos:
                usuario = db.query(Usuario).filter(Usuario.id == item.usuario_id).first()
                if not usuario or usuario.perfil != PerfilUsuario.MESTRE:
                    continue
                usuario.perfil = PerfilUsuario.JOGADOR
                usuario.usuario_responsavel = "script:rebaixar_mestres_sem_campanha"
                alterados += 1
            db.commit()
        return candidatos, alterados
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Lista ou rebaixa contas com perfil mestre que não possuem "
            "campanha como mestre_id em D&D 3.5, Tormenta ou GURPS."
        )
    )
    parser.add_argument(
        "--aplicar",
        action="store_true",
        help="Persiste perfil=jogador nos candidatos (padrão: dry-run).",
    )
    args = parser.parse_args()

    candidatos, alterados = rebaixar_mestres_sem_campanha(aplicar=args.aplicar)

    if not candidatos:
        print("Nenhum usuário perfil=mestre sem campanha encontrado.")
        return 0

    print(f"Candidatos a rebaixamento ({len(candidatos)}):")
    for item in candidatos:
        print(f"  - id={item.usuario_id} email={item.email} nome={item.nome!r}")

    if args.aplicar:
        print(f"\nRebaixados: {alterados}")
    else:
        print("\nDry-run. Use --aplicar para persistir as alterações.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
