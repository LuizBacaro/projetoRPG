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
_QTD_PRESENTES = 3


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


def calcular_tracos_duende(config: Dict[str, Any]) -> Dict[str, Any]:
    """Traços mecânicos derivados de tamanho e presentes."""
    tam = str((config or {}).get("tamanho_raca") or "medio").strip().lower()
    row = _tamanho_row(tam) or _tamanho_row("medio") or {}
    presentes = [
        str(p).strip().lower()
        for p in ((config or {}).get("presentes") or [])
        if str(p).strip()
    ]
    per_bonus: Dict[str, int] = {}
    if "lingua_da_natureza" in presentes:
        per_bonus["Adestramento"] = 2
        per_bonus["Sobrevivência"] = 2

    desloc_pairar = None
    if "voo" in presentes:
        base = int(row.get("deslocamento_m", 9) or 9)
        desloc_pairar = base + 3

    return {
        "tamanho": tam,
        "deslocamento_m": int(row.get("deslocamento_m", 9) or 9),
        "furtividade_bonus": int(row.get("furtividade_bonus", 0) or 0),
        "pericias_bonus": per_bonus,
        "deslocamento_pairar_m": desloc_pairar,
        "deslocamento_voo_m": None,
        "tipo_criatura": "espirito",
    }


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


def calcular_duende(ficha_json: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Resume configuração Duende validada."""
    du = ficha_json.get("duende")
    if not isinstance(du, dict):
        return None
    ok, motivo = validar_duende_ficha(ficha_json)
    attrs = calcular_modificadores_atributos_duende(du)
    tracos = calcular_tracos_duende(du)
    pm_bonus = 2 if du.get("geracao_aleatoria") else 0
    return {
        "valido": ok,
        "motivo": motivo,
        "modificadores_atributos": attrs,
        "tracos": tracos,
        "pm_bonus_geracao_aleatoria": pm_bonus,
        "limitacoes_fixas": [
            str(x.get("slug", ""))
            for x in (opcoes_duende_catalogo().get("limitacoes_fixas") or [])
            if isinstance(x, dict)
        ],
    }
