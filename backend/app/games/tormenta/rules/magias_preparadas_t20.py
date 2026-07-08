"""Teto e validação de magias preparadas — preparadores MB (mago, clérigo, druida…)."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from app.games.tormenta.rules.atributos_t20 import contribuicao_atributo_t20
from app.games.tormenta.rules.catalogo_t20 import metadados_magia_mb_por_slug
from app.games.tormenta.rules.grimorio_conjuracao_t20 import (
    modo_conjuracao_classe,
    slug_efetivo_tabelas_magia_mb,
)
from app.games.tormenta.rules.magias_progressao_mb_t20 import (
    circulo_maximo_magias_lancaveis_mb,
    tipo_lista_magias_por_classe_mb,
)
from app.games.tormenta.rules.regra_versao_t20 import (
    REGRA_VERSAO_V13,
    normalizar_regra_versao,
)

_DATA = Path(__file__).resolve().parent.parent / "data" / "magias_preparadas_mb.json"


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


def classe_usa_limite_preparadas_mb(
    slug_classe: str,
    *,
    regra_versao: Optional[str] = None,
    arcanista_caminho: Optional[str] = None,
) -> bool:
    if (
        modo_conjuracao_classe(slug_classe, regra_versao, arcanista_caminho)
        != "preparar"
    ):
        return False
    eff = slug_efetivo_tabelas_magia_mb(slug_classe, regra_versao, arcanista_caminho)
    return _classe_row(eff) is not None


def _mod_habilidade_preparadas(
    slug_classe: str,
    row: Dict[str, Any],
    *,
    for_valor: int = 10,
    des_valor: int = 10,
    con_valor: int = 10,
    int_valor: int = 10,
    sab_valor: int = 10,
    car_valor: int = 10,
    regra_versao: Optional[str] = None,
) -> int:
    ch = str(row.get("habilidade_chave") or "int").strip().lower()
    rv = normalizar_regra_versao(regra_versao)
    default = 0 if rv == REGRA_VERSAO_V13 else 10
    vals = {
        "for": for_valor,
        "des": des_valor,
        "con": con_valor,
        "int": int_valor,
        "sab": sab_valor,
        "car": car_valor,
    }
    return contribuicao_atributo_t20(int(vals.get(ch, default)), rv)


def teto_preparadas_mb(
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
    eff = slug_efetivo_tabelas_magia_mb(slug_classe, regra_versao, arcanista_caminho)
    row = _classe_row(eff)
    if not row:
        return None
    try:
        nv = max(1, min(40, int(nivel)))
    except (TypeError, ValueError):
        nv = 1
    formula = str(row.get("formula") or "").strip().lower()
    try:
        minimo = int(row.get("minimo", 1) or 1)
    except (TypeError, ValueError):
        minimo = 1
    if formula == "nivel_mais_mod_habilidade":
        mod = _mod_habilidade_preparadas(
            slug_classe,
            row,
            for_valor=for_valor,
            des_valor=des_valor,
            con_valor=con_valor,
            int_valor=int_valor,
            sab_valor=sab_valor,
            car_valor=car_valor,
            regra_versao=regra_versao,
        )
        return max(minimo, nv + mod)
    return None


def truques_contam_teto_preparadas_mb(
    slug_classe: str,
    *,
    regra_versao: Optional[str] = None,
    arcanista_caminho: Optional[str] = None,
) -> bool:
    eff = slug_efetivo_tabelas_magia_mb(slug_classe, regra_versao, arcanista_caminho)
    row = _classe_row(eff)
    if not row:
        return False
    return row.get("truques_contam_no_teto") is True


def exige_grimorio_para_preparar_mb(
    slug_classe: str,
    *,
    regra_versao: Optional[str] = None,
    arcanista_caminho: Optional[str] = None,
) -> bool:
    eff = slug_efetivo_tabelas_magia_mb(slug_classe, regra_versao, arcanista_caminho)
    row = _classe_row(eff)
    if not row:
        return False
    return row.get("exige_grimorio") is not False


def exige_repertorio_para_preparar_mb(
    slug_classe: str,
    *,
    regra_versao: Optional[str] = None,
    arcanista_caminho: Optional[str] = None,
) -> bool:
    """Preparadores divinos precisam ter a magia no repertório (papel conhecida)."""
    if exige_grimorio_para_preparar_mb(
        slug_classe,
        regra_versao=regra_versao,
        arcanista_caminho=arcanista_caminho,
    ):
        return False
    from app.games.tormenta.rules.magias_repertorio_aprendido_t20 import (
        classe_usa_limite_repertorio_mb,
    )

    return classe_usa_limite_repertorio_mb(
        slug_classe,
        regra_versao=regra_versao,
        arcanista_caminho=arcanista_caminho,
    )


def _slugs_grimorio(vinculos: List[Dict[str, Any]]) -> set[str]:
    out: set[str] = set()
    for v in vinculos:
        if not isinstance(v, dict):
            continue
        if str(v.get("papel", "")).strip().lower() != "grimorio":
            continue
        sl = str(v.get("magia_slug") or "").strip().lower()
        if sl:
            out.add(sl)
    return out


def _slugs_conhecidas(vinculos: List[Dict[str, Any]]) -> set[str]:
    out: set[str] = set()
    for v in vinculos:
        if not isinstance(v, dict):
            continue
        if str(v.get("papel", "")).strip().lower() != "conhecida":
            continue
        sl = str(v.get("magia_slug") or "").strip().lower()
        if sl:
            out.add(sl)
    return out


def contar_preparadas_no_teto(
    vinculos: List[Dict[str, Any]],
    *,
    slug_classe: str,
    metadados_por_slug: Optional[Dict[str, Dict[str, Any]]] = None,
    regra_versao: Optional[str] = None,
    arcanista_caminho: Optional[str] = None,
) -> int:
    meta_map = metadados_por_slug or {}
    truques_contam = truques_contam_teto_preparadas_mb(
        slug_classe,
        regra_versao=regra_versao,
        arcanista_caminho=arcanista_caminho,
    )
    total = 0
    for v in vinculos:
        if not isinstance(v, dict):
            continue
        if str(v.get("papel", "")).strip().lower() != "preparada":
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


def validar_adicionar_preparada_mb(
    *,
    slug_classe: str,
    nivel: int,
    magia_slug: str,
    circulo_magia: int,
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
    if not classe_usa_limite_preparadas_mb(
        slug_classe,
        regra_versao=regra_versao,
        arcanista_caminho=arcanista_caminho,
    ):
        return True, ""
    slug = str(magia_slug or "").strip().lower()
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
            f"Magia de {circ}º círculo: esta classe no nível {nivel} só prepara até o {cmax}º círculo (MB).",
        )
    tipo_esperado = tipo_lista_magias_por_classe_mb(slug_classe)
    if tipo_esperado:
        meta_map = metadados_por_slug or {}
        tipo_mag = None
        if slug in meta_map:
            tipo_mag = meta_map[slug].get("tipo")
        else:
            m = metadados_magia_mb_por_slug(slug)
            tipo_mag = m.get("tipo") if m else None
        if tipo_mag and str(tipo_mag).strip().lower() != tipo_esperado:
            return (
                False,
                f"Magia {tipo_mag} incompatível com a lista {tipo_esperado} da classe {slug_classe} (MB).",
            )
    if exige_grimorio_para_preparar_mb(
        slug_classe,
        regra_versao=regra_versao,
        arcanista_caminho=arcanista_caminho,
    ):
        if slug not in _slugs_grimorio(vinculos_existentes):
            return (
                False,
                "Só é possível preparar magias que já estão no livro (grimório) do personagem (MB).",
            )
    elif (
        exige_repertorio_para_preparar_mb(
            slug_classe,
            regra_versao=regra_versao,
            arcanista_caminho=arcanista_caminho,
        )
        and circ >= 1
    ):
        if slug not in _slugs_conhecidas(vinculos_existentes):
            return (
                False,
                "Só é possível preparar magias que já estão no repertório aprendido do personagem (MB).",
            )
    if circ == 0 and not truques_contam_teto_preparadas_mb(
        slug_classe,
        regra_versao=regra_versao,
        arcanista_caminho=arcanista_caminho,
    ):
        return True, ""
    teto = teto_preparadas_mb(
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
    if teto is None:
        return True, ""
    usado = contar_preparadas_no_teto(
        vinculos_existentes,
        slug_classe=slug_classe,
        metadados_por_slug=metadados_por_slug,
        regra_versao=regra_versao,
        arcanista_caminho=arcanista_caminho,
    )
    if usado >= teto:
        return (
            False,
            f"Limite de magias preparadas hoje: {usado}/{teto} (MB, {slug_classe}).",
        )
    return True, ""


def validar_lancar_magia_preparador_mb(
    *,
    slug_classe: str,
    magia_slug: str,
    circulo_magia: int,
    vinculos: List[Dict[str, Any]],
    divindade_slug: Optional[str] = None,
) -> Tuple[bool, str]:
    """Círculo ≥1 exige preparada; truque exige grimório (mago) ou repertório/devoção (divino)."""
    if not classe_usa_limite_preparadas_mb(slug_classe):
        return True, ""
    slug = str(magia_slug or "").strip().lower()
    try:
        circ = int(circulo_magia)
    except (TypeError, ValueError):
        circ = 0
    papeis_por_slug: Dict[str, set[str]] = {}
    for v in vinculos:
        if not isinstance(v, dict):
            continue
        sl = str(v.get("magia_slug") or "").strip().lower()
        pap = str(v.get("papel", "")).strip().lower()
        if sl and pap:
            papeis_por_slug.setdefault(sl, set()).add(pap)
    if circ >= 1:
        if "preparada" not in papeis_por_slug.get(slug, set()):
            return (
                False,
                "Magias de 1º círculo ou superior precisam estar preparadas hoje para serem lançadas (MB).",
            )
        return True, ""
    if not exige_grimorio_para_preparar_mb(slug_classe):
        papeis = papeis_por_slug.get(slug, set())
        if "conhecida" in papeis or "preparada" in papeis:
            return True, ""
        from app.games.tormenta.rules.devocao_divindade_t20 import (
            classe_usa_truque_devocao_mb,
            magia_e_truque_devocao_mb,
        )

        if (
            classe_usa_truque_devocao_mb(slug_classe)
            and divindade_slug
            and magia_e_truque_devocao_mb(divindade_slug, slug)
        ):
            return True, ""
        return (
            False,
            "Truques divinos precisam estar no repertório aprendido ou ser a prece da sua devoção (MB).",
        )
    if "grimorio" not in papeis_por_slug.get(slug, set()):
        return (
            False,
            "Truques precisam estar no livro (grimório) do personagem para serem lançados (MB).",
        )
    return True, ""


def preview_preparadas_mb(
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
    usa = classe_usa_limite_preparadas_mb(
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
    usado = contar_preparadas_no_teto(
        vinculos,
        slug_classe=slug_classe,
        metadados_por_slug=meta,
        regra_versao=regra_versao,
        arcanista_caminho=arcanista_caminho,
    )
    teto = (
        teto_preparadas_mb(
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
    mod = 0
    eff = slug_efetivo_tabelas_magia_mb(slug_classe, regra_versao, arcanista_caminho)
    row = _classe_row(eff)
    if row:
        mod = _mod_habilidade_preparadas(
            slug_classe,
            row,
            for_valor=for_valor,
            des_valor=des_valor,
            con_valor=con_valor,
            int_valor=int_valor,
            sab_valor=sab_valor,
            car_valor=car_valor,
            regra_versao=regra_versao,
        )
    return {
        "classe_slug": str(slug_classe).strip().lower(),
        "nivel": int(nivel),
        "usa_limite_preparadas": usa,
        "preparadas_usadas": usado,
        "preparadas_max": teto,
        "mod_habilidade_chave": mod,
        "truques_contam_teto": truques_contam_teto_preparadas_mb(
            slug_classe,
            regra_versao=regra_versao,
            arcanista_caminho=arcanista_caminho,
        ),
        "exige_grimorio": exige_grimorio_para_preparar_mb(
            slug_classe,
            regra_versao=regra_versao,
            arcanista_caminho=arcanista_caminho,
        ),
        "exige_repertorio": exige_repertorio_para_preparar_mb(
            slug_classe,
            regra_versao=regra_versao,
            arcanista_caminho=arcanista_caminho,
        ),
    }
