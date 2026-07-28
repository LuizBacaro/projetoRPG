"""Perícias Tormenta 20 — bônus, percepção passiva, testes e tabela de DCs."""

from __future__ import annotations

import json
import random
import unicodedata
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.games.tormenta.rules.atributos_t20 import (
    contribuicao_atributo_t20,
    lista_pericias_com_atributo,
)
from app.games.tormenta.rules.regra_versao_t20 import (
    REGRA_VERSAO_MB,
    REGRA_VERSAO_V13,
    normalizar_regra_versao,
)
from app.games.tormenta.rules.tracos_raciais_t20 import tracos_mecanicos_por_slug

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_DC_JSON = _DATA_DIR / "pericias_dc_mb.json"

_BONUS_TREINADO_MB = 2


@lru_cache(maxsize=1)
def _carregar_dcs() -> Dict[str, Any]:
    if not _DC_JSON.is_file():
        return {"dificuldades": [], "pericias_exemplos": {}}
    return json.loads(_DC_JSON.read_text(encoding="utf-8"))


def lista_dificuldades_padrao_mb() -> List[Dict[str, Any]]:
    rows = _carregar_dcs().get("dificuldades") or []
    if not isinstance(rows, list):
        return []
    return [dict(r) for r in rows if isinstance(r, dict)]


def bonus_meio_nivel_t20(nivel: int) -> int:
    """⌊nível / 2⌋ (MB e v1.3)."""
    try:
        nv = int(nivel)
    except (TypeError, ValueError):
        nv = 1
    return max(0, nv // 2)


def bonus_treinamento_por_nivel(nivel: int, regra_versao: Optional[str] = None) -> int:
    """
    Bônus de treinamento conforme patamar (v1.3 p.114):
    1–6 → +2; 7–14 → +4; 15+ → +6. MB legado: +2 fixo.
    """
    if normalizar_regra_versao(regra_versao) != REGRA_VERSAO_V13:
        return _BONUS_TREINADO_MB
    try:
        nv = int(nivel)
    except (TypeError, ValueError):
        nv = 1
    nv = max(1, min(40, nv))
    if nv >= 15:
        return 6
    if nv >= 7:
        return 4
    return 2


def bonus_pericia_classe_mb(treinado: bool, pericia_de_classe: bool) -> int:
    """Legado MB — preferir bonus_treinamento_por_nivel com regra_versao."""
    _ = pericia_de_classe
    return _BONUS_TREINADO_MB if treinado else 0


def _normalizar_nome_pericia(nome: str) -> str:
    s = unicodedata.normalize("NFKD", str(nome or "").strip().lower())
    return "".join(c for c in s if not unicodedata.combining(c))


def meta_pericia_por_nome(
    nome: str, regra_versao: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    alvo = _normalizar_nome_pericia(nome)
    if not alvo:
        return None
    for row in lista_pericias_com_atributo(regra_versao):
        if _normalizar_nome_pericia(row.get("nome", "")) == alvo:
            return row
        slug = str(row.get("slug", "")).strip().lower()
        if slug and slug == alvo.replace(" ", "_"):
            return row
    return None


def pode_usar_pericia_treinada(
    nome_pericia: str,
    treinado: bool,
    regra_versao: Optional[str] = None,
) -> tuple[bool, str]:
    """Bloqueia uso de perícia «somente treinada» sem treino (v1.3 p.114)."""
    meta = meta_pericia_por_nome(nome_pericia, regra_versao)
    if not meta or not meta.get("somente_treinado"):
        return True, ""
    if treinado:
        return True, ""
    return (
        False,
        f"{meta.get('nome', nome_pericia)}: perícia somente treinada — marque «Treinado» na ficha.",
    )


def calcular_bonus_pericia(
    *,
    nivel: int,
    mod_atributo: int,
    treinado: bool = False,
    graduacao: int = 0,
    outros: int = 0,
    bonus_uso: int = 0,
    racial_bonus: int = 0,
    penalidade_armadura: int = 0,
    pericia_de_classe: bool = False,
    regra_versao: Optional[str] = None,
) -> int:
    """
    MB: mod + ½ nv + graduação + treino (+2) + outros + bonus_uso + racial − penalidade.
    v1.3: valor atributo + ½ nv + treino (+2/+4/+6) + outros + bonus_uso + racial −
    penalidade (sem graduação).

    ``bonus_uso`` é o modificador do uso escolhido na rolagem (RF-T04i); não misturar
    com ``outros`` da linha da ficha.
    """
    rv = normalizar_regra_versao(regra_versao)
    meio = bonus_meio_nivel_t20(nivel)
    tre = bonus_treinamento_por_nivel(nivel, rv) if treinado else 0
    try:
        grad = int(graduacao)
    except (TypeError, ValueError):
        grad = 0
    if rv == REGRA_VERSAO_V13:
        grad = 0
    try:
        out = int(outros)
    except (TypeError, ValueError):
        out = 0
    try:
        uso = int(bonus_uso)
    except (TypeError, ValueError):
        uso = 0
    try:
        rac = int(racial_bonus)
    except (TypeError, ValueError):
        rac = 0
    try:
        pen = int(penalidade_armadura)
    except (TypeError, ValueError):
        pen = 0
    try:
        mod = int(mod_atributo)
    except (TypeError, ValueError):
        mod = 0
    _ = pericia_de_classe
    return mod + meio + grad + tre + out + uso + rac - pen


def percepcao_passiva_t20(bonus_percepcao: int) -> int:
    """Percepção passiva = 10 + bônus total de Percepção."""
    return 10 + int(bonus_percepcao)


def racial_bonus_pericia(
    slug_raca: str,
    nome_pericia: str,
    regra_versao: Optional[str] = None,
) -> int:
    row = tracos_mecanicos_por_slug(slug_raca, regra_versao)
    if not row:
        return 0
    per_map = row.get("pericias_bonus") or {}
    if not isinstance(per_map, dict):
        return 0
    nome = str(nome_pericia or "").strip()
    if not nome:
        return 0
    return int(per_map.get(nome, 0) or 0)


def rolar_teste_pericia(
    bonus: int,
    dc: int,
    *,
    seed: Optional[int] = None,
) -> Dict[str, Any]:
    """Rola 1d20 + bônus vs DC; retorna resultado estruturado."""
    rng = random.Random(seed) if seed is not None else random
    d20 = rng.randint(1, 20)
    total = d20 + int(bonus)
    dc_i = int(dc)
    sucesso = total >= dc_i
    falha_critica = d20 == 1
    sucesso_critico = d20 == 20
    return {
        "d20": d20,
        "bonus": int(bonus),
        "total": total,
        "dc": dc_i,
        "sucesso": sucesso,
        "falha_critica": falha_critica,
        "sucesso_critico": sucesso_critico,
        "margem": total - dc_i,
    }


def mod_atributo_de_valor(valor: int, regra_versao: Optional[str] = None) -> int:
    return contribuicao_atributo_t20(int(valor), regra_versao)
