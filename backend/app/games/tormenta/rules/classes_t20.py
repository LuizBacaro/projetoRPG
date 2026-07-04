"""Classes Tormenta 20 — MB legado e core v1.3 (Edição Jogo do Ano)."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.games.tormenta.rules.regra_versao_t20 import (
    REGRA_VERSAO_MB,
    REGRA_VERSAO_V13,
    normalizar_regra_versao,
)

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_CLASS_MB_JSON = _DATA_DIR / "classes_mb.json"
_CLASS_V13_JSON = _DATA_DIR / "classes_v13.json"
_CONJ_V13_JSON = _DATA_DIR / "conjuracao_classe_v13.json"
_CLASSES_HEROIS_ARTON_JSON = _DATA_DIR / "classes_herois_arton.json"


from app.games.tormenta.rules.beneficios_nivel_t20 import (
    lista_beneficios_por_nivel,
    lista_beneficios_por_nivel_mb,
)


def _carregar_classes_raw(regra_versao: str = REGRA_VERSAO_MB) -> Dict[str, Any]:
    path = (
        _CLASS_V13_JSON
        if normalizar_regra_versao(regra_versao) == REGRA_VERSAO_V13
        else _CLASS_MB_JSON
    )
    raw = path.read_text(encoding="utf-8")
    return json.loads(raw)


@lru_cache(maxsize=1)
def _pm_por_nivel_map_v13() -> Dict[str, int]:
    raw = _CONJ_V13_JSON.read_text(encoding="utf-8")
    data = json.loads(raw)
    out: Dict[str, int] = {}
    for row in data.get("classes") or []:
        if not isinstance(row, dict):
            continue
        slug = str(row.get("slug", "")).strip().lower()
        if not slug:
            continue
        try:
            out[slug] = int(row.get("pm_por_nivel", 0) or 0)
        except (TypeError, ValueError):
            pass
    extra = data.get("pm_por_nivel_nao_conjurador") or {}
    if isinstance(extra, dict):
        for slug, pm in extra.items():
            sk = str(slug).strip().lower()
            if not sk:
                continue
            try:
                out[sk] = int(pm or 0)
            except (TypeError, ValueError):
                pass
    return out


def _parse_habilidades_por_nivel(hab: Any) -> Dict[str, str]:
    hab_limpo: Dict[str, str] = {}
    if isinstance(hab, dict):
        for k, v in hab.items():
            kk = str(k).strip()
            if kk.isdigit() and 1 <= int(kk) <= 40:
                hab_limpo[kk] = str(v or "").strip()
    return hab_limpo


def _normalizar_classe_row(
    row: Dict[str, Any], pm_map: Optional[Dict[str, int]] = None
) -> Optional[Dict[str, Any]]:
    slug = str(row.get("slug", "")).strip()
    nome = str(row.get("nome", "")).strip()
    if not slug or not nome:
        return None
    bba_tipo = str(row.get("bba_tipo", "plein")).strip()
    if bba_tipo not in ("plein", "tres_quartos", "meio"):
        bba_tipo = "plein"
    item: Dict[str, Any] = {
        "slug": slug,
        "nome": nome,
        "abreviatura": str(row.get("abreviatura", "") or "").strip(),
        "bba_tipo": bba_tipo,
        "pv_inicial": int(row.get("pv_inicial", 8) or 8),
        "pv_por_nivel": int(row.get("pv_por_nivel", 2) or 0),
        "pericias_treinadas": str(row.get("pericias_treinadas", "") or "").strip(),
        "pericias_classe": str(row.get("pericias_classe", "") or "").strip(),
        "talentos_adicionais": str(row.get("talentos_adicionais", "") or "").strip(),
        "habilidades_por_nivel": _parse_habilidades_por_nivel(
            row.get("habilidades_por_nivel") or {}
        ),
        # campos de suplemento (pass-through; None = classe core)
        "fonte_catalogo": str(row.get("fonte_catalogo") or "core").strip(),
        "classe_variante_base": row.get("classe_variante_base"),
        "exclusivo_com": list(row.get("exclusivo_com") or []),
    }
    base_pt = row.get("pericias_treinadas_base")
    if base_pt is not None:
        try:
            item["pericias_treinadas_base"] = int(base_pt)
        except (TypeError, ValueError):
            pass
    ap = str(row.get("atributo_principal", "") or "").strip()
    if ap:
        item["atributo_principal"] = ap
    fixas = row.get("pericias_fixas")
    if isinstance(fixas, list):
        item["pericias_fixas"] = [str(x).strip() for x in fixas if str(x).strip()]
    if pm_map is not None:
        pm = pm_map.get(slug.lower())
        if pm is not None:
            item["pm_por_nivel"] = pm
        elif row.get("pm_por_nivel") is not None:
            # fallback: pm_por_nivel direto no JSON (classes de suplemento)
            try:
                item["pm_por_nivel"] = int(row["pm_por_nivel"])
            except (TypeError, ValueError):
                pass
    elif row.get("pm_por_nivel") is not None:
        try:
            item["pm_por_nivel"] = int(row["pm_por_nivel"])
        except (TypeError, ValueError):
            pass
    return item


def _aplicar_config_pericias_v13(item: Dict[str, Any]) -> None:
    from app.games.tormenta.rules.pericias_classe_t20 import config_pericias_classe_v13

    cfg = config_pericias_classe_v13(str(item.get("slug", "")))
    if not cfg:
        return
    item["pericias_fixas"] = cfg["pericias_fixas"]
    item["pericias_escolha_qtd"] = cfg["pericias_escolha_qtd"]
    item["pericias_escolha_de"] = cfg["pericias_escolha_de"]
    item["pericias_escolha_um_de"] = cfg["pericias_escolha_um_de"]
    item["vagas_classe"] = (
        len(cfg["pericias_fixas"])
        + len(cfg["pericias_escolha_um_de"])
        + int(cfg["pericias_escolha_qtd"])
    )


def _lista_classes_de_arquivo(regra_versao: str) -> List[Dict[str, Any]]:
    data = _carregar_classes_raw(regra_versao)
    rows = data.get("classes") or []
    out: List[Dict[str, Any]] = []
    if not isinstance(rows, list):
        return out
    pm_map = (
        _pm_por_nivel_map_v13()
        if normalizar_regra_versao(regra_versao) == REGRA_VERSAO_V13
        else None
    )
    for row in rows:
        if not isinstance(row, dict):
            continue
        parsed = _normalizar_classe_row(row, pm_map)
        if parsed:
            if normalizar_regra_versao(regra_versao) == REGRA_VERSAO_V13:
                _aplicar_config_pericias_v13(parsed)
            out.append(parsed)
    return out


def lista_classes_mb() -> List[Dict[str, Any]]:
    """Classes do MB com PV, perícias e mapa opcional habilidades por nível."""
    return _lista_classes_de_arquivo(REGRA_VERSAO_MB)


def lista_classes_v13() -> List[Dict[str, Any]]:
    """14 classes core v1.3 (Tabela 1-3)."""
    return _lista_classes_de_arquivo(REGRA_VERSAO_V13)


def lista_classes(regra_versao: Optional[str] = None) -> List[Dict[str, Any]]:
    """Lista classes conforme versão de regras (default MB — compatibilidade)."""
    if normalizar_regra_versao(regra_versao) == REGRA_VERSAO_V13:
        return lista_classes_v13()
    return lista_classes_mb()


def classe_por_slug(
    slug: str, regra_versao: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    s = str(slug or "").strip().lower()
    if not s:
        return None
    for row in lista_classes(regra_versao):
        if str(row.get("slug", "")).lower() == s:
            return row
    if normalizar_regra_versao(regra_versao) == REGRA_VERSAO_V13:
        for row in lista_classes_herois_arton():
            if str(row.get("slug", "")).lower() == s:
                return row
    return None


def bba_por_nivel_classe(nivel_classe: int, bba_tipo: str) -> int:
    """Bônus base de ataque para um único nível na classe (1..20)."""
    n = max(0, min(20, int(nivel_classe)))
    if n <= 0:
        return 0
    t = (bba_tipo or "plein").strip()
    if t == "meio":
        return n // 2
    if t == "tres_quartos":
        return (n * 3) // 4
    return n


# ---------------------------------------------------------------------------
# Heróis de Arton — Treinador + 14 classes variantes
# ---------------------------------------------------------------------------


@lru_cache(maxsize=1)
def _carregar_classes_herois_arton() -> Dict[str, Any]:
    if not _CLASSES_HEROIS_ARTON_JSON.is_file():
        return {"classes": []}
    return json.loads(_CLASSES_HEROIS_ARTON_JSON.read_text(encoding="utf-8"))


def lista_classes_herois_arton() -> List[Dict[str, Any]]:
    """Treinador + 14 classes variantes do suplemento Heróis de Arton v1.1."""
    rows = _carregar_classes_herois_arton().get("classes") or []
    out: List[Dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        parsed = _normalizar_classe_row(row, pm_map=None)
        if parsed:
            out.append(parsed)
    return out


def lista_classes_com_suplemento(
    regra_versao: Optional[str] = None,
    suplemento: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Classes core + suplemento quando ``suplemento='herois_arton'``."""
    from app.games.tormenta.rules.regra_versao_t20 import SUPLEMENTO_HEROIS_ARTON

    classes = lista_classes(regra_versao)
    if suplemento and str(suplemento).strip().lower() == SUPLEMENTO_HEROIS_ARTON:
        classes = classes + lista_classes_herois_arton()
    return classes


def validar_classe_variante(
    slug_nova_classe: str,
    slugs_classes_existentes: List[str],
) -> Optional[str]:
    """Valida compatibilidade de classe variante com classes já selecionadas.

    Retorna mensagem de erro se incompatível, ou ``None`` se OK.
    Regra: uma classe variante é mutuamente exclusiva com sua classe base e
    com todas as classes listadas em ``exclusivo_com``.
    """
    slug = str(slug_nova_classe or "").strip().lower()
    if not slug:
        return None

    # Buscar definição da nova classe no catálogo do suplemento
    todas_ha = lista_classes_herois_arton()
    nova_def = next((c for c in todas_ha if c["slug"] == slug), None)
    if nova_def is None:
        return None  # não é classe variante — sem restrição

    exclusivos = [str(e).strip().lower() for e in (nova_def.get("exclusivo_com") or [])]
    base = nova_def.get("classe_variante_base")
    if base:
        exclusivos.append(str(base).strip().lower())
    exclusivos = list(set(exclusivos))

    slugs_existentes_l = [str(s).strip().lower() for s in slugs_classes_existentes]

    conflitos = [s for s in slugs_existentes_l if s in exclusivos]
    if conflitos:
        nomes_conflito = ", ".join(conflitos)
        return (
            f"A classe variante '{nova_def['nome']}' é incompatível com: {nomes_conflito}. "
            "Classes variantes e suas bases são mutuamente exclusivas."
        )

    # Verificar também se outra classe variante já selecionada conflita com esta
    for slug_ex in slugs_existentes_l:
        classe_ex = next((c for c in todas_ha if c["slug"] == slug_ex), None)
        if classe_ex is None:
            continue
        exclusivos_ex = [str(e).lower() for e in (classe_ex.get("exclusivo_com") or [])]
        base_ex = classe_ex.get("classe_variante_base")
        if base_ex:
            exclusivos_ex.append(str(base_ex).lower())
        if slug in exclusivos_ex:
            return f"'{classe_ex['nome']}' já selecionada é incompatível com '{nova_def['nome']}'."

    return None


def validar_compatibilidade_classes_v13(
    ficha_json: Optional[Dict[str, Any]],
    nivel_personagem: int = 1,
) -> Optional[str]:
    """Valida exclusão mútua entre classes variantes e bases na ficha v1.3."""
    from app.games.tormenta.rules.progressao_pv_t20 import (
        niveis_multiclasse_v13_de_ficha,
    )

    fj = dict(ficha_json or {})
    try:
        nv = int(nivel_personagem)
    except (TypeError, ValueError):
        nv = 1
    linhas = niveis_multiclasse_v13_de_ficha(fj, nv)
    slugs = [str(linha.get("slug") or "").strip().lower() for linha in linhas]
    slugs = [s for s in slugs if s]
    for slug in slugs:
        outros = [s for s in slugs if s != slug]
        err = validar_classe_variante(slug, outros)
        if err:
            return err
    return None
