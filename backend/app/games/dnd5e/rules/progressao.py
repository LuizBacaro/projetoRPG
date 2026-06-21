"""Progressão de personagem D&D 5E — ficha_json v2, HP incremental, marcos feat/ASI."""

from __future__ import annotations

import random
from typing import Any, Dict, List, Optional, Sequence, Tuple

from app.games.dnd5e.data.classes_catalogo import NIVEIS_GANHO_FEAT
from app.games.dnd5e.rules.classes import nivel_por_xp
from app.games.dnd5e.rules.feat_efeitos import agregar_efeitos_feats
from app.games.dnd5e.rules.habilidades import HABILIDADE_MAX, validar_valor_habilidade
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
MAGIC_INITIATE_CLASSES = frozenset({"clerigo", "mago", "druida", "bruxo"})
FEATS_REQUEREM_ESCOLHA = frozenset(
    {"resilient", "magic-initiate", "skilled", "skill-expert"}
)
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
    if not (out.get("raca_slug") or "").strip():
        leg = (out.get("raca") or "").strip().lower()
        if leg:
            out["raca_slug"] = leg
    if not (out.get("classe_slug") or "").strip():
        leg = (out.get("classe") or "").strip().lower()
        if leg:
            out["classe_slug"] = leg
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
        chave: MATRIZ_PADRAO_VALORES[i] for i, chave in enumerate(CHAVES_HABILIDADE)
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
        raise ValueError(f"Valor {valor} inválido na compra de pontos (permitido 8–15)")
    return _CUSTO_COMPRA_PONTOS[valor]


def total_pontos_gastos(scores_base: Dict[str, int]) -> int:
    return sum(
        custo_compra_pontos(int(scores_base.get(chave, 8)))
        for chave in CHAVES_HABILIDADE
    )


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
                raise ValueError(f"Valor base de {chave} deve estar entre 3 e 18 (4d6)")
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
    fx = agregar_efeitos_feats(feats, "progressao")
    return int(fx.get("bonus_hp_por_nivel", 0))


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


def recalcular_ganhos_hp_rolls(
    hp_rolls: Sequence[Dict[str, Any]],
    novo_con_mod: int,
    *,
    nivel_max: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Atualiza ganho/con_mod de rolagens já registradas (PHB: CON retroativa)."""
    nivel_limite = max(1, min(20, int(nivel_max))) if nivel_max is not None else 20
    out: List[Dict[str, Any]] = []
    for item in normalizar_hp_rolls(hp_rolls):
        copia = dict(item)
        if int(copia["nivel"]) <= nivel_limite:
            roll = int(copia["roll"])
            con = int(novo_con_mod)
            copia["con_mod"] = con
            copia["ganho"] = max(1, roll + con)
        out.append(copia)
    return out


def aplicar_retroativo_con_hp_na_ficha(
    ficha: Dict[str, Any],
    *,
    con_mod_novo: int,
    nivel: int,
) -> Dict[str, Any]:
    out = migrar_ficha_para_v2(ficha)
    prog = dict(out.get("progressao") or {})
    hp_rolls = normalizar_hp_rolls(prog.get("hp_rolls") or [])
    if not hp_rolls:
        return out
    prog["hp_rolls"] = recalcular_ganhos_hp_rolls(
        hp_rolls,
        int(con_mod_novo),
        nivel_max=nivel,
    )
    out["progressao"] = prog
    return out


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


def humano_precisa_feat_nivel_1(ficha: Dict[str, Any]) -> bool:
    """True se raça humano ainda não registrou marco feat no nível 1."""
    raca = (ficha.get("raca_slug") or "").strip().lower()
    if raca != "humano":
        return False
    marcos = normalizar_marcos((ficha.get("progressao") or {}).get("marcos") or [])
    return not any(m["nivel"] == 1 and m["tipo"] == "feat" for m in marcos)


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
        tipo = (item.get("tipo") or "").strip().lower()
        if tipo not in ("feat", "asi"):
            continue
        if nivel == 1:
            if tipo != "feat":
                continue
        elif nivel not in NIVEIS_GANHO_FEAT:
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
        raise ValueError("O incremento deve somar exatamente +2 pontos de atributo")
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


def _attr_resilient_escolhido(feat_escolhas: Optional[Dict[str, Any]]) -> str:
    esc = feat_escolhas or {}
    return (
        str(esc.get("resilient") or esc.get("resilient_atributo") or "").strip().lower()
    )


def _classe_magic_initiate_escolhida(feat_escolhas: Optional[Dict[str, Any]]) -> str:
    esc = feat_escolhas or {}
    return (
        str(esc.get("magic_initiate") or esc.get("magic_initiate_classe") or "")
        .strip()
        .lower()
    )


def _skilled_pericias_completas(feat_escolhas: Optional[Dict[str, Any]]) -> bool:
    from app.games.dnd5e.rules.pericias import (
        SKILLED_FEAT_QTD,
        skilled_pericias_de_feat_escolhas,
    )

    return len(skilled_pericias_de_feat_escolhas(feat_escolhas)) == SKILLED_FEAT_QTD


def _skill_expert_escolhas_completas(feat_escolhas: Optional[Dict[str, Any]]) -> bool:
    from app.games.dnd5e.rules.pericias import (
        skill_expert_expertise_de_feat_escolhas,
        skill_expert_nova_de_feat_escolhas,
    )

    nova = skill_expert_nova_de_feat_escolhas(feat_escolhas)
    exp = skill_expert_expertise_de_feat_escolhas(feat_escolhas)
    return bool(nova and exp)


def _expertise_classe_completa(
    ficha: Dict[str, Any],
    classe_slug: str,
    nivel: int,
) -> bool:
    from app.games.dnd5e.rules.pericias import (
        calcular_slots_expertise_classe,
        normalizar_expertise_pericias,
    )

    slots = calcular_slots_expertise_classe(classe_slug, nivel)
    if slots <= 0:
        return True
    escolhidas = normalizar_expertise_pericias(ficha.get("expertise_pericias"))
    return len(escolhidas) >= slots


def mesclar_feat_escolhas(
    ficha: Dict[str, Any],
    novas: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    from app.games.dnd5e.rules.pericias import (
        normalizar_pericia_slug,
        normalizar_skilled_pericias,
    )

    out = migrar_ficha_para_v2(ficha)
    escolhas = dict(out.get("feat_escolhas") or {})
    for chave, valor in (novas or {}).items():
        if valor is None:
            continue
        key = str(chave).strip()
        if key in ("skilled_pericias", "skilled"):
            norm = normalizar_skilled_pericias(valor)
            if norm:
                escolhas["skilled_pericias"] = norm
            elif "skilled_pericias" in escolhas:
                del escolhas["skilled_pericias"]
            continue
        if key in (
            "skill_expert_nova",
            "skill_expert_pericia",
            "skill_expert_expertise",
            "skill_expert_especializacao",
        ):
            slug = normalizar_pericia_slug(str(valor))
            if key in ("skill_expert_nova", "skill_expert_pericia"):
                if slug:
                    escolhas["skill_expert_nova"] = slug
                elif "skill_expert_nova" in escolhas:
                    del escolhas["skill_expert_nova"]
            else:
                if slug:
                    escolhas["skill_expert_expertise"] = slug
                elif "skill_expert_expertise" in escolhas:
                    del escolhas["skill_expert_expertise"]
            continue
        txt = str(valor).strip().lower()
        if txt:
            escolhas[key] = txt
    out["feat_escolhas"] = escolhas
    return out


def validar_feat_escolhas_ficha(ficha: Dict[str, Any]) -> None:
    from app.games.dnd5e.rules.pericias import (
        aplicar_pericias_override,
        montar_proficiencias_automaticas,
        skilled_pericias_de_feat_escolhas,
        validar_skill_expert_escolhas,
        validar_skilled_pericias,
    )

    ficha_v2 = migrar_ficha_para_v2(ficha)
    feats = {(f or "").strip().lower() for f in (ficha_v2.get("feats") or [])}
    escolhas = ficha_v2.get("feat_escolhas") or {}
    classe_slug = (ficha_v2.get("classe_slug") or "").strip().lower()
    raca_slug = (ficha_v2.get("raca_slug") or "humano").strip().lower()
    if "resilient" in feats:
        attr = _attr_resilient_escolhido(escolhas)
        if attr not in CHAVES_HABILIDADE:
            raise ValueError("Resiliente exige escolha de atributo de salvaguarda")
    if "magic-initiate" in feats:
        cls = _classe_magic_initiate_escolhida(escolhas)
        if cls not in MAGIC_INITIATE_CLASSES:
            raise ValueError("Iniciado em Magia exige escolha de classe conjuradora")
    if "skilled" in feats:
        validar_skilled_pericias(skilled_pericias_de_feat_escolhas(escolhas))
    if "skill-expert" in feats and classe_slug:
        prof_auto = montar_proficiencias_automaticas(
            classe_slug=classe_slug,
            raca_slug=raca_slug,
            antecedente_slug=ficha_v2.get("antecedente_slug"),
            pericias_classe_escolhidas=ficha_v2.get("pericias_classe_escolhidas") or [],
            pericia_racial_extra=ficha_v2.get("pericia_racial_extra"),
            feats=list(ficha_v2.get("feats") or []),
            feat_escolhas=escolhas,
        )
        prof_final = aplicar_pericias_override(
            prof_auto, ficha_v2.get("pericias_override")
        )
        validar_skill_expert_escolhas(escolhas, proficientes=prof_final)


def pendencias_feat_escolhas(ficha: Dict[str, Any]) -> List[str]:
    ficha_v2 = migrar_ficha_para_v2(ficha)
    feats = {(f or "").strip().lower() for f in (ficha_v2.get("feats") or [])}
    escolhas = ficha_v2.get("feat_escolhas") or {}
    out: List[str] = []
    if (
        "resilient" in feats
        and _attr_resilient_escolhido(escolhas) not in CHAVES_HABILIDADE
    ):
        out.append("feat_escolha_resilient")
    if (
        "magic-initiate" in feats
        and _classe_magic_initiate_escolhida(escolhas) not in MAGIC_INITIATE_CLASSES
    ):
        out.append("feat_escolha_magic_initiate")
    if "skilled" in feats and not _skilled_pericias_completas(escolhas):
        out.append("feat_escolha_skilled")
    if "skill-expert" in feats and not _skill_expert_escolhas_completas(escolhas):
        out.append("feat_escolha_skill_expert")
    return out


def _validar_feat_escolhas_marco(
    slug: str,
    feat_escolhas: Optional[Dict[str, Any]],
) -> None:
    from app.games.dnd5e.rules.pericias import (
        skilled_pericias_de_feat_escolhas,
        validar_skilled_pericias,
    )

    s = (slug or "").strip().lower()
    esc = feat_escolhas or {}
    if s == "resilient":
        attr = _attr_resilient_escolhido(esc)
        if attr not in CHAVES_HABILIDADE:
            raise ValueError("Resiliente exige escolha de atributo de salvaguarda")
    if s == "magic-initiate":
        cls = _classe_magic_initiate_escolhida(esc)
        if cls not in MAGIC_INITIATE_CLASSES:
            raise ValueError("Iniciado em Magia exige escolha de classe conjuradora")
    if s == "skilled":
        validar_skilled_pericias(skilled_pericias_de_feat_escolhas(esc))
    if s == "skill-expert":
        from app.games.dnd5e.rules.pericias import (
            skill_expert_expertise_de_feat_escolhas,
            skill_expert_nova_de_feat_escolhas,
        )

        if not skill_expert_nova_de_feat_escolhas(
            esc
        ) or not skill_expert_expertise_de_feat_escolhas(esc):
            raise ValueError(
                "Especialista (Skill Expert) exige nova proficiência e perícia para expertise"
            )


def validar_marco(
    marco: Dict[str, Any],
    *,
    ficha: Dict[str, Any],
    nivel: int,
    scores_efetivos: Dict[str, int],
) -> None:
    nivel_marco = int(marco.get("nivel", 0))
    raca_slug = (ficha.get("raca_slug") or "").strip().lower()
    if nivel_marco == 1:
        if raca_slug != "humano":
            raise ValueError("Marco nível 1 só concede talento para humanos")
        if (marco.get("tipo") or "").strip().lower() != "feat":
            raise ValueError("Marco nível 1 humano deve ser talento (feat)")
    elif nivel_marco not in NIVEIS_GANHO_FEAT:
        raise ValueError(f"O nível {nivel_marco} não concede incremento nem talento")
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
        _validar_feat_escolhas_marco(slug, marco.get("feat_escolhas"))
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
        if marco.get("feat_escolhas"):
            out = mesclar_feat_escolhas(out, marco.get("feat_escolhas"))
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


def marcos_pendentes(
    nivel: int,
    marcos: Sequence[Dict[str, Any]],
    *,
    raca_slug: str = "",
) -> List[int]:
    nivel_ef = max(1, min(20, int(nivel)))
    registrados = {int(m["nivel"]) for m in normalizar_marcos(marcos)}
    pendentes = [n for n in NIVEIS_GANHO_FEAT if n <= nivel_ef and n not in registrados]
    if (
        (raca_slug or "").strip().lower() == "humano"
        and nivel_ef >= 1
        and 1 not in registrados
    ):
        pendentes = [1] + pendentes
    return sorted(set(pendentes))


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

    raca_slug = (ficha_v2.get("raca_slug") or "").strip()
    pendencias: List[str] = []
    for n in niveis_hp_pendentes(nivel, hp_rolls):
        pendencias.append(f"hp_nivel_{n}")
    if humano_precisa_feat_nivel_1(ficha_v2):
        pendencias.append("feat_nivel_1")
    for n in marcos_pendentes(nivel, marcos, raca_slug=raca_slug):
        if n == 1:
            continue
        pendencias.append(f"marco_nivel_{n}")
    pendencias.extend(pendencias_feat_escolhas(ficha_v2))
    if classe_slug and not _expertise_classe_completa(ficha_v2, classe_slug, nivel):
        pendencias.append("expertise_classe")

    esperados = calcular_ganhos_feats(nivel, raca_slug=raca_slug)
    feats = list(ficha_v2.get("feats") or [])
    if len(feats) < esperados and not marcos_pendentes(
        nivel, marcos, raca_slug=raca_slug
    ):
        pendencias.append("revisar_feats")

    if classe_slug and nivel >= 1:
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

    raca_slug = (ficha_v2.get("raca_slug") or "").strip()
    if humano_precisa_feat_nivel_1(ficha_v2):
        raise ValueError("Humano exige escolha de talento no nível 1")
    for n in marcos_pendentes(nivel, marcos, raca_slug=raca_slug):
        if n == 1:
            continue
        raise ValueError(f"Falta escolher incremento ou talento do nível {n}")

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


def calcular_cura_repouso_longo(
    nivel: int,
    con_mod: int,
    *,
    rng: Optional[random.Random] = None,
) -> Tuple[int, List[Dict[str, Any]]]:
    """Repouso longo (PHB simplificado): 1d8+CON por nível acima de 1, mín. 1 cada."""
    rng = rng or random.Random()
    cura_total = 0
    detalhes: List[Dict[str, Any]] = []
    for n in range(2, max(2, int(nivel) + 1)):
        roll = rng.randint(1, 8)
        ganho = max(1, int(roll) + int(con_mod))
        cura_total += ganho
        detalhes.append(
            {
                "nivel": n,
                "roll": int(roll),
                "con_mod": int(con_mod),
                "ganho": int(ganho),
            }
        )
    return cura_total, detalhes
