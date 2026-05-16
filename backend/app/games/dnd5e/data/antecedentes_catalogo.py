"""13 antecedentes PHB (resumo mecânico)."""

from __future__ import annotations

from typing import Any, Dict, List

BackgroundDict = Dict[str, Any]

ANTECEDENTES_CATALOGO: List[BackgroundDict] = [
    {
        "slug": "acolito",
        "nome": "Acolito",
        "pericias": ["Insight", "Religion"],
        "idiomas_qtd": 1,
        "equipamento": ["simbolo_sagrado", "livro_preces", "roupa_religiosa"],
        "ouro_extra": 15,
    },
    {
        "slug": "artesao-guilda",
        "nome": "Artesao de Guilda",
        "pericias": ["Insight", "Persuasion"],
        "idiomas_qtd": 1,
        "equipamento": ["ferramentas_profissionais", "carta_guilda"],
        "ouro_extra": 15,
    },
    {
        "slug": "criminoso",
        "nome": "Criminoso",
        "pericias": ["Deception", "Stealth"],
        "idiomas_qtd": 1,
        "equipamento": ["roupa_escura", "kit_disfarce"],
        "ouro_extra": 15,
    },
    {
        "slug": "forasteiro",
        "nome": "Forasteiro",
        "pericias": ["Athletics", "Survival"],
        "idiomas_qtd": 1,
        "equipamento": ["cajado", "armadilhas", "pele"],
        "ouro_extra": 10,
    },
    {
        "slug": "heroi-popular",
        "nome": "Heroi Popular",
        "pericias": ["Animal Handling", "Survival"],
        "idiomas_qtd": 0,
        "equipamento": ["ferramentas_artesao", "pa"],
        "ouro_extra": 10,
    },
    {
        "slug": "soldado",
        "nome": "Soldado",
        "pericias": ["Athletics", "Intimidation"],
        "idiomas_qtd": 1,
        "equipamento": ["insignia", "trofeu", "kit_jogos"],
        "ouro_extra": 10,
    },
    {
        "slug": "charlatao",
        "nome": "Charlatao",
        "pericias": ["Deception", "Sleight of Hand"],
        "idiomas_qtd": 0,
        "equipamento": ["roupa_fina", "kit_disfarce"],
        "ouro_extra": 15,
    },
    {
        "slug": "artista",
        "nome": "Artista",
        "pericias": ["Acrobatics", "Performance"],
        "idiomas_qtd": 0,
        "equipamento": ["instrumento", "admirecao"],
        "ouro_extra": 15,
    },
    {
        "slug": "eremita",
        "nome": "Eremita",
        "pericias": ["Medicine", "Religion"],
        "idiomas_qtd": 1,
        "equipamento": ["porta_pergaminho", "kit_herbalismo"],
        "ouro_extra": 5,
    },
    {
        "slug": "nobre",
        "nome": "Nobre",
        "pericias": ["History", "Persuasion"],
        "idiomas_qtd": 1,
        "equipamento": ["roupa_fina", "anel_sinete"],
        "ouro_extra": 25,
    },
    {
        "slug": "sabio",
        "nome": "Sabio",
        "pericias": ["Arcana", "History"],
        "idiomas_qtd": 2,
        "equipamento": ["vidro_tinta", "facas", "livro"],
        "ouro_extra": 10,
    },
    {
        "slug": "marinheiro",
        "nome": "Marinheiro",
        "pericias": ["Athletics", "Perception"],
        "idiomas_qtd": 0,
        "equipamento": ["roupa_comum", "adaga", "corda"],
        "ouro_extra": 10,
    },
    {
        "slug": "orphan",
        "nome": "Orfao das Ruas",
        "pericias": ["Sleight of Hand", "Stealth"],
        "idiomas_qtd": 0,
        "equipamento": ["faca", "mapa_cidade", "rato"],
        "ouro_extra": 10,
    },
]
