"""Montagem de ficha D&D 5E — atributos efetivos, PV nível 1, perícias, CA."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence

from app.games.dnd5e.data.classes_catalogo import CLASSES_CATALOGO
from app.games.dnd5e.rules.antecedentes import antecedente_do_catalogo
from app.games.dnd5e.rules.classes import classe_por_slug
from app.games.dnd5e.rules.condicoes_ficha import (
    CHAVE_FICHA_ARENA_CONDICOES,
    normalizar_condicoes_ficha,
)
from app.games.dnd5e.rules.equipamento import calcular_ac_de_slugs
from app.games.dnd5e.rules.habilidades import (
    HABILIDADE_MAX,
    HABILIDADE_MIN,
    calcular_bonus_proficiencia,
    calcular_modificador,
    validar_valor_habilidade,
)
from app.games.dnd5e.rules.pericias import (
    montar_grade_pericias,
    montar_proficiencias_pericias,
    montar_salvamentos,
)
from app.games.dnd5e.rules.racas import raca_por_slug
from app.games.dnd5e.rules.progressao import (
    calcular_hp_max_total,
    hp_max_nivel_1,
    listar_pendencias,
    montar_hp_resumo,
    registrar_hp_roll_na_ficha,
    migrar_ficha_para_v2,
    validar_progressao_ficha,
    validar_scores_base_por_metodo,
)
from app.games.dnd5e.rules.subclasses import validar_subclasse_para_classe

CHAVES_HABILIDADE = (
    "strength",
    "dexterity",
    "constitution",
    "intelligence",
    "wisdom",
    "charisma",
)

DADO_VIDA_FACES: Dict[str, int] = {
    "d6": 6,
    "d8": 8,
    "d10": 10,
    "d12": 12,
}


def _normalizar_bonus_extra(extra: Optional[Dict[str, int]]) -> Dict[str, int]:
    out: Dict[str, int] = {k: 0 for k in CHAVES_HABILIDADE}
    if not extra:
        return out
    for k, v in extra.items():
        key = (k or "").strip().lower()
        if key in out:
            out[key] = int(v)
    return out


def calcular_atributos_efetivos(
    scores_base: Dict[str, int],
    raca_slug: str,
    *,
    bonus_habilidade_extra: Optional[Dict[str, int]] = None,
) -> Dict[str, int]:
    """
    Soma valores base + bônus racial + bônus opcionais (ex.: meio-elfo +1 em duas habilidades).
    """
    raca = raca_por_slug(raca_slug)
    if raca is None:
        raise ValueError(f"Raça inválida: {raca_slug}")

    extra = _normalizar_bonus_extra(bonus_habilidade_extra)
    racial = dict(raca.get("bonus_habilidades") or {})

    efetivos: Dict[str, int] = {}
    for chave in CHAVES_HABILIDADE:
        base = int(scores_base.get(chave, 10))
        total = base + int(racial.get(chave, 0)) + extra[chave]
        validar_valor_habilidade(total)
        efetivos[chave] = total
    return efetivos


def calcular_modificadores(scores: Dict[str, int]) -> Dict[str, int]:
    return {k: calcular_modificador(scores[k]) for k in CHAVES_HABILIDADE}


def _montar_antecedente_resumo(
    antecedente_slug: Optional[str],
) -> Optional[Dict[str, Any]]:
    if not antecedente_slug:
        return None
    ant = antecedente_do_catalogo(antecedente_slug)
    if ant is None:
        raise ValueError(f"Antecedente inválido: {antecedente_slug}")
    return {
        "slug": ant.antecedente_id,
        "nome": ant.nome,
        "pericias": list(ant.pericias),
        "idiomas_qtd": ant.idiomas_qtd,
        "equipamento": list(ant.equipamento),
        "ouro_po": ant.ouro_extra,
    }


def montar_resumo_ficha(
    *,
    raca_slug: str,
    classe_slug: str,
    scores_base: Dict[str, int],
    bonus_habilidade_extra: Optional[Dict[str, int]] = None,
    bonus_atributo_feat: Optional[Dict[str, int]] = None,
    antecedente_slug: Optional[str] = None,
    nivel: int = 1,
    pericias_classe_escolhidas: Optional[Sequence[str]] = None,
    pericia_racial_extra: Optional[str] = None,
    subclasse_slug: Optional[str] = None,
    armadura_slug: Optional[str] = None,
    escudo_slug: Optional[str] = None,
    ficha_progressao: Optional[Dict[str, Any]] = None,
    feats: Optional[Sequence[str]] = None,
    hp_roll_nivel_1: Optional[int] = None,
) -> Dict[str, Any]:
    """Payload para preview API e validação da ficha."""
    raca = raca_por_slug(raca_slug)
    classe = classe_por_slug(classe_slug)
    if raca is None:
        raise ValueError(f"Raça inválida: {raca_slug}")
    if classe is None:
        raise ValueError(f"Classe inválida: {classe_slug}")

    nivel_ef = max(1, min(20, int(nivel)))
    sub = validar_subclasse_para_classe(subclasse_slug, classe_slug, nivel_ef)

    efetivos = calcular_atributos_efetivos(
        scores_base, raca_slug, bonus_habilidade_extra=bonus_habilidade_extra
    )
    if bonus_atributo_feat:
        for chave, delta in bonus_atributo_feat.items():
            if chave in efetivos:
                efetivos[chave] = int(efetivos[chave]) + int(delta)
                validar_valor_habilidade(efetivos[chave])
    mods = calcular_modificadores(efetivos)
    feats_list = list(feats or [])
    prog = (ficha_progressao or {}).get("progressao") if ficha_progressao else None
    hp_rolls = (prog or {}).get("hp_rolls") if isinstance(prog, dict) else None
    if hp_rolls is None and ficha_progressao:
        hp_rolls = ficha_progressao.get("hp_rolls")
    hp_rolls_list = list(hp_rolls or [])
    tem_roll_nivel_1 = any(
        int(r.get("nivel", 0)) == 1 for r in hp_rolls_list if isinstance(r, dict)
    )
    if hp_roll_nivel_1 is not None and not tem_roll_nivel_1:
        ficha_tmp, _ = registrar_hp_roll_na_ficha(
            migrar_ficha_para_v2(
                {"progressao": {"hp_rolls": hp_rolls_list, "marcos": []}}
            ),
            nivel=1,
            classe_slug=classe_slug,
            con_mod=mods["constitution"],
            roll=int(hp_roll_nivel_1),
        )
        hp_rolls_list = list((ficha_tmp.get("progressao") or {}).get("hp_rolls") or [])
    hp_total = calcular_hp_max_total(
        classe_slug,
        mods["constitution"],
        nivel_ef,
        hp_rolls_list,
        raca_slug=raca_slug,
        feats=feats_list,
    )
    hp1 = calcular_hp_max_total(
        classe_slug,
        mods["constitution"],
        1,
        hp_rolls_list,
        raca_slug=raca_slug,
        feats=feats_list,
    )
    hp_resumo = montar_hp_resumo(
        classe_slug,
        mods["constitution"],
        nivel_ef,
        hp_rolls_list,
        raca_slug=raca_slug,
        feats=feats_list,
    )
    hp = hp1
    ca_sem_armadura = 10 + mods["dexterity"]
    ca_total = calcular_ac_de_slugs(
        armadura_slug=armadura_slug,
        escudo_slug=escudo_slug,
        dex_mod=mods["dexterity"],
    )

    prof_pericias = montar_proficiencias_pericias(
        classe_slug=classe_slug,
        raca_slug=raca_slug,
        antecedente_slug=antecedente_slug,
        pericias_classe_escolhidas=pericias_classe_escolhidas,
        pericia_racial_extra=pericia_racial_extra,
        exigir_quantidade_classe=False,
    )

    resumo = {
        "raca": {"slug": raca["slug"], "nome": raca["nome"]},
        "classe": {
            "slug": classe["slug"],
            "nome": classe["nome"],
            "dado_vida": classe["dado_vida"],
            "pericias_escolha_qtd": int(classe.get("pericias_escolha_qtd", 0)),
            "pericias_escolha_de": list(classe.get("pericias_escolha_de") or []),
        },
        "subclasse": ({"slug": sub["slug"], "nome": sub["nome"]} if sub else None),
        "antecedente": _montar_antecedente_resumo(antecedente_slug),
        "antecedente_slug": antecedente_slug,
        "scores_base": {k: int(scores_base.get(k, 10)) for k in CHAVES_HABILIDADE},
        "scores_efetivos": efetivos,
        "modificadores": mods,
        "hp_max_nivel_1": hp,
        "hp_max_total": hp_total,
        "hp_resumo": hp_resumo,
        "feats": list(feats or []),
        "ca_base": ca_sem_armadura,
        "ca_total": ca_total,
        "armadura_slug": armadura_slug,
        "escudo_slug": escudo_slug,
        "iniciativa": mods["dexterity"],
        "velocidade_metros": float(raca.get("velocidade_metros", 9)),
        "tracos_resumo": raca.get("tracos_resumo", ""),
        "bonus_proficiencia": calcular_bonus_proficiencia(nivel_ef),
        "nivel": nivel_ef,
        "pericias_proficientes": prof_pericias,
        "pericias": montar_grade_pericias(
            modificadores=mods,
            proficientes=prof_pericias,
            nivel=nivel_ef,
        ),
        "salvamentos": montar_salvamentos(
            classe_slug=classe_slug,
            modificadores=mods,
            nivel=nivel_ef,
        ),
    }
    ficha_stub = {
        "raca_slug": raca_slug,
        "classe_slug": classe_slug,
        "feats": list(feats or []),
        "progressao": prog
        if isinstance(prog, dict)
        else {"hp_rolls": hp_rolls or [], "marcos": []},
    }
    resumo["pendencias"] = listar_pendencias(
        nivel=nivel_ef,
        classe_slug=classe_slug,
        con_mod=mods["constitution"],
        ficha=ficha_stub,
    )
    return resumo


def validar_ficha_para_gravacao(
    ficha: Dict[str, Any],
    *,
    nivel: int = 1,
    experiencia: int = 0,
    exigir_progressao_completa: bool = False,
) -> Dict[str, Any]:
    """
    Valida ficha completa (PHB criação) e devolve ficha enriquecida com resumo calculado.
    Levanta ValueError se regras não forem atendidas.
    """
    out = migrar_ficha_para_v2(ficha)
    raca_slug = (out.get("raca_slug") or "").strip()
    classe_slug = (out.get("classe_slug") or "").strip()
    if not raca_slug or not classe_slug:
        out_parcial = dict(out)
        if CHAVE_FICHA_ARENA_CONDICOES in out:
            out_parcial[CHAVE_FICHA_ARENA_CONDICOES] = normalizar_condicoes_ficha(
                out.get(CHAVE_FICHA_ARENA_CONDICOES)
            )
        return out_parcial

    scores_base = dict(out.get("scores_base") or {})
    metodo = (out.get("metodo_atributos") or "padrao").strip().lower()
    validar_scores_base_por_metodo(scores_base, metodo)

    raca = raca_por_slug(raca_slug)
    if raca and "proficiencia_pericia_extra" in (raca.get("caracteristicas") or []):
        if not (out.get("pericia_racial_extra") or "").strip():
            raise ValueError(
                "Raça exige escolha de uma perícia extra (proficiência racial)"
            )

    resumo = montar_resumo_ficha(
        raca_slug=raca_slug,
        classe_slug=classe_slug,
        scores_base=scores_base,
        bonus_habilidade_extra=out.get("bonus_habilidade_extra"),
        bonus_atributo_feat=out.get("bonus_atributo_feat"),
        antecedente_slug=out.get("antecedente_slug"),
        nivel=nivel,
        pericias_classe_escolhidas=out.get("pericias_classe_escolhidas") or [],
        pericia_racial_extra=out.get("pericia_racial_extra"),
        subclasse_slug=out.get("subclasse_slug"),
        armadura_slug=out.get("armadura_slug"),
        escudo_slug=out.get("escudo_slug"),
        ficha_progressao=out,
        feats=out.get("feats"),
    )

    # Validação estrita de perícias de classe na gravação.
    montar_proficiencias_pericias(
        classe_slug=classe_slug,
        raca_slug=raca_slug,
        antecedente_slug=out.get("antecedente_slug"),
        pericias_classe_escolhidas=out.get("pericias_classe_escolhidas") or [],
        pericia_racial_extra=out.get("pericia_racial_extra"),
        exigir_quantidade_classe=True,
    )

    if exigir_progressao_completa:
        validar_progressao_ficha(
            out,
            nivel=nivel,
            classe_slug=classe_slug,
            con_mod=resumo["modificadores"]["constitution"],
            experiencia=experiencia,
        )

    out["ca_base"] = resumo["ca_base"]
    out["ca_total"] = resumo["ca_total"]
    out["pericias_proficientes"] = resumo["pericias_proficientes"]
    out["hp_max_nivel_1_ref"] = resumo["hp_max_nivel_1"]
    out["hp_max_total_ref"] = resumo["hp_max_total"]
    out["pendencias"] = resumo.get("pendencias", [])
    if resumo.get("subclasse"):
        out["subclasse_nome"] = resumo["subclasse"]["nome"]
    if CHAVE_FICHA_ARENA_CONDICOES in out:
        out[CHAVE_FICHA_ARENA_CONDICOES] = normalizar_condicoes_ficha(
            out.get(CHAVE_FICHA_ARENA_CONDICOES)
        )
    return out


def validar_scores_base_criacao(scores_base: Dict[str, int]) -> None:
    """Criação: cada valor base entre 8 e 15 (matriz padrão / compra simplificada)."""
    validar_scores_base_por_metodo(scores_base, "padrao")


def listar_classes_para_ficha() -> List[Dict[str, Any]]:
    return list(CLASSES_CATALOGO)
