"""Validação de traços de antecedente na ficha."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.games.dnd5e.data.antecedentes_tracos_catalogo import (
    CATEGORIAS_TRACOS,
    tracos_opcoes_antecedente,
)

_LABELS = {
    "personalidade": "personalidade",
    "ideais": "ideal",
    "lacos": "laço",
    "fraquezas": "fraqueza",
}


def _lista_categoria(raw: Any, categoria: str) -> List[str]:
    if not isinstance(raw, dict):
        return []
    valor = raw.get(categoria)
    if isinstance(valor, list):
        return [str(x).strip() for x in valor if str(x).strip()]
    if valor:
        return [str(valor).strip()]
    return []


def normalizar_tracos_escolhidos(
    raw: Any,
    antecedente_slug: str,
) -> Dict[str, List[str]]:
    opcoes = tracos_opcoes_antecedente(antecedente_slug)
    out: Dict[str, List[str]] = {}
    for cat in CATEGORIAS_TRACOS:
        pool = set(opcoes.get(cat) or [])
        escolhidos = [item for item in _lista_categoria(raw, cat) if item in pool]
        out[cat] = [escolhidos[0]] if escolhidos else []
    return out


def tracos_estao_completos(tracos: Dict[str, List[str]]) -> bool:
    return all(tracos.get(cat) for cat in CATEGORIAS_TRACOS)


def validar_tracos_antecedente_na_ficha(
    ficha: Dict[str, Any]
) -> Optional[Dict[str, List[str]]]:
    slug = (ficha.get("antecedente_slug") or "").strip().lower() or None
    if not slug:
        if ficha.get("antecedente_tracos"):
            raise ValueError("Traços de antecedente exigem um antecedente selecionado")
        return None

    tracos = normalizar_tracos_escolhidos(ficha.get("antecedente_tracos"), slug)
    if tracos_estao_completos(tracos):
        return tracos

    faltando = [_LABELS[cat] for cat in CATEGORIAS_TRACOS if not tracos.get(cat)]
    raise ValueError(f"Escolha traço de {', '.join(faltando)} do antecedente")
