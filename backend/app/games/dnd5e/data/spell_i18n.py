"""Tradução leve EN→PT-BR para metadados e descrições SRD (5e)."""

from __future__ import annotations

import re
from typing import Optional

CASTING_TIME_PT = {
    "1 action": "1 ação",
    "1 bonus action": "1 ação bônus",
    "1 reaction": "1 reação",
    "1 minute": "1 minuto",
    "10 minutes": "10 minutos",
    "1 hour": "1 hora",
    "8 hours": "8 horas",
    "24 hours": "24 horas",
}

RANGE_PT = {
    "Self": "Pessoal",
    "Touch": "Toque",
    "Sight": "Visão",
    "Unlimited": "Ilimitado",
}

DURATION_PT = {
    "Instantaneous": "Instantâneo",
    "Concentration, up to 1 minute": "Concentração, até 1 minuto",
    "Concentration, up to 10 minutes": "Concentração, até 10 minutos",
    "Concentration, up to 1 hour": "Concentração, até 1 hora",
    "Concentration, up to 8 hours": "Concentração, até 8 horas",
    "Concentration, up to 24 hours": "Concentração, até 24 horas",
    "1 round": "1 rodada",
    "1 minute": "1 minuto",
    "10 minutes": "10 minutos",
    "1 hour": "1 hora",
    "8 hours": "8 horas",
    "24 hours": "24 horas",
    "Until dispelled": "Até ser dissipada",
    "Special": "Especial",
}

SAVE_PT = {
    "dex": "Destreza",
    "con": "Constituição",
    "wis": "Sabedoria",
    "int": "Inteligência",
    "cha": "Carisma",
    "for": "Força",
    "str": "Força",
    "nenhum": "Nenhum",
}

# Substituições frequentes em descrições SRD (ordem: frases longas primeiro).
_DESC_REPLACEMENTS: list[tuple[str, str]] = [
    (r"\bSaving Throw\b", "teste de resistência"),
    (r"\bsaving throw\b", "teste de resistência"),
    (r"\bspell attack\b", "ataque mágico"),
    (r"\bSpell attack\b", "Ataque mágico"),
    (r"\bhit points\b", "pontos de vida"),
    (r"\bHit points\b", "Pontos de vida"),
    (r"\bHit point\b", "Ponto de vida"),
    (r"\bcreature\b", "criatura"),
    (r"\bCreature\b", "Criatura"),
    (r"\bcreatures\b", "criaturas"),
    (r"\bCreatures\b", "Criaturas"),
    (r"\btarget\b", "alvo"),
    (r"\bTarget\b", "Alvo"),
    (r"\brange\b", "alcance"),
    (r"\bRange\b", "Alcance"),
    (r"\bduration\b", "duração"),
    (r"\bDuration\b", "Duração"),
    (r"\bconcentration\b", "concentração"),
    (r"\bConcentration\b", "Concentração"),
    (r"\britual\b", "ritual"),
    (r"\bRitual\b", "Ritual"),
    (r"\bComponents?\b", "Componentes"),
    (r"\bVerbal\b", "Verbal"),
    (r"\bSomatic\b", "Somático"),
    (r"\bMaterial\b", "Material"),
    (r"\bdamage\b", "dano"),
    (r"\bDamage\b", "Dano"),
    (r"\bAt Higher Levels\b", "Em Níveis Superiores"),
    (r"\bat higher levels\b", "em níveis superiores"),
    (r"\bYou\b", "Você"),
    (r"\byou\b", "você"),
    (r"\byour\b", "seu"),
    (r"\bYour\b", "Seu"),
]


def traduzir_tempo_conjuracao(texto: Optional[str]) -> Optional[str]:
    if not texto:
        return texto
    s = texto.strip()
    return CASTING_TIME_PT.get(s, s)


def traduzir_duracao(texto: Optional[str]) -> Optional[str]:
    if not texto:
        return texto
    s = texto.strip()
    if s in DURATION_PT:
        return DURATION_PT[s]
    if s.startswith("Concentration"):
        return s.replace("Concentration", "Concentração").replace("up to", "até")
    return s


def traduzir_alcance(
    texto: Optional[str], metros: Optional[int] = None
) -> Optional[str]:
    if metros and metros > 0:
        return f"{metros} m"
    if not texto:
        return texto
    s = texto.strip()
    return RANGE_PT.get(s, s)


def traduzir_teste_resistencia(slug: Optional[str]) -> Optional[str]:
    if not slug:
        return slug
    return SAVE_PT.get(slug.lower(), slug)


def traduzir_descricao_srd(texto: Optional[str]) -> Optional[str]:
    """Heurística EN→PT para descrições SRD (não substitui tradução editorial PHB)."""
    if not texto or not texto.strip():
        return texto
    out = texto
    for pattern, repl in _DESC_REPLACEMENTS:
        out = re.sub(pattern, repl, out)
    return out
