"""Perícias na criação/evolução MB — vagas treinadas e orçamento de graduações."""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

from app.games.tormenta.rules.atributos_t20 import modificador_atributo_t20
from app.games.tormenta.rules.classes_t20 import (
    lista_beneficios_por_nivel_mb,
    lista_classes_mb,
)
from app.games.tormenta.rules.tracos_raciais_t20 import tracos_mecanicos_por_slug


def parse_graduacao_beneficio(texto: str) -> Tuple[int, int]:
    """'+4/+0' → (pontos treinadas, pontos não treinadas)."""
    t = str(texto or "").strip()
    m = re.match(r"^\+?(\d+)\s*/\s*\+?(\d+)\s*$", t)
    if not m:
        return 0, 0
    return int(m.group(1)), int(m.group(2))


def beneficio_nivel_mb(nivel: int) -> Optional[Dict[str, Any]]:
    try:
        nv = int(nivel)
    except (TypeError, ValueError):
        nv = 1
    for row in lista_beneficios_por_nivel_mb():
        if int(row.get("nivel", 0)) == nv:
            return row
    return None


def pericias_treinadas_base_classe(slug_classe: str) -> Optional[int]:
    s = str(slug_classe or "").strip().lower()
    if not s:
        return None
    for row in lista_classes_mb():
        if str(row.get("slug", "")).lower() == s:
            base = row.get("pericias_treinadas_base")
            if base is not None:
                return int(base)
            return None
    return None


def pericias_treinadas_extra_raca(slug_raca: str) -> int:
    row = tracos_mecanicos_por_slug(slug_raca)
    if not row:
        return 0
    return int(row.get("pericias_treinadas_extra", 0) or 0)


def vagas_pericias_treinadas_mb(
    slug_classe: str,
    int_valor: int,
    slug_raca: Optional[str] = None,
) -> Optional[int]:
    base = pericias_treinadas_base_classe(slug_classe)
    if base is None:
        return None
    mod_int = max(0, modificador_atributo_t20(int(int_valor)))
    extra = pericias_treinadas_extra_raca(slug_raca or "")
    return int(base) + mod_int + extra


def orcamento_graduacoes_mb(nivel: int) -> Tuple[int, int]:
    ben = beneficio_nivel_mb(nivel)
    if not ben:
        return 0, 0
    return parse_graduacao_beneficio(str(ben.get("graduacao_pericias", "")))


def _graduacao_linha(p: Dict[str, Any]) -> int:
    if "graduacao" in p and p["graduacao"] is not None:
        try:
            return max(0, int(p["graduacao"]))
        except (TypeError, ValueError):
            pass
    try:
        return max(0, int(p.get("total", 0) or 0))
    except (TypeError, ValueError):
        return 0


def validar_pericias_ficha_mb(
    *,
    nivel: int,
    slug_classe: str,
    int_valor: int,
    slug_raca: Optional[str],
    pericias: List[Dict[str, Any]],
) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Valida orçamento MB de perícias treinadas e graduações.
    Retorna (ok, motivo, resumo).
    """
    vagas = vagas_pericias_treinadas_mb(slug_classe, int_valor, slug_raca)
    if vagas is None:
        return True, "", {"ignorado": True, "motivo": "classe_mb_desconhecida"}

    pts_tr, pts_ntr = orcamento_graduacoes_mb(nivel)
    lista = pericias if isinstance(pericias, list) else []

    count_tr = 0
    sum_grad_tr = 0
    sum_grad_ntr = 0

    for p in lista:
        if not isinstance(p, dict):
            continue
        tre = bool(p.get("treinado"))
        grad = _graduacao_linha(p)
        if tre:
            count_tr += 1
            sum_grad_tr += grad
        else:
            sum_grad_ntr += grad

    resumo = {
        "vagas_treinadas": vagas,
        "usadas_treinadas": count_tr,
        "pontos_grad_treinadas": pts_tr,
        "gasto_grad_treinadas": sum_grad_tr,
        "pontos_grad_nao_treinadas": pts_ntr,
        "gasto_grad_nao_treinadas": sum_grad_ntr,
        "nivel": int(nivel),
        "classe_slug": str(slug_classe).strip().lower(),
    }

    if count_tr > vagas:
        return (
            False,
            f"Perícias treinadas: {count_tr} marcadas, mas o orçamento MB é {vagas} "
            f"(classe + INT + bônus racial).",
            resumo,
        )
    if sum_grad_tr > pts_tr:
        return (
            False,
            f"Graduações em perícias treinadas: gastou {sum_grad_tr}, orçamento do nível é {pts_tr} (MB).",
            resumo,
        )
    if sum_grad_ntr > pts_ntr:
        return (
            False,
            f"Graduações em perícias não treinadas: gastou {sum_grad_ntr}, orçamento do nível é {pts_ntr} (MB).",
            resumo,
        )
    return True, "", resumo


def preview_pericias_criacao_mb(
    *,
    nivel: int,
    slug_classe: str,
    int_valor: int,
    slug_raca: Optional[str] = None,
    pericias: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    vagas = vagas_pericias_treinadas_mb(slug_classe, int_valor, slug_raca)
    pts_tr, pts_ntr = orcamento_graduacoes_mb(nivel)
    ok, motivo, resumo = validar_pericias_ficha_mb(
        nivel=nivel,
        slug_classe=slug_classe,
        int_valor=int_valor,
        slug_raca=slug_raca,
        pericias=pericias or [],
    )
    ben = beneficio_nivel_mb(nivel)
    return {
        "valido": ok,
        "motivo": motivo,
        "vagas_treinadas": vagas,
        "pontos_grad_treinadas": pts_tr,
        "pontos_grad_nao_treinadas": pts_ntr,
        "graduacao_pericias_texto": (
            str(ben.get("graduacao_pericias", "")) if ben else ""
        ),
        "mod_int": modificador_atributo_t20(int(int_valor)),
        "pericias_treinadas_extra_racial": pericias_treinadas_extra_raca(
            slug_raca or ""
        ),
        **resumo,
    }
