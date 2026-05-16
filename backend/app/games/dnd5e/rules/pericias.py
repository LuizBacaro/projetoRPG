"""Perícias D&D 5E — proficiências e bônus (PHB Cap. 7)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence

from app.games.dnd5e.data.classes_proficiencias import proficiencias_classe
from app.games.dnd5e.data.pericias_catalogo import (
    PERICIA_SLUG_POR_NOME_EN,
    PERICIAS_CATALOGO,
)
from app.games.dnd5e.rules.antecedentes import antecedente_do_catalogo
from app.games.dnd5e.rules.habilidades import calcular_bonus_proficiencia
from app.games.dnd5e.rules.racas import raca_por_slug


def normalizar_pericia_slug(valor: str) -> Optional[str]:
    """Aceita slug PT ou nome EN do catálogo de antecedentes."""
    key = (valor or "").strip().lower()
    if not key:
        return None
    for row in PERICIAS_CATALOGO:
        if row["slug"] == key:
            return key
    return PERICIA_SLUG_POR_NOME_EN.get(key)


def pericia_por_slug(slug: str) -> Optional[Dict[str, Any]]:
    key = normalizar_pericia_slug(slug)
    if not key:
        return None
    for row in PERICIAS_CATALOGO:
        if row["slug"] == key:
            return dict(row)
    return None


def listar_pericias_catalogo() -> List[Dict[str, Any]]:
    return list(PERICIAS_CATALOGO)


def _sem_duplicar(slugs: Sequence[str]) -> List[str]:
    seen: set[str] = set()
    out: List[str] = []
    for raw in slugs:
        s = normalizar_pericia_slug(raw)
        if s and s not in seen:
            seen.add(s)
            out.append(s)
    return out


def validar_escolhas_classe(
    classe_slug: str,
    escolhidas: Sequence[str],
    *,
    exigir_quantidade: bool = False,
) -> List[str]:
    prof = proficiencias_classe(classe_slug)
    qtd = int(prof.get("pericias_escolha_qtd", 0))
    pool = prof.get("pericias_escolha_de") or []
    normalizadas = _sem_duplicar(escolhidas)
    if len(normalizadas) > qtd:
        raise ValueError(
            f"Classe permite no máximo {qtd} perícia(s) à escolha; recebeu {len(normalizadas)}"
        )
    if pool:
        pool_set = set(pool)
        for s in normalizadas:
            if s not in pool_set:
                raise ValueError(f"Perícia '{s}' não é opção válida para a classe")
    else:
        for s in normalizadas:
            if pericia_por_slug(s) is None:
                raise ValueError(f"Perícia inválida: {s}")
    if exigir_quantidade and qtd > 0 and len(normalizadas) != qtd:
        raise ValueError(f"Escolha exatamente {qtd} perícia(s) de classe")
    if len(normalizadas) > qtd:
        raise ValueError(f"Escolha no máximo {qtd} perícia(s) de classe")
    return normalizadas


def montar_proficiencias_pericias(
    *,
    classe_slug: str,
    raca_slug: str,
    antecedente_slug: Optional[str] = None,
    pericias_classe_escolhidas: Optional[Sequence[str]] = None,
    pericia_racial_extra: Optional[str] = None,
    exigir_quantidade_classe: bool = False,
) -> List[str]:
    """Lista final de slugs de perícias em que o personagem é proficiente."""
    prof = proficiencias_classe(classe_slug)
    escolhidas = validar_escolhas_classe(
        classe_slug,
        pericias_classe_escolhidas or [],
        exigir_quantidade=exigir_quantidade_classe,
    )

    resultado: List[str] = list(escolhidas)

    if antecedente_slug:
        ant = antecedente_do_catalogo(antecedente_slug)
        if ant:
            for p in ant.pericias:
                s = normalizar_pericia_slug(p)
                if s:
                    resultado.append(s)

    raca = raca_por_slug(raca_slug)
    if raca and "proficiencia_pericia_extra" in (raca.get("caracteristicas") or []):
        extra = normalizar_pericia_slug(pericia_racial_extra or "")
        if extra:
            resultado.append(extra)

    return _sem_duplicar(resultado)


def calcular_bonus_pericia(
    pericia_slug: str,
    modificadores: Dict[str, int],
    proficiente: bool,
    nivel: int,
) -> int:
    row = pericia_por_slug(pericia_slug)
    if row is None:
        raise ValueError(f"Perícia inválida: {pericia_slug}")
    hab = row["habilidade"]
    base = int(modificadores.get(hab, 0))
    if proficiente:
        base += calcular_bonus_proficiencia(nivel)
    return base


def montar_grade_pericias(
    *,
    modificadores: Dict[str, int],
    proficientes: Sequence[str],
    nivel: int,
) -> List[Dict[str, Any]]:
    prof_set = set(_sem_duplicar(proficientes))
    grade: List[Dict[str, Any]] = []
    for row in PERICIAS_CATALOGO:
        slug = row["slug"]
        prof = slug in prof_set
        grade.append(
            {
                "slug": slug,
                "nome": row["nome"],
                "habilidade": row["habilidade"],
                "proficiente": prof,
                "bonus": calcular_bonus_pericia(slug, modificadores, prof, nivel),
            }
        )
    return grade


def montar_salvamentos(
    *,
    classe_slug: str,
    modificadores: Dict[str, int],
    nivel: int,
) -> List[Dict[str, Any]]:
    prof = proficiencias_classe(classe_slug)
    saves_prof = set(prof.get("salvamentos") or [])
    chaves = (
        "strength",
        "dexterity",
        "constitution",
        "intelligence",
        "wisdom",
        "charisma",
    )
    out: List[Dict[str, Any]] = []
    for chave in chaves:
        prof_flag = chave in saves_prof
        bonus = int(modificadores.get(chave, 0))
        if prof_flag:
            bonus += calcular_bonus_proficiencia(nivel)
        out.append(
            {
                "habilidade": chave,
                "proficiente": prof_flag,
                "bonus": bonus,
            }
        )
    return out
