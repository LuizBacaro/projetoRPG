"""Perícias Tormenta 20 — bônus, percepção passiva, testes e tabela de DCs."""

from __future__ import annotations

import json
import random
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.games.tormenta.rules.atributos_t20 import modificador_atributo_t20
from app.games.tormenta.rules.tracos_raciais_t20 import tracos_mecanicos_por_slug

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_DC_JSON = _DATA_DIR / "pericias_dc_mb.json"

_BONUS_TREINADO_T20 = 2


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
    """½ nível arredondado para baixo (MB)."""
    try:
        nv = int(nivel)
    except (TypeError, ValueError):
        nv = 1
    return max(0, nv // 2)


def bonus_pericia_classe_mb(treinado: bool, pericia_de_classe: bool) -> int:
    """Bônus de treinamento T20: +2 se treinado (perícia de classe segue mesma regra na ficha)."""
    _ = pericia_de_classe
    return _BONUS_TREINADO_T20 if treinado else 0


def calcular_bonus_pericia(
    *,
    nivel: int,
    mod_atributo: int,
    treinado: bool = False,
    graduacao: int = 0,
    outros: int = 0,
    racial_bonus: int = 0,
    penalidade_armadura: int = 0,
    pericia_de_classe: bool = False,
) -> int:
    """Bônus total = mod + ½ nv + graduação + treinado (+2) + outros + racial − penalidade armadura."""
    meio = bonus_meio_nivel_t20(nivel)
    tre = bonus_pericia_classe_mb(treinado, pericia_de_classe)
    try:
        grad = int(graduacao)
    except (TypeError, ValueError):
        grad = 0
    try:
        out = int(outros)
    except (TypeError, ValueError):
        out = 0
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
    return mod + meio + grad + tre + out + rac - pen


def percepcao_passiva_t20(bonus_percepcao: int) -> int:
    """Percepção passiva = 10 + bônus total de Percepção."""
    return 10 + int(bonus_percepcao)


def racial_bonus_pericia(slug_raca: str, nome_pericia: str) -> int:
    row = tracos_mecanicos_por_slug(slug_raca)
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


def mod_atributo_de_valor(valor: int) -> int:
    return modificador_atributo_t20(int(valor))
