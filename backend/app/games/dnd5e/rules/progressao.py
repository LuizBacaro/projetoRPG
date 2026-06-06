"""Progressão de personagem D&D 5E — ficha_json v2, HP incremental, marcos feat/ASI."""

from __future__ import annotations

import random
from typing import Any, Dict, List, Optional, Sequence, Tuple

from app.games.dnd5e.data.classes_catalogo import NIVEIS_GANHO_FEAT
from app.games.dnd5e.rules.classes import nivel_por_xp
from app.games.dnd5e.rules.habilidades import (
    HABILIDADE_MAX,
    validar_valor_habilidade,
)
from app.games.dnd5e.rules.talentos import (
    PersonagemFeats,
    calcular_ganhos_feats,
    feat_do_catalogo,
    validar_feat,
)

FICHA_FORMAT_VERSION = 2
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
METODOS_ATRIBUTOS = frozenset({"padrao", "4d6", "pontos"})
MATRIZ_PADRAO_VALORES = (15, 14, 13, 12, 10, 8)
_CUSTO_COMPRA_PONTOS = {8: 0, 9: 1, 10: 2, 11: 3, 12: 4, 13: 5, 14: 7, 15: 9}
ORCAMENTO_COMPRA_PONTOS = 27
_ORCAMENTO_COMPRA_PONTOS = ORCAMENTO_COMPRA_PONTOS


def migrar_ficha_para_v2(ficha: Dict[str, Any]) -> Dict[str, Any]:
    """Normaliza ficha legada (v1 ou sem versão) para contrato v2."""
    out = dict(ficha or {})
    versao = int(out.get("v") or 1)
    if versao < FICHA_FORMAT_VERSION:
        out["v"] = FICHA_FORMAT_VERSION
    if "metodo_atributos" not in out:
        out["metodo_atributos"] = "padrao"
    if "progressao" not in out or not isinstance(out.get("progressao"), dict):
        out["progressao"] = {"hp_rolls": [], "marcos": []}
    else:
        prog = dict(out["progressao"])
        prog.setdefault("hp_rolls", [])
        prog.setdefault("marcos", [])
        out["progressao"] = prog
    if "feats" not in out or not isinstance(out.get("feats"), list):
        out["feats"] = _feats_de_marcos(out.get("progressao", {}).get("marcos") or [])
    return out


def _feats_de_marcos(marcos: Sequence[Dict[str, Any]]) -> List[str]:
    feats: List[str] = []
    for marco in marcos:
        if (marco.get("tipo") or "").strip().lower() == "feat":
            slug = (marco.get("slug") or "").strip().lower()
            if slug and slug not in feats:
                feats.append(slug)
    return feats


def matriz_padrao_scores() -> Dict[str, int]:
    return {
        chave: MATRIZ_PADRAO_VALORES[i]
        for i, chave in enumerate(CHAVES_HABILIDADE)
    }


def gerar_scores_4d6(*, seed: Optional[int] = None) -> Dict[str, int]:
    rng = random.Random(seed)
    scores: Dict[str, int] = {}
    for chave in CHAVES_HABILIDADE:
        dados = sorted(rng.randint(1, 6) for _ in range(4))
        scores[chave] = sum(dados[1:])
    return scores


def custo_compra_pontos(valor: int) -> int:
    if valor not in _CUSTO_COMPRA_PONTOS:
        raise ValueError(
            f"Valor {valor} inválido na compra de pontos (permitido 8–15)"
        )
    return _CUSTO_COMPRA_PONTOS[valor]


def total_pontos_gastos(scores_base: Dict[str, int]) -> int:
    return sum(custo_compra_pontos(int(scores_base.get(chave, 8))) for chave in CHAVES_HABILIDADE)


def validar_scores_base_por_metodo(
    scores_base: Dict[str, int],
    metodo: str = "padrao",
) -> None:
    met = (metodo or "padrao").strip().lower()
    if met not in METODOS_ATRIBUTOS:
        raise ValueError(f"Método de atributos inválido: {metodo}")

    for chave in CHAVES_HABILIDADE:
        v = int(scores_base.get(chave, 10))
        if met == "4d6":
            if v < 3 or v > 18:
                raise ValueError(
                    f"Valor base de {chave} deve estar entre 3 e 18 (4d6)"
                )
        elif met == "pontos":
            if v < 8 or v > 15:
                raise ValueError(
                    f"Valor base de {chave} deve estar entre 8 e 15 (compra de pontos)"
                )
        else:
            if v < 8 or v > 15:
                raise ValueError(
                    f"Valor base de {chave} deve estar entre 8 e 15 na criação"
                )

    if met == "pontos":
        gasto = total_pontos_gastos(scores_base)
        if gasto > _ORCAMENTO_COMPRA_PONTOS:
            raise ValueError(
                f"Compra de pontos excede {_ORCAMENTO_COMPRA_PONTOS} "
                f"(gasto: {gasto})"
            )


def validar_nivel_vs_experiencia(nivel: int, experiencia: int) -> None:
    nivel_ef = max(1, min(20, int(nivel)))
    xp = max(0, int(experiencia))
    max_nivel = nivel_por_xp(xp)
    if nivel_ef > max_nivel:
        raise ValueError(
            f"Nível {nivel_ef} exige mais XP (máximo permitido com {xp} XP: {max_nivel})"
        )


def _faces_dado_vida(classe_slug: str) -> int:
    from app.games.dnd5e.rules.classes import classe_por_slug

    classe = classe_por_slug(classe_slug)
    if classe is None:
        raise ValueError(f"Classe inválida: {classe_slug}")
    return DADO_VIDA_FACES.get(str(classe.get("dado_vida", "d8")), 8)


def media_dado_vida(faces: int) -> int:
    return (faces + 1) // 2


def bonus_hp_por_nivel_racial(raca_slug: str) -> int:
    from app.games.dnd5e.rules.racas import raca_por_slug

    raca = raca_por_slug(raca_slug)
    if not raca:
        return 0
    return max(0, int(raca.get("bonus_hp_por_nivel", 0)))


def bonus_hp_por_nivel_feat(feats: Optional[Sequence[str]]) -> int:
    slugs = {(f or "").strip().lower() for f in (feats or [])}
    return 2 if "tough" in slugs else 0


def bonus_hp_extras_por_nivel(
    raca_slug: str = "",
    feats: Optional[Sequence[str]] = None,
) -> int:
    return bonus_hp_por_nivel_racial(raca_slug) + bonus_hp_por_nivel_feat(feats)


def calcular_ganho_hp_nivel(
    classe_slug: str,
    con_mod: int,
    *,
    roll: Optional[int] = None,
    usar_media: bool = False,
    usar_maximo: bool = False,
    rng: Optional[random.Random] = None,
) -> Tuple[int, int]:
    """Retorna (ganho_classe, valor_rolado). Ganho mínimo 1 (dado + CON)."""
    faces = _faces_dado_vida(classe_slug)
    if usar_maximo:
        valor_roll = faces
    elif usar_media:
        valor_roll = media_dado_vida(faces)
    elif roll is not None:
        valor_roll = int(roll)
    else:
        valor_roll = (rng or random.Random()).randint(1, faces)
    if valor_roll < 1 or valor_roll > faces:
        raise ValueError(f"Rolagem de dado de vida inválida: {valor_roll} (d{faces})")
    ganho = max(1, int(valor_roll) + int(con_mod))
    return ganho, int(valor_roll)


def calcular_ganho_hp_nivel_1(
    classe_slug: str,
    con_mod: int,
    *,
    roll: Optional[int] = None,
    usar_maximo: bool = True,
) -> Tuple[int, int]:
    """Nível 1: dado (máximo PHB se roll omitido) + CON, mínimo 1."""
    return calcular_ganho_hp_nivel(
        classe_slug,
        con_mod,
        roll=roll,
        usar_maximo=usar_maximo and roll is None,
    )


def normalizar_hp_rolls(hp_rolls: Any) -> List[Dict[str, Any]]:
    if not isinstance(hp_rolls, list):
        return []
    out: List[Dict[str, Any]] = []
    for item in hp_rolls:
        if not isinstance(item, dict):
            continue
        try:
            nivel = int(item.get("nivel", 0))
            roll = int(item.get("roll", 0))
            con_mod = int(item.get("con_mod", 0))
            ganho = int(item.get("ganho", max(1, roll + con_mod)))
        except (TypeError, ValueError):
            continue
        if nivel < 1 or nivel > 20:
            continue
        out.append(
            {
                "nivel": nivel,
                "roll": roll,
                "con_mod": con_mod,
                "ganho": ganho,
                "usar_media": bool(item.get("usar_media", False)),
            }
        )
    return sorted(out, key=lambda x: x["nivel"])


def niveis_hp_pendentes(nivel: int, hp_rolls: Sequence[Dict[str, Any]]) -> List[int]:
    nivel_ef = max(1, min(20, int(nivel)))
    registrados = {int(r["nivel"]) for r in hp_rolls}
    return [n for n in range(2, nivel_ef + 1) if n not in registrados]


def calcular_hp_max_total(
    classe_slug: str,
    con_mod: int,
    nivel: int,
    hp_rolls: Sequence[Dict[str, Any]],
    *,
    raca_slug: str = "",
    feats: Optional[Sequence[str]] = None,
) -> int:
    nivel_ef = max(1, min(20, int(nivel)))
    rolls_by_nivel = {
        int(item["nivel"]): item for item in normalizar_hp_rolls(list(hp_rolls))
    }
    extras = bonus_hp_extras_por_nivel(raca_slug, feats)
    total = 0

    if 1 in rolls_by_nivel:
        total += int(rolls_by_nivel[1]["ganho"]) + extras
    else:
        ganho1, _ = calcular_ganho_hp_nivel_1(classe_slug, con_mod, usar_maximo=True)
        total += ganho1 + extras

    for n in range(2, nivel_ef + 1):
        if n in rolls_by_nivel:
            total += int(rolls_by_nivel[n]["ganho"]) + extras

    return max(1, total)


def hp_max_nivel_1(
    classe_slug: str,
    constitution_mod: int,
    *,
    roll: Optional[int] = None,
    raca_slug: str = "",
    feats: Optional[Sequence[str]] = None,
) -> int:
    """PV no nível 1 = dado + CON (+ bônus raciais/feitos por nível)."""
    ganho, _ = calcular_ganho_hp_nivel_1(
        classe_slug,
        constitution_mod,
        roll=roll,
        usar_maximo=roll is None,
    )
    return ganho + bonus_hp_extras_por_nivel(raca_slug, feats)


def montar_hp_resumo(
    classe_slug: str,
    con_mod: int,
    nivel: int,
    hp_rolls: Sequence[Dict[str, Any]],
    *,
    raca_slug: str = "",
    feats: Optional[Sequence[str]] = None,
) -> Dict[str, Any]:
    from app.games.dnd5e.rules.classes import classe_por_slug

    classe = classe_por_slug(classe_slug) or {}
    faces = _faces_dado_vida(classe_slug)
    dado_vida = str(classe.get("dado_vida", "d8"))
    rolls_by_nivel = {
        int(item["nivel"]): item for item in normalizar_hp_rolls(list(hp_rolls))
    }
    bonus_racial = bonus_hp_por_nivel_racial(raca_slug)
    bonus_feat = bonus_hp_por_nivel_feat(feats)
    extras = bonus_racial + bonus_feat
    niveis: List[Dict[str, Any]] = []
    nivel_ef = max(1, min(20, int(nivel)))

    if 1 in rolls_by_nivel:
        item = rolls_by_nivel[1]
        ganho_classe = int(item["ganho"])
        roll_val = int(item["roll"])
    else:
        ganho_classe, roll_val = calcular_ganho_hp_nivel_1(
            classe_slug, con_mod, usar_maximo=True
        )

    niveis.append(
        {
            "nivel": 1,
            "roll": roll_val,
            "con_mod": con_mod,
            "ganho_classe": ganho_classe,
            "bonus_racial": bonus_racial,
            "bonus_feat": bonus_feat,
            "bonus_extra": extras,
            "subtotal": ganho_classe + extras,
        }
    )

    for n in range(2, nivel_ef + 1):
        if n not in rolls_by_nivel:
            continue
        item = rolls_by_nivel[n]
        ganho_classe = int(item["ganho"])
        niveis.append(
            {
                "nivel": n,
                "roll": int(item["roll"]),
                "con_mod": int(item["con_mod"]),
                "ganho_classe": ganho_classe,
                "bonus_racial": bonus_racial,
                "bonus_feat": bonus_feat,
                "bonus_extra": extras,
                "subtotal": ganho_classe + extras,
            }
        )

    total = calcular_hp_max_total(
        classe_slug,
        con_mod,
        nivel_ef,
        hp_rolls,
        raca_slug=raca_slug,
        feats=feats,
    )
    return {
        "dado_vida": dado_vida,
        "faces": faces,
        "con_mod": con_mod,
        "bonus_racial_por_nivel": bonus_racial,
        "bonus_feat_por_nivel": bonus_feat,
        "niveis": niveis,
        "total": total,
    }


def normalizar_marcos(marcos: Any) -> List[Dict[str, Any]]:
    if not isinstance(marcos, list):
        return []
    out: List[Dict[str, Any]] = []
    for item in marcos:
        if not isinstance(item, dict):
            continue
        try:
            nivel = int(item.get("nivel", 0))
        except (TypeError, ValueError):
            continue
        if nivel not in NIVEIS_GANHO_FEAT:
            continue
        tipo = (item.get("tipo") or "").strip().lower()
        if tipo not in ("feat", "asi"):
            continue
        marco: Dict[str, Any] = {"nivel": nivel, "tipo": tipo}
        if tipo == "feat":
            marco["slug"] = (item.get("slug") or "").strip().lower()
        else:
            dist = item.get("distribuicao") or {}
            if isinstance(dist, dict):
                marco["distribuicao"] = {
                    k: int(v)
                    for k, v in dist.items()
                    if k in CHAVES_HABILIDADE and int(v) > 0
                }
        out.append(marco)
    return sorted(out, key=lambda x: x["nivel"])


def validar_distribuicao_asi(distribuicao: Dict[str, int]) -> None:
    if not distribuicao:
        raise ValueError(
            "Incremento no Valor de Habilidade exige distribuição (+2 ou +1/+1)"
        )
    total = sum(int(v) for v in distribuicao.values())
    if total != 2:
        raise ValueError(
            "O incremento deve somar exatamente +2 pontos de atributo"
        )
    for chave, delta in distribuicao.items():
        if chave not in CHAVES_HABILIDADE:
            raise ValueError(f"Atributo inválido no incremento: {chave}")
        if int(delta) not in (1, 2):
            raise ValueError("Cada atributo recebe +1 ou +2 no incremento")


def _personagem_feats_de_ficha(
    ficha: Dict[str, Any],
    *,
    nivel: int,
    scores_efetivos: Dict[str, int],
) -> PersonagemFeats:
    from app.games.dnd5e.rules.habilidades import AbilityScores, PersonagemHabilidades

    classe_slug = (ficha.get("classe_slug") or "").strip().lower()
    return PersonagemFeats(
        habilidades=PersonagemHabilidades(
            abilities=AbilityScores(**scores_efetivos),
            nivel=nivel,
        ),
        feats=list(ficha.get("feats") or []),
        classes_niveis={classe_slug: nivel} if classe_slug else {},
        raca=(ficha.get("raca_slug") or "").strip(),
        spellcasting=False,
        bonus_atributo_feat=dict(ficha.get("bonus_atributo_feat") or {}),
    )


def validar_marco(
    marco: Dict[str, Any],
    *,
    ficha: Dict[str, Any],
    nivel: int,
    scores_efetivos: Dict[str, int],
) -> None:
    nivel_marco = int(marco.get("nivel", 0))
    if nivel_marco not in NIVEIS_GANHO_FEAT:
        raise ValueError(
            f"O nível {nivel_marco} não concede incremento nem talento"
        )
    if nivel < nivel_marco:
        raise ValueError(
            f"Personagem nível {nivel} ainda não atingiu marco do nível {nivel_marco}"
        )

    marcos_existentes = normalizar_marcos(
        (ficha.get("progressao") or {}).get("marcos") or []
    )
    if any(m["nivel"] == nivel_marco for m in marcos_existentes):
        raise ValueError(f"Marco do nível {nivel_marco} já registrado")

    tipo = (marco.get("tipo") or "").strip().lower()
    if tipo == "feat":
        slug = (marco.get("slug") or "").strip().lower()
        feat = feat_do_catalogo(slug)
        if feat is None:
            raise ValueError(f"Talento inválido: {slug}")
        personagem = _personagem_feats_de_ficha(
            ficha, nivel=nivel, scores_efetivos=scores_efetivos
        )
        if not validar_feat(feat, personagem):
            raise ValueError(f"Pré-requisitos não atendidos para o talento {slug}")
    elif tipo == "asi":
        validar_distribuicao_asi(dict(marco.get("distribuicao") or {}))
        for chave, delta in (marco.get("distribuicao") or {}).items():
            novo = int(scores_efetivos.get(chave, 10)) + int(delta)
            validar_valor_habilidade(novo)
            if novo > HABILIDADE_MAX:
                raise ValueError(
                    f"Incremento excede o máximo de {HABILIDADE_MAX} em {chave}"
                )
    else:
        raise ValueError("Marco deve ser incremento (asi) ou talento (feat)")


def aplicar_marco_na_ficha(
    ficha: Dict[str, Any],
    marco: Dict[str, Any],
) -> Dict[str, Any]:
    out = migrar_ficha_para_v2(ficha)
    prog = dict(out.get("progressao") or {})
    marcos = list(prog.get("marcos") or [])
    marcos.append(dict(marco))
    prog["marcos"] = normalizar_marcos(marcos)
    out["progressao"] = prog

    if (marco.get("tipo") or "").strip().lower() == "feat":
        feats = list(out.get("feats") or [])
        slug = (marco.get("slug") or "").strip().lower()
        if slug and slug not in feats:
            feats.append(slug)
        out["feats"] = feats
    elif (marco.get("tipo") or "").strip().lower() == "asi":
        bonus = dict(out.get("bonus_atributo_feat") or {})
        for chave, delta in (marco.get("distribuicao") or {}).items():
            bonus[chave] = int(bonus.get(chave, 0)) + int(delta)
        out["bonus_atributo_feat"] = bonus
    return out


def registrar_hp_roll_na_ficha(
    ficha: Dict[str, Any],
    *,
    nivel: int,
    classe_slug: str,
    con_mod: int,
    roll: Optional[int] = None,
    usar_media: bool = False,
    rng: Optional[random.Random] = None,
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    out = migrar_ficha_para_v2(ficha)
    prog = dict(out.get("progressao") or {})
    hp_rolls = normalizar_hp_rolls(prog.get("hp_rolls") or [])

    nivel_ef = int(nivel)
    if nivel_ef < 1 or nivel_ef > 20:
        raise ValueError("Rolagem de HP aplica-se aos níveis 1–20")
    if any(r["nivel"] == nivel_ef for r in hp_rolls):
        raise ValueError(f"HP do nível {nivel_ef} já registrado")

    if nivel_ef == 1:
        ganho, valor_roll = calcular_ganho_hp_nivel_1(
            classe_slug,
            con_mod,
            roll=roll,
            usar_maximo=roll is None and not usar_media,
        )
    else:
        ganho, valor_roll = calcular_ganho_hp_nivel(
            classe_slug,
            con_mod,
            roll=roll,
            usar_media=usar_media,
            rng=rng,
        )
    entrada = {
        "nivel": nivel_ef,
        "roll": valor_roll,
        "con_mod": con_mod,
        "ganho": ganho,
        "usar_media": usar_media,
    }
    hp_rolls.append(entrada)
    prog["hp_rolls"] = normalizar_hp_rolls(hp_rolls)
    out["progressao"] = prog
    return out, entrada


def marcos_pendentes(nivel: int, marcos: Sequence[Dict[str, Any]]) -> List[int]:
    nivel_ef = max(1, min(20, int(nivel)))
    registrados = {int(m["nivel"]) for m in normalizar_marcos(marcos)}
    return [n for n in NIVEIS_GANHO_FEAT if n <= nivel_ef and n not in registrados]


def listar_pendencias(
    *,
    nivel: int,
    classe_slug: str,
    con_mod: int,
    ficha: Dict[str, Any],
) -> List[str]:
    ficha_v2 = migrar_ficha_para_v2(ficha)
    prog = ficha_v2.get("progressao") or {}
    hp_rolls = normalizar_hp_rolls(prog.get("hp_rolls") or [])
    marcos = normalizar_marcos(prog.get("marcos") or [])

    pendencias: List[str] = []
    for n in niveis_hp_pendentes(nivel, hp_rolls):
        pendencias.append(f"hp_nivel_{n}")
    for n in marcos_pendentes(nivel, marcos):
        pendencias.append(f"marco_nivel_{n}")

    esperados = calcular_ganhos_feats(nivel)
    feats = list(ficha_v2.get("feats") or [])
    if len(feats) < esperados and not marcos_pendentes(nivel, marcos):
        pendencias.append("revisar_feats")

    if classe_slug and nivel >= 1:
        raca_slug = (ficha_v2.get("raca_slug") or "").strip()
        feats = list(ficha_v2.get("feats") or [])
        hp_total = calcular_hp_max_total(
            classe_slug,
            con_mod,
            nivel,
            hp_rolls,
            raca_slug=raca_slug,
            feats=feats,
        )
        if hp_total < 1:
            pendencias.append("hp_max_invalido")
    return pendencias


def validar_progressao_ficha(
    ficha: Dict[str, Any],
    *,
    nivel: int,
    classe_slug: str,
    con_mod: int,
    experiencia: int,
) -> None:
    ficha_v2 = migrar_ficha_para_v2(ficha)
    validar_nivel_vs_experiencia(nivel, experiencia)

    prog = ficha_v2.get("progressao") or {}
    hp_rolls = normalizar_hp_rolls(prog.get("hp_rolls") or [])
    marcos = normalizar_marcos(prog.get("marcos") or [])

    for n in niveis_hp_pendentes(nivel, hp_rolls):
        raise ValueError(f"Falta registrar PV do nível {n}")

    for n in marcos_pendentes(nivel, marcos):
        raise ValueError(
            f"Falta escolher incremento ou talento do nível {n}"
        )

    if classe_slug:
        raca_slug = (ficha_v2.get("raca_slug") or "").strip()
        feats = list(ficha_v2.get("feats") or [])
        calcular_hp_max_total(
            classe_slug,
            con_mod,
            nivel,
            hp_rolls,
            raca_slug=raca_slug,
            feats=feats,
        )
