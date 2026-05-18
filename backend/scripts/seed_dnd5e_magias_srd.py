#!/usr/bin/env python3
"""
Importa/atualiza magias SRD (5e-database) em dnd5e_magias.

Fonte: backend/data/dnd5e_srd_spells_en.json
  (baixar: curl -fsSL .../src/2014/en/5e-SRD-Spells.json -o backend/data/dnd5e_srd_spells_en.json)

Uso:
  cd backend && python scripts/seed_dnd5e_magias_srd.py
  python scripts/seed_dnd5e_magias_srd.py --fetch   # baixa JSON antes de importar
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.games.dnd5e.data.spell_i18n import (
    traduzir_alcance,
    traduzir_descricao_srd,
    traduzir_duracao,
    traduzir_tempo_conjuracao,
    traduzir_teste_resistencia,
)
from app.games.dnd5e.models.magia import Dnd5eMagia, Dnd5eMagiaClasse
from app.repositories.base import commit_with_rollback
from app.shared.core.database import SessionLocal

SRD_URL = (
    "https://raw.githubusercontent.com/5e-bits/5e-database/"
    "main/src/2014/en/5e-SRD-Spells.json"
)
DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "dnd5e_srd_spells_en.json"
TRANS_PATH = Path(__file__).resolve().parents[1] / "data" / "dnd5e_spell_translations_pt.json"

CLASS_MAP = {
    "wizard": "mago",
    "sorcerer": "feiticeiro",
    "warlock": "bruxo",
    "cleric": "clerigo",
    "druid": "druida",
    "bard": "bardo",
    "paladin": "paladino",
    "ranger": "patrulheiro",
    "artificer": "artifice",
}

SCHOOL_PT = {
    "abjuration": "abjuracao",
    "conjuration": "conjuracao",
    "divination": "adivinhacao",
    "enchantment": "encantamento",
    "evocation": "evocacao",
    "illusion": "ilusao",
    "necromancy": "necromancia",
    "transmutation": "transmutacao",
}


def _fetch_json(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(SRD_URL, timeout=120) as resp:
        path.write_bytes(resp.read())
    print(f"Baixado → {path}")


def _parse_range_feet(text: str) -> tuple[str | None, int | None]:
    s = (text or "").strip().lower()
    if s in ("self",):
        return "Pessoal", None
    if s in ("touch",):
        return "Toque", None
    m = re.match(r"(\d+)\s*feet", s)
    if m:
        ft = int(m.group(1))
        return f"{int(round(ft * 0.3))} m", ft
    if "mile" in s:
        return text, None
    return text or None, None


def _dano(spell: dict) -> str | None:
    dmg = spell.get("damage") or {}
    if not dmg:
        return None
    at_char = dmg.get("damage_at_character_level") or {}
    if at_char:
        return str(at_char.get("1") or at_char.get("5") or "")
    at_slot = dmg.get("damage_at_slot_level") or {}
    if at_slot:
        return str(at_slot.get(str(spell.get("level") or 1)) or "")
    return None


def _save(spell: dict) -> str:
    for key in ("dexterity", "constitution", "wisdom", "intelligence", "charisma", "strength"):
        dc = spell.get(f"dc_{key}")
        if dc:
            mapa = {
                "dexterity": "dex",
                "constitution": "con",
                "wisdom": "wis",
                "intelligence": "int",
                "charisma": "cha",
                "strength": "for",
            }
            return mapa.get(key, "nenhum")
    return "nenhum"


def _load_translations() -> dict:
    if not TRANS_PATH.is_file():
        return {}
    return json.loads(TRANS_PATH.read_text(encoding="utf-8"))


def spell_to_magia(spell: dict, trans: dict | None = None) -> Dnd5eMagia:
    comps = spell.get("components") or []
    school = spell.get("school") or {}
    school_idx = (school.get("index") or "").lower()
    desc = spell.get("desc") or []
    higher = spell.get("higher_level") or []
    alcance, metros = _parse_range_feet(spell.get("range") or "")
    slug = spell["index"]
    nome_en = spell["name"]
    t = (trans or {}).get(slug) or {}
    desc_en = "\n".join(desc) if desc else None
    desc_higher_en = "\n".join(higher) if higher else None
    desc_pt = t.get("descricao") or traduzir_descricao_srd(desc_en)
    desc_sup_pt = t.get("descricao_nivel_superior") or (
        traduzir_descricao_srd(desc_higher_en) if desc_higher_en else None
    )
    attack = spell.get("attack_type")
    return Dnd5eMagia(
        slug=slug,
        nome=t.get("nome") or nome_en,
        nome_en=nome_en,
        ataque_magico=attack if attack in ("ranged", "melee") else None,
        nivel=int(spell.get("level") or 0),
        escola=SCHOOL_PT.get(school_idx, school_idx or None),
        tempo_conjuracao=traduzir_tempo_conjuracao(spell.get("casting_time")),
        alcance_texto=traduzir_alcance(alcance, metros),
        alcance_metros=metros,
        duracao=traduzir_duracao(spell.get("duration")),
        requer_concentracao=bool(spell.get("concentration")),
        ritual=bool(spell.get("ritual")),
        componentes_verbal="V" in comps,
        componentes_somatico="S" in comps,
        componentes_material=spell.get("material"),
        dano=_dano(spell),
        teste_resistencia=traduzir_teste_resistencia(_save(spell)),
        descricao=desc_pt if desc_pt else None,
        descricao_en=desc_en,
        descricao_nivel_superior=desc_sup_pt,
        ativo=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fetch", action="store_true")
    args = parser.parse_args()

    if args.fetch or not DATA_PATH.is_file():
        _fetch_json(DATA_PATH)

    spells = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    trans = _load_translations()
    db = SessionLocal()
    novas = atualizadas = vinculos = 0
    try:
        for spell in spells:
            slug = spell["index"]
            row = db.query(Dnd5eMagia).filter(Dnd5eMagia.slug == slug).first()
            parsed = spell_to_magia(spell, trans)
            if row:
                for attr in (
                    "nome",
                    "nome_en",
                    "nivel",
                    "escola",
                    "tempo_conjuracao",
                    "alcance_texto",
                    "alcance_metros",
                    "duracao",
                    "requer_concentracao",
                    "ritual",
                    "componentes_verbal",
                    "componentes_somatico",
                    "componentes_material",
                    "dano",
                    "teste_resistencia",
                    "descricao",
                    "descricao_en",
                    "descricao_nivel_superior",
                    "ataque_magico",
                ):
                    setattr(row, attr, getattr(parsed, attr))
                magia = row
                atualizadas += 1
            else:
                magia = parsed
                db.add(magia)
                db.flush()
                novas += 1

            classes = {
                CLASS_MAP.get((c.get("index") or "").lower())
                for c in (spell.get("classes") or [])
            }
            classes.discard(None)
            for cls in classes:
                ja = (
                    db.query(Dnd5eMagiaClasse)
                    .filter(
                        Dnd5eMagiaClasse.magia_id == magia.id,
                        Dnd5eMagiaClasse.classe_slug == cls,
                    )
                    .first()
                )
                if not ja:
                    db.add(
                        Dnd5eMagiaClasse(
                            magia_id=magia.id,
                            classe_slug=cls,
                            nivel=magia.nivel,
                        )
                    )
                    vinculos += 1
        commit_with_rollback(db)
        print(
            f"SRD: {novas} novas, {atualizadas} atualizadas, "
            f"{vinculos} vínculos classe novos ({len(spells)} no JSON)."
        )
    finally:
        db.close()


if __name__ == "__main__":
    main()
