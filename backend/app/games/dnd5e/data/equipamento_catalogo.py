"""Tabelas resumidas de armas, armaduras e escudos (PHB Cap. 5)."""

from __future__ import annotations

from typing import Any, Dict, List

ArmaDict = Dict[str, Any]
ArmaduraDict = Dict[str, Any]

ARMAS_SIMPLES: List[ArmaDict] = [
    {
        "slug": "cacete",
        "nome": "Cacete",
        "tipo": "corpo_a_corpo",
        "dano": "1d4",
        "peso": 1,
        "custo": 1,
    },
    {
        "slug": "adaga",
        "nome": "Adaga",
        "tipo": "corpo_a_corpo",
        "dano": "1d4",
        "peso": 1,
        "custo": 2,
        "propriedades": ["leve", "finesse"],
    },
    {
        "slug": "lanca",
        "nome": "Lanca",
        "tipo": "corpo_a_corpo",
        "dano": "1d6",
        "peso": 3,
        "custo": 1,
        "propriedades": ["versatil"],
    },
    {
        "slug": "maca",
        "nome": "Maca",
        "tipo": "corpo_a_corpo",
        "dano": "1d6",
        "peso": 2,
        "custo": 1,
    },
]

ARMAS_MARCIAIS: List[ArmaDict] = [
    {
        "slug": "espada-longa",
        "nome": "Espada Longa",
        "tipo": "corpo_a_corpo",
        "dano": "1d8",
        "peso": 3,
        "custo": 15,
        "propriedades": ["versatil"],
    },
    {
        "slug": "espada-grande",
        "nome": "Espada Grande",
        "tipo": "corpo_a_corpo",
        "dano": "1d6",
        "peso": 6,
        "custo": 30,
        "propriedades": ["pesada", "duas_maos"],
    },
    {
        "slug": "arco-longo",
        "nome": "Arco Longo",
        "tipo": "distancia",
        "dano": "1d8",
        "peso": 2,
        "custo": 50,
        "alcance": "45/180m",
    },
]

ARMADURAS: List[ArmaduraDict] = [
    {
        "slug": "acolchoada",
        "nome": "Acolchoada",
        "tipo_armadura": "leve",
        "ca": 11,
        "penalidade_dex": "nenhuma",
        "peso": 8,
        "custo": 5,
    },
    {
        "slug": "couro",
        "nome": "Couro",
        "tipo_armadura": "leve",
        "ca": 11,
        "penalidade_dex": "nenhuma",
        "peso": 10,
        "custo": 10,
    },
    {
        "slug": "couro-batido",
        "nome": "Couro Batido",
        "tipo_armadura": "leve",
        "ca": 12,
        "penalidade_dex": "nenhuma",
        "peso": 13,
        "custo": 45,
    },
    {
        "slug": "peles",
        "nome": "Peles",
        "tipo_armadura": "media",
        "ca": 12,
        "penalidade_dex": "limitada",
        "peso": 12,
        "custo": 10,
    },
    {
        "slug": "camisote-malha",
        "nome": "Camisote de Malha",
        "tipo_armadura": "media",
        "ca": 13,
        "penalidade_dex": "limitada",
        "peso": 20,
        "custo": 50,
    },
    {
        "slug": "cota-malha",
        "nome": "Cota de Malha",
        "tipo_armadura": "media",
        "ca": 14,
        "penalidade_dex": "limitada",
        "peso": 25,
        "custo": 75,
    },
    {
        "slug": "brunea",
        "nome": "Brunea",
        "tipo_armadura": "media",
        "ca": 14,
        "penalidade_dex": "limitada",
        "peso": 20,
        "custo": 50,
    },
    {
        "slug": "meia-placa",
        "nome": "Meia-placa",
        "tipo_armadura": "media",
        "ca": 15,
        "penalidade_dex": "limitada",
        "peso": 40,
        "custo": 750,
    },
    {
        "slug": "cota-anéis",
        "nome": "Cota de Aneis",
        "tipo_armadura": "pesada",
        "ca": 14,
        "penalidade_dex": "nenhuma",
        "peso": 40,
        "custo": 30,
        "requisitos_forca": 0,
    },
    {
        "slug": "cota-malha-pesada",
        "nome": "Cota de Malha Pesada",
        "tipo_armadura": "pesada",
        "ca": 16,
        "penalidade_dex": "nenhuma",
        "peso": 55,
        "custo": 75,
        "requisitos_forca": 13,
    },
    {
        "slug": "placas",
        "nome": "Placas",
        "tipo_armadura": "pesada",
        "ca": 18,
        "penalidade_dex": "nenhuma",
        "peso": 65,
        "custo": 1500,
        "requisitos_forca": 15,
    },
]

ESCUDOS: List[Dict[str, Any]] = [
    {"slug": "escudo", "nome": "Escudo", "bonus_ac": 2, "peso": 6, "custo": 10},
]
