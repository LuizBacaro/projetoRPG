"""
Catálogo de espécies de familiar (PHB) — Mago e Feiticeiro.
"""

from __future__ import annotations

from typing import Any, Dict, List

_ESPECIES: List[Dict[str, Any]] = [
    {
        "slug": "cobra",
        "nome": "Cobra (víbora pequena)",
        "categoria": "reptil",
        "bonus_mestre": "+3 em testes de Blefar",
        "deslocamento": "6 m",
        "atributos_base": {
            "forca": 4,
            "destreza": 15,
            "constituicao": 11,
            "inteligencia": 2,
            "sabedoria": 12,
            "carisma": 2,
        },
        "armadura_natural_base": 0,
    },
    {
        "slug": "gato",
        "nome": "Gato",
        "categoria": "terrestre",
        "bonus_mestre": "+3 em testes de Furtividade",
        "deslocamento": "9 m",
        "atributos_base": {
            "forca": 3,
            "destreza": 15,
            "constituicao": 10,
            "inteligencia": 2,
            "sabedoria": 12,
            "carisma": 7,
        },
        "armadura_natural_base": 0,
    },
    {
        "slug": "lagarto",
        "nome": "Lagarto",
        "categoria": "reptil",
        "bonus_mestre": "+3 em testes de Escalar",
        "deslocamento": "9 m",
        "atributos_base": {
            "forca": 2,
            "destreza": 11,
            "constituicao": 10,
            "inteligencia": 2,
            "sabedoria": 12,
            "carisma": 5,
        },
        "armadura_natural_base": 0,
    },
    {
        "slug": "rato",
        "nome": "Rato",
        "categoria": "terrestre",
        "bonus_mestre": "+3 em testes de resistência de Fortitude",
        "deslocamento": "12 m",
        "atributos_base": {
            "forca": 2,
            "destreza": 15,
            "constituicao": 10,
            "inteligencia": 2,
            "sabedoria": 12,
            "carisma": 2,
        },
        "armadura_natural_base": 0,
    },
    {
        "slug": "texugo",
        "nome": "Texugo",
        "categoria": "terrestre",
        "bonus_mestre": "+3 em testes de resistência de Reflexos",
        "deslocamento": "9 m",
        "atributos_base": {
            "forca": 8,
            "destreza": 17,
            "constituicao": 15,
            "inteligencia": 2,
            "sabedoria": 12,
            "carisma": 6,
        },
        "armadura_natural_base": 0,
    },
    {
        "slug": "coruja",
        "nome": "Coruja",
        "categoria": "aereo",
        "bonus_mestre": "+3 em testes de Observar na penumbra",
        "deslocamento": "3 m, voo 18 m",
        "atributos_base": {
            "forca": 4,
            "destreza": 15,
            "constituicao": 10,
            "inteligencia": 2,
            "sabedoria": 14,
            "carisma": 4,
        },
        "armadura_natural_base": 0,
    },
    {
        "slug": "corvo",
        "nome": "Corvo",
        "categoria": "aereo",
        "bonus_mestre": "+3 em testes de Avaliação (fala um idioma)",
        "deslocamento": "3 m, voo 12 m",
        "atributos_base": {
            "forca": 2,
            "destreza": 15,
            "constituicao": 10,
            "inteligencia": 2,
            "sabedoria": 14,
            "carisma": 6,
        },
        "armadura_natural_base": 0,
    },
    {
        "slug": "falcao",
        "nome": "Falcão",
        "categoria": "aereo",
        "bonus_mestre": "+3 em testes de Observar em locais iluminados",
        "deslocamento": "3 m, voo 18 m",
        "atributos_base": {
            "forca": 6,
            "destreza": 15,
            "constituicao": 10,
            "inteligencia": 2,
            "sabedoria": 14,
            "carisma": 6,
        },
        "armadura_natural_base": 0,
    },
    {
        "slug": "morcego",
        "nome": "Morcego",
        "categoria": "aereo",
        "bonus_mestre": "+3 em testes de Ouvir",
        "deslocamento": "3 m, voo 18 m",
        "atributos_base": {
            "forca": 1,
            "destreza": 15,
            "constituicao": 10,
            "inteligencia": 2,
            "sabedoria": 12,
            "carisma": 6,
        },
        "armadura_natural_base": 0,
    },
    {
        "slug": "sapo",
        "nome": "Sapo",
        "categoria": "anfibio",
        "bonus_mestre": "+3 pontos de vida",
        "deslocamento": "6 m",
        "atributos_base": {
            "forca": 1,
            "destreza": 12,
            "constituicao": 11,
            "inteligencia": 2,
            "sabedoria": 14,
            "carisma": 4,
        },
        "armadura_natural_base": 0,
        "hp_extra_mestre": 3,
    },
]

_POR_SLUG = {e["slug"]: e for e in _ESPECIES}


def listar_especies() -> List[Dict[str, Any]]:
    return list(_ESPECIES)


def especie_por_slug(slug: str) -> Dict[str, Any] | None:
    return _POR_SLUG.get(str(slug or "").strip())
