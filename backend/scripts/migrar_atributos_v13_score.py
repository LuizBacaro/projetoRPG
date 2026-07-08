"""
RF-T01-ui-n — Detecta e migra atributos v1.3 salvos como score 10–18.

Fichas MB (`regra_versao` ausente ou `mb`) não são alteradas.

Uso (a partir da raiz do repo):
  python3 backend/scripts/migrar_atributos_v13_score.py
  python3 backend/scripts/migrar_atributos_v13_score.py --aplicar
  python3 backend/scripts/migrar_atributos_v13_score.py --id 42
  python3 backend/scripts/migrar_atributos_v13_score.py --aplicar --id 42
  python3 backend/scripts/migrar_atributos_v13_score.py --json

Requer DATABASE_URL (ou .env) como os demais scripts do backend.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import app.models  # noqa: F401 — registra mappers SQLAlchemy

from app.games.tormenta.models.personagem import TormentaPersonagem
from app.games.tormenta.rules.atributos_migracao_v13_t20 import (
    ATTR_COLS,
    aplicar_plano_migracao,
    planejar_migracao_personagem,
    resumo_plano,
)
from app.shared.core.database import SessionLocal


def _row_dict(p: TormentaPersonagem) -> Dict[str, Any]:
    return {col: getattr(p, col) for col in ATTR_COLS}


def auditar_e_migrar(
    *,
    aplicar: bool = False,
    personagem_id: Optional[int] = None,
) -> tuple[List[dict], int]:
    db = SessionLocal()
    relatorio: List[dict] = []
    migrados = 0

    try:
        q = db.query(TormentaPersonagem).order_by(TormentaPersonagem.id.asc())
        if personagem_id is not None:
            q = q.filter(TormentaPersonagem.id == int(personagem_id))

        for p in q.all():
            plano = planejar_migracao_personagem(
                personagem_id=p.id,
                nome=p.nome,
                tipo=p.tipo,
                ficha_json=p.ficha_json if isinstance(p.ficha_json, dict) else {},
                atributos_colunas=_row_dict(p),
            )
            if plano is None or not plano.precisa_migrar:
                continue

            item = {
                "personagem_id": plano.personagem_id,
                "nome": plano.nome,
                "tipo": plano.tipo,
                "motivo": plano.motivo,
                "alteracoes": [
                    {"campo": a.campo, "antes": a.antes, "depois": a.depois}
                    for a in plano.alteracoes_colunas + plano.alteracoes_compra
                ],
            }

            if aplicar:
                row = {
                    **{col: getattr(p, col) for col in ATTR_COLS},
                    "ficha_json": dict(p.ficha_json or {}),
                }
                snapshot = aplicar_plano_migracao(row, plano)
                for col in ATTR_COLS:
                    setattr(p, col, row[col])
                p.ficha_json = row["ficha_json"]
                item["snapshot"] = snapshot
                migrados += 1

            relatorio.append(item)

        if aplicar and migrados:
            db.commit()
    finally:
        db.close()

    return relatorio, migrados


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Migra atributos v1.3 gravados como score 10–18 (RF-T01-ui-n)"
    )
    parser.add_argument(
        "--aplicar",
        action="store_true",
        help="Persiste alterações (padrão: dry-run)",
    )
    parser.add_argument(
        "--id",
        type=int,
        default=None,
        help="Processa apenas este personagem Tormenta",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Saída em JSON (útil para CI/log)",
    )
    args = parser.parse_args()

    relatorio, migrados = auditar_e_migrar(
        aplicar=args.aplicar,
        personagem_id=args.id,
    )

    if args.json:
        print(
            json.dumps(
                {
                    "modo": "aplicar" if args.aplicar else "dry_run",
                    "candidatos": len(relatorio),
                    "migrados": migrados if args.aplicar else 0,
                    "itens": relatorio,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    if not relatorio:
        print("Nenhuma ficha v1.3 candidata à migração de score→nativo.")
        return 0

    print(
        f"{'Aplicando' if args.aplicar else 'Dry-run'}: "
        f"{len(relatorio)} ficha(s) candidata(s)."
    )
    for item in relatorio:
        print("---")
        print(
            f"#{item['personagem_id']} {item['nome']!r} ({item['tipo']}) "
            f"[{item['motivo']}]"
        )
        for alt in item["alteracoes"]:
            print(f"  {alt['campo']}: {alt['antes']} → {alt['depois']}")

    if args.aplicar:
        print(f"\nMigradas: {migrados} ficha(s). Auditoria em ficha_json._migracao_atributos_v13_score")
    else:
        print("\nDry-run concluído. Use --aplicar para gravar.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
