"""
Popula dnd5e_magias e dnd5e_magias_classes a partir de SpellDatabase.json.

Uso:
  cd backend && python scripts/seed_dnd5e_magias.py
  python scripts/seed_dnd5e_magias.py --json ../frontend/games/dnd5e/spellcasting/data/SpellDatabase.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.games.dnd5e.models.magia import Dnd5eMagia, Dnd5eMagiaClasse
from app.shared.core.database import SessionLocal
from app.repositories.base import commit_with_rollback

SAVE_MAP = {
    "strength": "for",
    "dexterity": "dex",
    "constitution": "con",
    "intelligence": "int",
    "wisdom": "wis",
    "charisma": "cha",
    "nenhum": "nenhum",
    "reflexos": "dex",
    "fortitude": "con",
    "vontade": "wis",
}

CASTING_UNIT = {
    "action": "1 ação",
    "bonus_action": "1 ação bônus",
    "reaction": "1 reação",
    "minute": "1 minuto",
    "hour": "1 hora",
}

RANGE_KIND = {
    "self": "Pessoal",
    "touch": "Toque",
    "feet": None,
    "sight": "Visão",
    "unlimited": "Ilimitado",
}


def _alcance(spell: dict) -> tuple[str | None, int | None]:
    r = spell.get("range") or {}
    kind = r.get("kind")
    if kind == "feet" and r.get("value"):
        metros = int(round(r["value"] * 0.3))
        return f"{metros} m", r["value"]
    return RANGE_KIND.get(kind), r.get("value")


def _duracao(spell: dict) -> str:
    d = spell.get("duration") or {}
    if d.get("instantaneous"):
        return "Instantâneo"
    if d.get("untilDispelled"):
        return "Até dissipar"
    val = d.get("value")
    unit = d.get("unit") or "minute"
    if not val:
        return ""
    unit_pt = {"round": "rodada", "minute": "minuto", "hour": "hora", "day": "dia"}.get(
        unit, unit
    )
    base = f"{val} {unit_pt}"
    if spell.get("concentration"):
        return f"Concentração, {base}"
    return base


def spell_to_row(spell: dict) -> Dnd5eMagia:
    comp = spell.get("components") or {}
    save = spell.get("saveInfo") or {}
    save_ability = save.get("ability")
    teste = SAVE_MAP.get(save_ability, save_ability) if save_ability else "nenhum"
    alcance_texto, alcance_metros = _alcance(spell)
    ct = spell.get("castingTime") or {}
    return Dnd5eMagia(
        slug=spell["id"],
        nome=spell["name"],
        nivel=int(spell.get("level", 0)),
        escola=(spell.get("school") or "").lower(),
        tempo_conjuracao=CASTING_UNIT.get(ct.get("unit"), "1 ação"),
        alcance_texto=alcance_texto,
        alcance_metros=alcance_metros,
        duracao=_duracao(spell),
        requer_concentracao=bool(spell.get("concentration")),
        ritual=bool(ct.get("ritual")),
        componentes_verbal=bool(comp.get("verbal")),
        componentes_somatico=bool(comp.get("somatic")),
        componentes_material=comp.get("material"),
        material_consumido=bool(comp.get("materialConsumed")),
        material_custo_gp=int(comp.get("materialCost") or 0),
        dano=(spell.get("damageInfo") or {}).get("dice"),
        teste_resistencia=teste if teste else "nenhum",
        descricao=spell.get("description"),
        descricao_nivel_superior=spell.get("higherLevelDescription"),
        ativo=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--json",
        default=str(
            Path(__file__).resolve().parents[2]
            / "frontend/games/dnd5e/spellcasting/data/SpellDatabase.json"
        ),
    )
    args = parser.parse_args()
    data = json.loads(Path(args.json).read_text(encoding="utf-8"))
    spells = data.get("spells") or []

    db = SessionLocal()
    try:
        inseridas = 0
        for spell in spells:
            slug = spell["id"]
            existente = db.query(Dnd5eMagia).filter(Dnd5eMagia.slug == slug).first()
            if existente:
                magia = existente
            else:
                magia = spell_to_row(spell)
                db.add(magia)
                db.flush()
                inseridas += 1

            for classe_slug in spell.get("classes") or []:
                slug_cls = str(classe_slug).strip().lower()
                ja = (
                    db.query(Dnd5eMagiaClasse)
                    .filter(
                        Dnd5eMagiaClasse.magia_id == magia.id,
                        Dnd5eMagiaClasse.classe_slug == slug_cls,
                    )
                    .first()
                )
                if not ja:
                    db.add(
                        Dnd5eMagiaClasse(
                            magia_id=magia.id,
                            classe_slug=slug_cls,
                            nivel=magia.nivel,
                        )
                    )
        commit_with_rollback(db)
        print(f"Seed 5e: {inseridas} magias novas, {len(spells)} no JSON.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
