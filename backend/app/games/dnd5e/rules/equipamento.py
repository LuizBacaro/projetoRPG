"""Equipamento D&D 5E — armas, armaduras, CA, encargo (Cap. 5)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional, Sequence

from app.games.dnd5e.data.equipamento_catalogo import (
    ARMADURAS,
    ARMAS_MARCIAIS,
    ARMAS_SIMPLES,
    ESCUDOS,
    ITENS_VARIADOS,
)

TipoDano = Literal["corte", "perfuracao", "impacto"]
TipoArmadura = Literal["roupa", "leve", "media", "pesada"]


@dataclass
class Arma:
    arma_id: str
    nome: str
    tipo: str = "corpo_a_corpo"
    dano: str = "1d6"
    tipo_dano: TipoDano = "corte"
    alcance: str = "toque"
    peso: float = 0.0
    custo: float = 0.0
    propriedades: List[str] = field(default_factory=list)
    requisitos: List[str] = field(default_factory=list)


@dataclass
class Armadura:
    armadura_id: str
    nome: str
    tipo_armadura: TipoArmadura = "leve"
    ca: int = 11
    peso: float = 0.0
    custo: float = 0.0
    requisitos_forca: int = 0
    penalidade_dex: str = "nenhuma"  # nenhuma | limitada
    desvantagem_furtividade: bool = False


@dataclass
class Escudo:
    escudo_id: str
    nome: str
    bonus_ac: int = 2
    peso: float = 6.0
    custo: float = 10.0


@dataclass
class Item:
    item_id: str
    nome: str
    categoria: str = "especial"
    peso: float = 0.0
    custo: float = 0.0
    quantidade: int = 1
    descricao: str = ""


def _row_para_armadura(row: Dict[str, Any]) -> Armadura:
    return Armadura(
        armadura_id=str(row["slug"]),
        nome=str(row.get("nome", "")),
        tipo_armadura=row.get("tipo_armadura", "leve"),
        ca=int(row.get("ca", 11)),
        peso=float(row.get("peso", 0)),
        custo=float(row.get("custo", 0)),
        requisitos_forca=int(row.get("requisitos_forca", 0)),
        penalidade_dex=str(row.get("penalidade_dex", "nenhuma")),
    )


def _row_para_arma(row: Dict[str, Any]) -> Arma:
    return Arma(
        arma_id=str(row["slug"]),
        nome=str(row.get("nome", "")),
        tipo=str(row.get("tipo", "corpo_a_corpo")),
        dano=str(row.get("dano", "1d6")),
        tipo_dano=row.get("tipo_dano", "corte"),
        alcance=str(row.get("alcance", "toque")),
        peso=float(row.get("peso", 0)),
        custo=float(row.get("custo", 0)),
        propriedades=list(row.get("propriedades") or []),
        requisitos=list(row.get("requisitos") or []),
    )


def _row_para_item(row: Dict[str, Any], quantidade: int = 1) -> Item:
    return Item(
        item_id=str(row["slug"]),
        nome=str(row.get("nome", "")),
        categoria=str(row.get("categoria", "especial")),
        peso=float(row.get("peso", 0)),
        custo=float(row.get("custo", 0)),
        quantidade=max(1, int(quantidade)),
        descricao=str(row.get("descricao", "")),
    )


def arma_por_slug(slug: Optional[str]) -> Optional[Arma]:
    if not slug:
        return None
    key = slug.strip().lower()
    for row in ARMAS_SIMPLES + ARMAS_MARCIAIS:
        if row.get("slug") == key:
            return _row_para_arma(row)
    return None


def item_por_slug(slug: Optional[str], quantidade: int = 1) -> Optional[Item]:
    if not slug:
        return None
    key = slug.strip().lower()
    for row in ITENS_VARIADOS:
        if row.get("slug") == key:
            return _row_para_item(row, quantidade)
    return None


def armadura_por_slug(slug: Optional[str]) -> Optional[Armadura]:
    if not slug:
        return None
    key = slug.strip().lower()
    for row in ARMADURAS:
        if row.get("slug") == key:
            return _row_para_armadura(row)
    return None


def escudo_por_slug(slug: Optional[str]) -> Optional[Escudo]:
    if not slug:
        return None
    key = slug.strip().lower()
    for row in ESCUDOS:
        if row.get("slug") == key:
            return Escudo(
                escudo_id=str(row["slug"]),
                nome=str(row.get("nome", "Escudo")),
                bonus_ac=int(row.get("bonus_ac", 2)),
                peso=float(row.get("peso", 6)),
                custo=float(row.get("custo", 10)),
            )
    return None


def calcular_ac_de_slugs(
    *,
    armadura_slug: Optional[str],
    escudo_slug: Optional[str],
    dex_mod: int,
) -> int:
    return calcular_ac_total(
        armadura_por_slug(armadura_slug),
        escudo_por_slug(escudo_slug),
        dex_mod,
    )


def calcular_ac_total(
    armadura: Optional[Armadura],
    escudo: Optional[Escudo],
    dex_mod: int,
) -> int:
    """CA base da armadura + DEX (conforme tipo) + escudo."""
    if armadura is None:
        base = 10 + dex_mod
    else:
        base = armadura.ca
        if armadura.tipo_armadura == "leve":
            base += dex_mod
        elif armadura.tipo_armadura == "media":
            base += min(dex_mod, 2)
        # pesada: sem bônus DEX
    if escudo is not None:
        base += escudo.bonus_ac
    return base


def calcular_dano_arma(arma: Arma, mod_atributo: int) -> str:
    """Representação textual do dano (NdM + mod) para exibição."""
    sinal = f"+{mod_atributo}" if mod_atributo >= 0 else str(mod_atributo)
    return f"{arma.dano}{sinal}"


def calcular_peso_total(itens: Sequence[Arma | Armadura | Escudo | Item]) -> float:
    total = 0.0
    for it in itens:
        if isinstance(it, Item):
            total += it.peso * max(1, it.quantidade)
        else:
            total += float(it.peso)
    return total


def capacidade_carga_libras(forca: int) -> float:
    """Peso máximo transportado sem encargo = FOR × 15 lb (PHB)."""
    return max(0, forca) * 15.0


def calcular_penalidade_encargo(
    peso_total: float,
    forca: int,
) -> int:
    """
    Redução de velocidade por encargo (simplificado PHB).
    Retorna penalidade em metros (0, 3 ou 6).
    """
    cap = capacidade_carga_libras(forca)
    if cap <= 0:
        return 6
    if peso_total <= cap:
        return 0
    if peso_total <= cap * 2:
        return 3
    return 6


def validar_peso_maximo(peso_total: float, forca: int) -> bool:
    """True se ainda pode se mover (peso <= 2× capacidade)."""
    cap = capacidade_carga_libras(forca)
    return peso_total <= cap * 2


def montar_resumo_equipamento(
    *,
    armadura_slug: Optional[str] = None,
    escudo_slug: Optional[str] = None,
    arma_principal_slug: Optional[str] = None,
    armas_slugs: Optional[Sequence[str]] = None,
    itens: Optional[Sequence[Dict[str, Any]]] = None,
    forca: int = 10,
    dex_mod: int = 0,
    ouro_po: float = 0,
) -> Dict[str, Any]:
    """Resumo de CA, peso, encargo e inventário para ficha/API."""
    armadura = armadura_por_slug(armadura_slug)
    escudo = escudo_por_slug(escudo_slug)
    ca_total = calcular_ac_total(armadura, escudo, dex_mod)

    peso_itens: List[float] = []
    if armadura:
        peso_itens.append(armadura.peso)
    if escudo:
        peso_itens.append(escudo.peso)

    arma_principal = arma_por_slug(arma_principal_slug)
    if arma_principal:
        peso_itens.append(arma_principal.peso)

    armas_resumo: List[Dict[str, Any]] = []
    vistos: set[str] = set()
    for slug in armas_slugs or []:
        key = str(slug or "").strip().lower()
        if not key or key in vistos:
            continue
        vistos.add(key)
        arma = arma_por_slug(key)
        if not arma:
            continue
        peso_itens.append(arma.peso)
        armas_resumo.append(
            {
                "slug": arma.arma_id,
                "nome": arma.nome,
                "dano": arma.dano,
                "peso": arma.peso,
            }
        )

    itens_resumo: List[Dict[str, Any]] = []
    objetos: List[Item] = []
    for row in itens or []:
        slug = str((row or {}).get("slug") or "").strip().lower()
        if not slug:
            continue
        qtd = max(1, int((row or {}).get("quantidade") or 1))
        item = item_por_slug(slug, qtd)
        if not item:
            continue
        objetos.append(item)
        itens_resumo.append(
            {
                "slug": item.item_id,
                "nome": item.nome,
                "quantidade": item.quantidade,
                "peso": item.peso * item.quantidade,
            }
        )

    peso_total = calcular_peso_total(objetos) + sum(peso_itens)
    cap = capacidade_carga_libras(forca)
    penalidade = calcular_penalidade_encargo(peso_total, forca)

    return {
        "ca_total": ca_total,
        "armadura_slug": armadura_slug,
        "escudo_slug": escudo_slug,
        "arma_principal_slug": arma_principal_slug,
        "arma_principal": (
            {
                "slug": arma_principal.arma_id,
                "nome": arma_principal.nome,
                "dano": arma_principal.dano,
            }
            if arma_principal
            else None
        ),
        "armas": armas_resumo,
        "itens": itens_resumo,
        "ouro_po": float(ouro_po or 0),
        "peso_total_lb": round(peso_total, 2),
        "capacidade_lb": cap,
        "penalidade_velocidade_m": penalidade,
        "sobrecarregado": not validar_peso_maximo(peso_total, forca),
    }
