"""Montagem de ficha D&D 5E — atributos efetivos, PV nível 1, perícias, CA."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence

from app.games.dnd5e.data.classes_catalogo import CLASSES_CATALOGO
from app.games.dnd5e.rules.antecedentes import antecedente_do_catalogo
from app.games.dnd5e.rules.classes import classe_por_slug
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
from app.games.dnd5e.rules.condicoes_ficha import (
    CHAVE_FICHA_ARENA_CONDICOES,
    normalizar_condicoes_ficha,
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


def hp_max_nivel_1(classe_slug: str, constitution_mod: int) -> int:
    """PV máximo no nível 1 = máximo do dado de vida + mod. CON (mín. 1)."""
    classe = classe_por_slug(classe_slug)
    if classe is None:
        raise ValueError(f"Classe inválida: {classe_slug}")
    faces = DADO_VIDA_FACES.get(str(classe.get("dado_vida", "d8")), 8)
    return max(1, faces + constitution_mod)


def _montar_antecedente_resumo(antecedente_slug: Optional[str]) -> Optional[Dict[str, Any]]:
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
    antecedente_slug: Optional[str] = None,
    nivel: int = 1,
    pericias_classe_escolhidas: Optional[Sequence[str]] = None,
    pericia_racial_extra: Optional[str] = None,
    subclasse_slug: Optional[str] = None,
    armadura_slug: Optional[str] = None,
    escudo_slug: Optional[str] = None,
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
    mods = calcular_modificadores(efetivos)
    hp = hp_max_nivel_1(classe_slug, mods["constitution"])
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

    return {
        "raca": {"slug": raca["slug"], "nome": raca["nome"]},
        "classe": {
            "slug": classe["slug"],
            "nome": classe["nome"],
            "dado_vida": classe["dado_vida"],
            "pericias_escolha_qtd": int(classe.get("pericias_escolha_qtd", 0)),
            "pericias_escolha_de": list(classe.get("pericias_escolha_de") or []),
        },
        "subclasse": (
            {"slug": sub["slug"], "nome": sub["nome"]} if sub else None
        ),
        "antecedente": _montar_antecedente_resumo(antecedente_slug),
        "antecedente_slug": antecedente_slug,
        "scores_base": {k: int(scores_base.get(k, 10)) for k in CHAVES_HABILIDADE},
        "scores_efetivos": efetivos,
        "modificadores": mods,
        "hp_max_nivel_1": hp,
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


def validar_ficha_para_gravacao(
    ficha: Dict[str, Any],
    *,
    nivel: int = 1,
) -> Dict[str, Any]:
    """
    Valida ficha completa (PHB criação) e devolve ficha enriquecida com resumo calculado.
    Levanta ValueError se regras não forem atendidas.
    """
    raca_slug = (ficha.get("raca_slug") or "").strip()
    classe_slug = (ficha.get("classe_slug") or "").strip()
    if not raca_slug or not classe_slug:
        out_parcial = dict(ficha)
        if CHAVE_FICHA_ARENA_CONDICOES in ficha:
            out_parcial[CHAVE_FICHA_ARENA_CONDICOES] = normalizar_condicoes_ficha(
                ficha.get(CHAVE_FICHA_ARENA_CONDICOES)
            )
        return out_parcial

    scores_base = dict(ficha.get("scores_base") or {})
    validar_scores_base_criacao(scores_base)

    raca = raca_por_slug(raca_slug)
    if raca and "proficiencia_pericia_extra" in (raca.get("caracteristicas") or []):
        if not (ficha.get("pericia_racial_extra") or "").strip():
            raise ValueError(
                "Raça exige escolha de uma perícia extra (proficiência racial)"
            )

    resumo = montar_resumo_ficha(
        raca_slug=raca_slug,
        classe_slug=classe_slug,
        scores_base=scores_base,
        bonus_habilidade_extra=ficha.get("bonus_habilidade_extra"),
        antecedente_slug=ficha.get("antecedente_slug"),
        nivel=nivel,
        pericias_classe_escolhidas=ficha.get("pericias_classe_escolhidas") or [],
        pericia_racial_extra=ficha.get("pericia_racial_extra"),
        subclasse_slug=ficha.get("subclasse_slug"),
        armadura_slug=ficha.get("armadura_slug"),
        escudo_slug=ficha.get("escudo_slug"),
    )

    # Validação estrita de perícias de classe na gravação.
    montar_proficiencias_pericias(
        classe_slug=classe_slug,
        raca_slug=raca_slug,
        antecedente_slug=ficha.get("antecedente_slug"),
        pericias_classe_escolhidas=ficha.get("pericias_classe_escolhidas") or [],
        pericia_racial_extra=ficha.get("pericia_racial_extra"),
        exigir_quantidade_classe=True,
    )

    out = dict(ficha)
    out["ca_base"] = resumo["ca_base"]
    out["ca_total"] = resumo["ca_total"]
    out["pericias_proficientes"] = resumo["pericias_proficientes"]
    out["hp_max_nivel_1_ref"] = resumo["hp_max_nivel_1"]
    if resumo.get("subclasse"):
        out["subclasse_nome"] = resumo["subclasse"]["nome"]
    if CHAVE_FICHA_ARENA_CONDICOES in ficha:
        out[CHAVE_FICHA_ARENA_CONDICOES] = normalizar_condicoes_ficha(
            ficha.get(CHAVE_FICHA_ARENA_CONDICOES)
        )
    return out


def validar_scores_base_criacao(scores_base: Dict[str, int]) -> None:
    """Criação: cada valor base entre 8 e 15 (matriz padrão / compra simplificada)."""
    for chave in CHAVES_HABILIDADE:
        v = int(scores_base.get(chave, 10))
        if v < 8 or v > 15:
            raise ValueError(
                f"Valor base de {chave} deve estar entre 8 e 15 na criação de personagem"
            )


def listar_classes_para_ficha() -> List[Dict[str, Any]]:
    return list(CLASSES_CATALOGO)
