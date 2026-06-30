"""Proficiência em armaduras e escudos — Tormenta 20 v1.3 (RF-T07e-1, p.152–153)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

# Tabela 1-3 v1.3 + paridade MB (Usar Armaduras / Usar Escudos).
_PROF_ARMADURA_V13: Dict[str, Dict[str, bool]] = {
    "arcanista": {"leve": False, "media": False, "pesada": False, "escudo": False},
    "barbaro": {"leve": True, "media": True, "pesada": False, "escudo": True},
    "bardo": {"leve": True, "media": False, "pesada": False, "escudo": True},
    "bucaneiro": {"leve": True, "media": False, "pesada": False, "escudo": True},
    "cacador": {"leve": True, "media": False, "pesada": False, "escudo": False},
    "cavaleiro": {"leve": True, "media": True, "pesada": True, "escudo": True},
    "clerigo": {"leve": True, "media": True, "pesada": True, "escudo": True},
    "druida": {"leve": True, "media": True, "pesada": False, "escudo": True},
    "guerreiro": {"leve": True, "media": True, "pesada": True, "escudo": True},
    "inventor": {"leve": True, "media": True, "pesada": False, "escudo": False},
    "ladino": {"leve": True, "media": False, "pesada": False, "escudo": False},
    "lutador": {"leve": True, "media": True, "pesada": False, "escudo": False},
    "nobre": {"leve": True, "media": False, "pesada": False, "escudo": True},
    "paladino": {"leve": True, "media": True, "pesada": True, "escudo": True},
}

_PROF_PADRAO = {"leve": False, "media": False, "pesada": False, "escudo": False}


def proficiencias_armadura_classe(slug_classe: Optional[str]) -> Dict[str, bool]:
    """Proficiências de armadura/escudo por slug de classe v1.3."""
    s = str(slug_classe or "").strip().lower()
    return dict(_PROF_ARMADURA_V13.get(s) or _PROF_PADRAO)


def normalizar_tipo_protecao(tipo: Any) -> str:
    t = str(tipo or "").strip().lower()
    if t in ("média", "media"):
        return "media"
    if t in ("leve", "pesada", "escudo"):
        return t
    return ""


def item_e_protecao_mecanica(item: Any) -> bool:
    """Item de proteção com efeito mecânico (CA ou penalidade)."""
    if not isinstance(item, dict):
        return False
    try:
        bonus = int(item.get("bonus_ca", 0) or 0)
        pen = int(item.get("penalidade", 0) or 0)
    except (TypeError, ValueError):
        return False
    return bonus != 0 or pen != 0


def proficiente_em_protecao(
    prof: Dict[str, bool],
    item: Any,
) -> bool:
    """True se a classe é proficiente no tipo de armadura/escudo equipado."""
    if not isinstance(item, dict):
        return True
    if not item_e_protecao_mecanica(item):
        return True
    tipo = normalizar_tipo_protecao(item.get("tipo"))
    if not tipo:
        return bool(prof.get("leve"))
    if tipo == "escudo":
        return bool(prof.get("escudo"))
    if tipo == "pesada":
        return bool(prof.get("pesada"))
    if tipo == "media":
        return bool(prof.get("media") or prof.get("pesada"))
    if tipo == "leve":
        return bool(prof.get("leve") or prof.get("media") or prof.get("pesada"))
    return True


def tem_protecao_sem_proficiencia(
    itens_protecao: Optional[List[Any]],
    slug_classe: Optional[str],
) -> bool:
    """
    True se algum item de proteção mecânico equipado exige proficiência que a classe não tem.
    Dispara penalidade em **todas** perícias For/Des (p.152–153).
    Sem slug de classe informado, assume proficiente (comportamento legado).
    """
    if not str(slug_classe or "").strip():
        return False
    prof = proficiencias_armadura_classe(slug_classe)
    for it in itens_protecao or []:
        if not isinstance(it, dict):
            continue
        if not item_e_protecao_mecanica(it):
            continue
        if not proficiente_em_protecao(prof, it):
            return True
    return False
