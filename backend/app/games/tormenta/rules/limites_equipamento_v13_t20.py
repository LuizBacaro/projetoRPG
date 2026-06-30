"""Limites de equipamento vestido/empunhado — Tormenta 20 v1.3 (RF-T07h-1, p.141)."""

from __future__ import annotations

import unicodedata
from typing import Any, Dict, List, Optional

MAX_VESTIDOS_MECANICOS = 4
MAX_EMPUNHADOS = 2

_COSMETICOS_NORM = frozenset(
    {
        "roupas de viajante",
        "roupas de plebeu",
        "traje de plebeu",
        "traje de sacerdote",
        "traje da corte",
        "traje estrangeiro",
        "uniforme militar",
    }
)


def _norm_nome(texto: Any) -> str:
    s = unicodedata.normalize("NFKD", str(texto or "").strip().lower())
    return "".join(c for c in s if not unicodedata.combining(c))


def normalizar_tipo_item(tipo: Any) -> str:
    t = str(tipo or "").strip().lower()
    if t in ("média", "media"):
        return "media"
    if t in ("leve", "pesada", "escudo", "arma"):
        return t
    return ""


def slot_equipamento_v13(item: Any) -> str:
    """
    Classifica slot de uso: vestido (armadura), empunhado (escudo/arma) ou outro.
    """
    if not isinstance(item, dict):
        return "outro"
    if item.get("empunhado") is True or item.get("slot") == "empunhado":
        return "empunhado"
    if item.get("slot") == "vestido":
        return "vestido"
    if item.get("cosmetico") is True:
        return "cosmetico"
    tipo = normalizar_tipo_item(item.get("tipo"))
    if tipo in ("leve", "media", "pesada"):
        return "vestido"
    if tipo == "escudo":
        return "empunhado"
    if tipo == "arma":
        return "empunhado"
    return "outro"


def ataque_empunhado_mecanico(ataque: Any) -> bool:
    """Arma na lista de ataques marcada como empunhada (conta no limite p.141)."""
    if not isinstance(ataque, dict):
        return False
    if ataque.get("empunhado") is not True:
        return False
    nome = str(ataque.get("nome") or "").strip()
    if not nome:
        return False
    dano = str(ataque.get("dano") or "").strip()
    bonus = str(ataque.get("bonus_ataque") or ataque.get("teste") or "").strip()
    return bool(dano or bonus)


def aplicar_limites_ficha(
    armaduras: Optional[List[Any]],
    ataques: Optional[List[Any]] = None,
) -> Dict[str, Any]:
    """
    Aplica limites vestido/empunhado na ficha completa.
    Empunhados: escudos (armaduras_protecao) + armas com `empunhado: true` (ataques).
    """
    out_arm: List[Dict[str, Any]] = []
    out_atq: List[Dict[str, Any]] = []
    vestidos = 0
    empunhados = 0

    for raw in armaduras or []:
        it = dict(raw) if isinstance(raw, dict) else {}
        if not item_beneficio_mecanico(it):
            it.setdefault("bonus_ativo", True)
            out_arm.append(it)
            continue
        slot = slot_equipamento_v13(it)
        if slot == "vestido":
            vestidos += 1
            it["bonus_ativo"] = vestidos <= MAX_VESTIDOS_MECANICOS
        elif slot == "empunhado":
            empunhados += 1
            it["bonus_ativo"] = empunhados <= MAX_EMPUNHADOS
        else:
            it.setdefault("bonus_ativo", True)
        out_arm.append(it)

    for raw in ataques or []:
        atk = dict(raw) if isinstance(raw, dict) else {}
        if ataque_empunhado_mecanico(atk):
            empunhados += 1
            atk["bonus_ativo"] = empunhados <= MAX_EMPUNHADOS
        else:
            atk.pop("bonus_ativo", None)
        out_atq.append(atk)

    return {"armaduras": out_arm, "ataques": out_atq}


def resumo_limites_ficha(
    armaduras: Optional[List[Any]],
    ataques: Optional[List[Any]] = None,
) -> Dict[str, Any]:
    """Contagem unificada escudos + armas empunhadas."""
    aplicado = aplicar_limites_ficha(armaduras, ataques)
    marcados_arm = aplicado["armaduras"]
    marcados_atq = aplicado["ataques"]
    vestidos = sum(
        1
        for it in marcados_arm
        if slot_equipamento_v13(it) == "vestido" and item_beneficio_mecanico(it)
    )
    empunhados = sum(
        1
        for it in marcados_arm
        if slot_equipamento_v13(it) == "empunhado" and item_beneficio_mecanico(it)
    ) + sum(1 for atk in marcados_atq if ataque_empunhado_mecanico(atk))
    avisos: List[str] = []
    if vestidos > MAX_VESTIDOS_MECANICOS:
        avisos.append(
            f"Máximo {MAX_VESTIDOS_MECANICOS} itens vestidos com benefício — "
            f"{vestidos - MAX_VESTIDOS_MECANICOS} excedente(s) não aplicam bônus."
        )
    if empunhados > MAX_EMPUNHADOS:
        avisos.append(
            f"Máximo {MAX_EMPUNHADOS} itens empunhados — "
            f"{empunhados - MAX_EMPUNHADOS} excedente(s) não aplicam bônus."
        )
    return {
        "vestidos": vestidos,
        "empunhados": empunhados,
        "max_vestidos": MAX_VESTIDOS_MECANICOS,
        "max_empunhados": MAX_EMPUNHADOS,
        "armaduras": marcados_arm,
        "ataques": marcados_atq,
        "avisos": avisos,
        "excedeu_vestidos": vestidos > MAX_VESTIDOS_MECANICOS,
        "excedeu_empunhados": empunhados > MAX_EMPUNHADOS,
    }


def item_cosmetico(item: Any) -> bool:
    if not isinstance(item, dict):
        return False
    if item.get("cosmetico") is True:
        return True
    if item.get("beneficio_mecanico") is False:
        return True
    nome = _norm_nome(item.get("nome"))
    if nome in _COSMETICOS_NORM:
        return True
    slot = slot_equipamento_v13(item)
    if slot == "outro":
        try:
            bonus = int(item.get("bonus_ca", 0) or 0)
            pen = int(item.get("penalidade", 0) or 0)
        except (TypeError, ValueError):
            bonus, pen = 0, 0
        return bonus == 0 and pen == 0
    return False


def item_beneficio_mecanico(item: Any) -> bool:
    if not isinstance(item, dict) or item_cosmetico(item):
        return False
    slot = slot_equipamento_v13(item)
    if slot not in ("vestido", "empunhado"):
        return False
    try:
        bonus = int(item.get("bonus_ca", 0) or 0)
        pen = int(item.get("penalidade", 0) or 0)
    except (TypeError, ValueError):
        bonus, pen = 0, 0
    if bonus != 0 or pen != 0:
        return True
    if slot == "empunhado" and (
        item.get("dano") or item.get("bonus_ataque") is not None
    ):
        return True
    return slot in ("vestido", "empunhado")


def aplicar_limites_equipamento(
    itens: Optional[List[Any]],
) -> List[Dict[str, Any]]:
    """
    Marca `bonus_ativo` em cada item conforme limites p.141.
    Vestidos com benefício: máx. 4 ativos; empunhados: máx. 2 ativos.
    """
    out: List[Dict[str, Any]] = []
    vestidos = 0
    empunhados = 0
    for raw in itens or []:
        it = dict(raw) if isinstance(raw, dict) else {}
        if not item_beneficio_mecanico(it):
            it.setdefault("bonus_ativo", True)
            out.append(it)
            continue
        slot = slot_equipamento_v13(it)
        if slot == "vestido":
            vestidos += 1
            it["bonus_ativo"] = vestidos <= MAX_VESTIDOS_MECANICOS
        elif slot == "empunhado":
            empunhados += 1
            it["bonus_ativo"] = empunhados <= MAX_EMPUNHADOS
        else:
            it.setdefault("bonus_ativo", True)
        out.append(it)
    return out


def resumo_limites_equipamento(itens: Optional[List[Any]]) -> Dict[str, Any]:
    """Contagem e avisos para UI/API."""
    marcados = aplicar_limites_equipamento(itens)
    vestidos = sum(
        1
        for it in marcados
        if slot_equipamento_v13(it) == "vestido" and item_beneficio_mecanico(it)
    )
    empunhados = sum(
        1
        for it in marcados
        if slot_equipamento_v13(it) == "empunhado" and item_beneficio_mecanico(it)
    )
    inativos = [it for it in marcados if it.get("bonus_ativo") is False]
    avisos: List[str] = []
    if vestidos > MAX_VESTIDOS_MECANICOS:
        avisos.append(
            f"Máximo {MAX_VESTIDOS_MECANICOS} itens vestidos com benefício — "
            f"{vestidos - MAX_VESTIDOS_MECANICOS} excedente(s) não aplicam bônus."
        )
    if empunhados > MAX_EMPUNHADOS:
        avisos.append(
            f"Máximo {MAX_EMPUNHADOS} itens empunhados — "
            f"{empunhados - MAX_EMPUNHADOS} excedente(s) não aplicam bônus."
        )
    return {
        "vestidos": vestidos,
        "empunhados": empunhados,
        "max_vestidos": MAX_VESTIDOS_MECANICOS,
        "max_empunhados": MAX_EMPUNHADOS,
        "itens": marcados,
        "avisos": avisos,
        "excedeu_vestidos": vestidos > MAX_VESTIDOS_MECANICOS,
        "excedeu_empunhados": empunhados > MAX_EMPUNHADOS,
    }


def soma_bonus_ca_ativos(itens: Optional[List[Any]]) -> int:
    """Soma bônus de CA apenas de itens com `bonus_ativo` ≠ False."""
    marcados = aplicar_limites_equipamento(itens)
    total = 0
    for it in marcados:
        if it.get("bonus_ativo") is False:
            continue
        try:
            total += int(it.get("bonus_ca", 0) or 0)
        except (TypeError, ValueError):
            pass
    return total


def soma_bonus_ca_ficha(
    armaduras: Optional[List[Any]],
    ataques: Optional[List[Any]] = None,
) -> int:
    """CA ativa considerando limites na ficha completa (só armaduras/escudos)."""
    aplicado = aplicar_limites_ficha(armaduras, ataques)
    return soma_bonus_ca_ativos(aplicado["armaduras"])


def validar_adicionar_equipamento(
    itens_atuais: Optional[List[Any]],
    novo_item: Any,
    *,
    ataques: Optional[List[Any]] = None,
) -> Dict[str, Any]:
    """Preview ao equipar um item — retorna avisos sem mutar a lista."""
    lista = list(itens_atuais or [])
    lista.append(novo_item if isinstance(novo_item, dict) else {})
    res = resumo_limites_ficha(lista, ataques)
    novo_slot = slot_equipamento_v13(novo_item)
    novo_mec = item_beneficio_mecanico(novo_item)
    permitir = True
    if novo_mec and novo_slot == "empunhado" and res["empunhados"] > MAX_EMPUNHADOS:
        permitir = True
    if novo_mec and novo_slot == "vestido" and res["vestidos"] > MAX_VESTIDOS_MECANICOS:
        permitir = True
    return {
        "permitir": permitir,
        "slot": novo_slot,
        "resumo": res,
        "aviso": res["avisos"][-1] if res["avisos"] else "",
    }
