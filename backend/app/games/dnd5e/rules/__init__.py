"""Regras D&D 5E (motor puro — sem persistência)."""

from app.games.dnd5e.rules.combate import (
    Combatente,
    RodadaCombate,
    StatusVida,
    ataque_atinge_ca,
    calcular_dano,
    calcular_iniciativa,
    verificar_morte,
)
from app.games.dnd5e.rules.habilidades import (
    AbilityScores,
    PersonagemHabilidades,
    calcular_bonus_proficiencia,
    calcular_modificador,
    validar_valor_habilidade,
)
from app.games.dnd5e.rules.magia import (
    Conjurador,
    calcular_dc_magia,
    lancar_magia,
    recuperar_espacos_repouso_longo,
    salvaguarda_atinge_dc,
)

__all__ = [
    "AbilityScores",
    "PersonagemHabilidades",
    "calcular_modificador",
    "calcular_bonus_proficiencia",
    "validar_valor_habilidade",
    "Combatente",
    "RodadaCombate",
    "StatusVida",
    "calcular_iniciativa",
    "ataque_atinge_ca",
    "calcular_dano",
    "verificar_morte",
    "Conjurador",
    "calcular_dc_magia",
    "lancar_magia",
    "salvaguarda_atinge_dc",
    "recuperar_espacos_repouso_longo",
]
