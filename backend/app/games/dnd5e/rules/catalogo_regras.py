"""Agregação de catálogos estáticos expostos pela API de regras 5E."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.games.dnd5e.data.equipamento_catalogo import (
    ARMAS_MARCIAIS,
    ARMAS_SIMPLES,
    ARMADURAS,
    ESCUDOS,
)
from app.games.dnd5e.data.magias_catalogo import MAGIAS_CATALOGO
from app.games.dnd5e.data.spell_slots_full_caster import (
    CLASSE_HABILIDADE_PRIMARIA,
    FULL_CASTER_SLOTS,
)
from app.games.dnd5e.rules.antecedentes import listar_antecedentes
from app.games.dnd5e.rules.combate import CONDICOES_NOMES, CONDICOES_PADRAO
from app.games.dnd5e.rules.talentos import listar_feats_por_categoria, niveis_com_ganho_feat


def metadados_combate() -> Dict[str, Any]:
    condicoes = [
        {"slug": c, "nome": CONDICOES_NOMES.get(c, c.replace("_", " ").title())}
        for c in sorted(CONDICOES_PADRAO)
    ]
    return {
        "formula_iniciativa": "1d20 + modificador de Destreza",
        "formula_ataque": "1d20 + mod. atributo + bônus de proficiência (se proficiente)",
        "formula_dano": "dados da arma + mod. atributo",
        "critico_em": 20,
        "rodada_segundos": 6,
        "condicoes": condicoes,
        "tipos_dano": ["corte", "perfuracao", "impacto", "fogo", "frio", "raio", "acido", "trovao", "necrotico", "radiante", "psiquico", "forca"],
        "acoes_turno": ["acao", "movimento", "reacao", "acao_bonus"],
        "salvamentos_morte": {
            "sucessos_para_estabilizar": 3,
            "falhas_para_morte": 3,
            "cd": 10,
        },
    }


def listar_magias_catalogo(
    *,
    nivel: Optional[int] = None,
    escola: Optional[str] = None,
    q: Optional[str] = None,
) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    q_norm = (q or "").strip().lower()
    escola_norm = (escola or "").strip().lower()
    for row in MAGIAS_CATALOGO:
        if nivel is not None and row.get("nivel") != nivel:
            continue
        if escola_norm and (row.get("escola") or "").lower() != escola_norm:
            continue
        if q_norm:
            nome = str(row.get("nome", "")).lower()
            slug = str(row.get("slug", "")).lower()
            if q_norm not in nome and q_norm not in slug:
                continue
        out.append(dict(row))
    return out


def payload_conjuracao_mb() -> Dict[str, Any]:
    """Metadados de conjuração (slots full caster + habilidade primária por classe)."""
    return {
        "habilidade_primaria_por_classe": dict(CLASSE_HABILIDADE_PRIMARIA),
        "espacos_conjurador_completo_por_nivel": {
            str(n): slots for n, slots in FULL_CASTER_SLOTS.items()
        },
        "formula_cd": "8 + bônus de proficiência + mod. habilidade primária",
        "formula_bonus_ataque_magia": "bônus de proficiência + mod. habilidade primária",
    }


def listar_equipamento_catalogo() -> Dict[str, Any]:
    return {
        "armas_simples": list(ARMAS_SIMPLES),
        "armas_marciais": list(ARMAS_MARCIAIS),
        "armaduras": list(ARMADURAS),
        "escudos": list(ESCUDOS),
    }


def listar_talentos_catalogo(
    *,
    tipo_bonus: Optional[str] = None,
    q: Optional[str] = None,
) -> List[Dict[str, Any]]:
    feats = listar_feats_por_categoria(tipo_bonus)
    q_norm = (q or "").strip().lower()
    rows: List[Dict[str, Any]] = []
    for f in feats:
        if q_norm:
            if q_norm not in f.nome.lower() and q_norm not in f.slug.lower():
                continue
        rows.append(
            {
                "slug": f.slug,
                "nome": f.nome,
                "tipo_bonus": f.tipo_bonus,
                "requisito_nivel": f.requisito_nivel,
                "requisitos": f.prerequisitos,
                "bonus_especial": f.bonus_especial,
            }
        )
    return rows


def listar_antecedentes_catalogo() -> List[Dict[str, Any]]:
    return [
        {
            "slug": a.antecedente_id,
            "nome": a.nome,
            "pericias": a.pericias,
            "idiomas_qtd": a.idiomas_qtd,
            "equipamento": a.equipamento,
            "ouro_extra": a.ouro_extra,
        }
        for a in listar_antecedentes()
    ]


def niveis_feat_ganho() -> List[int]:
    return list(niveis_com_ganho_feat())
