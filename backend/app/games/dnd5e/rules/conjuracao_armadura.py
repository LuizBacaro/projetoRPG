"""Regra PHB: conjuração falha se armadura/escudo equipados sem proficiência de classe."""

from __future__ import annotations

from typing import Optional, Tuple

from app.games.dnd5e.data.classes_proficiencias import proficiencias_classe
from app.games.dnd5e.rules.equipamento import armadura_por_slug, escudo_por_slug


def _tipo_armadura_pt(tipo: str) -> str:
    mapa = {"leve": "leve", "media": "média", "pesada": "pesada", "roupa": "roupas"}
    return mapa.get((tipo or "").strip().lower(), tipo)


def validar_conjuracao_armadura(
    classe_slug: str,
    *,
    armadura_slug: Optional[str] = None,
    escudo_slug: Optional[str] = None,
) -> Tuple[bool, str]:
    """
    Retorna (pode_conjurar, mensagem_erro).
    PHB: se usar armadura ou escudo sem proficiência, não pode conjurar magias.
    """
    prof = proficiencias_classe(classe_slug)
    armaduras_ok = {a.lower() for a in (prof.get("armaduras") or [])}
    escudo_ok = bool(prof.get("escudos"))

    if armadura_slug:
        arm = armadura_por_slug(armadura_slug)
        if arm:
            tipo = (arm.tipo_armadura or "leve").lower()
            if tipo not in armaduras_ok:
                return (
                    False,
                    f"Conjuração bloqueada: sem proficiência em armadura {_tipo_armadura_pt(tipo)}.",
                )

    if escudo_slug:
        if escudo_por_slug(escudo_slug) and not escudo_ok:
            return (
                False,
                "Conjuração bloqueada: sem proficiência em escudo.",
            )

    return True, ""
