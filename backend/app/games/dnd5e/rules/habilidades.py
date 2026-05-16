"""Habilidades D&D 5E — modificadores e bônus de proficiência (Cap. 1)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict

HABILIDADE_MIN = 1
HABILIDADE_MAX = 25
NIVEL_MIN = 1
NIVEL_MAX = 20


def validar_valor_habilidade(valor: int) -> None:
    if not HABILIDADE_MIN <= valor <= HABILIDADE_MAX:
        raise ValueError(
            f"Valor de habilidade deve estar entre {HABILIDADE_MIN} e {HABILIDADE_MAX}"
        )


def calcular_modificador(valor: int) -> int:
    """Modificador = (valor - 10) // 2 (arredondado para baixo)."""
    validar_valor_habilidade(valor)
    return (valor - 10) // 2


def calcular_bonus_proficiencia(nivel: int) -> int:
    """Tabela PHB: +2 (1–4), +3 (5–8), +4 (9–12), +5 (13–16), +6 (17–20)."""
    if nivel < NIVEL_MIN:
        nivel = NIVEL_MIN
    if nivel > NIVEL_MAX:
        nivel = NIVEL_MAX
    if nivel <= 4:
        return 2
    if nivel <= 8:
        return 3
    if nivel <= 12:
        return 4
    if nivel <= 16:
        return 5
    return 6


@dataclass(frozen=True)
class AbilityScores:
    """Seis habilidades (STR, DEX, CON, INT, WIS, CHA)."""

    strength: int = 10
    dexterity: int = 10
    constitution: int = 10
    intelligence: int = 10
    wisdom: int = 10
    charisma: int = 10

    def __post_init__(self) -> None:
        for v in (
            self.strength,
            self.dexterity,
            self.constitution,
            self.intelligence,
            self.wisdom,
            self.charisma,
        ):
            validar_valor_habilidade(v)

    def as_dict(self) -> Dict[str, int]:
        return {
            "strength": self.strength,
            "dexterity": self.dexterity,
            "constitution": self.constitution,
            "intelligence": self.intelligence,
            "wisdom": self.wisdom,
            "charisma": self.charisma,
        }


@dataclass
class PersonagemHabilidades:
    """Ficha mínima de atributos + nível com getters de modificador."""

    abilities: AbilityScores = field(default_factory=AbilityScores)
    nivel: int = 1

    def __post_init__(self) -> None:
        if not NIVEL_MIN <= self.nivel <= NIVEL_MAX:
            raise ValueError(f"Nivel deve estar entre {NIVEL_MIN} e {NIVEL_MAX}")

    @property
    def strength_mod(self) -> int:
        return calcular_modificador(self.abilities.strength)

    @property
    def dexterity_mod(self) -> int:
        return calcular_modificador(self.abilities.dexterity)

    @property
    def constitution_mod(self) -> int:
        return calcular_modificador(self.abilities.constitution)

    @property
    def intelligence_mod(self) -> int:
        return calcular_modificador(self.abilities.intelligence)

    @property
    def wisdom_mod(self) -> int:
        return calcular_modificador(self.abilities.wisdom)

    @property
    def charisma_mod(self) -> int:
        return calcular_modificador(self.abilities.charisma)

    @property
    def bonus_proficiencia(self) -> int:
        return calcular_bonus_proficiencia(self.nivel)

    def modificador_salvamento(self, atributo: str, proficiente: bool = False) -> int:
        chave = atributo.strip().lower()
        mods = {
            "str": self.strength_mod,
            "for": self.strength_mod,
            "strength": self.strength_mod,
            "dex": self.dexterity_mod,
            "des": self.dexterity_mod,
            "dexterity": self.dexterity_mod,
            "con": self.constitution_mod,
            "constitution": self.constitution_mod,
            "int": self.intelligence_mod,
            "intelligence": self.intelligence_mod,
            "wis": self.wisdom_mod,
            "sab": self.wisdom_mod,
            "wisdom": self.wisdom_mod,
            "cha": self.charisma_mod,
            "car": self.charisma_mod,
            "charisma": self.charisma_mod,
        }
        base = mods.get(chave, 0)
        return base + (self.bonus_proficiencia if proficiente else 0)
