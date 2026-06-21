"""Helpers de feats em combate — salvamento, Lucky, iniciativa, Magic Initiate."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Tuple

from app.games.dnd5e.rules.feat_efeitos import agregar_efeitos_feats
from app.games.dnd5e.rules.raca_traits import resolver_salvamento_racial

SAVE_PARA_ATRIBUTO = {
    "fortitude": "constitution",
    "reflexos": "dexterity",
    "vontade": "wisdom",
}

MAGIC_INITIATE_PACOTES: Dict[str, Dict[str, Any]] = {
    "clerigo": {
        "nome": "Clérigo",
        "atributo": "wisdom",
        "truques": ["orientacao", "chama-sagrada"],
        "magia_1": "bencao",
    },
    "mago": {
        "nome": "Mago",
        "atributo": "intelligence",
        "truques": ["raio-de-fogo", "mao-magica"],
        "magia_1": "escudo-arcano",
    },
    "druida": {
        "nome": "Druida",
        "atributo": "wisdom",
        "truques": ["guidance", "chama-producao"],
        "magia_1": "goodberry",
    },
    "bruxo": {
        "nome": "Bruxo",
        "atributo": "charisma",
        "truques": ["toque-chocante", "prestidigitacao"],
        "magia_1": "armadura-de-aco",
    },
}


def bonus_iniciativa_feats(feats: Optional[Sequence[str]]) -> int:
    fx = agregar_efeitos_feats(feats, "combate")
    return int(fx.get("bonus_iniciativa", 0))


def lucky_max_pontos(feats: Optional[Sequence[str]]) -> int:
    fx = agregar_efeitos_feats(feats, "combate")
    return int(fx.get("lucky_rerolls_descanso_longo", 0) or 0)


def aplicar_lucky_se_solicitado(
    roll: int,
    *,
    usar_lucky: bool,
    lucky_restantes: int,
    feats: Optional[Sequence[str]],
    rng=None,
) -> Tuple[int, int, Optional[int]]:
    """Rerrola o d20 se Lucky disponível; retorna (roll, lucky_restantes, reroll)."""
    max_pts = lucky_max_pontos(feats)
    if not usar_lucky or max_pts <= 0 or lucky_restantes <= 0:
        return roll, lucky_restantes, None
    from app.games.dnd5e.rules.dados import rolar_d20

    reroll = int(rng(1, 20)) if rng else rolar_d20()
    return reroll, max(0, lucky_restantes - 1), reroll


def proficiente_resilient(
    feats: Optional[Sequence[str]],
    feat_escolhas: Optional[Dict[str, Any]],
    *,
    save_tipo: str = "",
) -> bool:
    if not feats or "resilient" not in {(f or "").lower() for f in feats}:
        return False
    escolhas = feat_escolhas or {}
    attr = str(
        escolhas.get("resilient") or escolhas.get("resilient_atributo") or ""
    ).lower()
    if not attr:
        return False
    save_key = (save_tipo or "").strip().lower()
    return SAVE_PARA_ATRIBUTO.get(save_key, "") == attr


def resolver_salvamento_com_feats(
    mod_atributo: int,
    bonus_proficiencia: int,
    cd: int,
    *,
    proficiente: bool = False,
    raca_slug: str = "",
    categoria: str = "",
    condicoes: Optional[Sequence[str]] = None,
    rolagem_d20: Optional[int] = None,
    aplicar_sorte_halfling_flag: bool = True,
    feats: Optional[Sequence[str]] = None,
    feat_escolhas: Optional[Dict[str, Any]] = None,
    save_tipo: str = "",
    usar_lucky: bool = False,
    lucky_restantes: int = 0,
    rng=None,
) -> dict:
    prof = proficiente or proficiente_resilient(
        feats, feat_escolhas, save_tipo=save_tipo
    )
    roll_forced = rolagem_d20
    lucky_reroll = None
    lucky_depois = lucky_restantes
    if roll_forced is not None and usar_lucky:
        roll_forced, lucky_depois, lucky_reroll = aplicar_lucky_se_solicitado(
            roll_forced,
            usar_lucky=True,
            lucky_restantes=lucky_restantes,
            feats=feats,
            rng=rng,
        )
    out = resolver_salvamento_racial(
        mod_atributo,
        bonus_proficiencia,
        cd,
        proficiente=prof,
        raca_slug=raca_slug,
        categoria=categoria,
        condicoes=condicoes,
        rolagem_d20=roll_forced,
        aplicar_sorte_halfling_flag=aplicar_sorte_halfling_flag,
        rng=rng,
    )
    if rolagem_d20 is None and usar_lucky and lucky_reroll is None:
        roll, lucky_depois, lucky_reroll = aplicar_lucky_se_solicitado(
            int(out["rolagem"]),
            usar_lucky=True,
            lucky_restantes=lucky_restantes,
            feats=feats,
            rng=rng,
        )
        if lucky_reroll is not None:
            out = resolver_salvamento_racial(
                mod_atributo,
                bonus_proficiencia,
                cd,
                proficiente=prof,
                raca_slug=raca_slug,
                categoria=categoria,
                condicoes=condicoes,
                rolagem_d20=roll,
                aplicar_sorte_halfling_flag=False,
                rng=rng,
            )
    out["proficiente_resilient"] = prof and not proficiente
    out["lucky_reroll"] = lucky_reroll
    out["lucky_restantes"] = lucky_depois
    return out


def resumo_magic_initiate(
    feat_escolhas: Optional[Dict[str, Any]]
) -> Optional[Dict[str, Any]]:
    escolhas = feat_escolhas or {}
    classe = str(
        escolhas.get("magic_initiate") or escolhas.get("magic_initiate_classe") or ""
    ).lower()
    if not classe:
        return None
    pacote = MAGIC_INITIATE_PACOTES.get(classe)
    if not pacote:
        return {"classe": classe, "resumo": f"Iniciado em Magia ({classe})"}
    return {
        "classe": classe,
        "classe_nome": pacote["nome"],
        "atributo": pacote["atributo"],
        "truques": list(pacote["truques"]),
        "magia_1": pacote["magia_1"],
        "resumo": (
            f"2 truques ({', '.join(pacote['truques'])}); "
            f"1×/{'descanso longo'} {pacote['magia_1']} (1º nível)"
        ),
    }


def war_caster_vantagem_concentracao(feats: Optional[Sequence[str]]) -> bool:
    fx = agregar_efeitos_feats(feats, "combate")
    return bool(fx.get("war_caster_concentracao_vantagem"))
