"""Nove raças jogáveis PHB (resumo mecânico para API/ficha)."""

from __future__ import annotations

from typing import Any, Dict, List

RacaDict = Dict[str, Any]

RACAS_CATALOGO: List[RacaDict] = [
    {
        "slug": "anao",
        "nome": "Anão",
        "tamanho": "Médio",
        "velocidade_metros": 7.5,
        "bonus_habilidades": {"constitution": 2},
        "bonus_hp_por_nivel": 1,
        "tracos_resumo": "Visão no escuro 18 m; +2 em salvamentos contra veneno; bônus +2 com machados; +1 PV/nível.",
        "caracteristicas": ["visao_escuro_18m", "resistencia_veneno", "bonus_machados"],
    },
    {
        "slug": "elfo",
        "nome": "Elfo",
        "tamanho": "Médio",
        "velocidade_metros": 9,
        "bonus_habilidades": {"dexterity": 2},
        "tracos_resumo": "Visão no escuro 18 m; imunidade a sono mágico; vantagem contra encantamento.",
        "caracteristicas": [
            "visao_escuro_18m",
            "imunidade_sono_magico",
            "vantagem_encantamento",
        ],
    },
    {
        "slug": "halfling",
        "nome": "Halfling",
        "tamanho": "Pequeno",
        "velocidade_metros": 6,
        "bonus_habilidades": {"dexterity": 2},
        "tracos_resumo": "Sorte (rerrolar 1d20/dia); agilidade (ignorar oportunidade ao sair); tamanho Pequeno.",
        "caracteristicas": ["sorte", "agilidade", "tamanho_pequeno"],
    },
    {
        "slug": "humano",
        "nome": "Humano",
        "tamanho": "Médio",
        "velocidade_metros": 9,
        "bonus_habilidades": {
            "strength": 1,
            "dexterity": 1,
            "constitution": 1,
            "intelligence": 1,
            "wisdom": 1,
            "charisma": 1,
        },
        "tracos_resumo": "Feat extra no nível 1; +1 proficiência em perícia à escolha.",
        "caracteristicas": ["feat_extra_nivel_1", "proficiencia_pericia_extra"],
    },
    {
        "slug": "draconato",
        "nome": "Draconato",
        "tamanho": "Médio",
        "velocidade_metros": 9,
        "bonus_habilidades": {"strength": 2, "charisma": 1},
        "tracos_resumo": "Ancestralidade dracônica; resistência 5 ao dano ancestral; sopro inalado (2d6).",
        "caracteristicas": [
            "ancestralidade_draconica",
            "resistencia_dano_ancestral",
            "sopro_inalado",
        ],
    },
    {
        "slug": "gnomo",
        "nome": "Gnomo",
        "tamanho": "Pequeno",
        "velocidade_metros": 7.5,
        "bonus_habilidades": {"intelligence": 2},
        "tracos_resumo": "Vantagem em salvamentos INT/WIS/CHA contra magia; vantagem em testes de mágica.",
        "caracteristicas": ["vantagem_salv_magia", "vantagem_testes_magia"],
    },
    {
        "slug": "meio_elfo",
        "nome": "Meio-Elfo",
        "tamanho": "Médio",
        "velocidade_metros": 9,
        "bonus_habilidades": {"charisma": 2},
        "escolhe_duas_mais1": True,
        "tracos_resumo": "Dois aumentos de habilidade extras (+1 cada); proficiência em perícia à escolha.",
        "caracteristicas": [
            "dois_bonus_habilidade_extra",
            "proficiencia_pericia_extra",
        ],
    },
    {
        "slug": "meio_orc",
        "nome": "Meio-Orc",
        "tamanho": "Médio",
        "velocidade_metros": 9,
        "bonus_habilidades": {"strength": 2, "constitution": 1, "intelligence": -2},
        "tracos_resumo": "Agressividade (ação bônus com HP ≤ metade); vantagem em Intimidação.",
        "caracteristicas": ["agressividade", "vantagem_intimidacao"],
    },
    {
        "slug": "tiefling",
        "nome": "Tiefling",
        "tamanho": "Médio",
        "velocidade_metros": 9,
        "bonus_habilidades": {"charisma": 2},
        "tracos_resumo": "Herança infernal; resistência 5 a fogo; visão no escuro 18 m.",
        "caracteristicas": ["heranca_infernal", "resistencia_fogo", "visao_escuro_18m"],
    },
]
