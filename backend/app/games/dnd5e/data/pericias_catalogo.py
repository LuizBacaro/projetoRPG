"""Dezoito perícias PHB — slug, rótulo PT e habilidade associada."""

from __future__ import annotations

from typing import Any, Dict, List

PericiaDict = Dict[str, Any]

PERICIAS_CATALOGO: List[PericiaDict] = [
    {"slug": "acrobacia", "nome": "Acrobacia", "habilidade": "dexterity"},
    {"slug": "adestrar_animais", "nome": "Adestrar Animais", "habilidade": "wisdom"},
    {"slug": "arcanismo", "nome": "Arcanismo", "habilidade": "intelligence"},
    {"slug": "atletismo", "nome": "Atletismo", "habilidade": "strength"},
    {"slug": "atuacao", "nome": "Atuação", "habilidade": "charisma"},
    {"slug": "enganacao", "nome": "Enganação", "habilidade": "charisma"},
    {"slug": "furtividade", "nome": "Furtividade", "habilidade": "dexterity"},
    {"slug": "historia", "nome": "História", "habilidade": "intelligence"},
    {"slug": "intimidacao", "nome": "Intimidação", "habilidade": "charisma"},
    {"slug": "intuicao", "nome": "Intuição", "habilidade": "wisdom"},
    {"slug": "investigacao", "nome": "Investigação", "habilidade": "intelligence"},
    {"slug": "medicina", "nome": "Medicina", "habilidade": "wisdom"},
    {"slug": "natureza", "nome": "Natureza", "habilidade": "intelligence"},
    {"slug": "percepcao", "nome": "Percepção", "habilidade": "wisdom"},
    {"slug": "persuasao", "nome": "Persuasão", "habilidade": "charisma"},
    {"slug": "prestidigitacao", "nome": "Prestidigitação", "habilidade": "dexterity"},
    {"slug": "religiao", "nome": "Religião", "habilidade": "intelligence"},
    {"slug": "sobrevivencia", "nome": "Sobrevivência", "habilidade": "wisdom"},
]

# Nomes em inglês usados no catálogo de antecedentes (5e-database).
PERICIA_SLUG_POR_NOME_EN: Dict[str, str] = {
    "acrobatics": "acrobacia",
    "animal handling": "adestrar_animais",
    "arcana": "arcanismo",
    "athletics": "atletismo",
    "deception": "enganacao",
    "history": "historia",
    "insight": "intuicao",
    "intimidation": "intimidacao",
    "investigation": "investigacao",
    "medicine": "medicina",
    "nature": "natureza",
    "perception": "percepcao",
    "performance": "atuacao",
    "persuasion": "persuasao",
    "religion": "religiao",
    "sleight of hand": "prestidigitacao",
    "stealth": "furtividade",
    "survival": "sobrevivencia",
}
