"""Doze classes PHB + tabela de experiência (níveis 1–20)."""

from __future__ import annotations

from typing import Any, Dict, List

ClasseDict = Dict[str, Any]
XpDict = Dict[str, int]

CLASSES_CATALOGO: List[ClasseDict] = [
    {
        "slug": "barbaro",
        "nome": "Bárbaro",
        "dado_vida": "d12",
        "habilidade_primaria": "Força",
        "habilidade_primaria_chave": "strength",
    },
    {
        "slug": "bardo",
        "nome": "Bardo",
        "dado_vida": "d8",
        "habilidade_primaria": "Carisma",
        "habilidade_primaria_chave": "charisma",
    },
    {
        "slug": "bruxo",
        "nome": "Bruxo",
        "dado_vida": "d8",
        "habilidade_primaria": "Carisma",
        "habilidade_primaria_chave": "charisma",
    },
    {
        "slug": "clerigo",
        "nome": "Clérigo",
        "dado_vida": "d8",
        "habilidade_primaria": "Sabedoria",
        "habilidade_primaria_chave": "wisdom",
    },
    {
        "slug": "druida",
        "nome": "Druida",
        "dado_vida": "d8",
        "habilidade_primaria": "Sabedoria",
        "habilidade_primaria_chave": "wisdom",
    },
    {
        "slug": "feiticeiro",
        "nome": "Feiticeiro",
        "dado_vida": "d6",
        "habilidade_primaria": "Carisma",
        "habilidade_primaria_chave": "charisma",
    },
    {
        "slug": "guerreiro",
        "nome": "Guerreiro",
        "dado_vida": "d10",
        "habilidade_primaria": "Força",
        "habilidade_primaria_chave": "strength",
    },
    {
        "slug": "ladino",
        "nome": "Ladino",
        "dado_vida": "d8",
        "habilidade_primaria": "Destreza",
        "habilidade_primaria_chave": "dexterity",
    },
    {
        "slug": "mago",
        "nome": "Mago",
        "dado_vida": "d6",
        "habilidade_primaria": "Inteligência",
        "habilidade_primaria_chave": "intelligence",
    },
    {
        "slug": "monge",
        "nome": "Monge",
        "dado_vida": "d8",
        "habilidade_primaria": "Destreza",
        "habilidade_primaria_chave": "dexterity",
    },
    {
        "slug": "paladino",
        "nome": "Paladino",
        "dado_vida": "d10",
        "habilidade_primaria": "Força",
        "habilidade_primaria_chave": "strength",
    },
    {
        "slug": "patrulheiro",
        "nome": "Patrulheiro",
        "dado_vida": "d10",
        "habilidade_primaria": "Destreza",
        "habilidade_primaria_chave": "dexterity",
    },
]

TABELA_XP_POR_NIVEL: List[XpDict] = [
    {"nivel": 1, "xp_total": 0},
    {"nivel": 2, "xp_total": 300},
    {"nivel": 3, "xp_total": 900},
    {"nivel": 4, "xp_total": 2700},
    {"nivel": 5, "xp_total": 6500},
    {"nivel": 6, "xp_total": 14000},
    {"nivel": 7, "xp_total": 23000},
    {"nivel": 8, "xp_total": 34000},
    {"nivel": 9, "xp_total": 48000},
    {"nivel": 10, "xp_total": 64000},
    {"nivel": 11, "xp_total": 85000},
    {"nivel": 12, "xp_total": 110000},
    {"nivel": 13, "xp_total": 140000},
    {"nivel": 14, "xp_total": 170000},
    {"nivel": 15, "xp_total": 205000},
    {"nivel": 16, "xp_total": 250000},
    {"nivel": 17, "xp_total": 300000},
    {"nivel": 18, "xp_total": 355000},
    {"nivel": 19, "xp_total": 420000},
    {"nivel": 20, "xp_total": 500000},
]

NIVEIS_GANHO_FEAT = [4, 8, 12, 16, 19]
