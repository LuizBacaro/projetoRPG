"""Espaços de feitiço — conjurador completo (Mago, Clérigo, Druida) níveis 1–20."""

from __future__ import annotations

# Índice 0 = truques (sem slot); 1–9 = níveis de magia
FULL_CASTER_SLOTS: dict[int, list[int]] = {
    1: [0, 2, 0, 0, 0, 0, 0, 0, 0, 0],
    2: [0, 3, 0, 0, 0, 0, 0, 0, 0, 0],
    3: [0, 4, 2, 0, 0, 0, 0, 0, 0, 0],
    4: [0, 4, 3, 0, 0, 0, 0, 0, 0, 0],
    5: [0, 4, 3, 2, 0, 0, 0, 0, 0, 0],
    6: [0, 4, 3, 3, 0, 0, 0, 0, 0, 0],
    7: [0, 4, 4, 3, 2, 0, 0, 0, 0, 0],
    8: [0, 4, 4, 3, 3, 0, 0, 0, 0, 0],
    9: [0, 4, 4, 4, 3, 2, 0, 0, 0, 0],
    10: [0, 4, 4, 4, 3, 3, 0, 0, 0, 0],
    11: [0, 4, 4, 4, 4, 3, 2, 0, 0, 0],
    12: [0, 4, 4, 4, 4, 3, 3, 0, 0, 0],
    13: [0, 4, 4, 4, 4, 4, 3, 2, 0, 0],
    14: [0, 4, 4, 4, 4, 4, 3, 3, 0, 0],
    15: [0, 4, 4, 4, 4, 4, 4, 3, 2, 0],
    16: [0, 4, 4, 4, 4, 4, 4, 3, 3, 0],
    17: [0, 4, 4, 4, 4, 4, 4, 4, 3, 2],
    18: [0, 4, 4, 4, 4, 4, 4, 4, 3, 3],
    19: [0, 4, 4, 4, 4, 4, 4, 4, 4, 3],
    20: [0, 4, 4, 4, 4, 4, 4, 4, 4, 4],
}

CLASSE_HABILIDADE_PRIMARIA: dict[str, str] = {
    "mago": "int",
    "clerigo": "wis",
    "druida": "wis",
    "bardo": "cha",
    "feiticeiro": "cha",
    "paladino": "cha",
    "patrulheiro": "wis",
    "bruxo": "cha",
    "monge": "wis",
}
