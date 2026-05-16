"""Catálogo resumido de feats 5E (~50 entradas por categoria)."""

from __future__ import annotations

from typing import Any, Dict, List

FeatDict = Dict[str, Any]

FEATS_CATALOGO: List[FeatDict] = [
    # Atributo / gerais
    {
        "slug": "ability-score-improvement",
        "nome": "Ability Score Improvement",
        "tipo_bonus": "Atributo",
        "requisito_nivel": 4,
    },
    {"slug": "alert", "nome": "Alert", "tipo_bonus": "Atributo", "requisito_nivel": 1},
    {
        "slug": "athlete",
        "nome": "Athlete",
        "tipo_bonus": "Atributo",
        "requisito_nivel": 1,
    },
    {
        "slug": "resilient",
        "nome": "Resilient",
        "tipo_bonus": "Atributo",
        "requisito_nivel": 1,
    },
    {
        "slug": "war-caster",
        "nome": "War Caster",
        "tipo_bonus": "Atributo",
        "requisitos": ["spellcasting"],
        "requisito_nivel": 1,
    },
    # Combate
    {
        "slug": "archery",
        "nome": "Archery",
        "tipo_bonus": "Combate",
        "bonus_especial": {"ataque_arco": 2},
    },
    {"slug": "blade-master", "nome": "Blade Master", "tipo_bonus": "Combate"},
    {"slug": "charger", "nome": "Charger", "tipo_bonus": "Combate"},
    {
        "slug": "defensive-duelist",
        "nome": "Defensive Duelist",
        "tipo_bonus": "Combate",
        "requisitos": {"dex_min": 13},
    },
    {"slug": "dual-wielder", "nome": "Dual Wielder", "tipo_bonus": "Combate"},
    {
        "slug": "great-weapon-master",
        "nome": "Great Weapon Master",
        "tipo_bonus": "Combate",
        "requisitos": {"str_min": 13},
    },
    {
        "slug": "heavy-armor-master",
        "nome": "Heavy Armor Master",
        "tipo_bonus": "Combate",
    },
    {"slug": "martial-adept", "nome": "Martial Adept", "tipo_bonus": "Combate"},
    {
        "slug": "medium-armor-master",
        "nome": "Medium Armor Master",
        "tipo_bonus": "Combate",
        "requisitos": {"dex_min": 13},
    },
    {"slug": "mounted-combatant", "nome": "Mounted Combatant", "tipo_bonus": "Combate"},
    {"slug": "polearm-master", "nome": "Polearm Master", "tipo_bonus": "Combate"},
    {"slug": "sentinel", "nome": "Sentinel", "tipo_bonus": "Combate"},
    {"slug": "sharpshooter", "nome": "Sharpshooter", "tipo_bonus": "Combate"},
    {
        "slug": "two-weapon-fighting",
        "nome": "Two-Weapon Fighting",
        "tipo_bonus": "Combate",
    },
    # Magia
    {
        "slug": "eldritch-sight",
        "nome": "Eldritch Sight",
        "tipo_bonus": "Magia",
        "requisitos": ["spellcasting"],
    },
    {"slug": "magic-initiate", "nome": "Magic Initiate", "tipo_bonus": "Magia"},
    {
        "slug": "ritual-caster",
        "nome": "Ritual Caster",
        "tipo_bonus": "Magia",
        "requisitos": {"int_min": 13},
    },
    {
        "slug": "spell-sniper",
        "nome": "Spell Sniper",
        "tipo_bonus": "Magia",
        "requisitos": ["spellcasting"],
    },
    {
        "slug": "telekinetic",
        "nome": "Telekinetic",
        "tipo_bonus": "Magia",
        "requisitos": {"cha_min": 13},
    },
    {
        "slug": "telepathic",
        "nome": "Telepathic",
        "tipo_bonus": "Magia",
        "requisitos": {"wis_min": 12},
    },
    # Perícia (amostra)
    {
        "slug": "skilled",
        "nome": "Skilled",
        "tipo_bonus": "Perícia",
        "bonus_especial": {"pericias_extra": 3},
    },
    {"slug": "observant", "nome": "Observant", "tipo_bonus": "Perícia"},
    {
        "slug": "actor",
        "nome": "Actor",
        "tipo_bonus": "Perícia",
        "requisitos": {"cha_min": 13},
    },
    {"slug": "linguist", "nome": "Linguist", "tipo_bonus": "Perícia"},
    {"slug": "expert-duplicator", "nome": "Expert Duplicator", "tipo_bonus": "Perícia"},
    # Utilidade
    {"slug": "lucky", "nome": "Lucky", "tipo_bonus": "Utilidade"},
    {"slug": "healer", "nome": "Healer", "tipo_bonus": "Utilidade"},
    {"slug": "heavily-armored", "nome": "Heavily Armored", "tipo_bonus": "Utilidade"},
    {"slug": "lightly-armored", "nome": "Lightly Armored", "tipo_bonus": "Utilidade"},
    {
        "slug": "moderately-armored",
        "nome": "Moderately Armored",
        "tipo_bonus": "Utilidade",
    },
    {"slug": "mobile", "nome": "Mobile", "tipo_bonus": "Utilidade"},
    {"slug": "dungeon-delver", "nome": "Dungeon Delver", "tipo_bonus": "Utilidade"},
    {
        "slug": "keen-mind",
        "nome": "Keen Mind",
        "tipo_bonus": "Utilidade",
        "requisitos": {"int_min": 13},
    },
    {"slug": "mage-slayer", "nome": "Mage Slayer", "tipo_bonus": "Utilidade"},
    {"slug": "ritualist", "nome": "Ritualist", "tipo_bonus": "Utilidade"},
    {"slug": "savage-attacker", "nome": "Savage Attacker", "tipo_bonus": "Utilidade"},
    {"slug": "shield-master", "nome": "Shield Master", "tipo_bonus": "Utilidade"},
    {"slug": "tavern-brawler", "nome": "Tavern Brawler", "tipo_bonus": "Utilidade"},
    {"slug": "tough", "nome": "Tough", "tipo_bonus": "Utilidade"},
    {"slug": "weapon-master", "nome": "Weapon Master", "tipo_bonus": "Utilidade"},
    {"slug": "crossbow-expert", "nome": "Crossbow Expert", "tipo_bonus": "Combate"},
    {
        "slug": "grappler",
        "nome": "Grappler",
        "tipo_bonus": "Combate",
        "requisitos": {"str_min": 13},
    },
    {
        "slug": "inspiring-leader",
        "nome": "Inspiring Leader",
        "tipo_bonus": "Utilidade",
        "requisitos": {"cha_min": 13},
    },
    {"slug": "magic-user", "nome": "Magic User", "tipo_bonus": "Magia"},
    {
        "slug": "medium-armor-training",
        "nome": "Medium Armor Training",
        "tipo_bonus": "Utilidade",
    },
    {"slug": "polearm-savant", "nome": "Polearm Savant", "tipo_bonus": "Combate"},
    {"slug": "shield-training", "nome": "Shield Training", "tipo_bonus": "Utilidade"},
    {
        "slug": "skulker",
        "nome": "Skulker",
        "tipo_bonus": "Perícia",
        "requisitos": {"dex_min": 13},
    },
    {"slug": "spell-focus", "nome": "Spell Focus", "tipo_bonus": "Magia"},
    {"slug": "weapon-expert", "nome": "Weapon Expert", "tipo_bonus": "Combate"},
]

NIVEIS_GANHO_FEAT = (4, 8, 12, 16, 19)
