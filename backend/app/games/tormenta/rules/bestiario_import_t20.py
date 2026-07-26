"""Importação de criaturas do catálogo stub MB → personagem monstro/NPC."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.games.tormenta.rules.ameaca_bloco_t20 import ameaca_minima
from app.games.tormenta.rules.catalogo_t20 import obter_bestiario_mb_por_slug
from app.games.tormenta.schemas.personagem import TormentaPersonagemCreate
from app.shared.exceptions.custom_exceptions import DadosInvalidos


def _int_field(row: Dict[str, Any], key: str, default: int = 0) -> int:
    try:
        return int(row.get(key, default))
    except (TypeError, ValueError):
        return default


def _ataques_de_entrada(row: Dict[str, Any]) -> List[Dict[str, str]]:
    raw = row.get("ataques")
    if not isinstance(raw, list):
        return []
    out: List[Dict[str, str]] = []
    for i, item in enumerate(raw):
        if not isinstance(item, dict):
            continue
        nome = str(item.get("nome") or item.get("arma") or f"Ataque {i + 1}").strip()
        bonus = str(
            item.get("bonus_ataque")
            if item.get("bonus_ataque") is not None
            else item.get("teste") or ""
        ).strip()
        dano = str(item.get("dano") or "").strip()
        if not nome and not bonus and not dano:
            continue
        out.append(
            {
                "nome": nome or f"Ataque {i + 1}",
                "bonus_ataque": bonus or "+0",
                "dano": dano or "—",
            }
        )
    return out


def mapear_bestiario_para_create(
    entrada: Dict[str, Any],
    *,
    tipo: str = "monstro",
    campanha_id: Optional[int] = None,
    nome_override: Optional[str] = None,
) -> TormentaPersonagemCreate:
    t = (tipo or "monstro").strip().lower()
    if t not in ("monstro", "npc"):
        raise DadosInvalidos(
            "tipo deve ser monstro ou npc para importação do bestiário"
        )

    nome = (nome_override or entrada.get("nome") or "").strip()
    if not nome:
        raise DadosInvalidos("Entrada do bestiário sem nome")

    pv_max = max(1, _int_field(entrada, "pv_max", 1))
    ataques = _ataques_de_entrada(entrada)
    slug = str(entrada.get("slug") or "").strip()

    ficha_json: Dict[str, Any] = {
        "regra_versao": "mb",
        "bestiario_slug": slug or None,
        "bestiario_fonte": "stub_mb",
    }
    if ataques:
        ficha_json["ataques"] = ataques

    nd = entrada.get("nd")
    nd_int = None
    if nd is not None:
        nd_int = _int_field(entrada, "nd", 0) or None
        ficha_json["nd"] = nd_int
    tipo_criatura = str(entrada.get("tipo_criatura") or "").strip()
    if tipo_criatura:
        ficha_json["tipo_criatura"] = tipo_criatura

    am = ameaca_minima(
        nd=nd_int if nd_int is not None else max(0, _int_field(entrada, "nivel", 1)),
        papel_combate="solo",
    )
    if tipo_criatura:
        am["tipo_criatura"] = tipo_criatura
    if ataques:
        am["acoes"]["corpo_a_corpo"] = [
            {
                "nome": a.get("nome") or "Ataque",
                "ataque": a.get("bonus_ataque") or "+0",
                "dano": a.get("dano") or "—",
                "critico": "",
            }
            for a in ataques
        ]
    ficha_json["ameaca"] = am

    return TormentaPersonagemCreate(
        tipo=t,
        nome=nome,
        campanha_id=campanha_id,
        for_valor=_int_field(entrada, "for_valor", 10),
        des_valor=_int_field(entrada, "des_valor", 10),
        con_valor=_int_field(entrada, "con_valor", 10),
        int_valor=_int_field(entrada, "int_valor", 10),
        sab_valor=_int_field(entrada, "sab_valor", 10),
        car_valor=_int_field(entrada, "car_valor", 10),
        pv_max=pv_max,
        pv_atual=pv_max,
        ca=max(0, _int_field(entrada, "ca", 10)),
        rd=str(entrada.get("rd") or "").strip(),
        nivel=max(0, _int_field(entrada, "nivel", _int_field(entrada, "nd", 1))),
        iniciativa=_int_field(entrada, "iniciativa", 0),
        deslocamento=str(entrada.get("deslocamento") or "").strip(),
        tamanho=str(entrada.get("tamanho") or "").strip(),
        fort_total=_int_field(entrada, "fort_total", 0),
        ref_total=_int_field(entrada, "ref_total", 0),
        von_total=_int_field(entrada, "von_total", 0),
        ficha_json=ficha_json,
    )


def criar_payload_import_bestiario(
    slug: str,
    *,
    tipo: str = "monstro",
    campanha_id: Optional[int] = None,
    nome_override: Optional[str] = None,
) -> TormentaPersonagemCreate:
    entrada = obter_bestiario_mb_por_slug(slug)
    if not entrada:
        raise DadosInvalidos(f"Criatura não encontrada no bestiário: {slug!r}")
    return mapear_bestiario_para_create(
        entrada,
        tipo=tipo,
        campanha_id=campanha_id,
        nome_override=nome_override,
    )
