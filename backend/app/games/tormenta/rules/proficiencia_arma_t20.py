"""Proficiência em armas — Tormenta 20 v1.3 (RF-T05-v13c, p.142)."""

from __future__ import annotations

from typing import Any, Optional

from app.games.tormenta.rules.catalogo_armas_v13_t20 import mapa_armas_v13_por_nome
from app.games.tormenta.rules.catalogo_t20 import lista_equipamentos_mb_catalogo
from app.games.tormenta.rules.kit_inicial_v13_t20 import proficiencias_kit_v13

PENALIDADE_ARMA_NAO_PROFICIENTE = -5


def _norm_nome(texto: Any) -> str:
    import unicodedata

    s = unicodedata.normalize("NFKD", str(texto or "").strip().lower())
    return "".join(c for c in s if not unicodedata.combining(c))


def proficiencias_arma_classe(slug_classe: Optional[str]) -> dict[str, bool]:
    """Todos proficientes em simples/desarmado; marcial conforme classe (kit v1.3)."""
    kit = proficiencias_kit_v13(str(slug_classe or "").strip().lower())
    return {
        "simples": True,
        "marcial": bool(kit.get("marcial")),
        "exotica": False,
        "desarmado": True,
    }


def normalizar_proficiencia_arma(valor: Any) -> str:
    t = str(valor or "simples").strip().lower()
    if t in ("exótica", "exotica"):
        return "exotica"
    if t in ("simples", "marcial", "de fogo", "desarmado", "natural"):
        return t
    return "simples"


def proficiente_em_arma(
    slug_classe: Optional[str],
    proficiencia_arma: Any,
) -> bool:
    prof_arma = normalizar_proficiencia_arma(proficiencia_arma)
    prof_cl = proficiencias_arma_classe(slug_classe)
    if prof_arma in ("desarmado", "natural"):
        return bool(prof_cl.get("desarmado", True))
    if prof_arma == "simples":
        return bool(prof_cl.get("simples", True))
    if prof_arma == "marcial":
        return bool(prof_cl.get("marcial"))
    if prof_arma in ("exotica", "de fogo"):
        return bool(prof_cl.get("exotica"))
    return True


def proficiencia_arma_por_nome(nome_arma: Optional[str]) -> str:
    """Resolve proficiência do catálogo MB + overlay v1.3."""
    chave = _norm_nome(nome_arma)
    if not chave:
        return "simples"
    overlay = mapa_armas_v13_por_nome().get(chave)
    if overlay and overlay.get("proficiencia"):
        return normalizar_proficiencia_arma(overlay.get("proficiencia"))
    for row in lista_equipamentos_mb_catalogo():
        if _norm_nome(row.get("nome")) == chave:
            if row.get("proficiencia"):
                return normalizar_proficiencia_arma(row.get("proficiencia"))
            break
    return "simples"


def penalidade_ataque_arma(
    slug_classe: Optional[str],
    *,
    nome_arma: Optional[str] = None,
    proficiencia_arma: Optional[str] = None,
) -> int:
    """0 ou −5 conforme proficiência da classe na arma (p.142)."""
    prof = (
        proficiencia_arma
        if proficiencia_arma
        else proficiencia_arma_por_nome(nome_arma)
    )
    if proficiente_em_arma(slug_classe, prof):
        return 0
    return PENALIDADE_ARMA_NAO_PROFICIENTE


def ajustar_bonus_ataque_v13(
    bonus_base: int,
    slug_classe: Optional[str],
    *,
    nome_arma: Optional[str] = None,
    proficiencia_arma: Optional[str] = None,
) -> dict[str, Any]:
    prof = (
        proficiencia_arma
        if proficiencia_arma
        else proficiencia_arma_por_nome(nome_arma)
    )
    pen = penalidade_ataque_arma(slug_classe, proficiencia_arma=prof)
    proficiente = pen == 0
    return {
        "bonus_base": int(bonus_base),
        "bonus_efetivo": int(bonus_base) + pen,
        "penalidade_nao_proficiente": abs(pen),
        "proficiente": proficiente,
        "proficiencia_arma": prof,
    }
