"""Variantes raciais PHB — linhagem dracônica (draconato) e herança infernal (tiefling)."""

from __future__ import annotations

from typing import Any, Dict, List

VarianteDict = Dict[str, Any]

# Oito linhagens dracônicas (PHB)
DRACONATO_VARIANTES: List[VarianteDict] = [
    {"slug": "black", "nome": "Negro", "tipo_dano": "acido", "tipo_dano_pt": "Ácido"},
    {
        "slug": "blue",
        "nome": "Azul",
        "tipo_dano": "eletricidade",
        "tipo_dano_pt": "Eletricidade",
    },
    {"slug": "brass", "nome": "Latão", "tipo_dano": "fogo", "tipo_dano_pt": "Fogo"},
    {
        "slug": "bronze",
        "nome": "Bronze",
        "tipo_dano": "eletricidade",
        "tipo_dano_pt": "Eletricidade",
    },
    {"slug": "copper", "nome": "Cobre", "tipo_dano": "acido", "tipo_dano_pt": "Ácido"},
    {"slug": "gold", "nome": "Ouro", "tipo_dano": "fogo", "tipo_dano_pt": "Fogo"},
    {"slug": "green", "nome": "Verde", "tipo_dano": "veneno", "tipo_dano_pt": "Veneno"},
    {"slug": "red", "nome": "Vermelho", "tipo_dano": "fogo", "tipo_dano_pt": "Fogo"},
]

# Quatro heranças infernais (resumo PHB / variantes clássicas)
TIEFLING_VARIANTES: List[VarianteDict] = [
    {
        "slug": "asmodeus",
        "nome": "Asmodeus",
        "tipo_dano": "fogo",
        "tipo_dano_pt": "Fogo",
    },
    {
        "slug": "levistus",
        "nome": "Levistus",
        "tipo_dano": "frio",
        "tipo_dano_pt": "Frio",
    },
    {
        "slug": "glasya",
        "nome": "Glasya",
        "tipo_dano": "veneno",
        "tipo_dano_pt": "Veneno",
    },
    {"slug": "zariel", "nome": "Zariel", "tipo_dano": "fogo", "tipo_dano_pt": "Fogo"},
]

RACA_VARIANTES: Dict[str, List[VarianteDict]] = {
    "draconato": DRACONATO_VARIANTES,
    "tiefling": TIEFLING_VARIANTES,
}
