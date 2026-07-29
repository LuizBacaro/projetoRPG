"""Importação do bestiário MM 3.5 → combatente monstro."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Tuple

from app.games.dnd35.rules.bestiario_mm35 import (
    nivel_sugerido,
    obter_bestiario_por_slug,
)
from app.shared.exceptions.custom_exceptions import DadosInvalidos


def _int(row: Dict[str, Any], key: str, default: int = 0) -> int:
    try:
        return int(row.get(key, default))
    except (TypeError, ValueError):
        return default


def _ataques(row: Dict[str, Any]) -> List[Dict[str, str]]:
    raw = row.get("ataques")
    if not isinstance(raw, list):
        return []
    out: List[Dict[str, str]] = []
    for i, item in enumerate(raw):
        if not isinstance(item, dict):
            continue
        nome = str(item.get("nome") or f"Ataque {i + 1}").strip()
        bonus = str(item.get("bonus_ataque") or "+0").strip() or "+0"
        dano = str(item.get("dano") or "1d6").strip() or "1d6"
        tipo = str(item.get("tipo_dano") or "").strip()
        out.append(
            {
                "nome": nome,
                "bonus_ataque": bonus,
                "dano": dano,
                "tipo_dano": tipo,
            }
        )
    return out


def mapear_bestiario_para_combatente(
    slug: str,
    *,
    tipo: str = "monstro",
    campanha_id: Optional[int] = None,
    nome_override: Optional[str] = None,
    foto_url: Optional[str] = None,
) -> Tuple[Dict[str, Any], List[Dict[str, str]], Dict[str, Any]]:
    """
    Retorna (payload_create, ataques, overrides_pos_create).

    overrides_pos_create: ca/toque/surpresa/bba/habilidades — aplicados após
    ``criar`` porque o service recalcula defesas pela fórmula de armadura.
    """
    entrada = obter_bestiario_por_slug(slug)
    if not entrada:
        raise DadosInvalidos(f"Criatura do bestiário não encontrada: {slug}")

    if entrada.get("nd") is None and not entrada.get("categoria_idade"):
        raise DadosInvalidos(
            "Esta entrada é uma espécie-pai (ex.: Dragão Azul). "
            "Importe uma linha por idade (filhote, jovem…)."
        )

    t = (tipo or "monstro").strip().lower()
    if t not in ("monstro", "npc"):
        raise DadosInvalidos("tipo deve ser monstro ou npc")

    nome = (nome_override or entrada.get("nome") or "").strip()
    if not nome:
        raise DadosInvalidos("Entrada do bestiário sem nome")

    hp = max(1, _int(entrada, "hp_maximo", 1))
    ini = max(0, _int(entrada, "iniciativa", 0))
    nivel = nivel_sugerido(entrada)
    tipo_criatura = str(entrada.get("tipo_criatura") or "Monstro").strip() or "Monstro"
    ataques = _ataques(entrada)

    especiais = []
    for key in ("ataques_especiais", "qualidades_especiais"):
        for item in entrada.get(key) or []:
            txt = str(item).strip()
            if txt and txt not in especiais:
                especiais.append(txt)
    hab_json = (
        json.dumps(
            [{"nome": n, "descricao": ""} for n in especiais], ensure_ascii=False
        )
        if especiais
        else ""
    )

    payload: Dict[str, Any] = {
        "nome": nome,
        "tipo": t,
        "classe": tipo_criatura[:50],
        "raca": str(entrada.get("tamanho") or "")[:50],
        "raca_slug": "",
        "alinhamento": str(entrada.get("tendencia") or "")[:30],
        "pagina_referencia": str(entrada.get("pagina_referencia") or "")[:100],
        "hp_maximo": hp,
        "iniciativa": ini,
        "forca": max(1, min(50, _int(entrada, "for_valor", 10) or 1)),
        "destreza": max(1, min(50, _int(entrada, "des_valor", 10) or 1)),
        "constituicao": max(1, min(50, _int(entrada, "con_valor", 10) or 1)),
        "inteligencia": max(1, min(50, _int(entrada, "int_valor", 10) or 1)),
        "sabedoria": max(1, min(50, _int(entrada, "sab_valor", 10) or 1)),
        "carisma": max(1, min(50, _int(entrada, "car_valor", 10) or 1)),
        "fortitude": _int(entrada, "fortitude", 0),
        "reflexos": _int(entrada, "reflexos", 0),
        "vontade": _int(entrada, "vontade", 0),
        "nivel": nivel,
        "pontos": 0,
        "pc": 0,
        "pp": 0,
        "po": 0,
        "pl": 0,
        "ca": _int(entrada, "ca", 10),
        "toque": _int(entrada, "toque", 10),
        "surpresa": _int(entrada, "surpresa", 10),
    }
    if campanha_id is not None:
        payload["campanha_id"] = int(campanha_id)
    if foto_url:
        payload["foto_url"] = foto_url

    # Constituição 0 (mortos-vivos/limos): schema exige ≥1 — usar 10 e marcar nas habilidades.
    if _int(entrada, "con_valor", 10) <= 0:
        payload["constituicao"] = 10
        if "sem constituição" not in [x.lower() for x in especiais]:
            especiais.append("sem Constituição (morto-vivo/limo/elemental)")
            hab_json = json.dumps(
                [{"nome": n, "descricao": ""} for n in especiais], ensure_ascii=False
            )
    if _int(entrada, "int_valor", 10) <= 0:
        payload["inteligencia"] = 1
    if _int(entrada, "for_valor", 10) <= 0:
        payload["forca"] = 1

    overrides = {
        "ca": _int(entrada, "ca", 10),
        "toque": _int(entrada, "toque", 10),
        "surpresa": _int(entrada, "surpresa", 10),
        "bonus_base_ataque": str(entrada.get("ataque_base") or "").strip(),
        "habilidades_especiais": hab_json,
        "iniciativa": ini,
        "fortitude": _int(entrada, "fortitude", 0),
        "reflexos": _int(entrada, "reflexos", 0),
        "vontade": _int(entrada, "vontade", 0),
    }
    return payload, ataques, overrides
