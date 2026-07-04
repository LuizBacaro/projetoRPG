"""Traços raciais mecânicos Tormenta 20 — MB e v1.3."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.games.tormenta.rules.duende_t20 import calcular_tracos_duende
from app.games.tormenta.rules.escolhas_raciais_t20 import aplicar_escolhas_ao_preview
from app.games.tormenta.rules.regra_versao_t20 import (
    REGRA_VERSAO_MB,
    REGRA_VERSAO_V13,
    normalizar_regra_versao,
)

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_TRACOS_MB_JSON = _DATA_DIR / "tracos_mecanicos_mb.json"
_TRACOS_V13_JSON = _DATA_DIR / "tracos_mecanicos_v13.json"
_TRACOS_HEROIS_ARTON_JSON = _DATA_DIR / "tracos_mecanicos_herois_arton.json"

# Legado MB → v1.3 quando ficha antiga usa slug MB no motor v13.
_SLUG_ALIASES_V13: Dict[str, str] = {
    "halfling": "hynne",
}

_TAMANHO_UI: Dict[str, str] = {
    "minusculo": "Min",
    "pequeno": "P",
    "medio": "M",
    "grande": "G",
    "enorme": "En",
    "colossal": "Col",
}

_TAMANHO_LABEL: Dict[str, str] = {
    "minusculo": "Minúsculo",
    "pequeno": "Pequeno",
    "medio": "Médio",
    "grande": "Grande",
    "enorme": "Enorme",
    "colossal": "Colossal",
}


def _enriquecer_tamanho_desloc(
    preview: Dict[str, Any],
    row: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    out = dict(preview)
    if not row:
        out["tamanho_ui"] = None
        out["tamanho_label"] = None
        out["deslocamento_natacao_m"] = None
        out["deslocamento_voo_m"] = None
        out["deslocamento_pairar_m"] = None
        out["desloc_nao_reduz_armadura_carga"] = False
        return out
    tam = str(row.get("tamanho") or "medio").strip().lower()
    out["tamanho_ui"] = _TAMANHO_UI.get(tam, "M")
    out["tamanho_label"] = _TAMANHO_LABEL.get(tam, "Médio")
    for key in (
        "deslocamento_natacao_m",
        "deslocamento_voo_m",
        "deslocamento_pairar_m",
    ):
        val = row.get(key)
        out[key] = int(val) if val is not None else None
    out["desloc_nao_reduz_armadura_carga"] = bool(
        row.get("desloc_nao_reduz_armadura_carga")
    )
    return out


def _resolver_slug(slug: str, regra_versao: str) -> str:
    s = str(slug or "").strip().lower()
    if normalizar_regra_versao(regra_versao) == REGRA_VERSAO_V13:
        return _SLUG_ALIASES_V13.get(s, s)
    return s


@lru_cache(maxsize=2)
def _carregar_tracos(regra_versao: str = REGRA_VERSAO_MB) -> Dict[str, Any]:
    path = (
        _TRACOS_V13_JSON
        if normalizar_regra_versao(regra_versao) == REGRA_VERSAO_V13
        else _TRACOS_MB_JSON
    )
    if not path.is_file():
        return {"racas": {}}
    return json.loads(path.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def _carregar_tracos_herois_arton() -> Dict[str, Any]:
    """Traços mecânicos das raças do suplemento Heróis de Arton v1.1."""
    if not _TRACOS_HEROIS_ARTON_JSON.is_file():
        return {"racas": {}}
    return json.loads(_TRACOS_HEROIS_ARTON_JSON.read_text(encoding="utf-8"))


def tracos_mecanicos_por_slug(
    slug: str,
    regra_versao: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Efeitos mecânicos da raça ou None se slug desconhecido.

    Procura primeiro nos traços core (MB/v1.3) e depois no suplemento Heróis de Arton.
    """
    rv = normalizar_regra_versao(regra_versao)
    s = _resolver_slug(slug, rv)
    if not s:
        return None
    racas = _carregar_tracos(rv).get("racas") or {}
    if not isinstance(racas, dict):
        return None
    row = racas.get(s)
    if isinstance(row, dict):
        return dict(row)
    # fallback: verificar raças do suplemento Heróis de Arton
    racas_ha = _carregar_tracos_herois_arton().get("racas") or {}
    row_ha = racas_ha.get(s) if isinstance(racas_ha, dict) else None
    if isinstance(row_ha, dict):
        return dict(row_ha)
    return None


def humano_versatil_pericias_extra(humano_versatil: Optional[str]) -> int:
    """Humano v1.3 Versátil: 2 perícias (padrão) ou 1 perícia + 1 poder geral."""
    v = str(humano_versatil or "").strip().lower()
    if v == "pericia_poder":
        return 1
    return 2


def tamanho_racial_de_ficha(ficha_json: Optional[Dict[str, Any]]) -> str:
    """Tamanho de combate derivado da raça (e config Duende quando aplicável)."""
    from app.games.tormenta.rules.regra_versao_t20 import regra_versao_de_ficha

    fj = ficha_json if isinstance(ficha_json, dict) else {}
    slug = str(fj.get("raca_tormenta_slug") or fj.get("raca") or "").strip().lower()
    if not slug or slug == "__livre__":
        return "medio"
    rv = regra_versao_de_ficha(fj)
    duende_cfg = fj.get("duende") if slug == "duende" else None
    prev = preview_tracos_raciais(
        slug,
        regra_versao=rv,
        duende_config=duende_cfg if isinstance(duende_cfg, dict) else None,
    )
    return str(prev.get("tamanho") or "medio").strip().lower()


def _escolhas_resumo_ha(slug: str, row: Dict[str, Any]) -> List[str]:
    """Linhas de resumo para traços raciais Heróis de Arton."""
    s = str(slug or "").strip().lower()
    linhas: List[str] = []
    if row.get("magia_instintiva"):
        linhas.append("Magia Instintiva (Sab no lugar de atributo-chave arcano)")
    if row.get("sentidos_misticos"):
        linhas.append("Sentidos Místicos (Visão Mística básica permanente)")
    if row.get("cancao_melancolia"):
        linhas.append(
            "Canção da Melancolia (pior de 2d20 em Vontade vs efeitos mentais)"
        )
    if row.get("forca_dos_titas"):
        linhas.append(
            "Força dos Titãs (dado extra no dano máximo, 1 PM, limite = mod. Força)"
        )
    if row.get("armas_aumentadas"):
        linhas.append("Armas aumentadas (tamanho Grande)")
    mb = int(row.get("manobra_bonus", 0) or 0)
    if mb:
        sinal = "+" if mb > 0 else ""
        linhas.append(f"Manobras {sinal}{mb} (tamanho {row.get('tamanho', 'grande')})")
    if row.get("instrumentista_magico"):
        linhas.append("Instrumentista Mágico (conjuração via instrumento em mãos)")
    if row.get("ambicao_herdada"):
        linhas.append("Ambição Herdada (1 poder geral ou único de origem na criação)")
    if row.get("considerado_elfo"):
        linhas.append("Considerado elfo para pré-requisitos")
    if row.get("pm_bonus_por_nivel_impar"):
        linhas.append("+1 PM a cada nível ímpar")
    if int(row.get("pm_aprimoramento_conjuracao", 0) or 0):
        linhas.append(
            f"+{int(row['pm_aprimoramento_conjuracao'])} PM para aprimoramentos ao lançar magia"
        )
    if row.get("visao_penumbra"):
        linhas.append("Visão na penumbra")
    return linhas


def pericias_treinadas_extra_de_tracos(
    slug: str,
    regra_versao: Optional[str] = None,
    *,
    humano_versatil: Optional[str] = None,
) -> int:
    rv = normalizar_regra_versao(regra_versao)
    s = _resolver_slug(slug, rv)
    if rv == REGRA_VERSAO_V13 and s == "humano":
        return humano_versatil_pericias_extra(humano_versatil)
    row = tracos_mecanicos_por_slug(slug, rv)
    if not row:
        return 0
    return int(row.get("pericias_treinadas_extra", 0) or 0)


def preview_tracos_raciais(
    slug: str,
    *,
    pericias_nomes: Optional[List[str]] = None,
    regra_versao: Optional[str] = None,
    humano_versatil: Optional[str] = None,
    lefou_deformidade_modo: Optional[str] = None,
    lefou_deformidade_pericias: Optional[List[str]] = None,
    qareen_ascendencia: Optional[str] = None,
    osteon_memoria_modo: Optional[str] = None,
    osteon_memoria_pericia: Optional[str] = None,
    sereia_magias: Optional[List[str]] = None,
    golem_fonte_elemental: Optional[str] = None,
    kliren_pericia: Optional[str] = None,
    kliren_oficio: Optional[str] = None,
    silfide_magias: Optional[List[str]] = None,
    duende_config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Resumo de bônus raciais aplicáveis para a ficha.
    `pericias_nomes` opcional: lista de nomes de perícias para mapear bônus por nome.
    """
    rv = normalizar_regra_versao(regra_versao)
    s = _resolver_slug(slug, rv)
    row = tracos_mecanicos_por_slug(slug, rv)
    if not row:
        return {
            "slug": s or slug,
            "encontrado": False,
            "regra_versao": rv,
            "tamanho": None,
            "deslocamento_m": None,
            "ca_bonus": 0,
            "ca_vs_grande_ou_maior": 0,
            "ataque_bonus": 0,
            "furtividade_bonus": 0,
            "fortitude_bonus": 0,
            "reflexos_bonus": 0,
            "vontade_bonus": 0,
            "pericias_bonus": {},
            "pericias_treinadas_extra": 0,
            "reducao_dano": {},
            "imunidades_dano": {},
            "magias_inatas": [],
            "escolhas_resumo": [],
            "pericias_treinadas_escolha": [],
            "tamanho_ui": None,
            "tamanho_label": None,
            "deslocamento_natacao_m": None,
            "deslocamento_voo_m": None,
            "deslocamento_pairar_m": None,
            "desloc_nao_reduz_armadura_carga": False,
        }

    per_map = row.get("pericias_bonus") or {}
    if not isinstance(per_map, dict):
        per_map = {}

    out_per: Dict[str, int] = {}
    if pericias_nomes:
        for nome in pericias_nomes:
            n = str(nome or "").strip()
            if n and n in per_map:
                out_per[n] = int(per_map[n])
    else:
        out_per = {str(k): int(v) for k, v in per_map.items()}

    extra = pericias_treinadas_extra_de_tracos(
        slug, rv, humano_versatil=humano_versatil
    )

    base = {
        "slug": s,
        "encontrado": True,
        "regra_versao": rv,
        "tamanho": row.get("tamanho"),
        "deslocamento_m": row.get("deslocamento_m"),
        "ca_bonus": int(row.get("ca_bonus", 0) or 0),
        "ca_vs_grande_ou_maior": int(row.get("ca_vs_grande_ou_maior", 0) or 0),
        "ataque_bonus": int(row.get("ataque_bonus", 0) or 0),
        "furtividade_bonus": int(row.get("furtividade_bonus", 0) or 0),
        "fortitude_bonus": int(row.get("fortitude_bonus", 0) or 0),
        "reflexos_bonus": int(row.get("reflexos_bonus", 0) or 0),
        "vontade_bonus": int(row.get("vontade_bonus", 0) or 0),
        "pericias_bonus": out_per,
        "pericias_treinadas_extra": extra,
        "reducao_dano": {},
        "imunidades_dano": {},
        "magias_inatas": [],
        "escolhas_resumo": [],
        "pericias_treinadas_escolha": [],
    }
    if s == "duende" and isinstance(duende_config, dict) and duende_config:
        dt = calcular_tracos_duende(duende_config)
        base["tamanho"] = dt.get("tamanho")
        base["deslocamento_m"] = dt.get("deslocamento_m")
        base["furtividade_bonus"] = int(dt.get("furtividade_bonus", 0) or 0)
        base["ca_bonus"] = int(dt.get("ca_bonus", 0) or 0)
        base["ataque_bonus"] = int(dt.get("ataque_bonus", 0) or 0)
        base["manobra_bonus"] = int(dt.get("manobra_bonus", 0) or 0)
        pb = dt.get("pericias_bonus") or {}
        if isinstance(pb, dict):
            base["pericias_bonus"] = {str(k): int(v) for k, v in pb.items()}
        rd = dt.get("reducao_dano") or {}
        if isinstance(rd, dict) and rd:
            base["reducao_dano"] = {str(k): int(v) for k, v in rd.items()}
        mag = dt.get("magias_inatas") or []
        if isinstance(mag, list) and mag:
            base["magias_inatas"] = [str(m) for m in mag]
        resumo = list(dt.get("escolhas_resumo") or [])
        lim = list(dt.get("limitacoes_resumo") or [])
        base["escolhas_resumo"] = resumo + [f"Limitação: {x}" for x in lim if x]
        row_tam = {
            "tamanho": dt.get("tamanho"),
            "deslocamento_m": dt.get("deslocamento_m"),
            "deslocamento_pairar_m": dt.get("deslocamento_pairar_m"),
            "deslocamento_voo_m": dt.get("deslocamento_voo_m"),
        }
    else:
        row_tam = row
    base["manobra_bonus"] = int(row.get("manobra_bonus", 0) or 0)
    base["armas_aumentadas"] = bool(row.get("armas_aumentadas"))
    ha_resumo = _escolhas_resumo_ha(s, row)
    if ha_resumo and not base.get("escolhas_resumo"):
        base["escolhas_resumo"] = ha_resumo
    base = _enriquecer_tamanho_desloc(base, row_tam)
    return aplicar_escolhas_ao_preview(
        base,
        slug,
        regra_versao=rv,
        lefou_deformidade_modo=lefou_deformidade_modo,
        lefou_deformidade_pericias=lefou_deformidade_pericias,
        qareen_ascendencia=qareen_ascendencia,
        golem_fonte_elemental=golem_fonte_elemental,
        kliren_pericia=kliren_pericia,
        kliren_oficio=kliren_oficio,
        osteon_memoria_modo=osteon_memoria_modo,
        osteon_memoria_pericia=osteon_memoria_pericia,
        sereia_magias=sereia_magias,
        silfide_magias=silfide_magias,
    )
