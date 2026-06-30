"""Perícias na criação/evolução — vagas treinadas e orçamento (MB e v1.3)."""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

from app.games.tormenta.rules.atributos_t20 import (
    contribuicao_atributo_t20,
    modificador_atributo_t20,
)
from app.games.tormenta.rules.beneficios_nivel_t20 import (
    beneficio_nivel,
    beneficio_nivel_mb,
)
from app.games.tormenta.rules.classes_t20 import lista_classes
from app.games.tormenta.rules.origens_t20 import contar_vagas_pericias_extra_origem
from app.games.tormenta.rules.pericias_classe_t20 import (
    preview_pericias_classe_v13,
    vagas_classe_v13,
    validar_pericias_classe_v13,
)
from app.games.tormenta.rules.racas_t20 import lista_racas
from app.games.tormenta.rules.regra_versao_t20 import (
    REGRA_VERSAO_MB,
    REGRA_VERSAO_V13,
    normalizar_regra_versao,
)
from app.games.tormenta.rules.tracos_raciais_t20 import (
    pericias_treinadas_extra_de_tracos,
    tracos_mecanicos_por_slug,
)


def parse_graduacao_beneficio(texto: str) -> Tuple[int, int]:
    """'+4/+0' → (pontos treinadas, pontos não treinadas)."""
    t = str(texto or "").strip()
    m = re.match(r"^\+?(\d+)\s*/\s*\+?(\d+)\s*$", t)
    if not m:
        return 0, 0
    return int(m.group(1)), int(m.group(2))


def orcamento_graduacoes_mb(nivel: int) -> Tuple[int, int]:
    return orcamento_graduacoes_por_nivel(nivel, REGRA_VERSAO_MB)


def orcamento_graduacoes_por_nivel(
    nivel: int, regra_versao: Optional[str] = None
) -> Tuple[int, int]:
    rv = normalizar_regra_versao(regra_versao)
    if rv == REGRA_VERSAO_V13:
        return 0, 0
    ben = beneficio_nivel(nivel, rv)
    if not ben:
        return 0, 0
    return parse_graduacao_beneficio(str(ben.get("graduacao_pericias", "")))


def pericias_treinadas_base_classe(
    slug_classe: str, regra_versao: Optional[str] = None
) -> Optional[int]:
    s = str(slug_classe or "").strip().lower()
    if not s:
        return None
    for row in lista_classes(regra_versao):
        if str(row.get("slug", "")).lower() == s:
            base = row.get("pericias_treinadas_base")
            if base is not None:
                return int(base)
            return None
    return None


def pericias_treinadas_extra_raca(
    slug_raca: str,
    regra_versao: Optional[str] = None,
    *,
    humano_versatil: Optional[str] = None,
) -> int:
    s = str(slug_raca or "").strip().lower()
    rv = normalizar_regra_versao(regra_versao)
    if rv == REGRA_VERSAO_V13 and s == "humano":
        return pericias_treinadas_extra_de_tracos(
            slug_raca, rv, humano_versatil=humano_versatil
        )
    extra_lista = 0
    if s:
        for row in lista_racas(regra_versao):
            if str(row.get("slug", "")).lower() == s:
                extra_lista = int(row.get("pericias_treinadas_extra", 0) or 0)
                break
    extra_tracos = pericias_treinadas_extra_de_tracos(
        slug_raca, rv, humano_versatil=humano_versatil
    )
    if extra_lista > 0:
        return extra_lista
    return extra_tracos


def int_extra_vagas_pericias(int_valor: int, regra_versao: Optional[str] = None) -> int:
    """MB: max(0, mod INT). v1.3: valor de INT se positivo, senão 0."""
    rv = normalizar_regra_versao(regra_versao)
    if rv == REGRA_VERSAO_V13:
        v = contribuicao_atributo_t20(int(int_valor), rv)
        return max(0, v)
    return max(0, modificador_atributo_t20(int(int_valor)))


def vagas_pericias_treinadas(
    slug_classe: str,
    int_valor: int,
    slug_raca: Optional[str] = None,
    regra_versao: Optional[str] = None,
    *,
    humano_versatil: Optional[str] = None,
) -> Optional[int]:
    rv = normalizar_regra_versao(regra_versao)
    extra_int = int_extra_vagas_pericias(int_valor, rv)
    extra = pericias_treinadas_extra_raca(
        slug_raca or "", rv, humano_versatil=humano_versatil
    )
    if rv == REGRA_VERSAO_V13:
        base_cl = vagas_classe_v13(slug_classe)
        if base_cl is None:
            base = pericias_treinadas_base_classe(slug_classe, rv)
            if base is None:
                return None
            return int(base) + extra_int + extra
        return int(base_cl) + extra_int + extra
    base = pericias_treinadas_base_classe(slug_classe, rv)
    if base is None:
        return None
    return int(base) + extra_int + extra


def vagas_pericias_treinadas_mb(
    slug_classe: str,
    int_valor: int,
    slug_raca: Optional[str] = None,
) -> Optional[int]:
    return vagas_pericias_treinadas(slug_classe, int_valor, slug_raca, "mb")


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
    return validar_pericias_ficha(
        nivel=nivel,
        slug_classe=slug_classe,
        int_valor=int_valor,
        slug_raca=slug_raca,
        pericias=pericias,
        regra_versao="mb",
    )


def validar_pericias_ficha_v13(
    *,
    nivel: int,
    slug_classe: str,
    int_valor: int,
    slug_raca: Optional[str],
    pericias: List[Dict[str, Any]],
) -> Tuple[bool, str, Dict[str, Any]]:
    return validar_pericias_ficha(
        nivel=nivel,
        slug_classe=slug_classe,
        int_valor=int_valor,
        slug_raca=slug_raca,
        pericias=pericias,
        regra_versao="v13",
    )


def validar_pericias_ficha(
    *,
    nivel: int,
    slug_classe: str,
    int_valor: int,
    slug_raca: Optional[str],
    pericias: List[Dict[str, Any]],
    regra_versao: Optional[str] = None,
    humano_versatil: Optional[str] = None,
    origem_beneficios: Optional[List[str]] = None,
) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Valida orçamento de perícias treinadas (e graduações MB).
    v1.3: só conta vagas treinadas; graduações MB ignoradas.
    """
    rv = normalizar_regra_versao(regra_versao)
    vagas = vagas_pericias_treinadas(
        slug_classe, int_valor, slug_raca, rv, humano_versatil=humano_versatil
    )
    if vagas is None:
        return True, "", {"ignorado": True, "motivo": "classe_desconhecida"}

    extra_origem = 0
    if rv == REGRA_VERSAO_V13:
        extra_origem = contar_vagas_pericias_extra_origem(origem_beneficios or [])
    vagas_efetivas = vagas + extra_origem if vagas is not None else vagas

    pts_tr, pts_ntr = orcamento_graduacoes_por_nivel(nivel, rv)
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

    edicao = "v1.3" if rv == REGRA_VERSAO_V13 else "MB"
    resumo = {
        "vagas_treinadas": vagas_efetivas,
        "vagas_treinadas_base": vagas,
        "pericias_treinadas_extra_origem": extra_origem,
        "usadas_treinadas": count_tr,
        "pontos_grad_treinadas": pts_tr,
        "gasto_grad_treinadas": sum_grad_tr,
        "pontos_grad_nao_treinadas": pts_ntr,
        "gasto_grad_nao_treinadas": sum_grad_ntr,
        "nivel": int(nivel),
        "classe_slug": str(slug_classe).strip().lower(),
        "regra_versao": rv,
    }

    if count_tr > vagas_efetivas:
        return (
            False,
            f"Perícias treinadas: {count_tr} marcadas, mas o orçamento ({edicao}) é {vagas_efetivas} "
            f"(classe + INT + bônus racial"
            + (f" + origem (+{extra_origem})" if extra_origem else "")
            + ").",
            resumo,
        )
    if rv == REGRA_VERSAO_V13:
        extra_int = int_extra_vagas_pericias(int_valor, rv)
        extra_racial = pericias_treinadas_extra_raca(
            slug_raca or "", rv, humano_versatil=humano_versatil
        )
        ok_cl, motivo_cl, res_cl = validar_pericias_classe_v13(
            slug_classe=slug_classe,
            pericias=lista,
            int_valor=int_valor,
            slug_raca=slug_raca,
            int_extra=extra_int,
            racial_extra=extra_racial,
            origem_extra=extra_origem,
        )
        resumo["pericias_classe"] = res_cl
        if not ok_cl:
            return False, motivo_cl, resumo
    if rv != REGRA_VERSAO_V13:
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


def preview_pericias_criacao(
    *,
    nivel: int,
    slug_classe: str,
    int_valor: int,
    slug_raca: Optional[str] = None,
    pericias: Optional[List[Dict[str, Any]]] = None,
    regra_versao: Optional[str] = None,
    humano_versatil: Optional[str] = None,
    origem_beneficios: Optional[List[str]] = None,
) -> Dict[str, Any]:
    rv = normalizar_regra_versao(regra_versao)
    vagas = vagas_pericias_treinadas(
        slug_classe, int_valor, slug_raca, rv, humano_versatil=humano_versatil
    )
    extra_origem = (
        contar_vagas_pericias_extra_origem(origem_beneficios or [])
        if rv == REGRA_VERSAO_V13
        else 0
    )
    pts_tr, pts_ntr = orcamento_graduacoes_por_nivel(nivel, rv)
    ok, motivo, resumo = validar_pericias_ficha(
        nivel=nivel,
        slug_classe=slug_classe,
        int_valor=int_valor,
        slug_raca=slug_raca,
        pericias=pericias or [],
        regra_versao=rv,
        humano_versatil=humano_versatil,
        origem_beneficios=origem_beneficios,
    )
    ben = beneficio_nivel(nivel, rv)
    contrib_int = int_extra_vagas_pericias(int_valor, rv)
    out = {
        "valido": ok,
        "motivo": motivo,
        "regra_versao": rv,
        "vagas_treinadas": (vagas + extra_origem) if vagas is not None else vagas,
        "vagas_treinadas_base": vagas,
        "pericias_treinadas_extra_origem": extra_origem,
        "pontos_grad_treinadas": pts_tr,
        "pontos_grad_nao_treinadas": pts_ntr,
        "graduacao_pericias_texto": (
            str(ben.get("graduacao_pericias", "")) if ben else ""
        ),
        "mod_int": contrib_int,
        "pericias_treinadas_extra_racial": pericias_treinadas_extra_raca(
            slug_raca or "", rv, humano_versatil=humano_versatil
        ),
        **resumo,
    }
    if rv == REGRA_VERSAO_V13:
        prev_cl = preview_pericias_classe_v13(slug_classe)
        if prev_cl:
            out["pericias_classe_config"] = prev_cl
    return out


def preview_pericias_criacao_mb(
    *,
    nivel: int,
    slug_classe: str,
    int_valor: int,
    slug_raca: Optional[str] = None,
    pericias: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    return preview_pericias_criacao(
        nivel=nivel,
        slug_classe=slug_classe,
        int_valor=int_valor,
        slug_raca=slug_raca,
        pericias=pericias,
        regra_versao="mb",
    )
