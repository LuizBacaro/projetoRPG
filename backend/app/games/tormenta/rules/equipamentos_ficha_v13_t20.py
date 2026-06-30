"""Equipamentos automáticos v1.3 — origem e kit inicial."""

from __future__ import annotations

import re
import unicodedata
from typing import Any, Dict, List, Optional

from app.games.tormenta.rules.kit_inicial_v13_t20 import itens_kit_inicial_v13
from app.games.tormenta.rules.origens_t20 import (
    lista_origens_v13,
    resolver_itens_origem_v13,
)
from app.games.tormenta.rules.regra_versao_t20 import (
    REGRA_VERSAO_V13,
    regra_versao_de_ficha,
)

AUTO_EQUIP_NOTA_PREFIX = "auto:v13:"


def _normalizar_slug(texto: str) -> str:
    s = unicodedata.normalize("NFKD", str(texto or ""))
    s = s.encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "_", s).strip("_")


def nota_auto_equip_v13(tipo: str, chave: str) -> str:
    return f"{AUTO_EQUIP_NOTA_PREFIX}{tipo}:{_normalizar_slug(chave)}"


def _slug_origem_de_ficha(ficha_json: dict) -> str:
    slug = str(ficha_json.get("origem_slug") or "").strip().lower()
    if slug:
        return slug
    orig_nome = str(ficha_json.get("origem") or "").strip().lower()
    if not orig_nome:
        return ""
    for row in lista_origens_v13():
        if str(row.get("nome") or "").strip().lower() == orig_nome:
            return str(row.get("slug") or "")
    return ""


def listar_equipamentos_sync_v13(ficha_json: Optional[dict]) -> List[Dict[str, Any]]:
    """
    Equipamentos que a ficha v1.3 deve ter em SQL (origem + kit inicial).
    Retorna dicts com nome, quantidade, notas.
    """
    fj = dict(ficha_json or {})
    if regra_versao_de_ficha(fj) != REGRA_VERSAO_V13:
        return []

    out: List[Dict[str, Any]] = []
    seen_notas: set[str] = set()

    def _add(tipo: str, chave: str, nome: str, qtd: int = 1) -> None:
        n = str(nome or "").strip()
        if not n:
            return
        nota = nota_auto_equip_v13(tipo, chave)
        if nota in seen_notas:
            return
        seen_notas.add(nota)
        out.append({"nome": n, "quantidade": max(1, int(qtd)), "notas": nota})

    slug_origem = _slug_origem_de_ficha(fj)
    if slug_origem:
        for i, nome in enumerate(resolver_itens_origem_v13(slug_origem, fj)):
            _add("origem", f"{slug_origem}_{i}_{_normalizar_slug(nome)}", nome)

    for i, row in enumerate(itens_kit_inicial_v13(fj)):
        _add(
            "kit",
            f"item_{i}_{_normalizar_slug(row.get('nome', ''))}",
            row["nome"],
            row.get("quantidade", 1),
        )

    return out
