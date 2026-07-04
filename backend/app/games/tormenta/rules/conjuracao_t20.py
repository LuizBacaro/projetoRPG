"""Conjuração T20 — PM, habilidade-chave, custo por círculo (MB e v1.3)."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

from app.games.tormenta.rules.atributos_t20 import contribuicao_atributo_t20
from app.games.tormenta.rules.regra_versao_t20 import (
    REGRA_VERSAO_MB,
    REGRA_VERSAO_V13,
    normalizar_regra_versao,
)

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_CONJ_JSON = _DATA_DIR / "conjuracao_classe_mb.json"
_CONJ_V13_JSON = _DATA_DIR / "conjuracao_classe_v13.json"

HabilidadeChaveConjuracao = Literal["int", "sab", "car"]

_CUSTO_PM_V13 = {0: 0, 1: 1, 2: 3, 3: 6, 4: 10, 5: 15}


@lru_cache(maxsize=2)
def _carregar_conjuracao(regra_versao: str = REGRA_VERSAO_MB) -> Dict[str, Any]:
    path = (
        _CONJ_V13_JSON
        if normalizar_regra_versao(regra_versao) == REGRA_VERSAO_V13
        else _CONJ_JSON
    )
    if not path.is_file():
        return {"classes": []}
    return json.loads(path.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def _carregar_conjuracao_classe_mb() -> Dict[str, Any]:
    return _carregar_conjuracao(REGRA_VERSAO_MB)


def _pm_por_nivel_v13(slug: str) -> Optional[int]:
    data = _carregar_conjuracao(REGRA_VERSAO_V13)
    slug_l = str(slug or "").strip().lower()
    for row in data.get("classes") or []:
        if isinstance(row, dict) and str(row.get("slug", "")).lower() == slug_l:
            return int(row.get("pm_por_nivel", 0))
    extra = data.get("pm_por_nivel_nao_conjurador") or {}
    if isinstance(extra, dict) and slug_l in extra:
        return int(extra[slug_l])
    return None


def habilidade_chave_conjuracao_v13(
    slug_classe: str, arcanista_caminho: Optional[str] = None
) -> Optional[HabilidadeChaveConjuracao]:
    slug = str(slug_classe or "").strip().lower()
    data = _carregar_conjuracao(REGRA_VERSAO_V13)
    for row in data.get("classes") or []:
        if not isinstance(row, dict) or str(row.get("slug", "")).lower() != slug:
            continue
        if slug == "arcanista":
            caminhos = row.get("caminhos") or {}
            cam = str(arcanista_caminho or "mago").strip().lower()
            sub = caminhos.get(cam) if isinstance(caminhos, dict) else None
            if isinstance(sub, dict):
                ch = str(sub.get("habilidade_chave", "int")).lower()
                return ch if ch in ("int", "sab", "car") else "int"  # type: ignore[return-value]
        ch = str(row.get("habilidade_chave", "")).lower()
        if ch in ("int", "sab", "car"):
            return ch  # type: ignore[return-value]
    return None


def lista_regras_conjuracao_classe_mb() -> List[Dict[str, Any]]:
    return _lista_regras_conjuracao_mb()


def _lista_regras_conjuracao_mb() -> List[Dict[str, Any]]:
    data = _carregar_conjuracao_classe_mb()
    rows = data.get("classes") or []
    out: List[Dict[str, Any]] = []
    if not isinstance(rows, list):
        return out
    for row in rows:
        if not isinstance(row, dict):
            continue
        slug = str(row.get("slug", "")).strip().lower()
        if not slug:
            continue
        ch = str(row.get("habilidade_chave", "")).strip().lower()
        if ch not in ("int", "sab", "car"):
            continue
        try:
            pm_c = int(row.get("pm_constante", 0))
            pm_n = int(row.get("pm_por_nivel", 0))
            ini = int(row.get("conjuracao_inicia_nivel", 1) or 1)
        except (TypeError, ValueError):
            continue
        if ini < 1 or ini > 20:
            continue
        out.append(
            {
                "slug": slug,
                "habilidade_chave": ch,
                "pm_constante": pm_c,
                "pm_por_nivel": pm_n,
                "conjuracao_inicia_nivel": ini,
                "modo_conjuracao": str(
                    row.get("modo_conjuracao", "preparar") or "preparar"
                ),
            }
        )
    return sorted(out, key=lambda x: x["slug"])


# ---------------------------------------------------------------------------
# Heróis de Arton — overrides raciais de habilidade-chave de conjuração
# ---------------------------------------------------------------------------

#: Raças cujo traço racial substitui a habilidade-chave de conjuração arcana.
#: Fonte: Heróis de Arton v1.1 p.8 (Eiradaan — Magia Instintiva).
_OVERRIDE_HABILIDADE_CHAVE_POR_RACA: Dict[str, Dict[str, str]] = {
    # raca_slug -> {classe_slug -> nova_habilidade_chave}
    # "any_arcana" é um marcador especial para qualquer classe que usa INT arcano.
    "eiradaan": {"arcanista": "sab"},
}


def override_habilidade_chave_por_raca(
    slug_raca: Optional[str],
    slug_classe: Optional[str],
    habilidade_atual: Optional[str],
) -> Optional[HabilidadeChaveConjuracao]:
    """Retorna a habilidade-chave substituída por traço racial, ou ``habilidade_atual`` se não houver override.

    Exemplo: Eiradaan arcanista → "sab" no lugar de "int".
    """
    if not slug_raca or not slug_classe:
        return habilidade_atual  # type: ignore[return-value]
    overrides = _OVERRIDE_HABILIDADE_CHAVE_POR_RACA.get(
        str(slug_raca).strip().lower(), {}
    )
    nova = overrides.get(str(slug_classe).strip().lower())
    if nova and nova in ("int", "sab", "car"):
        return nova  # type: ignore[return-value]
    return habilidade_atual  # type: ignore[return-value]


def lista_regras_conjuracao_por_versao(
    regra_versao: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Regras de conjuração/PM por classe conforme edição."""
    rv = normalizar_regra_versao(regra_versao)
    if rv != REGRA_VERSAO_V13:
        return lista_regras_conjuracao_classe_mb()
    data = _carregar_conjuracao(REGRA_VERSAO_V13)
    out: List[Dict[str, Any]] = []
    for row in data.get("classes") or []:
        if not isinstance(row, dict):
            continue
        slug = str(row.get("slug", "")).strip().lower()
        if not slug:
            continue
        out.append(
            {
                "slug": slug,
                "habilidade_chave": str(row.get("habilidade_chave", "")).lower(),
                "pm_constante": 0,
                "pm_por_nivel": int(row.get("pm_por_nivel", 0) or 0),
                "conjuracao_inicia_nivel": int(
                    row.get("conjuracao_inicia_nivel", 1) or 1
                ),
                "modo_conjuracao": str(
                    row.get("modo_conjuracao", "preparar") or "preparar"
                ),
            }
        )
    extra = data.get("pm_por_nivel_nao_conjurador") or {}
    if isinstance(extra, dict):
        for slug, pm in extra.items():
            s = str(slug).strip().lower()
            if not s:
                continue
            out.append(
                {
                    "slug": s,
                    "habilidade_chave": "int",
                    "pm_constante": 0,
                    "pm_por_nivel": int(pm),
                    "conjuracao_inicia_nivel": 1,
                    "modo_conjuracao": "nao_conjura",
                }
            )
    return sorted(out, key=lambda x: x["slug"])


def _mapa_conjuracao_por_slug() -> Dict[str, Dict[str, Any]]:
    return {str(r["slug"]).lower(): r for r in lista_regras_conjuracao_classe_mb()}


def mapa_conjuracao_por_slug(
    regra_versao: Optional[str] = None,
) -> Dict[str, Dict[str, Any]]:
    """Mapa slug → linha de conjuração conforme edição (MB ou v1.3)."""
    rv = normalizar_regra_versao(regra_versao)
    if rv == REGRA_VERSAO_V13:
        return {
            str(r["slug"]).lower(): r
            for r in lista_regras_conjuracao_por_versao(REGRA_VERSAO_V13)
            if str(r.get("modo_conjuracao", "")).lower() != "nao_conjura"
        }
    return _mapa_conjuracao_por_slug()


def classe_conjuracao_mb_registrada(slug: str) -> bool:
    """True se o slug está na tabela MB de conjuração (bardo, mago, paladino etc.)."""
    s = str(slug or "").strip().lower()
    return bool(s and s in _mapa_conjuracao_por_slug())


def habilidade_chave_conjuracao_efetiva(
    slug_classe: str,
    regra_versao: Optional[str] = None,
    arcanista_caminho: Optional[str] = None,
    slug_raca: Optional[str] = None,
) -> Optional[HabilidadeChaveConjuracao]:
    hk = habilidade_chave_conjuracao(slug_classe, regra_versao, arcanista_caminho)
    if not hk:
        return None
    return override_habilidade_chave_por_raca(slug_raca, slug_classe, hk)


def modificador_conjuracao_efetivo(
    slug_classe: str,
    forca: int,
    destreza: int,
    constituicao: int,
    inteligencia: int,
    sabedoria: int,
    carisma: int,
    regra_versao: Optional[str] = None,
    arcanista_caminho: Optional[str] = None,
    slug_raca: Optional[str] = None,
) -> Optional[int]:
    hk = habilidade_chave_conjuracao_efetiva(
        slug_classe, regra_versao, arcanista_caminho, slug_raca
    )
    if not hk:
        return None
    return _modificador_chave(
        hk,
        forca,
        destreza,
        constituicao,
        inteligencia,
        sabedoria,
        carisma,
        regra_versao,
    )


def habilidade_chave_conjuracao(
    slug_classe: str,
    regra_versao: Optional[str] = None,
    arcanista_caminho: Optional[str] = None,
) -> Optional[HabilidadeChaveConjuracao]:
    if normalizar_regra_versao(regra_versao) == REGRA_VERSAO_V13:
        return habilidade_chave_conjuracao_v13(slug_classe, arcanista_caminho)
    slug = str(slug_classe or "").strip().lower()
    if not slug:
        return None
    row = _mapa_conjuracao_por_slug().get(slug)
    if not row:
        return None
    ch = row.get("habilidade_chave")
    if ch in ("int", "sab", "car"):
        return ch  # type: ignore[return-value]
    return None


def _modificador_chave(
    habilidade: HabilidadeChaveConjuracao,
    forca: int,
    destreza: int,
    constituicao: int,
    inteligencia: int,
    sabedoria: int,
    carisma: int,
    regra_versao: Optional[str] = None,
) -> int:
    if habilidade == "int":
        return contribuicao_atributo_t20(inteligencia, regra_versao)
    if habilidade == "sab":
        return contribuicao_atributo_t20(sabedoria, regra_versao)
    return contribuicao_atributo_t20(carisma, regra_versao)


def modificador_conjuracao_mb(
    slug_classe: str,
    forca: int,
    destreza: int,
    constituicao: int,
    inteligencia: int,
    sabedoria: int,
    carisma: int,
    regra_versao: Optional[str] = None,
    arcanista_caminho: Optional[str] = None,
) -> Optional[int]:
    """Contribuição do atributo-chave (mod. MB ou valor v1.3)."""
    hk = habilidade_chave_conjuracao(slug_classe, regra_versao, arcanista_caminho)
    if not hk:
        return None
    return _modificador_chave(
        hk,
        forca,
        destreza,
        constituicao,
        inteligencia,
        sabedoria,
        carisma,
        regra_versao,
    )


def cd_resistencia_magia_t20(
    nivel_personagem: int,
    atributo_chave_valor: int,
    regra_versao: Optional[str] = None,
) -> int:
    """CD de magia: MB usa mod+10+½n; v1.3 usa 10 + ⌊n/2⌋ + valor atributo."""
    try:
        n = int(nivel_personagem)
    except (TypeError, ValueError):
        n = 1
    meio = max(0, n // 2)
    if normalizar_regra_versao(regra_versao) == REGRA_VERSAO_V13:
        return 10 + meio + int(atributo_chave_valor)
    return (
        10
        + meio
        + contribuicao_atributo_t20(int(atributo_chave_valor), REGRA_VERSAO_MB)
    )


def pontos_magia_maximos_conjuracao(
    slug_classe: str,
    nivel_classe: int,
    forca: int,
    destreza: int,
    constituicao: int,
    inteligencia: int,
    sabedoria: int,
    carisma: int,
    regra_versao: Optional[str] = None,
    arcanista_caminho: Optional[str] = None,
) -> Optional[int]:
    """PM máximos. MB: fórmula por conjurador; v1.3: nível × pm_por_nivel (todas as classes)."""
    slug = str(slug_classe or "").strip().lower()
    try:
        n = int(nivel_classe)
    except (TypeError, ValueError):
        return None
    if n < 1 or n > 40:
        return None
    rv = normalizar_regra_versao(regra_versao)
    if rv == REGRA_VERSAO_V13:
        pm_n = _pm_por_nivel_v13(slug)
        if pm_n is None:
            return None
        return n * pm_n
    row = _mapa_conjuracao_por_slug().get(slug)
    if not row:
        return None
    ini = int(row["conjuracao_inicia_nivel"])
    if n < ini:
        return None
    ch: HabilidadeChaveConjuracao = row["habilidade_chave"]  # type: ignore[assignment]
    mod = _modificador_chave(
        ch, forca, destreza, constituicao, inteligencia, sabedoria, carisma, rv
    )
    pm_c = int(row["pm_constante"])
    pm_n = int(row["pm_por_nivel"])
    if ini == 1:
        return pm_c + mod + (n - 1) * pm_n
    return pm_c + mod + (n - ini) * pm_n


# Nome legado (mana); no MB o recurso são Pontos de Magia (PM).
pontos_mana_maximos_conjuracao = pontos_magia_maximos_conjuracao


def custo_pm_preparar_ou_lancar_magia(
    circulo: int, regra_versao: Optional[str] = None
) -> int:
    """PM para preparar/lançar. MB: C PM; v1.3: 1/3/6/10/15 (Tabela 4-1)."""
    try:
        c = int(circulo)
    except (TypeError, ValueError):
        return 0
    if c <= 0:
        return 0
    if normalizar_regra_versao(regra_versao) == REGRA_VERSAO_V13:
        return _CUSTO_PM_V13.get(min(c, 5), 15)
    return min(c, 20)


def texto_custo_pm_por_circulo_mb(regra_versao: Optional[str] = None) -> str:
    rv = normalizar_regra_versao(regra_versao)
    data = _carregar_conjuracao(rv)
    meta = data.get("_meta") if isinstance(data.get("_meta"), dict) else {}
    t = meta.get("custo_magia")
    if isinstance(t, str) and t.strip():
        return t.strip()
    if rv == REGRA_VERSAO_V13:
        return (
            "1º: 1 PM; 2º: 3; 3º: 6; 4º: 10; 5º: 15. Truques via aprimoramento (0 PM)."
        )
    return "Truque (círculo 0): 0 PM. Círculo C≥1: C PM."


def pm_aprimoramento_bonus_racial(slug_raca: Optional[str]) -> int:
    """PM extra para aprimoramentos ao lançar magia (Eiradaan: +1)."""
    from app.games.tormenta.rules.tracos_raciais_t20 import tracos_mecanicos_por_slug

    row = tracos_mecanicos_por_slug(slug_raca, REGRA_VERSAO_V13)
    if not row:
        return 0
    return int(row.get("pm_aprimoramento_conjuracao", 0) or 0)


def instrumentista_magico_racial(slug_raca: Optional[str]) -> bool:
    """True se a raça pode conjurar via instrumento (Sátiro)."""
    from app.games.tormenta.rules.tracos_raciais_t20 import tracos_mecanicos_por_slug

    row = tracos_mecanicos_por_slug(slug_raca, REGRA_VERSAO_V13)
    return bool(row and row.get("instrumentista_magico"))


def pode_conjurar_via_instrumento(
    slug_raca: Optional[str],
    *,
    instrumento_empunhado: bool,
) -> bool:
    """Instrumentista Mágico exige instrumento em mãos."""
    return instrumentista_magico_racial(slug_raca) and bool(instrumento_empunhado)
