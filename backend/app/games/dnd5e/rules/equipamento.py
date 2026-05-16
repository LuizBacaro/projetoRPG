"""Equipamento D&D 5E — armas, armaduras, CA, encargo (Cap. 5)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Literal, Optional, Sequence

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
