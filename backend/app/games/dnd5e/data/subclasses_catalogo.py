"""Subclasses PHB (resumo) — escolha típica no nível 3."""

from __future__ import annotations

from typing import Any, Dict, List

SubclasseDict = Dict[str, Any]

SUBCLASSES_CATALOGO: List[SubclasseDict] = [
    {
        "slug": "berserker",
        "nome": "Caminho do Berserker",
        "classe_slug": "barbaro",
        "nivel_escolha": 3,
    },
    {
        "slug": "totem",
        "nome": "Caminho do Guerreiro Totêmico",
        "classe_slug": "barbaro",
        "nivel_escolha": 3,
    },
    {
        "slug": "collegio-conhecimento",
        "nome": "Colégio do Conhecimento",
        "classe_slug": "bardo",
        "nivel_escolha": 3,
    },
    {
        "slug": "collegio-valor",
        "nome": "Colégio da Bravura",
        "classe_slug": "bardo",
        "nivel_escolha": 3,
    },
    {
        "slug": "arcano",
        "nome": "Patrono Arquifada",
        "classe_slug": "bruxo",
        "nivel_escolha": 1,
    },
    {
        "slug": "demônio",
        "nome": "Patrono Infernal",
        "classe_slug": "bruxo",
        "nivel_escolha": 1,
    },
    {
        "slug": "vida",
        "nome": "Domínio da Vida",
        "classe_slug": "clerigo",
        "nivel_escolha": 1,
    },
    {
        "slug": "guerra",
        "nome": "Domínio da Guerra",
        "classe_slug": "clerigo",
        "nivel_escolha": 1,
    },
    {
        "slug": "terra",
        "nome": "Círculo da Terra",
        "classe_slug": "druida",
        "nivel_escolha": 2,
    },
    {
        "slug": "lua",
        "nome": "Círculo da Lua",
        "classe_slug": "druida",
        "nivel_escolha": 2,
    },
    {
        "slug": "draconica",
        "nome": "Ascendência Dracônica",
        "classe_slug": "feiticeiro",
        "nivel_escolha": 1,
    },
    {
        "slug": "selvagem",
        "nome": "Magia Selvagem",
        "classe_slug": "feiticeiro",
        "nivel_escolha": 1,
    },
    {
        "slug": "campeao",
        "nome": "Campeão",
        "classe_slug": "guerreiro",
        "nivel_escolha": 3,
    },
    {
        "slug": "mestre-batalha",
        "nome": "Mestre de Batalha",
        "classe_slug": "guerreiro",
        "nivel_escolha": 3,
    },
    {"slug": "ladrao", "nome": "Ladino", "classe_slug": "ladino", "nivel_escolha": 3},
    {
        "slug": "assassino",
        "nome": "Assassino",
        "classe_slug": "ladino",
        "nivel_escolha": 3,
    },
    {
        "slug": "evocacao",
        "nome": "Escola de Evocação",
        "classe_slug": "mago",
        "nivel_escolha": 2,
    },
    {
        "slug": "abjuracao",
        "nome": "Escola de Abjuração",
        "classe_slug": "mago",
        "nivel_escolha": 2,
    },
    {
        "slug": "maos-abertas",
        "nome": "Caminho das Mãos Abertas",
        "classe_slug": "monge",
        "nivel_escolha": 3,
    },
    {
        "slug": "sombra",
        "nome": "Caminho das Sombras",
        "classe_slug": "monge",
        "nivel_escolha": 3,
    },
    {
        "slug": "devocao",
        "nome": "Juramento de Devoção",
        "classe_slug": "paladino",
        "nivel_escolha": 3,
    },
    {
        "slug": "vinganca",
        "nome": "Juramento de Vingança",
        "classe_slug": "paladino",
        "nivel_escolha": 3,
    },
    {
        "slug": "cacador",
        "nome": "Caçador",
        "classe_slug": "patrulheiro",
        "nivel_escolha": 3,
    },
    {
        "slug": "mestre-bestas",
        "nome": "Mestre das Bestas",
        "classe_slug": "patrulheiro",
        "nivel_escolha": 3,
    },
]
