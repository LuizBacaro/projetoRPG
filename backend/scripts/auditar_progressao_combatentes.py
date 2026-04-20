"""
Auditoria de progressão de combatentes (BBA e resistências).

Uso:
  python backend/scripts/auditar_progressao_combatentes.py
  python backend/scripts/auditar_progressao_combatentes.py --corrigir
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.bonus_base_ataque import calcular_bonus_base_ataque, calcular_resistencias_base
from app.core.database import SessionLocal
from app.models.combatente import Combatente


@dataclass
class Divergencia:
    combatente_id: int
    nome: str
    classe: str
    nivel: int
    campo: str
    atual: str
    esperado: str


def _mod(valor: int | None) -> int:
    try:
        return (int(valor) - 10) // 2
    except (TypeError, ValueError):
        return 0


def auditar(corrigir: bool = False) -> tuple[list[Divergencia], int]:
    db = SessionLocal()
    divergencias: list[Divergencia] = []
    corrigidos = 0

    try:
        combatentes = db.query(Combatente).filter(Combatente.deleted_at.is_(None)).order_by(Combatente.id).all()
        for c in combatentes:
            bba_esperado = calcular_bonus_base_ataque(c.classe, c.nivel)
            saves_base = calcular_resistencias_base(c.classe, c.nivel)

            if bba_esperado is not None and (c.bonus_base_ataque or "") != bba_esperado:
                divergencias.append(
                    Divergencia(c.id, c.nome, c.classe, c.nivel, "bonus_base_ataque", str(c.bonus_base_ataque), bba_esperado)
                )
                if corrigir:
                    c.bonus_base_ataque = bba_esperado

            if saves_base is not None:
                fort_base, ref_base, vont_base = saves_base
                fort_total = fort_base + _mod(c.constituicao)
                ref_total = ref_base + _mod(c.destreza)
                vont_total = vont_base + _mod(c.sabedoria)

                checks = [
                    ("fortitude_base", c.fortitude_base, fort_base),
                    ("reflexos_base", c.reflexos_base, ref_base),
                    ("vontade_base", c.vontade_base, vont_base),
                    ("fortitude", c.fortitude, fort_total),
                    ("reflexos", c.reflexos, ref_total),
                    ("vontade", c.vontade, vont_total),
                ]
                for campo, atual, esperado in checks:
                    if atual != esperado:
                        divergencias.append(
                            Divergencia(c.id, c.nome, c.classe, c.nivel, campo, str(atual), str(esperado))
                        )
                        if corrigir:
                            setattr(c, campo, esperado)

        if corrigir and divergencias:
            db.commit()
            corrigidos = len({d.combatente_id for d in divergencias})
    finally:
        db.close()

    return divergencias, corrigidos


def main() -> int:
    parser = argparse.ArgumentParser(description="Audita progressão de combatentes")
    parser.add_argument("--corrigir", action="store_true", help="Aplica correções automaticamente")
    args = parser.parse_args()

    divergencias, corrigidos = auditar(corrigir=args.corrigir)
    if not divergencias:
        print("✅ Auditoria concluída: nenhuma divergência encontrada.")
        return 0

    print(f"⚠️  Divergências encontradas: {len(divergencias)}")
    for d in divergencias:
        print(
            f"- #{d.combatente_id} {d.nome} ({d.classe} nv {d.nivel}) "
            f"{d.campo}: atual={d.atual} esperado={d.esperado}"
        )

    if args.corrigir:
        print(f"✅ Correção aplicada em {corrigidos} combatente(s).")
    else:
        print("ℹ️  Execute com --corrigir para aplicar as correções.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
