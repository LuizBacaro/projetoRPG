"""Grimório — validação de papéis (preparar / espontâneo / foco) e gasto de PM."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Literal, Optional, Tuple

from app.games.tormenta.rules.catalogo_t20 import metadados_magia_mb_por_slug
from app.games.tormenta.rules.conjuracao_t20 import (
    custo_pm_preparar_ou_lancar_magia,
    pontos_magia_maximos_conjuracao,
)
from app.games.tormenta.rules.regra_versao_t20 import (
    REGRA_VERSAO_MB,
    REGRA_VERSAO_V13,
    normalizar_regra_versao,
    regra_versao_de_ficha,
)

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_CONJ_JSON = _DATA_DIR / "conjuracao_classe_mb.json"
_CONJ_V13_JSON = _DATA_DIR / "conjuracao_classe_v13.json"

ModoConjuracaoMb = Literal["preparar", "espontaneo"]
ModoConjuracao = Literal["preparar", "espontaneo", "foco"]
_PAPEIS = frozenset({"grimorio", "conhecida", "preparada"})


@lru_cache(maxsize=1)
def _carregar_conj() -> Dict[str, Any]:
    if not _CONJ_JSON.is_file():
        return {"classes": []}
    return json.loads(_CONJ_JSON.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def _carregar_conj_v13() -> Dict[str, Any]:
    if not _CONJ_V13_JSON.is_file():
        return {"classes": []}
    return json.loads(_CONJ_V13_JSON.read_text(encoding="utf-8"))


def contexto_conjuracao_de_ficha(
    ficha_json: Optional[Dict[str, Any]],
) -> Dict[str, Optional[str]]:
    """Extrai slug, versão de regras e caminho do arcanista a partir de ficha_json."""
    fj = ficha_json if isinstance(ficha_json, dict) else {}
    slug = str(fj.get("tormenta_classe_mb_slug") or "").strip().lower()
    rv = regra_versao_de_ficha(fj)
    cam_raw = str(fj.get("arcanista_caminho") or "").strip().lower()
    cam = cam_raw if cam_raw in ("bruxo", "mago", "feiticeiro") else None
    return {
        "regra_versao": rv,
        "slug_classe": slug or None,
        "arcanista_caminho": cam if slug == "arcanista" else None,
    }


def slug_efetivo_tabelas_magia_mb(
    slug_classe: str,
    regra_versao: Optional[str] = None,
    arcanista_caminho: Optional[str] = None,
) -> str:
    """
    Slug usado nas tabelas MB de grimório / conhecidas / preparadas.
    Arcanista v1.3: mago → mago; feiticeiro/bruxo → feiticeiro; caçador → ranger.
    """
    s = str(slug_classe or "").strip().lower()
    if normalizar_regra_versao(regra_versao) != REGRA_VERSAO_V13:
        return s
    if s == "arcanista":
        cam = str(arcanista_caminho or "mago").strip().lower()
        if cam == "mago":
            return "mago"
        if cam in ("feiticeiro", "bruxo"):
            return "feiticeiro"
        return "mago"
    if s == "cacador":
        return "ranger"
    return s


def modo_conjuracao_classe_mb(slug_classe: str) -> Optional[ModoConjuracaoMb]:
    """preparar (mago/clérigo/druida/paladino/ranger) ou espontaneo (bardo/feiticeiro)."""
    s = str(slug_classe or "").strip().lower()
    rows = _carregar_conj().get("classes") or []
    if not isinstance(rows, list):
        return None
    for row in rows:
        if not isinstance(row, dict):
            continue
        if str(row.get("slug", "")).strip().lower() != s:
            continue
        modo = str(row.get("modo_conjuracao", "preparar") or "preparar").strip().lower()
        if modo in ("preparar", "espontaneo"):
            return modo  # type: ignore[return-value]
        return "preparar"
    return None


def modo_conjuracao_classe(
    slug_classe: str,
    regra_versao: Optional[str] = None,
    arcanista_caminho: Optional[str] = None,
) -> Optional[ModoConjuracao]:
    """Modo de conjuração conforme edição (MB ou v1.3, incluindo caminhos do arcanista)."""
    rv = normalizar_regra_versao(regra_versao)
    s = str(slug_classe or "").strip().lower()
    if rv != REGRA_VERSAO_V13:
        return modo_conjuracao_classe_mb(s)  # type: ignore[return-value]
    for row in _carregar_conj_v13().get("classes") or []:
        if not isinstance(row, dict) or str(row.get("slug", "")).strip().lower() != s:
            continue
        if s == "arcanista":
            caminhos = row.get("caminhos") or {}
            cam = str(arcanista_caminho or "mago").strip().lower()
            sub = caminhos.get(cam) if isinstance(caminhos, dict) else None
            if isinstance(sub, dict):
                modo = (
                    str(sub.get("modo_conjuracao", "preparar") or "preparar")
                    .strip()
                    .lower()
                )
                if modo in ("preparar", "espontaneo", "foco"):
                    return modo  # type: ignore[return-value]
            return "preparar"
        modo = str(row.get("modo_conjuracao", "preparar") or "preparar").strip().lower()
        if modo in ("preparar", "espontaneo"):
            return modo  # type: ignore[return-value]
        return "preparar"
    return None


def _classe_usa_livro_grimorio_mb(
    slug_classe: str,
    *,
    regra_versao: Optional[str] = None,
    arcanista_caminho: Optional[str] = None,
) -> bool:
    from app.games.tormenta.rules.magias_grimorio_aprendizado_t20 import (
        classe_usa_limite_grimorio_mb,
    )

    return classe_usa_limite_grimorio_mb(
        slug_classe,
        regra_versao=regra_versao,
        arcanista_caminho=arcanista_caminho,
    )


def _classe_usa_repertorio_aprendido_mb(
    slug_classe: str,
    *,
    regra_versao: Optional[str] = None,
    arcanista_caminho: Optional[str] = None,
) -> bool:
    from app.games.tormenta.rules.magias_repertorio_aprendido_t20 import (
        classe_usa_limite_repertorio_mb,
    )

    return classe_usa_limite_repertorio_mb(
        slug_classe,
        regra_versao=regra_versao,
        arcanista_caminho=arcanista_caminho,
    )


def validar_papel_magia_para_classe(
    slug_classe: str,
    papel: str,
    *,
    conjuracao_manual: bool = False,
    regra_versao: Optional[str] = None,
    arcanista_caminho: Optional[str] = None,
) -> Tuple[bool, str]:
    """Valida se o papel (grimorio/conhecida/preparada) é permitido para a classe."""
    if conjuracao_manual:
        return True, ""
    p = str(papel or "").strip().lower()
    if p not in _PAPEIS:
        return False, "papel deve ser grimorio, conhecida ou preparada"
    modo = modo_conjuracao_classe(slug_classe, regra_versao, arcanista_caminho)
    if modo is None:
        return True, ""
    if modo == "foco":
        if p == "grimorio":
            return (
                False,
                "Bruxo conjura via foco arcano — não usa grimório (livro); use conhecida.",
            )
        if p == "preparada":
            return (
                False,
                "Bruxo não prepara magias — registre as magias do foco como conhecida.",
            )
        return True, ""
    if modo == "espontaneo":
        if p == "grimorio":
            return (
                False,
                "Classes espontâneas (bardo, feiticeiro) não usam grimório — use conhecida.",
            )
        return True, ""
    # preparar
    if p == "conhecida":
        if _classe_usa_repertorio_aprendido_mb(
            slug_classe,
            regra_versao=regra_versao,
            arcanista_caminho=arcanista_caminho,
        ):
            return True, ""
        return (
            False,
            "O mago usa grimório (livro) — papel conhecida não se aplica; use grimorio.",
        )
    if p == "grimorio" and not _classe_usa_livro_grimorio_mb(
        slug_classe,
        regra_versao=regra_versao,
        arcanista_caminho=arcanista_caminho,
    ):
        return (
            False,
            "Clérigo, druida, paladino e caçador não usam livro de magias — use repertório aprendido (conhecida).",
        )
    return True, ""


def custo_pm_magia_slug(magia_slug: str, regra_versao: Optional[str] = None) -> int:
    meta = metadados_magia_mb_por_slug(magia_slug)
    if not meta:
        return 0
    try:
        circulo = int(meta.get("circulo", 0) or 0)
    except (TypeError, ValueError):
        circulo = 0
    return custo_pm_preparar_ou_lancar_magia(circulo, regra_versao)


def simular_gasto_pm(
    *,
    classe_slug: str,
    nivel: int,
    for_valor: int,
    des_valor: int,
    con_valor: int,
    int_valor: int,
    sab_valor: int,
    car_valor: int,
    pa_atual: int,
    magia_slug: str,
    custo_pm_override: Optional[int] = None,
    regra_versao: Optional[str] = None,
    arcanista_caminho: Optional[str] = None,
) -> Dict[str, Any]:
    """Calcula custo e novo saldo de PM sem persistir."""
    rv = regra_versao or REGRA_VERSAO_MB
    if custo_pm_override is not None:
        custo = int(custo_pm_override)
    else:
        custo = custo_pm_magia_slug(magia_slug, rv)
    pm_max = pontos_magia_maximos_conjuracao(
        classe_slug,
        nivel,
        for_valor,
        des_valor,
        con_valor,
        int_valor,
        sab_valor,
        car_valor,
        regra_versao=rv,
        arcanista_caminho=arcanista_caminho,
    )
    atual = int(pa_atual)
    novo = atual - custo
    permitido = novo >= 0 or custo == 0
    return {
        "custo_pm": custo,
        "pa_atual_antes": atual,
        "pa_atual_depois": novo,
        "pa_max": pm_max,
        "permitido": permitido,
        "motivo": "" if permitido else "PM insuficientes para lançar esta magia.",
    }
