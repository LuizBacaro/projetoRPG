"""Catálogo resumido de talentos (feats) 5E — nomes em português (PHB)."""

from __future__ import annotations

from typing import Any, Dict, List

FeatDict = Dict[str, Any]

FEATS_CATALOGO: List[FeatDict] = [
    # Atributo / gerais
    {"slug": "alert", "nome": "Alerta", "tipo_bonus": "Atributo", "requisito_nivel": 1},
    {"slug": "athlete", "nome": "Atleta", "tipo_bonus": "Atributo", "requisito_nivel": 1},
    {
        "slug": "resilient",
        "nome": "Resiliente",
        "tipo_bonus": "Atributo",
        "requisito_nivel": 1,
    },
    {
        "slug": "war-caster",
        "nome": "Conjurador em Combate",
        "tipo_bonus": "Atributo",
        "requisitos": ["spellcasting"],
        "requisito_nivel": 1,
    },
    # Combate
    {
        "slug": "archery",
        "nome": "Arquearia",
        "tipo_bonus": "Combate",
        "bonus_especial": {"ataque_arco": 2},
    },
    {"slug": "blade-master", "nome": "Mestre das Lâminas", "tipo_bonus": "Combate"},
    {"slug": "charger", "nome": "Investida", "tipo_bonus": "Combate"},
    {
        "slug": "defensive-duelist",
        "nome": "Duelista Defensivo",
        "tipo_bonus": "Combate",
        "requisitos": {"dex_min": 13},
    },
    {"slug": "dual-wielder", "nome": "Empunhadura Dupla", "tipo_bonus": "Combate"},
    {
        "slug": "great-weapon-master",
        "nome": "Mestre em Armas Grandes",
        "tipo_bonus": "Combate",
        "requisitos": {"str_min": 13},
    },
    {
        "slug": "heavy-armor-master",
        "nome": "Mestre em Armadura Pesada",
        "tipo_bonus": "Combate",
    },
    {"slug": "martial-adept", "nome": "Adepto Marcial", "tipo_bonus": "Combate"},
    {
        "slug": "medium-armor-master",
        "nome": "Mestre em Armadura Média",
        "tipo_bonus": "Combate",
        "requisitos": {"dex_min": 13},
    },
    {"slug": "mounted-combatant", "nome": "Combatente Montado", "tipo_bonus": "Combate"},
    {"slug": "polearm-master", "nome": "Mestre em Armas de Haste", "tipo_bonus": "Combate"},
    {"slug": "sentinel", "nome": "Sentinela", "tipo_bonus": "Combate"},
    {"slug": "sharpshooter", "nome": "Atirador de Elite", "tipo_bonus": "Combate"},
    {
        "slug": "two-weapon-fighting",
        "nome": "Combate com Duas Armas",
        "tipo_bonus": "Combate",
    },
    # Magia
    {
        "slug": "eldritch-sight",
        "nome": "Visão Mística",
        "tipo_bonus": "Magia",
        "requisitos": ["spellcasting"],
    },
    {"slug": "magic-initiate", "nome": "Iniciado em Magia", "tipo_bonus": "Magia"},
    {
        "slug": "ritual-caster",
        "nome": "Conjurador Ritualístico",
        "tipo_bonus": "Magia",
        "requisitos": {"int_min": 13},
    },
    {
        "slug": "spell-sniper",
        "nome": "Atirador de Magias",
        "tipo_bonus": "Magia",
        "requisitos": ["spellcasting"],
    },
    {
        "slug": "telekinetic",
        "nome": "Telecinético",
        "tipo_bonus": "Magia",
        "requisitos": {"cha_min": 13},
    },
    {
        "slug": "telepathic",
        "nome": "Telepático",
        "tipo_bonus": "Magia",
        "requisitos": {"wis_min": 12},
    },
    # Perícia
    {
        "slug": "skilled",
        "nome": "Habilidoso",
        "tipo_bonus": "Perícia",
        "bonus_especial": {"pericias_extra": 3},
    },
    {"slug": "observant", "nome": "Observador", "tipo_bonus": "Perícia"},
    {
        "slug": "actor",
        "nome": "Ator",
        "tipo_bonus": "Perícia",
        "requisitos": {"cha_min": 13},
    },
    {"slug": "linguist", "nome": "Linguista", "tipo_bonus": "Perícia"},
    {"slug": "expert-duplicator", "nome": "Especialista em Cópias", "tipo_bonus": "Perícia"},
    # Utilidade
    {"slug": "lucky", "nome": "Sortudo", "tipo_bonus": "Utilidade"},
    {"slug": "healer", "nome": "Curandeiro", "tipo_bonus": "Utilidade"},
    {"slug": "heavily-armored", "nome": "Armadura Pesada", "tipo_bonus": "Utilidade"},
    {"slug": "lightly-armored", "nome": "Armadura Leve", "tipo_bonus": "Utilidade"},
    {
        "slug": "moderately-armored",
        "nome": "Armadura Média",
        "tipo_bonus": "Utilidade",
    },
    {"slug": "mobile", "nome": "Ágil", "tipo_bonus": "Utilidade"},
    {"slug": "dungeon-delver", "nome": "Explorador de Masmorras", "tipo_bonus": "Utilidade"},
    {
        "slug": "keen-mind",
        "nome": "Mente Aguçada",
        "tipo_bonus": "Utilidade",
        "requisitos": {"int_min": 13},
    },
    {"slug": "mage-slayer", "nome": "Matador de Magos", "tipo_bonus": "Utilidade"},
    {"slug": "ritualist", "nome": "Ritualista", "tipo_bonus": "Utilidade"},
    {"slug": "savage-attacker", "nome": "Atacante Selvagem", "tipo_bonus": "Utilidade"},
    {"slug": "shield-master", "nome": "Mestre em Escudos", "tipo_bonus": "Utilidade"},
    {"slug": "tavern-brawler", "nome": "Brigão de Taverna", "tipo_bonus": "Utilidade"},
    {"slug": "tough", "nome": "Robusto", "tipo_bonus": "Utilidade"},
    {"slug": "weapon-master", "nome": "Mestre em Armas", "tipo_bonus": "Utilidade"},
    {"slug": "crossbow-expert", "nome": "Especialista em Bestas", "tipo_bonus": "Combate"},
    {
        "slug": "grappler",
        "nome": "Agarrador",
        "tipo_bonus": "Combate",
        "requisitos": {"str_min": 13},
    },
    {
        "slug": "inspiring-leader",
        "nome": "Líder Inspirador",
        "tipo_bonus": "Utilidade",
        "requisitos": {"cha_min": 13},
    },
    {"slug": "magic-user", "nome": "Usuário de Magia", "tipo_bonus": "Magia"},
    {
        "slug": "medium-armor-training",
        "nome": "Treinamento em Armadura Média",
        "tipo_bonus": "Utilidade",
    },
    {"slug": "polearm-savant", "nome": "Especialista em Haste", "tipo_bonus": "Combate"},
    {"slug": "shield-training", "nome": "Treinamento com Escudo", "tipo_bonus": "Utilidade"},
    {
        "slug": "skulker",
        "nome": "Furtivo",
        "tipo_bonus": "Perícia",
        "requisitos": {"dex_min": 13},
    },
    {"slug": "spell-focus", "nome": "Foco em Magia", "tipo_bonus": "Magia"},
    {"slug": "weapon-expert", "nome": "Especialista em Armas", "tipo_bonus": "Combate"},
]

NIVEIS_GANHO_FEAT = (4, 8, 12, 16, 19)
