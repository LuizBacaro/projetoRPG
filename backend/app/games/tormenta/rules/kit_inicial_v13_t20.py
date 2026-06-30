"""Equipamento inicial v1.3 — p.140."""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from app.games.tormenta.rules.classes_t20 import classe_por_slug
from app.games.tormenta.rules.regra_versao_t20 import (
    REGRA_VERSAO_V13,
    regra_versao_de_ficha,
)

KIT_FIXO_V13 = [
    "Mochila",
    "Saco de dormir",
    "Roupas de viajante",
]

ARMADURAS_LEVES_V13 = [
    "Armadura de couro",
    "Armadura de couro batido",
    "Armadura de gibão de peles",
]

ARMADURA_PESADA_KIT_V13 = "Brunea"

# Proficiências de kit (v1.3 p.140 + Tabela 1-3).
_PROF_KIT_V13: Dict[str, Dict[str, bool]] = {
    "arcanista": {
        "marcial": False,
        "pesada": False,
        "escudo": False,
        "sem_armadura": True,
    },
    "barbaro": {
        "marcial": True,
        "pesada": False,
        "escudo": True,
        "sem_armadura": False,
    },
    "bardo": {"marcial": True, "pesada": False, "escudo": True, "sem_armadura": False},
    "bucaneiro": {
        "marcial": True,
        "pesada": False,
        "escudo": True,
        "sem_armadura": False,
    },
    "cacador": {
        "marcial": True,
        "pesada": False,
        "escudo": False,
        "sem_armadura": False,
    },
    "cavaleiro": {
        "marcial": True,
        "pesada": True,
        "escudo": True,
        "sem_armadura": False,
    },
    "clerigo": {
        "marcial": False,
        "pesada": True,
        "escudo": True,
        "sem_armadura": False,
    },
    "druida": {
        "marcial": False,
        "pesada": False,
        "escudo": True,
        "sem_armadura": False,
    },
    "guerreiro": {
        "marcial": True,
        "pesada": True,
        "escudo": True,
        "sem_armadura": False,
    },
    "inventor": {
        "marcial": True,
        "pesada": False,
        "escudo": False,
        "sem_armadura": False,
    },
    "ladino": {
        "marcial": True,
        "pesada": False,
        "escudo": False,
        "sem_armadura": False,
    },
    "lutador": {
        "marcial": True,
        "pesada": False,
        "escudo": False,
        "sem_armadura": False,
    },
    "nobre": {"marcial": True, "pesada": False, "escudo": True, "sem_armadura": False},
    "paladino": {
        "marcial": True,
        "pesada": True,
        "escudo": True,
        "sem_armadura": False,
    },
}


def proficiencias_kit_v13(slug_classe: str) -> Dict[str, bool]:
    s = str(slug_classe or "").strip().lower()
    base = dict(
        _PROF_KIT_V13.get(s)
        or {"marcial": False, "pesada": False, "escudo": False, "sem_armadura": False}
    )
    row = classe_por_slug(s, REGRA_VERSAO_V13)
    if row:
        txt = str(row.get("talentos_adicionais") or "").lower()
        if "marcial" in txt or "completas" in txt:
            base["marcial"] = True
        if "pesad" in txt or "completas" in txt:
            base["pesada"] = True
        if "escudo" in txt:
            base["escudo"] = True
    return base


def opcoes_kit_inicial_v13(slug_classe: str) -> Dict[str, Any]:
    prof = proficiencias_kit_v13(slug_classe)
    return {
        "fixos": list(KIT_FIXO_V13),
        "arma_simples": True,
        "arma_marcial": bool(prof.get("marcial")),
        "armadura_leve": not prof.get("sem_armadura"),
        "armadura_pesada_opcao": bool(prof.get("pesada")),
        "armaduras_leves": list(ARMADURAS_LEVES_V13),
        "armadura_pesada": ARMADURA_PESADA_KIT_V13,
        "escudo": bool(prof.get("escudo")),
        "sem_armadura": bool(prof.get("sem_armadura")),
        "dinheiro_formula": "4d6",
    }


def _norm_item(nome: str) -> str:
    n = str(nome or "").strip()
    aliases = {
        "Arma simples corpo a corpo": "Clava",
        "Traje de plebeu": "Roupas de plebeu",
        "Traje de sacerdote": "Roupas de viajante",
        "Traje da corte": "Roupas de viajante",
        "Traje estrangeiro": "Roupas de viajante",
        "Uniforme militar": "Roupas de viajante",
        "Bolas de malabarismo": "Bolas de malabarismo",
    }
    return aliases.get(n, n) if n else n


def itens_kit_inicial_v13(ficha_json: Optional[dict]) -> List[Dict[str, Any]]:
    """Itens do kit p.140 a partir de `kit_inicial_v13` na ficha."""
    fj = dict(ficha_json or {})
    if regra_versao_de_ficha(fj) != REGRA_VERSAO_V13:
        return []
    if int(fj.get("nivel_ficha") or fj.get("nivel") or 1) > 1:
        return []
    kit = fj.get("kit_inicial_v13")
    if not isinstance(kit, dict):
        return []

    slug_classe = str(fj.get("tormenta_classe_mb_slug") or "").strip().lower()
    prof = proficiencias_kit_v13(slug_classe)
    out: List[Dict[str, Any]] = []

    def _add(nome: str, qtd: int = 1) -> None:
        n = _norm_item(nome)
        if n:
            out.append({"nome": n, "quantidade": max(1, int(qtd))})

    for nome in KIT_FIXO_V13:
        _add(nome)

    arma_s = str(kit.get("arma_simples") or "").strip()
    if arma_s:
        _add(arma_s)

    if prof.get("marcial"):
        arma_m = str(kit.get("arma_marcial") or "").strip()
        if arma_m:
            _add(arma_m)

    if not prof.get("sem_armadura"):
        arm = str(kit.get("armadura") or "").strip()
        if arm:
            if arm.lower() == "brunea" and prof.get("pesada"):
                _add(ARMADURA_PESADA_KIT_V13)
            elif arm in ARMADURAS_LEVES_V13 or arm.lower().startswith("armadura"):
                _add(arm)
            elif prof.get("pesada") and arm == ARMADURA_PESADA_KIT_V13:
                _add(arm)

    if prof.get("escudo") and kit.get("escudo"):
        _add("Escudo leve de madeira")

    return out
