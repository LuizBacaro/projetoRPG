#!/usr/bin/env python3
"""
Aplica traduções PT-BR (Foundry dnd5e-pt-br): nomes e descrições editoriais.

Uso:
  cd backend && python scripts/build_dnd5e_spell_translations_pt.py
  python scripts/apply_dnd5e_magias_pt.py
  python scripts/apply_dnd5e_magias_pt.py --also-metadata  # tempo/alcance/duração
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.games.dnd5e.data.spell_i18n import (
    traduzir_alcance,
    traduzir_duracao,
    traduzir_tempo_conjuracao,
    traduzir_teste_resistencia,
)
from app.games.dnd5e.models.magia import Dnd5eMagia
from app.repositories.base import commit_with_rollback
from app.shared.core.database import SessionLocal

TRANS_PATH = Path(__file__).resolve().parents[1] / "data" / "dnd5e_spell_translations_pt.json"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--also-metadata",
        action="store_true",
        help="Traduz tempo/alcance/duração/resistência (heurística SRD)",
    )
    args = parser.parse_args()

    if not TRANS_PATH.is_file():
        print("Execute antes: python scripts/build_dnd5e_spell_translations_pt.py")
        raise SystemExit(1)

    trans = json.loads(TRANS_PATH.read_text(encoding="utf-8"))
    db = SessionLocal()
    nomes = desc = meta = 0
    try:
        for row in db.query(Dnd5eMagia).filter(Dnd5eMagia.ativo.is_(True)):
            t = trans.get(row.slug)
            if t:
                if t.get("nome_en"):
                    row.nome_en = t["nome_en"]
                elif not row.nome_en and row.nome:
                    row.nome_en = row.nome
                if t.get("nome"):
                    row.nome = t["nome"]
                    nomes += 1
                if t.get("descricao"):
                    if not row.descricao_en and row.descricao:
                        row.descricao_en = row.descricao
                    row.descricao = t["descricao"]
                    desc += 1
                if t.get("descricao_nivel_superior"):
                    row.descricao_nivel_superior = t["descricao_nivel_superior"]

            if args.also_metadata:
                row.tempo_conjuracao = traduzir_tempo_conjuracao(row.tempo_conjuracao)
                row.duracao = traduzir_duracao(row.duracao)
                row.alcance_texto = traduzir_alcance(row.alcance_texto, row.alcance_metros)
                if row.teste_resistencia:
                    row.teste_resistencia = traduzir_teste_resistencia(
                        row.teste_resistencia
                    )
                meta += 1

        commit_with_rollback(db)
        print(
            f"Aplicado: {nomes} nomes, {desc} descrições PT (Foundry), "
            f"metadados={meta if args.also_metadata else 'ignorado'}."
        )
    finally:
        db.close()


if __name__ == "__main__":
    main()
