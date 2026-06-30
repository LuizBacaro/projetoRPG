"""Carga e espaços — Tormenta 20 v1.3 (RF-T07f, p.141)."""

from __future__ import annotations

import json
import unicodedata
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_OCUP_JSON = _DATA_DIR / "carga_ocupacao_v13.json"

PENALIDADE_SOBRECARGA = 5
DESLOCAMENTO_SOBRECARGA_M = 3


def limite_carga_for(for_valor: int) -> int:
    """
    Limite normal de espaços: 10 + 2×FOR (FOR ≥ 0) ou 10 + FOR (FOR negativa: −1/ponto).
    """
    f = int(for_valor)
    if f >= 0:
        return max(0, 10 + 2 * f)
    return max(0, 10 + f)


def limite_carga_maximo(for_valor: int) -> int:
    """Máximo absoluto = 2× o limite normal."""
    return max(0, 2 * limite_carga_for(for_valor))


def _normalizar_chave(texto: str) -> str:
    s = unicodedata.normalize("NFKD", str(texto or "").strip().lower())
    return "".join(c for c in s if not unicodedata.combining(c))


@lru_cache(maxsize=1)
def _carregar_ocupacao() -> Dict[str, Any]:
    if not _OCUP_JSON.is_file():
        return {}
    return json.loads(_OCUP_JSON.read_text(encoding="utf-8"))


def espacos_moedas(moedas_total: int) -> int:
    """1 espaço por 1.000 moedas (qualquer tipo)."""
    try:
        n = int(moedas_total)
    except (TypeError, ValueError):
        n = 0
    if n <= 0:
        return 0
    return n // 1000


def _espacos_escudo(nome_norm: str, cfg: Dict[str, Any]) -> Optional[float]:
    for frag in cfg.get("escudo_pesado_nomes") or []:
        if _normalizar_chave(str(frag)) in nome_norm:
            return 2.0
    if "escudo" in nome_norm and "pesad" in nome_norm:
        return 2.0
    if "escudo" in nome_norm or "broquel" in nome_norm:
        return 1.0
    return None


def espacos_por_item(item: Dict[str, Any]) -> float:
    """
    Espaços ocupados por unidade do item.
    Prioridade: campo explícito → zero → nome → tipo proteção → categoria → padrão leve → 1.
    """
    if not isinstance(item, dict):
        return 1.0
    if item.get("espacos") is not None:
        try:
            return max(0.0, float(item["espacos"]))
        except (TypeError, ValueError):
            pass
    if item.get("ocupa_espaco") is False:
        return 0.0

    cfg = _carregar_ocupacao()
    nome = str(item.get("nome") or "").strip()
    nome_norm = _normalizar_chave(nome)

    for z in cfg.get("zero_espacos_nomes") or []:
        if _normalizar_chave(str(z)) == nome_norm:
            return 0.0

    por_nome = cfg.get("por_nome") or {}
    if isinstance(por_nome, dict):
        for chave, val in por_nome.items():
            if _normalizar_chave(str(chave)) == nome_norm:
                return float(val)

    tipo_prot = str(item.get("tipo") or "").strip().lower()
    por_tipo = cfg.get("por_tipo_protecao") or {}
    if tipo_prot and isinstance(por_tipo, dict) and tipo_prot in por_tipo:
        esp = float(por_tipo[tipo_prot])
        if tipo_prot == "escudo":
            esc = _espacos_escudo(nome_norm, cfg)
            if esc is not None:
                return esc
        return esp

    esc = _espacos_escudo(nome_norm, cfg)
    if esc is not None:
        return esc

    cat = _normalizar_chave(str(item.get("categoria") or ""))
    por_cat = cfg.get("por_categoria") or {}
    if cat and isinstance(por_cat, dict):
        for chave, val in por_cat.items():
            if _normalizar_chave(str(chave)) in cat or cat in _normalizar_chave(
                str(chave)
            ):
                return float(val)

    for frag in cfg.get("meio_espaco_padroes") or []:
        if _normalizar_chave(str(frag)) in nome_norm:
            return 0.5

    if "duas m" in cat or "duas m" in nome_norm or "duas maos" in nome_norm:
        return 2.0
    if "armadura leve" in cat or (tipo_prot == "leve"):
        return 2.0
    if "armadura pesada" in cat or (tipo_prot == "pesada"):
        return 5.0
    if "armadura" in cat or "armadura" in nome_norm:
        return 2.0

    return 1.0


def _quantidade_item(item: Dict[str, Any]) -> int:
    try:
        q = int(item.get("quantidade", 1) or 1)
    except (TypeError, ValueError):
        q = 1
    return max(1, q)


def espacos_inventario(itens: Optional[List[Any]]) -> float:
    """Soma espaços de todos os itens (quantidade incluída)."""
    total = 0.0
    for raw in itens or []:
        if not isinstance(raw, dict):
            continue
        esp = espacos_por_item(raw)
        total += esp * _quantidade_item(raw)
    return total


def estado_carga(for_valor: int, espacos_usados: float) -> str:
    """
    normal | sobrecarregado | acima_maximo
    """
    lim = limite_carga_for(for_valor)
    max_lim = limite_carga_maximo(for_valor)
    usado = float(espacos_usados)
    if usado <= lim:
        return "normal"
    if usado <= max_lim:
        return "sobrecarregado"
    return "acima_maximo"


def preview_carga_v13(
    *,
    for_valor: int,
    itens: Optional[List[Any]] = None,
    moedas_total: int = 0,
) -> Dict[str, Any]:
    """Resumo completo de carga v1.3 para API/ficha."""
    lim = limite_carga_for(for_valor)
    max_lim = limite_carga_maximo(for_valor)
    esp_moedas = espacos_moedas(moedas_total)
    esp_itens = espacos_inventario(itens)
    usado = esp_itens + esp_moedas
    estado = estado_carga(for_valor, usado)
    sobrecarga = estado == "sobrecarregado" or estado == "acima_maximo"

    detalhes: List[Dict[str, Any]] = []
    for raw in itens or []:
        if not isinstance(raw, dict):
            continue
        nome = str(raw.get("nome") or "").strip() or "—"
        qtd = _quantidade_item(raw)
        esp_u = espacos_por_item(raw)
        detalhes.append(
            {
                "nome": nome,
                "quantidade": qtd,
                "espacos_unidade": esp_u,
                "espacos_total": round(esp_u * qtd, 2),
            }
        )
    if esp_moedas > 0:
        detalhes.append(
            {
                "nome": "Moedas",
                "quantidade": int(moedas_total),
                "espacos_unidade": esp_moedas,
                "espacos_total": float(esp_moedas),
            }
        )

    return {
        "limite": lim,
        "limite_maximo": max_lim,
        "espacos_usados": round(usado, 2),
        "espacos_itens": round(esp_itens, 2),
        "espacos_moedas": esp_moedas,
        "estado": estado,
        "sobrecarga": sobrecarga,
        "penalidade_armadura_extra": PENALIDADE_SOBRECARGA if sobrecarga else 0,
        "deslocamento_extra_m": DESLOCAMENTO_SOBRECARGA_M if sobrecarga else 0,
        "detalhes": detalhes,
    }


def formatar_espacos(valor: float) -> str:
    """Ex.: 12, 12.5, 0.5"""
    if abs(valor - round(valor)) < 0.001:
        return str(int(round(valor)))
    if abs(valor * 2 - round(valor * 2)) < 0.001:
        v = round(valor * 2) / 2
        return str(v).replace(".0", "")
    return str(round(valor, 2))
