"""Defesa (CA) Tormenta 20 v1.3."""

from __future__ import annotations

from app.games.tormenta.rules.defesa_t20 import defesa_base_ca


def test_defesa_v13_des_2() -> None:
    assert defesa_base_ca(2, "v13") == 12


def test_defesa_v13_des_0() -> None:
    assert defesa_base_ca(0, "v13") == 10


def test_defesa_mb_des_12() -> None:
    """MB: DES 12 → mod +1 → CA 11."""
    assert defesa_base_ca(12, "mb") == 11
