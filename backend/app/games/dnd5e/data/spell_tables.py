"""Tabelas PHB — slots, magias conhecidas e preparação (D&D 5e)."""

from __future__ import annotations

# Índice = nível da magia (0 = truque); valor = slots totais
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

# Bruxo — todos os slots no mesmo nível (índice do nível do slot usado)
WARLOCK_SLOTS: dict[int, tuple[int, int]] = {
    # nivel_personagem: (qtd_slots, nivel_do_slot)
    1: (1, 1),
    2: (2, 1),
    3: (2, 2),
    4: (2, 2),
    5: (2, 3),
    6: (2, 3),
    7: (2, 4),
    8: (2, 4),
    9: (2, 5),
    10: (2, 5),
    11: (3, 5),
    12: (3, 5),
    13: (3, 6),
    14: (3, 6),
    15: (3, 7),
    16: (3, 7),
    17: (4, 7),
    18: (4, 7),
    19: (4, 8),
    20: (4, 8),
}

# Paladino / Patrulheiro (meio-conjurador)
HALF_CASTER_SLOTS: dict[int, list[int]] = {
    1: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    2: [0, 2, 0, 0, 0, 0, 0, 0, 0, 0],
    3: [0, 3, 0, 0, 0, 0, 0, 0, 0, 0],
    4: [0, 3, 0, 0, 0, 0, 0, 0, 0, 0],
    5: [0, 4, 2, 0, 0, 0, 0, 0, 0, 0],
    6: [0, 4, 2, 0, 0, 0, 0, 0, 0, 0],
    7: [0, 4, 3, 0, 0, 0, 0, 0, 0, 0],
    8: [0, 4, 3, 0, 0, 0, 0, 0, 0, 0],
    9: [0, 4, 3, 2, 0, 0, 0, 0, 0, 0],
    10: [0, 4, 3, 2, 0, 0, 0, 0, 0, 0],
    11: [0, 4, 3, 3, 0, 0, 0, 0, 0, 0],
    12: [0, 4, 3, 3, 0, 0, 0, 0, 0, 0],
    13: [0, 4, 3, 3, 1, 0, 0, 0, 0, 0],
    14: [0, 4, 3, 3, 1, 0, 0, 0, 0, 0],
    15: [0, 4, 3, 3, 2, 0, 0, 0, 0, 0],
    16: [0, 4, 3, 3, 2, 0, 0, 0, 0, 0],
    17: [0, 4, 3, 3, 2, 1, 0, 0, 0, 0],
    18: [0, 4, 3, 3, 2, 1, 0, 0, 0, 0],
    19: [0, 4, 3, 3, 2, 2, 0, 0, 0, 0],
    20: [0, 4, 3, 3, 2, 2, 0, 0, 0, 0],
}

# Magias conhecidas (Bardo, Feiticeiro, Bruxo, etc.) — total excluindo truques
KNOWN_SPELLS_FULL: dict[int, int] = {
    1: 2,
    2: 3,
    3: 4,
    4: 5,
    5: 6,
    6: 7,
    7: 8,
    8: 9,
    9: 10,
    10: 11,
    11: 12,
    12: 12,
    13: 13,
    14: 13,
    15: 14,
    16: 14,
    17: 15,
    18: 15,
    19: 15,
    20: 15,
}

KNOWN_SPELLS_WARLOCK: dict[int, int] = {
    1: 2,
    2: 3,
    3: 4,
    4: 5,
    5: 6,
    6: 7,
    7: 8,
    8: 9,
    9: 10,
    10: 10,
    11: 11,
    12: 11,
    13: 12,
    14: 12,
    15: 13,
    16: 13,
    17: 14,
    18: 14,
    19: 15,
    20: 15,
}

# --- Modo de lista de magias (PHB 5e) ---
# Full caster preparado: mod habilidade + nível de personagem (mín. 1).
# Ver docs/dnd5e/issue-conjuracao-paladino-patrulheiro.md antes de alterar.
PREPARED_FULL_CASTER_CLASSES = frozenset({"mago", "clerigo", "druida"})
PREPARED_HALF_CASTER_CLASSES = frozenset({"paladino"})
PREPARED_CLASSES = PREPARED_FULL_CASTER_CLASSES | PREPARED_HALF_CASTER_CLASSES

KNOWN_CLASSES = frozenset({"bardo", "feiticeiro", "bruxo", "patrulheiro"})

# Patrulheiro — Spells Known (PHB); índice = nível de personagem
KNOWN_SPELLS_HALF_CASTER: dict[int, int] = {
    2: 2,
    3: 3,
    4: 3,
    5: 4,
    6: 2,
    7: 3,
    8: 3,
    9: 4,
    10: 4,
    11: 5,
    12: 5,
    13: 6,
    14: 6,
    15: 7,
    16: 7,
    17: 8,
    18: 8,
    19: 9,
    20: 9,
}

SHORT_REST_RECOVER_ALL = frozenset({"bruxo"})


def magias_preparadas_max_full_caster(mod_habilidade: int, nivel: int) -> int:
    """Mago, clérigo, druida — mod + nível (mín. 1)."""
    return max(1, mod_habilidade + nivel)


def magias_preparadas_max_paladino(mod_habilidade: int, nivel: int) -> int:
    """Paladino PHB — mod CAR + floor(nível/2) (mín. 1)."""
    return max(1, mod_habilidade + nivel // 2)
