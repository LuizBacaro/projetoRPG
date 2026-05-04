"""Ordem de turno GURPS 4E (Lite / padrão mesa): maior Velocidade básica primeiro."""

from __future__ import annotations

import random
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from app.games.gurps.models.personagem import GurpsPersonagem


def _velocidade_basica_como_float(personagem: GurpsPersonagem) -> float:
    v = personagem.velocidade_valor
    if v is None:
        return 0.0
    if isinstance(v, Decimal):
        return float(v)
    return float(v)


def ordenar_personagens_para_turno_gurps(
    personagens: List[GurpsPersonagem],
    rng: Optional[random.Random] = None,
) -> List[GurpsPersonagem]:
    """
    Ordena para agir primeiro quem tem maior VB; empate por maior DX; empate final por sorteio.

    Não usa o campo `iniciativa` (legado/UI). Ver decisão de produto G0.1 / RF-A01.
    """
    r = rng if rng is not None else random.Random()
    chaves = [
        (-_velocidade_basica_como_float(p), -(p.dx_valor or 0), r.random(), p)
        for p in personagens
    ]
    chaves.sort(key=lambda t: (t[0], t[1], t[2]))
    return [t[3] for t in chaves]
