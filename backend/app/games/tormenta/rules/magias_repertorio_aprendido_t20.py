"""Orçamento de magias aprendidas no repertório — preparadores divinos MB (RF-T44d)."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from app.games.tormenta.rules.atributos_t20 import modificador_atributo_t20
from app.games.tormenta.rules.conjuracao_t20 import habilidade_chave_conjuracao
from app.games.tormenta.rules.grimorio_conjuracao_t20 import (
    modo_conjuracao_classe,
    slug_efetivo_tabelas_magia_mb,
)
from app.games.tormenta.rules.magias_progressao_mb_t20 import (
    circulo_maximo_magias_lancaveis_mb,
    tipo_lista_magias_por_classe_mb,
)

_DATA = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "magias_repertorio_aprendido_mb.json"
)


@lru_cache(maxsize=1)
def _carregar() -> Dict[str, Any]:
    if not _DATA.is_file():
        return {"classes": {}}
    return json.loads(_DATA.read_text(encoding="utf-8"))


def _classe_row(slug_classe: str) -> Optional[Dict[str, Any]]:
    s = str(slug_classe or "").strip().lower()
    if not s:
        return None
    classes = _carregar().get("classes") or {}
    row = classes.get(s)
    return row if isinstance(row, dict) else None


def classe_usa_limite_repertorio_mb(
    slug_classe: str,
    *,
    regra_versao: Optional[str] = None,
    arcanista_caminho: Optional[str] = None,
) -> bool:
    """Preparador divino com tabela de magias aprendidas (não mago)."""
    if (
        modo_conjuracao_classe(slug_classe, regra_versao, arcanista_caminho)
        != "preparar"
    ):
        return False
    eff = slug_efetivo_tabelas_magia_mb(slug_classe, regra_versao, arcanista_caminho)
    if eff == "mago":
        return False
    return _classe_row(eff) is not None


def _mod_habilidade_chave(
    slug_classe: str,
    *,
    for_valor: int = 10,
    des_valor: int = 10,
    con_valor: int = 10,
    int_valor: int = 10,
    sab_valor: int = 10,
    car_valor: int = 10,
) -> int:
    ch = habilidade_chave_conjuracao(slug_classe) or "sab"
    vals = {
        "for": for_valor,
        "des": des_valor,
        "con": con_valor,
        "int": int_valor,
        "sab": sab_valor,
        "car": car_valor,
    }
    return modificador_atributo_t20(int(vals.get(ch, 10)))


def orcamento_repertorio_mb(
    slug_classe: str,
    nivel: int,
    *,
    for_valor: int = 10,
    des_valor: int = 10,
    con_valor: int = 10,
    int_valor: int = 10,
    sab_valor: int = 10,
    car_valor: int = 10,
    regra_versao: Optional[str] = None,
    arcanista_caminho: Optional[str] = None,
) -> Optional[int]:
    """Máximo de magias de círculo ≥1 no repertório aprendido."""
    eff = slug_efetivo_tabelas_magia_mb(slug_classe, regra_versao, arcanista_caminho)
    row = _classe_row(eff)
    if not row:
        return None
    try:
        nv = max(1, min(40, int(nivel)))
    except (TypeError, ValueError):
        nv = 1
    inicial = row.get("inicial") or {}
    try:
        base_c1 = int(inicial.get("magias_circulo_1", 0) or 0)
    except (TypeError, ValueError):
        base_c1 = 0
    mod = _mod_habilidade_chave(
        slug_classe,
        for_valor=for_valor,
        des_valor=des_valor,
        con_valor=con_valor,
        int_valor=int_valor,
        sab_valor=sab_valor,
        car_valor=car_valor,
    )
    if inicial.get("bonus_mod_habilidade_circulo_1") is True:
        base_c1 += mod
    try:
        por_nv = int(row.get("magias_por_nivel_apos_1", 2) or 2)
    except (TypeError, ValueError):
        por_nv = 2
    extra = max(0, nv - 1) * max(0, por_nv)
    return max(0, base_c1 + extra)


def truques_contam_orcamento_repertorio_mb(
    slug_classe: str,
    *,
    regra_versao: Optional[str] = None,
    arcanista_caminho: Optional[str] = None,
) -> bool:
    eff = slug_efetivo_tabelas_magia_mb(slug_classe, regra_versao, arcanista_caminho)
    row = _classe_row(eff)
    if not row:
        return False
    return row.get("truques_contam_no_orcamento") is True


def contar_repertorio_no_orcamento(
    vinculos: List[Dict[str, Any]],
    *,
    slug_classe: str,
    metadados_por_slug: Optional[Dict[str, Dict[str, Any]]] = None,
    regra_versao: Optional[str] = None,
    arcanista_caminho: Optional[str] = None,
) -> int:
    meta_map = metadados_por_slug or {}
    truques_contam = truques_contam_orcamento_repertorio_mb(
        slug_classe,
        regra_versao=regra_versao,
        arcanista_caminho=arcanista_caminho,
    )
    total = 0
    for v in vinculos:
        if not isinstance(v, dict):
            continue
        if str(v.get("papel", "")).strip().lower() != "conhecida":
            continue
        circ = None
        if v.get("circulo") is not None:
            try:
                circ = int(v["circulo"])
            except (TypeError, ValueError):
                circ = None
        slug = str(v.get("magia_slug") or "").strip().lower()
        if circ is None and slug in meta_map:
            try:
                circ = int(meta_map[slug].get("circulo", 0) or 0)
            except (TypeError, ValueError):
                circ = 0
        if circ is None:
            circ = 0
        if circ == 0 and not truques_contam:
            continue
        total += 1
    return total


def validar_adicionar_repertorio_mb(
    *,
    slug_classe: str,
    nivel: int,
    circulo_magia: int,
    tipo_magia: Optional[str],
    vinculos_existentes: List[Dict[str, Any]],
    for_valor: int = 10,
    des_valor: int = 10,
    con_valor: int = 10,
    int_valor: int = 10,
    sab_valor: int = 10,
    car_valor: int = 10,
    metadados_por_slug: Optional[Dict[str, Dict[str, Any]]] = None,
    regra_versao: Optional[str] = None,
    arcanista_caminho: Optional[str] = None,
) -> Tuple[bool, str]:
    if not classe_usa_limite_repertorio_mb(
        slug_classe,
        regra_versao=regra_versao,
        arcanista_caminho=arcanista_caminho,
    ):
        return True, ""
    try:
        circ = int(circulo_magia)
    except (TypeError, ValueError):
        circ = 0
    cmax = circulo_maximo_magias_lancaveis_mb(
        slug_classe,
        nivel,
        regra_versao=regra_versao,
        arcanista_caminho=arcanista_caminho,
    )
    if circ > cmax:
        return (
            False,
            f"Magia de {circ}º círculo: esta classe no nível {nivel} só aprende até o {cmax}º círculo (MB).",
        )
    tipo_esperado = tipo_lista_magias_por_classe_mb(slug_classe)
    if tipo_esperado and tipo_magia:
        if str(tipo_magia).strip().lower() != tipo_esperado:
            return (
                False,
                f"Magia {tipo_magia} incompatível com a lista {tipo_esperado} da classe {slug_classe} (MB).",
            )
    if circ == 0 and not truques_contam_orcamento_repertorio_mb(
        slug_classe,
        regra_versao=regra_versao,
        arcanista_caminho=arcanista_caminho,
    ):
        return True, ""
    orc = orcamento_repertorio_mb(
        slug_classe,
        nivel,
        for_valor=for_valor,
        des_valor=des_valor,
        con_valor=con_valor,
        int_valor=int_valor,
        sab_valor=sab_valor,
        car_valor=car_valor,
        regra_versao=regra_versao,
        arcanista_caminho=arcanista_caminho,
    )
    if orc is None:
        return True, ""
    usado = contar_repertorio_no_orcamento(
        vinculos_existentes,
        slug_classe=slug_classe,
        metadados_por_slug=metadados_por_slug,
        regra_versao=regra_versao,
        arcanista_caminho=arcanista_caminho,
    )
    if usado >= orc:
        return (
            False,
            f"Limite de magias aprendidas no repertório: {usado}/{orc} (MB, {slug_classe}).",
        )
    return True, ""


def preview_repertorio_mb(
    *,
    slug_classe: str,
    nivel: int,
    vinculos: Optional[List[Dict[str, Any]]] = None,
    for_valor: int = 10,
    des_valor: int = 10,
    con_valor: int = 10,
    int_valor: int = 10,
    sab_valor: int = 10,
    car_valor: int = 10,
    regra_versao: Optional[str] = None,
    arcanista_caminho: Optional[str] = None,
) -> Dict[str, Any]:
    from app.games.tormenta.rules.catalogo_t20 import metadados_magia_mb_por_slug

    vinculos = vinculos or []
    usa = classe_usa_limite_repertorio_mb(
        slug_classe,
        regra_versao=regra_versao,
        arcanista_caminho=arcanista_caminho,
    )
    meta: Dict[str, Dict[str, Any]] = {}
    for v in vinculos:
        if not isinstance(v, dict):
            continue
        sl = str(v.get("magia_slug") or "").strip().lower()
        if sl and sl not in meta:
            m = metadados_magia_mb_por_slug(sl)
            if m:
                meta[sl] = m
    usado = contar_repertorio_no_orcamento(
        vinculos,
        slug_classe=slug_classe,
        metadados_por_slug=meta,
        regra_versao=regra_versao,
        arcanista_caminho=arcanista_caminho,
    )
    orc = (
        orcamento_repertorio_mb(
            slug_classe,
            nivel,
            for_valor=for_valor,
            des_valor=des_valor,
            con_valor=con_valor,
            int_valor=int_valor,
            sab_valor=sab_valor,
            car_valor=car_valor,
            regra_versao=regra_versao,
            arcanista_caminho=arcanista_caminho,
        )
        if usa
        else None
    )
    truques_rep = sum(
        1
        for v in vinculos
        if isinstance(v, dict)
        and str(v.get("papel", "")).strip().lower() == "conhecida"
        and int(
            (meta.get(str(v.get("magia_slug") or "").strip().lower()) or {}).get(
                "circulo", 0
            )
            or 0
        )
        == 0
    )
    return {
        "classe_slug": str(slug_classe).strip().lower(),
        "nivel": int(nivel),
        "usa_limite_repertorio": usa,
        "repertorio_usadas": usado,
        "repertorio_max": orc,
        "truques_no_repertorio": truques_rep,
        "truques_contam_orcamento": truques_contam_orcamento_repertorio_mb(
            slug_classe,
            regra_versao=regra_versao,
            arcanista_caminho=arcanista_caminho,
        ),
        "circulo_max_lancavel": circulo_maximo_magias_lancaveis_mb(
            slug_classe,
            nivel,
            regra_versao=regra_versao,
            arcanista_caminho=arcanista_caminho,
        ),
    }
