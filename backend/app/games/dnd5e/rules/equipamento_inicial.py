"""Equipamento inicial por classe — aplicação na ficha."""

from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional

from app.games.dnd5e.data.equipamento_inicial_catalogo import (
    EQUIPAMENTO_INICIAL_POR_CLASSE,
    pacote_equipamento_classe,
)
from app.games.dnd5e.rules.classes import CLASSE_SLUGS_VALIDOS
from app.games.dnd5e.rules.equipamento import arma_por_slug, item_por_slug


def _nome_item(slug: str, *, tipo: str = "item") -> str:
    if tipo == "arma":
        arma = arma_por_slug(slug)
        return arma.nome if arma else slug.replace("-", " ").title()
    item = item_por_slug(slug)
    return item.nome if item else slug.replace("-", " ").title()


def _item_inventario_classe(
    slug: str,
    classe_slug: str,
    *,
    quantidade: int = 1,
    tipo: str = "item",
) -> Dict[str, Any]:
    item_slug = (slug or "").strip().lower()
    return {
        "id": f"cls_{classe_slug}_{item_slug}_{uuid.uuid4().hex[:8]}",
        "slug": item_slug,
        "nome": _nome_item(item_slug, tipo=tipo),
        "quantidade": max(1, int(quantidade)),
        "fonte": "classe",
        "classe_slug": classe_slug,
    }


def _remover_itens_classe(
    equipamentos: List[Dict[str, Any]],
    classe_slug: str,
) -> List[Dict[str, Any]]:
    alvo = (classe_slug or "").strip().lower()
    if not alvo:
        return list(equipamentos)
    return [
        item
        for item in equipamentos
        if not (
            isinstance(item, dict)
            and item.get("fonte") == "classe"
            and str(item.get("classe_slug") or "").strip().lower() == alvo
        )
    ]


def _mesclar_item(
    equipamentos: List[Dict[str, Any]],
    slug: str,
    classe_slug: str,
    *,
    quantidade: int = 1,
    tipo: str = "item",
) -> None:
    item_slug = (slug or "").strip().lower()
    if not item_slug:
        return
    existente = next(
        (
            x
            for x in equipamentos
            if isinstance(x, dict)
            and x.get("fonte") == "classe"
            and str(x.get("classe_slug") or "").strip().lower() == classe_slug
            and str(x.get("slug") or "").strip().lower() == item_slug
        ),
        None,
    )
    if existente:
        existente["quantidade"] = int(existente.get("quantidade") or 1) + int(
            quantidade
        )
        return
    equipamentos.append(
        _item_inventario_classe(
            item_slug, classe_slug, quantidade=quantidade, tipo=tipo
        )
    )


def aplicar_equipamento_classe_na_ficha(
    ficha: Dict[str, Any],
    *,
    forcar: bool = False,
) -> Dict[str, Any]:
    """Aplica pacote PHB padrão da classe. Substitui pacote anterior da mesma origem."""
    out = dict(ficha or {})
    slug_atual = (out.get("classe_slug") or "").strip().lower() or None
    slug_aplicado = (out.get("classe_equip_slug") or "").strip().lower() or None

    if (
        not forcar
        and slug_atual
        and slug_atual == slug_aplicado
        and out.get("classe_equip_aplicado")
    ):
        return out

    inv = dict(out.get("inventario") or {})
    equipamentos = [
        dict(item) for item in (inv.get("equipamentos") or []) if isinstance(item, dict)
    ]

    if slug_aplicado:
        equipamentos = _remover_itens_classe(equipamentos, slug_aplicado)

    out["classe_equip_aplicado"] = False
    out["classe_equip_slug"] = slug_atual
    out.pop("classe_equip_nome", None)

    if not slug_atual or slug_atual not in CLASSE_SLUGS_VALIDOS:
        out.pop("classe_equip_slug", None)
        inv["equipamentos"] = equipamentos
        out["inventario"] = inv
        return out

    pacote = pacote_equipamento_classe(slug_atual)
    if pacote is None:
        inv["equipamentos"] = equipamentos
        out["inventario"] = inv
        return out

    for row in pacote.get("itens") or []:
        _mesclar_item(
            equipamentos,
            str(row.get("slug") or ""),
            slug_atual,
            quantidade=int(row.get("quantidade") or 1),
            tipo="item",
        )
    for row in pacote.get("armas_extras") or []:
        _mesclar_item(
            equipamentos,
            str(row.get("slug") or ""),
            slug_atual,
            quantidade=int(row.get("quantidade") or 1),
            tipo="arma",
        )

    armadura = (pacote.get("armadura_slug") or "").strip().lower()
    escudo = (pacote.get("escudo_slug") or "").strip().lower()
    arma = (pacote.get("arma_principal_slug") or "").strip().lower()

    if armadura:
        out["armadura_slug"] = armadura
        inv["armadura_slug"] = armadura
    if escudo:
        out["escudo_slug"] = escudo
        inv["escudo_slug"] = escudo
    elif not escudo and forcar:
        pass
    if arma:
        out["arma_principal_slug"] = arma
        inv["arma_principal_slug"] = arma

    inv["equipamentos"] = equipamentos
    out["inventario"] = inv
    out["classe_equip_aplicado"] = True
    out["classe_equip_nome"] = str(pacote.get("nome_pacote") or "")
    return out


def listar_pacotes_equipamento_classe() -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for slug in sorted(EQUIPAMENTO_INICIAL_POR_CLASSE):
        pacote = EQUIPAMENTO_INICIAL_POR_CLASSE[slug]
        out.append({"classe_slug": slug, **pacote})
    return out
