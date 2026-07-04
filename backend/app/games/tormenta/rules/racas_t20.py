"""Raças Tormenta 20 (Módulo Básico) — lista e ajustes de habilidades para a ficha."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from app.games.tormenta.rules.escolhas_raciais_t20 import (
    escolhas_por_raca,
    flag_escolha_por_tipo,
)
from app.games.tormenta.rules.regra_versao_t20 import (
    REGRA_VERSAO_MB,
    normalizar_regra_versao,
)

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_RACAS_JSON = _DATA_DIR / "racas_mb.json"
_RACAS_V13_JSON = _DATA_DIR / "racas_v13.json"
_RACAS_HEROIS_ARTON_JSON = _DATA_DIR / "racas_herois_arton.json"


@lru_cache(maxsize=2)
def _carregar_racas(regra_versao: str = "mb") -> Dict[str, Any]:
    from app.games.tormenta.rules.regra_versao_t20 import REGRA_VERSAO_V13

    path = (
        _RACAS_V13_JSON
        if normalizar_regra_versao(regra_versao) == REGRA_VERSAO_V13
        else _RACAS_JSON
    )
    raw = path.read_text(encoding="utf-8")
    return json.loads(raw)


@lru_cache(maxsize=1)
def _carregar_racas_mb() -> Dict[str, Any]:
    return _carregar_racas("mb")


@lru_cache(maxsize=1)
def _carregar_racas_herois_arton() -> Dict[str, Any]:
    """Carrega raças do suplemento Heróis de Arton v1.1."""
    if not _RACAS_HEROIS_ARTON_JSON.is_file():
        return {"racas": []}
    return json.loads(_RACAS_HEROIS_ARTON_JSON.read_text(encoding="utf-8"))


def idiomas_mb_extras() -> Tuple[str, List[Dict[str, str]]]:
    """Texto geral de idiomas (MB) + tabela Idioma / quem costuma falar."""
    data = _carregar_racas_mb()
    geral = str(data.get("idiomas_geral_mb", "") or "").strip()
    raw_tab = data.get("idiomas_tabela_mb") or []
    tabela: List[Dict[str, str]] = []
    if isinstance(raw_tab, list):
        for it in raw_tab:
            if not isinstance(it, dict):
                continue
            idioma = str(it.get("idioma", "")).strip()
            if not idioma:
                continue
            tabela.append(
                {
                    "idioma": idioma,
                    "falantes": str(it.get("falantes", "") or "").strip(),
                }
            )
    return geral, tabela


def lista_racas_mb() -> List[Dict[str, Any]]:
    return lista_racas(REGRA_VERSAO_MB)


def _processar_racas(
    rows: List[Any],
    *,
    regra_versao: Optional[str] = None,
    fonte_catalogo: str = "core",
) -> List[Dict[str, Any]]:
    """Converte lista raw de raças (JSON) no formato normalizado da API."""
    out: List[Dict[str, Any]] = []
    for row in rows:
        slug = str(row.get("slug", "")).strip()
        nome = str(row.get("nome", "")).strip()
        if not slug or not nome:
            continue
        ajustes = row.get("ajustes") or {}
        if not isinstance(ajustes, dict):
            ajustes = {}
        ajustes_limpo: Dict[str, int] = {}
        for k, v in ajustes.items():
            kk = str(k).lower().strip()
            if kk in ("for", "des", "con", "int", "sab", "car"):
                ajustes_limpo[kk] = int(v)
        ir = row.get("idioma_racial_mb", None)
        idioma_racial: str | None
        if ir is None:
            idioma_racial = None
        else:
            s = str(ir).strip()
            idioma_racial = s if s else None
        excl_raw = row.get("excluir_atributos_mais2") or []
        excluir: List[str] = []
        if isinstance(excl_raw, list):
            for x in excl_raw:
                xx = str(x).lower().strip()
                if xx in ("for", "des", "con", "int", "sab", "car"):
                    excluir.append(xx)
        esc_cfg = escolhas_por_raca(slug, regra_versao)
        esc_tipo = str((esc_cfg or {}).get("tipo") or "")
        esc_flag = flag_escolha_por_tipo(esc_tipo, slug)
        # campo fonte_catalogo: usa o do JSON se explícito, senão o padrão do caller
        fc = str(row.get("fonte_catalogo") or fonte_catalogo).strip()
        out.append(
            {
                "slug": slug,
                "nome": nome,
                "fonte_catalogo": fc,
                "ajustes": ajustes_limpo,
                "escolhe_duas_mais2": bool(row.get("escolhe_duas_mais2")),
                "escolhe_tres_mais1": bool(row.get("escolhe_tres_mais1")),
                "escolhe_um_mais2": bool(row.get("escolhe_um_mais2")),
                "escolhe_um_mais1": bool(row.get("escolhe_um_mais1")),
                "escolhe_dois_mais1": bool(row.get("escolhe_dois_mais1")),
                "escolhe_suraggel_subtipo": bool(row.get("escolhe_suraggel_subtipo")),
                "escolhe_lefou_deformidade": esc_flag == "escolhe_lefou_deformidade",
                "escolhe_qareen_ascendencia": esc_flag == "escolhe_qareen_ascendencia",
                "escolhe_osteon_memoria": esc_flag == "escolhe_osteon_memoria",
                "escolhe_sereia_magias": esc_flag == "escolhe_sereia_magias",
                "escolhe_golem_fonte": esc_flag == "escolhe_golem_fonte",
                "escolhe_kliren_hibrido": esc_flag == "escolhe_kliren_hibrido",
                "escolhe_silfide_magias": esc_flag == "escolhe_silfide_magias",
                "magias_inatas_v13": esc_flag == "magias_inatas_v13",
                "excluir_atributos_mais2": excluir,
                "excluir_atributos_mais1": [
                    str(x).lower().strip()
                    for x in (row.get("excluir_atributos_mais1") or [])
                    if str(x).lower().strip()
                    in ("for", "des", "con", "int", "sab", "car")
                ],
                "mod_car_fixo": int(row.get("mod_car_fixo", 0) or 0),
                "tracos_resumo": str(row.get("tracos_resumo", "")).strip(),
                "idioma_racial_mb": idioma_racial,
                "pericias_treinadas_extra": int(
                    row.get("pericias_treinadas_extra", 0) or 0
                ),
                "construcao_modular_duende": bool(row.get("construcao_modular_duende")),
            }
        )
    return out


def lista_racas(regra_versao: Optional[str] = None) -> List[Dict[str, Any]]:
    """Lista ordenada de raças para API/ficha conforme edição (mb ou v13).

    Retorna apenas raças core. Para incluir suplemento Heróis de Arton,
    use ``lista_racas_com_suplemento``.
    """
    data = _carregar_racas(normalizar_regra_versao(regra_versao))
    return _processar_racas(
        data.get("racas", []),
        regra_versao=regra_versao,
        fonte_catalogo="core",
    )


def lista_racas_herois_arton() -> List[Dict[str, Any]]:
    """Lista de raças do suplemento Heróis de Arton v1.1."""
    data = _carregar_racas_herois_arton()
    return _processar_racas(
        data.get("racas", []),
        fonte_catalogo="herois_arton",
    )


def lista_racas_com_suplemento(
    regra_versao: Optional[str] = None,
    suplemento: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Lista raças core + suplemento quando ``suplemento='herois_arton'``."""
    from app.games.tormenta.rules.regra_versao_t20 import SUPLEMENTO_HEROIS_ARTON

    racas = lista_racas(regra_versao)
    if suplemento and str(suplemento).strip().lower() == SUPLEMENTO_HEROIS_ARTON:
        racas = racas + lista_racas_herois_arton()
    return racas
