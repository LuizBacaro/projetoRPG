"""Infraestrutura central de efeitos de talentos (feats) — ficha, combate e progressão."""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional, Sequence

ContextoFeat = Literal["ficha_preview", "combate", "progressao"]

_CHAVES_NUMERICAS = (
    "bonus_iniciativa",
    "bonus_hp_por_nivel",
    "bonus_ataque",
    "bonus_ataque_distancia",
    "bonus_ataque_corpo_a_corpo",
    "bonus_dano",
)


def _efeito_vazio() -> Dict[str, Any]:
    return {k: 0 for k in _CHAVES_NUMERICAS}


def _merge_efeitos(base: Dict[str, Any], delta: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(base)
    for chave in _CHAVES_NUMERICAS:
        out[chave] = int(out.get(chave, 0)) + int(delta.get(chave, 0))
    for chave, valor in delta.items():
        if chave in _CHAVES_NUMERICAS:
            continue
        if chave not in out:
            out[chave] = valor
        elif isinstance(out[chave], list) and isinstance(valor, list):
            out[chave] = list(out[chave]) + list(valor)
        elif isinstance(out[chave], dict) and isinstance(valor, dict):
            merged = dict(out[chave])
            merged.update(valor)
            out[chave] = merged
    return out


def aplicar_feat_efeito(
    feat_slug: str,
    contexto: ContextoFeat,
    *,
    corpo_a_corpo: bool = True,
    distancia: bool = False,
    feat_escolhas: Optional[Dict[str, Any]] = None,
    **_: Any,
) -> Dict[str, Any]:
    """
    Hook único por talento. Retorna modificadores parciais para o contexto pedido.
    Feats sem efeito mecânico neste contexto retornam dict vazio de bônus.
    """
    slug = (feat_slug or "").strip().lower()
    out = _efeito_vazio()

    if slug == "alert" and contexto in ("ficha_preview", "combate"):
        out["bonus_iniciativa"] = 5

    if slug == "tough" and contexto in ("ficha_preview", "progressao"):
        out["bonus_hp_por_nivel"] = 2

    if slug == "archery" and contexto == "combate" and distancia:
        out["bonus_ataque_distancia"] = 2

    if slug == "sharpshooter" and contexto == "combate" and distancia:
        # Penalidade -5/+10 dano fica para UI futura; aqui só registramos tag
        out["feat_sharpshooter"] = True

    if slug == "great-weapon-master" and contexto == "combate" and corpo_a_corpo:
        out["feat_gwm"] = True

    if slug == "lucky" and contexto == "combate":
        out["lucky_rerolls_descanso_longo"] = 3

    if slug == "resilient" and contexto == "combate":
        escolhas = feat_escolhas or {}
        attr = str(
            escolhas.get("resilient") or escolhas.get("resilient_atributo") or ""
        )
        out["resilient_save_prof"] = True
        if attr:
            out["resilient_atributo"] = attr.lower()

    if slug == "observant" and contexto == "ficha_preview":
        out["passive_perception_bonus"] = 5
        out["passive_investigation_bonus"] = 5

    if slug == "war-caster" and contexto == "combate":
        out["war_caster_concentracao_vantagem"] = True

    if slug == "magic-initiate" and contexto in ("ficha_preview", "combate"):
        from app.games.dnd5e.rules.feat_combate import resumo_magic_initiate

        resumo = resumo_magic_initiate(feat_escolhas)
        if resumo:
            out["magic_initiate"] = resumo

    return out


def agregar_efeitos_feats(
    feats: Optional[Sequence[str]],
    contexto: ContextoFeat,
    *,
    feat_escolhas: Optional[Dict[str, Any]] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Agrega efeitos de todos os feats do personagem para um contexto."""
    acumulado = _efeito_vazio()
    extras: Dict[str, Any] = {}
    kw = dict(kwargs)
    kw["feat_escolhas"] = feat_escolhas
    for slug in feats or []:
        parcial = aplicar_feat_efeito(slug, contexto, **kw)
        for chave in _CHAVES_NUMERICAS:
            acumulado[chave] = int(acumulado.get(chave, 0)) + int(parcial.get(chave, 0))
        for chave, valor in parcial.items():
            if chave in _CHAVES_NUMERICAS:
                continue
            extras[chave] = valor
    acumulado.update(extras)
    return acumulado


def bonus_ataque_feats(
    feats: Optional[Sequence[str]],
    *,
    corpo_a_corpo: bool = True,
    distancia: bool = False,
    bonus_extra_manual: int = 0,
) -> int:
    """Soma bônus de ataque de feats para a arena."""
    fx = agregar_efeitos_feats(
        feats,
        "combate",
        corpo_a_corpo=corpo_a_corpo,
        distancia=distancia,
    )
    total = int(bonus_extra_manual)
    total += int(fx.get("bonus_ataque", 0))
    if distancia:
        total += int(fx.get("bonus_ataque_distancia", 0))
    elif corpo_a_corpo:
        total += int(fx.get("bonus_ataque_corpo_a_corpo", 0))
    return total
