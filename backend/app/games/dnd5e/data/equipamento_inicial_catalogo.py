"""Pacotes de equipamento inicial por classe (PHB Cap. 5 — escolha padrão simplificada)."""

from __future__ import annotations

from typing import Any, Dict, List, TypedDict


class ItemPacote(TypedDict):
    slug: str
    quantidade: int


class PacoteEquipamentoClasse(TypedDict):
    nome_pacote: str
    armadura_slug: str
    escudo_slug: str
    arma_principal_slug: str
    itens: List[ItemPacote]
    armas_extras: List[ItemPacote]


# Um pacote padrão por classe usando slugs do catálogo local (`equipamento_catalogo.py`).
EQUIPAMENTO_INICIAL_POR_CLASSE: Dict[str, PacoteEquipamentoClasse] = {
    "barbaro": {
        "nome_pacote": "Equipamento de bárbaro",
        "armadura_slug": "peles",
        "escudo_slug": "",
        "arma_principal_slug": "espada-grande",
        "itens": [
            {"slug": "mochila", "quantidade": 1},
            {"slug": "corda", "quantidade": 1},
        ],
        "armas_extras": [{"slug": "adaga", "quantidade": 2}],
    },
    "bardo": {
        "nome_pacote": "Equipamento de bardo",
        "armadura_slug": "couro",
        "escudo_slug": "",
        "arma_principal_slug": "espada-longa",
        "itens": [
            {"slug": "mochila", "quantidade": 1},
            {"slug": "lanterna", "quantidade": 1},
        ],
        "armas_extras": [{"slug": "adaga", "quantidade": 1}],
    },
    "bruxo": {
        "nome_pacote": "Equipamento de bruxo",
        "armadura_slug": "couro",
        "escudo_slug": "",
        "arma_principal_slug": "adaga",
        "itens": [
            {"slug": "mochila", "quantidade": 1},
            {"slug": "corda", "quantidade": 1},
        ],
        "armas_extras": [{"slug": "adaga", "quantidade": 1}],
    },
    "clerigo": {
        "nome_pacote": "Equipamento de clérigo",
        "armadura_slug": "brunea",
        "escudo_slug": "escudo",
        "arma_principal_slug": "maca",
        "itens": [
            {"slug": "mochila", "quantidade": 1},
        ],
        "armas_extras": [{"slug": "adaga", "quantidade": 1}],
    },
    "druida": {
        "nome_pacote": "Equipamento de druida",
        "armadura_slug": "couro",
        "escudo_slug": "escudo",
        "arma_principal_slug": "cacete",
        "itens": [
            {"slug": "mochila", "quantidade": 1},
        ],
        "armas_extras": [{"slug": "adaga", "quantidade": 1}],
    },
    "feiticeiro": {
        "nome_pacote": "Equipamento de feiticeiro",
        "armadura_slug": "",
        "escudo_slug": "",
        "arma_principal_slug": "adaga",
        "itens": [
            {"slug": "mochila", "quantidade": 1},
            {"slug": "corda", "quantidade": 1},
        ],
        "armas_extras": [{"slug": "adaga", "quantidade": 1}],
    },
    "guerreiro": {
        "nome_pacote": "Equipamento de guerreiro",
        "armadura_slug": "cota-anéis",
        "escudo_slug": "escudo",
        "arma_principal_slug": "espada-longa",
        "itens": [
            {"slug": "mochila", "quantidade": 1},
        ],
        "armas_extras": [{"slug": "arco-longo", "quantidade": 1}],
    },
    "ladino": {
        "nome_pacote": "Equipamento de ladino",
        "armadura_slug": "couro-endurecido",
        "escudo_slug": "",
        "arma_principal_slug": "espada-longa",
        "itens": [
            {"slug": "mochila", "quantidade": 1},
            {"slug": "kit-ladrao", "quantidade": 1},
        ],
        "armas_extras": [
            {"slug": "arco-longo", "quantidade": 1},
            {"slug": "adaga", "quantidade": 1},
        ],
    },
    "mago": {
        "nome_pacote": "Equipamento de mago",
        "armadura_slug": "",
        "escudo_slug": "",
        "arma_principal_slug": "adaga",
        "itens": [
            {"slug": "mochila", "quantidade": 1},
            {"slug": "corda", "quantidade": 1},
            {"slug": "lanterna", "quantidade": 1},
        ],
        "armas_extras": [{"slug": "adaga", "quantidade": 1}],
    },
    "monge": {
        "nome_pacote": "Equipamento de monge",
        "armadura_slug": "",
        "escudo_slug": "",
        "arma_principal_slug": "cacete",
        "itens": [
            {"slug": "mochila", "quantidade": 1},
        ],
        "armas_extras": [{"slug": "adaga", "quantidade": 10}],
    },
    "paladino": {
        "nome_pacote": "Equipamento de paladino",
        "armadura_slug": "cota-anéis",
        "escudo_slug": "escudo",
        "arma_principal_slug": "espada-longa",
        "itens": [
            {"slug": "mochila", "quantidade": 1},
        ],
        "armas_extras": [{"slug": "adaga", "quantidade": 1}],
    },
    "patrulheiro": {
        "nome_pacote": "Equipamento de patrulheiro",
        "armadura_slug": "couro-endurecido",
        "escudo_slug": "",
        "arma_principal_slug": "espada-longa",
        "itens": [
            {"slug": "mochila", "quantidade": 1},
            {"slug": "corda", "quantidade": 1},
        ],
        "armas_extras": [
            {"slug": "arco-longo", "quantidade": 1},
            {"slug": "adaga", "quantidade": 1},
        ],
    },
}


def pacote_equipamento_classe(classe_slug: str) -> PacoteEquipamentoClasse | None:
    key = (classe_slug or "").strip().lower()
    row = EQUIPAMENTO_INICIAL_POR_CLASSE.get(key)
    return dict(row) if row else None
