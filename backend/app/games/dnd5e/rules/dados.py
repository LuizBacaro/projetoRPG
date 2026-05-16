"""Utilitários de dados (dados polyhedra) para regras 5E."""

from __future__ import annotations

import re
from typing import Callable, Optional

_ROLL_DICE_RE = re.compile(r"^(\d+)d(\d+)$", re.IGNORECASE)


def rolar_dado(
    expressao: str,
    rng: Optional[Callable[[int, int], int]] = None,
) -> int:
    """Rola expressão NdM (ex.: ``1d20``, ``2d8``). Sem modificador."""
    m = _ROLL_DICE_RE.match((expressao or "").strip())
    if not m:
        raise ValueError(f"Expressao de dado invalida: {expressao!r}")
    n, faces = int(m.group(1)), int(m.group(2))
    if n < 1 or faces < 1:
        raise ValueError(f"Expressao de dado invalida: {expressao!r}")

    if rng is not None:
        return sum(rng(1, faces) for _ in range(n))

    import random

    return sum(random.randint(1, faces) for _ in range(n))


def rolar_d20(rng: Optional[Callable[[int, int], int]] = None) -> int:
    if rng is not None:
        return rng(1, 20)
    import random

    return random.randint(1, 20)
