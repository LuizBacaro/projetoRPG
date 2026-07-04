"""Melhor Amigo — regras do Treinador (Heróis de Arton v1.1, p.20–23)."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_TRUQUES_JSON = _DATA_DIR / "truques_melhor_amigo.json"
_TIPOS_JSON = _DATA_DIR / "tipos_melhor_amigo.json"

# Truques disponíveis por nível de Treinador: nível → qtd. máxima de truques
# Níveis 1: 2, 4: 3, 7: 4, 10: 5 (Tabela p.20)
_TRUQUES_POR_NIVEL: Dict[int, int] = {
    1: 2,
    2: 2,
    3: 2,
    4: 3,
    5: 3,
    6: 3,
    7: 4,
    8: 4,
    9: 4,
    10: 5,
}


@lru_cache(maxsize=1)
def _carregar_truques() -> Dict[str, Any]:
    if not _TRUQUES_JSON.is_file():
        return {"truques": []}
    return json.loads(_TRUQUES_JSON.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def _carregar_tipos() -> Dict[str, Any]:
    if not _TIPOS_JSON.is_file():
        return {"tipos": []}
    return json.loads(_TIPOS_JSON.read_text(encoding="utf-8"))


def lista_truques_melhor_amigo() -> List[Dict[str, Any]]:
    """Todos os truques disponíveis para o Melhor Amigo."""
    rows = _carregar_truques().get("truques") or []
    out: List[Dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        slug = str(row.get("slug", "")).strip()
        if not slug:
            continue
        out.append(
            {
                "slug": slug,
                "nome": str(row.get("nome", slug)).strip(),
                "descricao": str(row.get("descricao", "")).strip(),
                "nivel_minimo": int(row.get("nivel_minimo", 1) or 1),
                "pre_requisito": row.get("pre_requisito"),
            }
        )
    return sorted(out, key=lambda x: (x["nivel_minimo"], x["nome"].lower()))


def truques_disponiveis(nivel_treinador: int) -> List[Dict[str, Any]]:
    """Truques cujo `nivel_minimo` é satisfeito pelo nível atual do Treinador."""
    try:
        nv = max(1, int(nivel_treinador))
    except (TypeError, ValueError):
        nv = 1
    return [t for t in lista_truques_melhor_amigo() if t["nivel_minimo"] <= nv]


def qtd_truques_por_nivel(nivel_treinador: int) -> int:
    """Quantidade máxima de truques que o Melhor Amigo pode ter no nível dado."""
    try:
        nv = max(1, int(nivel_treinador))
    except (TypeError, ValueError):
        nv = 1
    # Para níveis acima de 10 mantém 5 truques (valor máximo na tabela)
    return _TRUQUES_POR_NIVEL.get(min(nv, 10), 5)


def lista_tipos_melhor_amigo() -> List[Dict[str, Any]]:
    """Tipos de Melhor Amigo com bônus automáticos."""
    rows = _carregar_tipos().get("tipos") or []
    out: List[Dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        slug = str(row.get("slug", "")).strip()
        if not slug:
            continue
        out.append(
            {
                "slug": slug,
                "nome": str(row.get("nome", slug)).strip(),
                "descricao": str(row.get("descricao", "")).strip(),
                "bonus_atributos": dict(row.get("bonus_atributos") or {}),
                "sentidos": list(row.get("sentidos") or []),
                "imunidades": list(row.get("imunidades") or []),
                "bonus_pericias": dict(row.get("bonus_pericias") or {}),
                "rd_bonus": int(row.get("rd_bonus", 0) or 0),
                "margem_ameaca_bonus": int(row.get("margem_ameaca_bonus", 0) or 0),
                "notas": str(row.get("notas", "")).strip(),
            }
        )
    return out


def bonus_por_tipo_amigo(slug_tipo: str) -> Optional[Dict[str, Any]]:
    """Bônus automáticos para o tipo de parceiro fornecido."""
    s = str(slug_tipo or "").strip().lower()
    for t in lista_tipos_melhor_amigo():
        if t["slug"] == s:
            return t
    return None


def _nivel_treinador_de_ficha(ficha_json: Dict[str, Any]) -> int:
    """Nível de Treinador na ficha (multiclasse ou bloco melhor_amigo)."""
    from app.games.tormenta.rules.progressao_pv_t20 import (
        niveis_multiclasse_v13_de_ficha,
    )

    try:
        nv_personagem = int(ficha_json.get("nivel") or 1)
    except (TypeError, ValueError):
        nv_personagem = 1
    for linha in niveis_multiclasse_v13_de_ficha(ficha_json, nv_personagem):
        if str(linha.get("slug") or "").lower() == "treinador":
            try:
                return max(1, int(linha.get("nivel") or 1))
            except (TypeError, ValueError):
                return 1
    ma = ficha_json.get("melhor_amigo")
    if isinstance(ma, dict):
        try:
            return max(1, int(ma.get("nivel") or 1))
        except (TypeError, ValueError):
            pass
    return 1


def validar_melhor_amigo_ficha(ficha_json: Dict[str, Any]) -> tuple[bool, str]:
    """Valida o bloco ``ficha_json.melhor_amigo`` quando presente."""
    ma = ficha_json.get("melhor_amigo")
    if not ma:
        return True, ""
    if not isinstance(ma, dict):
        return False, "melhor_amigo deve ser um objeto."
    tipo = str(ma.get("tipo") or "").strip().lower()
    if not tipo:
        return False, "Melhor Amigo: informe o tipo do parceiro."
    if bonus_por_tipo_amigo(tipo) is None:
        return False, f"Melhor Amigo: tipo inválido '{tipo}'."

    nv_treinador = _nivel_treinador_de_ficha(ficha_json)
    truques_raw = ma.get("truques") or []
    if not isinstance(truques_raw, list):
        return False, "Melhor Amigo: truques deve ser uma lista."
    truques = [str(t).strip().lower() for t in truques_raw if str(t).strip()]
    if len(truques) != len(set(truques)):
        return False, "Melhor Amigo: truques duplicados."

    qtd_max = qtd_truques_por_nivel(nv_treinador)
    if len(truques) > qtd_max:
        return False, (
            f"Melhor Amigo: no nível {nv_treinador} do Treinador, "
            f"máximo de {qtd_max} truques."
        )

    catalogo = {t["slug"]: t for t in truques_disponiveis(nv_treinador)}
    for slug in truques:
        if slug not in catalogo:
            return False, f"Melhor Amigo: truque '{slug}' indisponível neste nível."
        pre = catalogo[slug].get("pre_requisito")
        if pre and str(pre).strip().lower() not in truques:
            return False, (
                f"Melhor Amigo: truque '{slug}' exige pré-requisito '{pre}'."
            )
    return True, ""


def calcular_melhor_amigo(ficha_json: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Resume bônus e truques do Melhor Amigo a partir de ``ficha_json``."""
    ma = ficha_json.get("melhor_amigo")
    if not isinstance(ma, dict):
        return None

    ok, motivo = validar_melhor_amigo_ficha(ficha_json)
    tipo = str(ma.get("tipo") or "").strip().lower()
    truques = [
        str(t).strip().lower() for t in (ma.get("truques") or []) if str(t).strip()
    ]
    nv_treinador = _nivel_treinador_de_ficha(ficha_json)
    try:
        nv_parceiro = max(1, int(ma.get("nivel") or 1))
    except (TypeError, ValueError):
        nv_parceiro = 1

    bonus = bonus_por_tipo_amigo(tipo) or {}
    truques_detalhe = [t for t in lista_truques_melhor_amigo() if t["slug"] in truques]

    return {
        "valido": ok,
        "motivo": motivo,
        "nome": str(ma.get("nome") or "").strip(),
        "tipo": tipo,
        "nivel_parceiro": nv_parceiro,
        "nivel_treinador": nv_treinador,
        "truques": truques,
        "truques_detalhe": truques_detalhe,
        "qtd_maxima_truques": qtd_truques_por_nivel(nv_treinador),
        "bonus_tipo": {
            "bonus_atributos": dict(bonus.get("bonus_atributos") or {}),
            "sentidos": list(bonus.get("sentidos") or []),
            "imunidades": list(bonus.get("imunidades") or []),
            "bonus_pericias": dict(bonus.get("bonus_pericias") or {}),
            "rd_bonus": int(bonus.get("rd_bonus", 0) or 0),
            "margem_ameaca_bonus": int(bonus.get("margem_ameaca_bonus", 0) or 0),
        },
    }
