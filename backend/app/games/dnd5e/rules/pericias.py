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


SKILLED_FEAT_QTD = 3

# PHB — Ladino (1, 6) e Bardo (3, 10): +2 perícias em cada marco
EXPERTISE_CLASSE_MARCOS: Dict[str, List[tuple[int, int]]] = {
    "ladino": [(1, 2), (6, 2)],
    "bardo": [(3, 2), (10, 2)],
}


def normalizar_skilled_pericias(valor: Any) -> List[str]:
    """Normaliza lista de perícias do talento Perito (Skilled) — até 3 slugs distintos."""
    if valor is None:
        return []
    if isinstance(valor, str):
        partes = [p.strip() for p in valor.replace(";", ",").split(",") if p.strip()]
    elif isinstance(valor, (list, tuple)):
        partes = [str(p).strip() for p in valor if str(p).strip()]
    else:
        return []
    return _sem_duplicar(partes)


def skilled_pericias_de_feat_escolhas(
    feat_escolhas: Optional[Dict[str, Any]],
) -> List[str]:
    esc = feat_escolhas or {}
    raw = esc.get("skilled_pericias")
    if raw is None:
        raw = esc.get("skilled")
    return normalizar_skilled_pericias(raw)


def validar_skilled_pericias(slugs: Sequence[str]) -> List[str]:
    norm = normalizar_skilled_pericias(list(slugs))
    if len(norm) != SKILLED_FEAT_QTD:
        raise ValueError(
            f"Perito (Skilled) exige exatamente {SKILLED_FEAT_QTD} perícias distintas"
        )
    for slug in norm:
        if pericia_por_slug(slug) is None:
            raise ValueError(f"Perícia inválida no talento Perito: {slug}")
    return norm


def proficiencias_feat_skilled(
    feats: Optional[Sequence[str]],
    feat_escolhas: Optional[Dict[str, Any]],
) -> List[str]:
    feats_set = {(f or "").strip().lower() for f in (feats or [])}
    if "skilled" not in feats_set:
        return []
    return skilled_pericias_de_feat_escolhas(feat_escolhas)


def calcular_slots_expertise_classe(classe_slug: str, nivel: int) -> int:
    """Quantidade de perícias com Expertise concedidas pela classe (PHB)."""
    key = (classe_slug or "").strip().lower()
    marcos = EXPERTISE_CLASSE_MARCOS.get(key) or []
    niv = max(1, min(20, int(nivel)))
    total = 0
    for min_lvl, qtd in marcos:
        if niv >= min_lvl:
            total += qtd
    return total


def normalizar_expertise_pericias(valor: Any) -> List[str]:
    """Lista de slugs com Expertise (classe); slugs distintos, ordem preservada."""
    if valor is None:
        return []
    if isinstance(valor, str):
        partes = [p.strip() for p in valor.replace(";", ",").split(",") if p.strip()]
    elif isinstance(valor, (list, tuple)):
        partes = [str(p).strip() for p in valor if str(p).strip()]
    else:
        return []
    return _sem_duplicar(partes)


def skill_expert_nova_de_feat_escolhas(
    feat_escolhas: Optional[Dict[str, Any]],
) -> Optional[str]:
    esc = feat_escolhas or {}
    raw = esc.get("skill_expert_nova") or esc.get("skill_expert_pericia")
    if raw is None:
        return None
    return normalizar_pericia_slug(str(raw))


def skill_expert_expertise_de_feat_escolhas(
    feat_escolhas: Optional[Dict[str, Any]],
) -> Optional[str]:
    esc = feat_escolhas or {}
    raw = esc.get("skill_expert_expertise") or esc.get("skill_expert_especializacao")
    if raw is None:
        return None
    return normalizar_pericia_slug(str(raw))


def proficiencias_feat_skill_expert(
    feats: Optional[Sequence[str]],
    feat_escolhas: Optional[Dict[str, Any]],
) -> List[str]:
    feats_set = {(f or "").strip().lower() for f in (feats or [])}
    if "skill-expert" not in feats_set:
        return []
    nova = skill_expert_nova_de_feat_escolhas(feat_escolhas)
    return [nova] if nova else []


def montar_expertise_efetiva(
    expertise_pericias: Optional[Sequence[str]],
    *,
    feats: Optional[Sequence[str]] = None,
    feat_escolhas: Optional[Dict[str, Any]] = None,
) -> List[str]:
    """Expertise de classe + perícia do talento Especialista (Skill Expert)."""
    out = normalizar_expertise_pericias(expertise_pericias)
    feats_set = {(f or "").strip().lower() for f in (feats or [])}
    if "skill-expert" in feats_set:
        exp = skill_expert_expertise_de_feat_escolhas(feat_escolhas)
        if exp and exp not in out:
            out.append(exp)
    return out


def validar_expertise_pericias_classe(
    expertise_pericias: Sequence[str],
    *,
    classe_slug: str,
    nivel: int,
    proficientes: Sequence[str],
) -> List[str]:
    norm = normalizar_expertise_pericias(list(expertise_pericias))
    max_slots = calcular_slots_expertise_classe(classe_slug, nivel)
    if len(norm) > max_slots:
        raise ValueError(
            f"Expertise de classe permite no máximo {max_slots} perícia(s); "
            f"recebeu {len(norm)}"
        )
    prof_set = set(_sem_duplicar(proficientes))
    for slug in norm:
        if pericia_por_slug(slug) is None:
            raise ValueError(f"Perícia inválida na expertise: {slug}")
        if slug not in prof_set:
            raise ValueError(f"Expertise exige proficiência em '{slug}'")
    return norm


def validar_skill_expert_escolhas(
    feat_escolhas: Optional[Dict[str, Any]],
    *,
    proficientes: Sequence[str],
) -> tuple[str, str]:
    nova = skill_expert_nova_de_feat_escolhas(feat_escolhas)
    exp = skill_expert_expertise_de_feat_escolhas(feat_escolhas)
    if not nova or pericia_por_slug(nova) is None:
        raise ValueError(
            "Especialista (Skill Expert) exige escolha de uma nova proficiência"
        )
    if not exp or pericia_por_slug(exp) is None:
        raise ValueError(
            "Especialista (Skill Expert) exige escolha de perícia para expertise"
        )
    prof_set = set(_sem_duplicar(proficientes))
    if exp not in prof_set:
        raise ValueError(
            "Expertise do Especialista exige proficiência na perícia escolhida"
        )
    return nova, exp


def _override_flag(val: Any) -> Optional[bool]:
    if val is True or val == 1 or str(val).lower() in ("1", "true", "sim", "yes"):
        return True
    if (
        val is False
        or val == 0
        or str(val).lower() in ("0", "false", "nao", "não", "no")
    ):
        return False
    return None


def normalizar_pericias_override(
    override: Optional[Dict[str, Any]],
) -> Dict[str, bool]:
    out: Dict[str, bool] = {}
    for slug, val in (override or {}).items():
        s = normalizar_pericia_slug(str(slug))
        flag = _override_flag(val)
        if s and flag is not None:
            out[s] = flag
    return out


def aplicar_pericias_override(
    base_proficientes: Sequence[str],
    override: Optional[Dict[str, Any]],
) -> List[str]:
    """Aplica overrides manuais sobre proficiências automáticas (classe/raça/antecedente)."""
    prof_set = set(_sem_duplicar(base_proficientes))
    for slug, flag in normalizar_pericias_override(override).items():
        if flag:
            prof_set.add(slug)
        else:
            prof_set.discard(slug)
    return _sem_duplicar(list(prof_set))


def validar_pericias_override(override: Optional[Dict[str, Any]]) -> Dict[str, bool]:
    norm = normalizar_pericias_override(override)
    for raw_slug, val in (override or {}).items():
        if _override_flag(val) is None:
            continue
        slug = normalizar_pericia_slug(str(raw_slug))
        if not slug or pericia_por_slug(slug) is None:
            raise ValueError(f"Perícia inválida no override: {raw_slug}")
    return norm


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


def montar_proficiencias_automaticas(
    *,
    classe_slug: str,
    raca_slug: str,
    antecedente_slug: Optional[str] = None,
    pericias_classe_escolhidas: Optional[Sequence[str]] = None,
    pericia_racial_extra: Optional[str] = None,
    feats: Optional[Sequence[str]] = None,
    feat_escolhas: Optional[Dict[str, Any]] = None,
    exigir_quantidade_classe: bool = False,
) -> List[str]:
    """Proficiências de classe, antecedente, raça e talento Perito (Skilled), sem override manual."""
    base = montar_proficiencias_pericias(
        classe_slug=classe_slug,
        raca_slug=raca_slug,
        antecedente_slug=antecedente_slug,
        pericias_classe_escolhidas=pericias_classe_escolhidas,
        pericia_racial_extra=pericia_racial_extra,
        exigir_quantidade_classe=exigir_quantidade_classe,
    )
    extras = proficiencias_feat_skilled(feats, feat_escolhas)
    extras += proficiencias_feat_skill_expert(feats, feat_escolhas)
    return _sem_duplicar(base + extras)


def calcular_bonus_pericia(
    pericia_slug: str,
    modificadores: Dict[str, int],
    proficiente: bool,
    nivel: int,
    *,
    expertise: bool = False,
) -> int:
    row = pericia_por_slug(pericia_slug)
    if row is None:
        raise ValueError(f"Perícia inválida: {pericia_slug}")
    hab = row["habilidade"]
    base = int(modificadores.get(hab, 0))
    if proficiente:
        mult = 2 if expertise else 1
        base += calcular_bonus_proficiencia(nivel) * mult
    return base


def montar_grade_pericias(
    *,
    modificadores: Dict[str, int],
    proficientes: Sequence[str],
    nivel: int,
    expertise_pericias: Optional[Sequence[str]] = None,
) -> List[Dict[str, Any]]:
    prof_set = set(_sem_duplicar(proficientes))
    exp_set = set(montar_expertise_efetiva(expertise_pericias))
    grade: List[Dict[str, Any]] = []
    for row in PERICIAS_CATALOGO:
        slug = row["slug"]
        prof = slug in prof_set
        tem_exp = prof and slug in exp_set
        grade.append(
            {
                "slug": slug,
                "nome": row["nome"],
                "habilidade": row["habilidade"],
                "proficiente": prof,
                "expertise": tem_exp,
                "bonus": calcular_bonus_pericia(
                    slug, modificadores, prof, nivel, expertise=tem_exp
                ),
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
