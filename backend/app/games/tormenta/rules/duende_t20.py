"""Duende — raça modular Heróis de Arton v1.1 (p.10–13)."""

from __future__ import annotations

import json
import random
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_PRESENTES_JSON = _DATA_DIR / "presentes_duende.json"
_OPCOES_JSON = _DATA_DIR / "opcoes_duende.json"

_ATTRS = ("for", "des", "con", "int", "sab", "car")
_NATUREZAS = frozenset({"animal", "vegetal", "mineral"})
_TAMANHOS = frozenset({"minusculo", "pequeno", "medio", "grande"})
_TABU_PEN = frozenset({"diplomacia", "iniciativa", "luta", "percepcao"})
_TABU_PERICIA_NOME: Dict[str, str] = {
    "diplomacia": "Diplomacia",
    "iniciativa": "Iniciativa",
    "luta": "Luta",
    "percepcao": "Percepção",
}
_PATAMARES_TROCA_PODER = (5, 10, 15, 20)
_QTD_PRESENTES = 3

# Metadados mecânicos dos 12 Presentes (HA p.11–12).
_PRESENTES_MECANICOS: Dict[str, Dict[str, Any]] = {
    "afinidade_elemental": {
        "custo_pm": 0,
        "resumo": "Afinidade Elemental (magias/movimento do elemento escolhido)",
    },
    "encantar_objetos": {
        "custo_pm": 3,
        "resumo": "Encantar Objetos (3 PM, encanta item até fim da cena)",
    },
    "enfeiticar": {
        "custo_pm": 0,
        "resumo": "Enfeitiçar (como arcanista de mesmo nível)",
        "magia_como_classe": "enfeiticar",
    },
    "invisibilidade": {
        "custo_pm": 0,
        "resumo": "Invisibilidade (como arcanista de mesmo nível)",
        "magia_como_classe": "invisibilidade",
    },
    "lingua_da_natureza": {
        "custo_pm": 0,
        "resumo": "Língua da Natureza (+2 Adestramento/Sobrevivência; fala com animais/plantas)",
        "pericias_bonus": {"Adestramento": 2, "Sobrevivência": 2},
    },
    "maldicao": {
        "custo_pm": 3,
        "resumo": "Maldição (3 PM, alcance curto; resistência e efeito escolhidos)",
    },
    "mais_la_do_que_aqui": {
        "custo_pm": 2,
        "resumo": "Mais Lá do que Aqui (2 PM: camuflagem leve, +5 Furtividade)",
    },
    "metamorfose_animal": {
        "custo_pm": 3,
        "resumo": "Metamorfose Animal (3 PM, forma selvagem; conjura na forma)",
    },
    "sonhos_profeticos": {
        "custo_pm": 3,
        "resumo": "Sonhos Proféticos (1×/cena, 3 PM: rola 1d20 antecipado para teste)",
    },
    "velocidade_do_pensamento": {
        "custo_pm": 2,
        "resumo": "Velocidade do Pensamento (2 PM: ação padrão extra no 1º turno)",
    },
    "visao_feerica": {
        "custo_pm": 0,
        "resumo": "Visão Feérica (penumbra + Visão Mística permanente)",
        "visao_penumbra": True,
        "sentidos_misticos": True,
    },
    "voo": {
        "custo_pm": 1,
        "resumo": "Voo (pairar +3 m desloc.; voo 1 PM/rodada)",
        "pairar_desloc_extra_m": 3,
    },
}


@lru_cache(maxsize=1)
def _carregar_presentes() -> Dict[str, Any]:
    if not _PRESENTES_JSON.is_file():
        return {"presentes": []}
    return json.loads(_PRESENTES_JSON.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def _carregar_opcoes() -> Dict[str, Any]:
    if not _OPCOES_JSON.is_file():
        return {}
    return json.loads(_OPCOES_JSON.read_text(encoding="utf-8"))


def lista_presentes_duende() -> List[Dict[str, Any]]:
    rows = _carregar_presentes().get("presentes") or []
    out: List[Dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        slug = str(row.get("slug", "")).strip().lower()
        if not slug:
            continue
        out.append(
            {
                "slug": slug,
                "nome": str(row.get("nome", slug)).strip(),
                "descricao": str(row.get("descricao", "")).strip(),
                "requer_opcao": row.get("requer_opcao"),
            }
        )
    return sorted(out, key=lambda x: x["nome"].lower())


def opcoes_duende_catalogo() -> Dict[str, Any]:
    """Naturezas, tamanhos, tabus, limitações e sub-opções de presentes."""
    data = _carregar_opcoes()
    return {
        "naturezas": list(data.get("naturezas") or []),
        "tamanhos": list(data.get("tamanhos") or []),
        "tabu_penalidades": list(data.get("tabu_penalidades") or []),
        "limitacoes_fixas": list(data.get("limitacoes_fixas") or []),
        "afinidade_elementos": list(data.get("afinidade_elementos") or []),
        "maldicao_resistencias": list(data.get("maldicao_resistencias") or []),
        "maldicao_efeitos": list(data.get("maldicao_efeitos") or []),
        "formas_selvagem_metamorfose": list(
            data.get("formas_selvagem_metamorfose") or []
        ),
        "qtd_presentes": _QTD_PRESENTES,
        "pm_bonus_geracao_aleatoria": 2,
        "patamares_troca_poder": list(_PATAMARES_TROCA_PODER),
    }


def _slug_set(rows: List[Any]) -> frozenset[str]:
    out = set()
    for row in rows:
        if isinstance(row, dict):
            s = str(row.get("slug", "")).strip().lower()
            if s:
                out.add(s)
    return frozenset(out)


def _presentes_por_slug() -> Dict[str, Dict[str, Any]]:
    return {p["slug"]: p for p in lista_presentes_duende()}


def _tamanho_row(slug: str) -> Optional[Dict[str, Any]]:
    s = str(slug or "").strip().lower()
    for row in opcoes_duende_catalogo().get("tamanhos") or []:
        if isinstance(row, dict) and str(row.get("slug", "")).lower() == s:
            return row
    return None


def calcular_modificadores_atributos_duende(config: Dict[str, Any]) -> Dict[str, int]:
    """Modificadores raciais de atributo a partir do bloco duende."""
    out = {k: 0 for k in _ATTRS}
    if not isinstance(config, dict):
        return out

    natureza = str(config.get("natureza") or "").strip().lower()
    if natureza == "animal":
        nat_attr = str(config.get("natureza_atributo") or "").strip().lower()
        if nat_attr in _ATTRS:
            out[nat_attr] += 1

    dons_raw = config.get("dons") or []
    if isinstance(dons_raw, list):
        for d in dons_raw:
            k = str(d or "").strip().lower()
            if k in _ATTRS:
                out[k] += 1

    tam = str(config.get("tamanho_raca") or "").strip().lower()
    row = _tamanho_row(tam)
    if row:
        if row.get("mod_for") is not None:
            out["for"] += int(row["mod_for"])
        if row.get("mod_des") is not None:
            out["des"] += int(row["mod_des"])
    return out


def _modificadores_tamanho_duende(tamanho: str) -> Dict[str, int]:
    """CA/ataque/manobra conforme Tabela 1-21 para o tamanho escolhido."""
    from app.games.tormenta.rules.combate_t20 import manobra_bonus_tamanho

    tam = str(tamanho or "medio").strip().lower()
    o = {"minusculo": 0, "pequeno": 1, "medio": 2, "grande": 3}.get(tam, 2)
    ca = 1 if o <= 1 else (-1 if o >= 3 else 0)
    atk = 1 if o <= 1 or o >= 3 else 0
    return {
        "ca_bonus": ca,
        "ataque_bonus": atk,
        "manobra_bonus": manobra_bonus_tamanho(tam),
    }


def _limitacoes_fixas_resumo() -> List[str]:
    linhas: List[str] = []
    for row in opcoes_duende_catalogo().get("limitacoes_fixas") or []:
        if not isinstance(row, dict):
            continue
        slug = str(row.get("slug") or "").strip().lower()
        nome = str(row.get("nome") or slug).strip()
        if slug == "tabu":
            continue
        desc = str(row.get("descricao") or "").strip()
        linhas.append(f"{nome}: {desc}" if desc else nome)
    return linhas


def _tabu_penalidade_pericia(config: Dict[str, Any]) -> Tuple[Optional[str], int]:
    pen = str((config or {}).get("tabu_penalidade") or "").strip().lower()
    if pen not in _TABU_PEN:
        return None, 0
    nome = _TABU_PERICIA_NOME.get(pen)
    mod = -5
    for row in opcoes_duende_catalogo().get("tabu_penalidades") or []:
        if isinstance(row, dict) and str(row.get("slug", "")).lower() == pen:
            mod = int(row.get("modificador", -5) or -5)
            break
    return nome, mod


def _aplicar_natureza_tracos(
    tracos: Dict[str, Any], natureza: str, opcoes: Dict[str, Any]
) -> None:
    nat = str(natureza or "").strip().lower()
    resumo = tracos.setdefault("escolhas_resumo", [])
    if not isinstance(resumo, list):
        resumo = []
        tracos["escolhas_resumo"] = resumo
    if nat == "vegetal":
        resumo.append("Natureza Vegetal + Florescer Feérico")
        tracos["natureza_vegetal"] = True
    elif nat == "mineral":
        rd = tracos.setdefault("reducao_dano", {})
        if isinstance(rd, dict):
            for tipo in ("corte", "fogo", "perfuracao"):
                rd[tipo] = 5
        tracos["imunidade_metabolismo"] = True
        resumo.append("Mineral: RD 5 (corte/fogo/perfuração); imune a metabolismo")


def _aplicar_presentes_tracos(
    tracos: Dict[str, Any],
    presentes: List[str],
    opcoes: Dict[str, Any],
) -> None:
    per_bonus: Dict[str, int] = dict(tracos.get("pericias_bonus") or {})
    resumo: List[str] = list(tracos.get("escolhas_resumo") or [])
    magias: List[str] = list(tracos.get("magias_inatas") or [])
    presentes_ativos: List[Dict[str, Any]] = []

    for slug in presentes:
        meta = _PRESENTES_MECANICOS.get(slug) or {}
        cat = _presentes_por_slug().get(slug) or {}
        nome = str(cat.get("nome") or slug).replace("_", " ").title()
        item: Dict[str, Any] = {
            "slug": slug,
            "nome": nome,
            "custo_pm": int(meta.get("custo_pm", 0) or 0),
        }
        if meta.get("magia_como_classe"):
            item["magia_como_classe"] = meta["magia_como_classe"]
            magias.append(str(meta["magia_como_classe"]))
        presentes_ativos.append(item)
        linha = str(meta.get("resumo") or cat.get("descricao") or nome).strip()
        if linha and linha not in resumo:
            resumo.append(linha)
        pb = meta.get("pericias_bonus") or {}
        if isinstance(pb, dict):
            for k, v in pb.items():
                per_bonus[str(k)] = int(per_bonus.get(str(k), 0) or 0) + int(v)
        if meta.get("visao_penumbra"):
            tracos["visao_penumbra"] = True
        if meta.get("sentidos_misticos"):
            tracos["sentidos_misticos"] = True
        if meta.get("pairar_desloc_extra_m"):
            base = int(tracos.get("deslocamento_m", 9) or 9)
            tracos["deslocamento_pairar_m"] = base + int(meta["pairar_desloc_extra_m"])
        if slug == "afinidade_elemental":
            el = str((opcoes or {}).get("afinidade_elemental") or "").strip().lower()
            if el:
                resumo.append(f"Afinidade Elemental: {el}")

    tracos["pericias_bonus"] = per_bonus
    tracos["escolhas_resumo"] = resumo
    tracos["magias_inatas"] = sorted(set(magias))
    tracos["presentes_ativos"] = presentes_ativos


def calcular_tracos_duende(config: Dict[str, Any]) -> Dict[str, Any]:
    """Traços mecânicos derivados de natureza, tamanho, presentes e tabu."""
    cfg = config if isinstance(config, dict) else {}
    tam = str(cfg.get("tamanho_raca") or "medio").strip().lower()
    row = _tamanho_row(tam) or _tamanho_row("medio") or {}
    presentes = [
        str(p).strip().lower() for p in (cfg.get("presentes") or []) if str(p).strip()
    ]
    opcoes = cfg.get("presentes_opcoes") or {}
    if not isinstance(opcoes, dict):
        opcoes = {}
    for raw in cfg.get("trocas_poder_presente") or []:
        if not isinstance(raw, dict):
            continue
        pslug = str(raw.get("presente") or "").strip().lower()
        if pslug and pslug not in presentes:
            presentes.append(pslug)
        tro_opc = raw.get("opcoes")
        if isinstance(tro_opc, dict):
            for chave, val in tro_opc.items():
                opcoes[chave] = val

    tam_mod = _modificadores_tamanho_duende(tam)
    tracos: Dict[str, Any] = {
        "tamanho": tam,
        "deslocamento_m": int(row.get("deslocamento_m", 9) or 9),
        "furtividade_bonus": int(row.get("furtividade_bonus", 0) or 0),
        "pericias_bonus": {},
        "deslocamento_pairar_m": None,
        "deslocamento_voo_m": None,
        "tipo_criatura": "espirito",
        "ca_bonus": tam_mod["ca_bonus"],
        "ataque_bonus": tam_mod["ataque_bonus"],
        "manobra_bonus": tam_mod["manobra_bonus"],
        "reducao_dano": {},
        "imunidades_dano": {},
        "magias_inatas": [],
        "escolhas_resumo": [],
        "limitacoes_resumo": _limitacoes_fixas_resumo(),
        "presentes_ativos": [],
    }

    _aplicar_natureza_tracos(tracos, str(cfg.get("natureza") or ""), opcoes)
    _aplicar_presentes_tracos(tracos, presentes, opcoes)

    if "voo" in presentes:
        tracos["voo_pm_por_rodada"] = 1

    tabu_nome, tabu_mod = _tabu_penalidade_pericia(cfg)
    if tabu_nome:
        pb = tracos.setdefault("pericias_bonus", {})
        if isinstance(pb, dict):
            pb[tabu_nome] = int(pb.get(tabu_nome, 0) or 0) + tabu_mod
        tabu_txt = str(cfg.get("tabu_texto") or "").strip()
        if tabu_txt:
            tracos.setdefault("escolhas_resumo", []).append(
                f"Tabu ({tabu_nome} {tabu_mod}): {tabu_txt}"
            )

    return tracos


def validar_duende_ficha(
    ficha_json: Dict[str, Any],
    *,
    exigir_bloco: bool = True,
) -> Tuple[bool, str]:
    """Valida ``ficha_json.duende`` quando a raça é Duende."""
    slug = str(ficha_json.get("raca_tormenta_slug") or "").strip().lower()
    du = ficha_json.get("duende")
    if slug != "duende":
        if du and exigir_bloco:
            return False, "Bloco duende só é permitido para raça Duende."
        return True, ""

    if not du:
        return False, "Duende: configure natureza, tamanho, dons, presentes e tabu."
    if not isinstance(du, dict):
        return False, "duende deve ser um objeto."

    natureza = str(du.get("natureza") or "").strip().lower()
    if natureza not in _NATUREZAS:
        return False, "Duende: escolha natureza animal, vegetal ou mineral."

    tamanho = str(du.get("tamanho_raca") or "").strip().lower()
    if tamanho not in _TAMANHOS:
        return False, "Duende: escolha tamanho minúsculo, pequeno, médio ou grande."

    if natureza == "animal":
        nat_attr = str(du.get("natureza_atributo") or "").strip().lower()
        if nat_attr not in _ATTRS:
            return False, "Duende animal: escolha o atributo +1 da natureza."

    dons_raw = du.get("dons") or []
    if not isinstance(dons_raw, list):
        return False, "Duende: dons deve ser uma lista."
    dons = [str(d).strip().lower() for d in dons_raw if str(d).strip()]
    if len(dons) != 2:
        return False, "Duende: escolha exatamente dois Dons (+1 em cada atributo)."
    if len(set(dons)) != 2:
        return False, "Duende: os dois Dons devem ser atributos diferentes."
    if any(d not in _ATTRS for d in dons):
        return False, "Duende: don inválido."

    presentes_raw = du.get("presentes") or []
    if not isinstance(presentes_raw, list):
        return False, "Duende: presentes deve ser uma lista."
    presentes = [str(p).strip().lower() for p in presentes_raw if str(p).strip()]
    if len(presentes) != _QTD_PRESENTES:
        return False, f"Duende: escolha exatamente {_QTD_PRESENTES} Presentes."
    if len(set(presentes)) != _QTD_PRESENTES:
        return False, "Duende: presentes duplicados."

    catalogo = _presentes_por_slug()
    for p in presentes:
        if p not in catalogo:
            return False, f"Duende: presente inválido '{p}'."

    opcoes = du.get("presentes_opcoes") or {}
    if opcoes and not isinstance(opcoes, dict):
        return False, "Duende: presentes_opcoes deve ser um objeto."

    elems = _slug_set(opcoes_duende_catalogo().get("afinidade_elementos") or [])
    if "afinidade_elemental" in presentes:
        el = str((opcoes or {}).get("afinidade_elemental") or "").strip().lower()
        if el not in elems:
            return (
                False,
                "Duende: Afinidade Elemental exige elemento água, fogo ou vegetação.",
            )

    if "maldicao" in presentes:
        mal = (opcoes or {}).get("maldicao") or {}
        if not isinstance(mal, dict):
            return False, "Duende: Maldição exige resistência e efeito."
        res = str(mal.get("resistencia") or "").strip().lower()
        efe = str(mal.get("efeito") or "").strip().lower()
        res_ok = _slug_set(opcoes_duende_catalogo().get("maldicao_resistencias") or [])
        efe_ok = _slug_set(opcoes_duende_catalogo().get("maldicao_efeitos") or [])
        if res not in res_ok or efe not in efe_ok:
            return False, "Duende: Maldição — resistência ou efeito inválido."

    if "metamorfose_animal" in presentes:
        forma = str((opcoes or {}).get("metamorfose_animal") or "").strip().lower()
        formas = _slug_set(
            opcoes_duende_catalogo().get("formas_selvagem_metamorfose") or []
        )
        if forma not in formas:
            return False, "Duende: Metamorfose Animal exige forma selvagem."

    tabu_txt = str(du.get("tabu_texto") or "").strip()
    if len(tabu_txt) < 3:
        return False, "Duende: descreva o tabu (mínimo 3 caracteres)."
    pen = str(du.get("tabu_penalidade") or "").strip().lower()
    if pen not in _TABU_PEN:
        return (
            False,
            "Duende: escolha penalidade do tabu (Diplomacia, Iniciativa, Luta ou Percepção).",
        )

    if du.get("geracao_aleatoria") is not None and not isinstance(
        du.get("geracao_aleatoria"), bool
    ):
        return False, "Duende: geracao_aleatoria deve ser booleano."

    trocas = du.get("trocas_poder_presente") or []
    if trocas and not isinstance(trocas, list):
        return False, "Duende: trocas_poder_presente deve ser uma lista."
    seen_nv: set = set()
    for raw in trocas:
        if not isinstance(raw, dict):
            return False, "Duende: cada troca poder→presente deve ser um objeto."
        try:
            nv = int(raw.get("nivel") or 0)
        except (TypeError, ValueError):
            return False, "Duende: nível inválido em troca poder→presente."
        if nv in seen_nv:
            return False, "Duende: patamar duplicado em troca poder→presente."
        seen_nv.add(nv)
        if nv not in _PATAMARES_TROCA_PODER:
            return (
                False,
                "Duende: troca poder→presente só nos patamares 5, 10, 15 ou 20.",
            )
        pslug = str(raw.get("presente") or "").strip().lower()
        if pslug not in catalogo:
            return False, f"Duende: presente inválido na troca '{pslug}'."
        tro_opc = raw.get("opcoes") if isinstance(raw.get("opcoes"), dict) else {}
        if pslug == "afinidade_elemental" and pslug not in presentes:
            el = str(tro_opc.get("afinidade_elemental") or "").strip().lower()
            if el not in elems:
                return (
                    False,
                    "Duende: troca Afinidade Elemental exige elemento água, fogo ou vegetação.",
                )
        if pslug == "maldicao" and pslug not in presentes:
            mal = tro_opc.get("maldicao") or {}
            if not isinstance(mal, dict):
                return False, "Duende: troca Maldição exige resistência e efeito."
            res = str(mal.get("resistencia") or "").strip().lower()
            efe = str(mal.get("efeito") or "").strip().lower()
            res_ok = _slug_set(
                opcoes_duende_catalogo().get("maldicao_resistencias") or []
            )
            efe_ok = _slug_set(opcoes_duende_catalogo().get("maldicao_efeitos") or [])
            if res not in res_ok or efe not in efe_ok:
                return False, "Duende: troca Maldição — resistência ou efeito inválido."
        if pslug == "metamorfose_animal" and pslug not in presentes:
            forma = str(tro_opc.get("metamorfose_animal") or "").strip().lower()
            formas = _slug_set(
                opcoes_duende_catalogo().get("formas_selvagem_metamorfose") or []
            )
            if forma not in formas:
                return False, "Duende: troca Metamorfose Animal exige forma selvagem."

    return True, ""


def rolar_duende_aleatorio() -> Dict[str, Any]:
    """Gera configuração aleatória (1d3, 1d4, 2d6, 3d12) conforme livro."""
    op = opcoes_duende_catalogo()
    naturezas = [str(n["slug"]).lower() for n in op.get("naturezas") or []]
    tamanhos = [str(t["slug"]).lower() for t in op.get("tamanhos") or []]
    presentes_all = [p["slug"] for p in lista_presentes_duende()]

    idx_nat = random.randint(1, 3)
    natureza = naturezas[idx_nat - 1] if idx_nat <= len(naturezas) else "animal"

    idx_tam = random.randint(1, 4)
    tamanho = tamanhos[idx_tam - 1] if idx_tam <= len(tamanhos) else "medio"

    d1 = random.randint(1, 6)
    d2 = random.randint(1, 6)
    attr_map = list(_ATTRS)
    don_a = attr_map[d1 - 1]
    don_b = attr_map[d2 - 1]
    if don_a == don_b:
        alt = attr_map[(d2 % 5) + (1 if d2 % 5 == 0 else 0)]
        for cand in attr_map:
            if cand != don_a:
                alt = cand
                break
        don_b = alt
    dons = [don_a, don_b]

    picks: List[str] = []
    tentativas = 0
    while len(picks) < _QTD_PRESENTES and presentes_all and tentativas < 48:
        tentativas += 1
        roll = random.randint(1, 12)
        slug = (
            presentes_all[roll - 1] if roll <= len(presentes_all) else presentes_all[0]
        )
        if slug not in picks:
            picks.append(slug)

    out: Dict[str, Any] = {
        "natureza": natureza,
        "tamanho_raca": tamanho,
        "dons": dons,
        "presentes": picks,
        "tabu_texto": "",
        "tabu_penalidade": "diplomacia",
        "geracao_aleatoria": True,
        "presentes_opcoes": {},
    }
    if natureza == "animal":
        out["natureza_atributo"] = attr_map[random.randint(0, 5)]
    return out


def presentes_duende_slugs_ficha(ficha_json: Optional[Dict[str, Any]]) -> List[str]:
    """Presentes iniciais + extras por troca de poder de classe."""
    fj = ficha_json if isinstance(ficha_json, dict) else {}
    du = fj.get("duende")
    if not isinstance(du, dict):
        return []
    seen: set[str] = set()
    out: List[str] = []
    for raw in du.get("presentes") or []:
        s = str(raw or "").strip().lower()
        if s and s not in seen:
            seen.add(s)
            out.append(s)
    for raw in du.get("trocas_poder_presente") or []:
        if not isinstance(raw, dict):
            continue
        s = str(raw.get("presente") or "").strip().lower()
        if s and s not in seen:
            seen.add(s)
            out.append(s)
    return out


def patamares_troca_poder_duende() -> Tuple[int, ...]:
    return _PATAMARES_TROCA_PODER


def calcular_duende(ficha_json: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Resume configuração Duende validada."""
    du = ficha_json.get("duende")
    if not isinstance(du, dict):
        return None
    ok, motivo = validar_duende_ficha(ficha_json)
    attrs = calcular_modificadores_atributos_duende(du)
    tracos = calcular_tracos_duende(du)
    pm_bonus = 2 if du.get("geracao_aleatoria") else 0
    trocas = [
        dict(t) for t in (du.get("trocas_poder_presente") or []) if isinstance(t, dict)
    ]
    return {
        "valido": ok,
        "motivo": motivo,
        "modificadores_atributos": attrs,
        "tracos": tracos,
        "pm_bonus_geracao_aleatoria": pm_bonus,
        "trocas_poder_presente": trocas,
        "patamares_troca_poder": list(_PATAMARES_TROCA_PODER),
        "limitacoes_fixas": [
            str(x.get("slug", ""))
            for x in (opcoes_duende_catalogo().get("limitacoes_fixas") or [])
            if isinstance(x, dict)
        ],
    }
