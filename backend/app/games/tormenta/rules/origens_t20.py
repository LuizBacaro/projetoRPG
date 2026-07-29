"""Origens Tormenta 20 v1.3 — Tabela 1-19."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.games.tormenta.rules.atributos_t20 import lista_pericias_com_atributo
from app.games.tormenta.rules.pericias_t20 import (
    _normalizar_nome_pericia,
    meta_pericia_por_nome,
)
from app.games.tormenta.rules.regra_versao_t20 import (
    REGRA_VERSAO_V13,
    regra_versao_de_ficha,
)

_DATA = Path(__file__).resolve().parent.parent / "data" / "origens_v13.json"
_DATA_ITENS = Path(__file__).resolve().parent.parent / "data" / "origens_itens_v13.json"
_DATA_HEROIS_ARTON = (
    Path(__file__).resolve().parent.parent / "data" / "origens_herois_arton.json"
)


@lru_cache(maxsize=1)
def _documento_itens() -> Dict[str, Any]:
    if not _DATA_ITENS.is_file():
        return {"itens_por_origem": {}, "escolhas_por_origem": {}}
    return json.loads(_DATA_ITENS.read_text(encoding="utf-8"))


def itens_origem_catalogo_v13(slug: str) -> List[str]:
    s = str(slug or "").strip().lower()
    raw = (_documento_itens().get("itens_por_origem") or {}).get(s) or []
    if not isinstance(raw, list):
        return []
    return [str(x).strip() for x in raw if str(x).strip()]


def escolhas_origem_catalogo_v13(slug: str) -> Optional[Dict[str, Any]]:
    s = str(slug or "").strip().lower()
    cfg = (_documento_itens().get("escolhas_por_origem") or {}).get(s)
    return dict(cfg) if isinstance(cfg, dict) else None


def resolver_itens_origem_v13(
    slug_origem: str, ficha_json: Optional[dict] = None
) -> List[str]:
    """Itens grátis da origem (com escolhas resolvidas)."""
    s = str(slug_origem or "").strip().lower()
    if not s:
        return []
    esc = escolhas_origem_catalogo_v13(s)
    if esc:
        fj = dict(ficha_json or {})
        campo = str(esc.get("campo") or "item")
        opcoes = esc.get("opcoes") or []
        escolha_map = fj.get("origem_itens_escolha") or {}
        pick = ""
        if isinstance(escolha_map, dict):
            pick = (
                str(escolha_map.get(s) or escolha_map.get(campo) or "").strip().lower()
            )
        if not pick:
            pick = str(esc.get("default") or "").strip().lower()
        for op in opcoes:
            if isinstance(op, dict) and str(op.get("slug") or "").lower() == pick:
                return [
                    str(x).strip() for x in (op.get("itens") or []) if str(x).strip()
                ]
        if opcoes and isinstance(opcoes[0], dict):
            return [
                str(x).strip() for x in (opcoes[0].get("itens") or []) if str(x).strip()
            ]
        return []
    return itens_origem_catalogo_v13(s)


@lru_cache(maxsize=1)
def _documento() -> Dict[str, Any]:
    if not _DATA.is_file():
        return {"origens": []}
    return json.loads(_DATA.read_text(encoding="utf-8"))


def lista_origens_v13() -> List[Dict[str, Any]]:
    rows = _documento().get("origens") or []
    out: List[Dict[str, Any]] = []
    if not isinstance(rows, list):
        return out
    for row in rows:
        if not isinstance(row, dict):
            continue
        slug = str(row.get("slug", "")).strip().lower()
        if not slug:
            continue
        out.append(
            {
                "slug": slug,
                "nome": str(row.get("nome", "") or slug).strip(),
                "pagina": int(row.get("pagina", 0) or 0),
                "beneficios_pericias": list(row.get("beneficios_pericias") or []),
                "beneficios_poderes": list(row.get("beneficios_poderes") or []),
                "poder_unico": row.get("poder_unico"),
                "itens": itens_origem_catalogo_v13(slug),
                "itens_escolha": escolhas_origem_catalogo_v13(slug),
            }
        )
    return sorted(out, key=lambda x: x["nome"].lower())


def origem_por_slug(slug: str) -> Optional[Dict[str, Any]]:
    s = str(slug or "").strip().lower()
    if not s:
        return None
    for row in lista_origens_v13():
        if row.get("slug") == s:
            return row
    for row in lista_origens_herois_arton():
        if row.get("slug") == s:
            return row
    return None


# ---------------------------------------------------------------------------
# Heróis de Arton — origens especiais
# ---------------------------------------------------------------------------


@lru_cache(maxsize=1)
def _documento_herois_arton() -> Dict[str, Any]:
    if not _DATA_HEROIS_ARTON.is_file():
        return {"origens": []}
    return json.loads(_DATA_HEROIS_ARTON.read_text(encoding="utf-8"))


def lista_origens_herois_arton() -> List[Dict[str, Any]]:
    """Origens especiais do suplemento Heróis de Arton v1.1 (benefício fixo)."""
    rows = _documento_herois_arton().get("origens") or []
    out: List[Dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        slug = str(row.get("slug", "")).strip().lower()
        if not slug:
            continue
        out.append(
            {
                "slug": slug,
                "nome": str(row.get("nome", "") or slug).strip(),
                "pagina": int(row.get("pagina", 0) or 0),
                "fonte_catalogo": str(
                    row.get("fonte_catalogo") or "herois_arton"
                ).strip(),
                "beneficios_pericias": list(row.get("beneficios_pericias") or []),
                "beneficios_poderes": list(row.get("beneficios_poderes") or []),
                "poderes_escolher": row.get("poderes_escolher"),
                "poder_unico": row.get("poder_unico"),
                "itens": list(row.get("itens") or []),
                "itens_escolha": row.get("itens_escolha"),
                "troca_pericia_treinada": bool(row.get("troca_pericia_treinada")),
                "beneficio_fixo": bool(row.get("beneficio_fixo")),
                "notas": str(row.get("notas") or "").strip(),
                "efeitos": list(row.get("efeitos") or []),
                "habilidades_ativas": list(row.get("habilidades_ativas") or []),
            }
        )
    return sorted(out, key=lambda x: x["nome"].lower())


def habilidade_ativa_origem(
    slug_origem: str, habilidade_id: str
) -> Optional[Dict[str, Any]]:
    """Resolve uma habilidade acionável diretamente no catálogo da origem."""
    origem = origem_por_slug(slug_origem)
    alvo = str(habilidade_id or "").strip().lower()
    if not origem or not alvo:
        return None
    for raw in origem.get("habilidades_ativas") or []:
        if not isinstance(raw, dict):
            continue
        if str(raw.get("id") or "").strip().lower() != alvo:
            continue
        habilidade = dict(raw)
        habilidade["origem_slug"] = str(origem.get("slug") or slug_origem)
        habilidade["origem_nome"] = str(origem.get("nome") or slug_origem)
        habilidade["pagina"] = int(origem.get("pagina") or 0)
        return habilidade
    return None


def lista_origens_com_suplemento(
    suplemento: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Origens core v1.3 + suplemento quando ``suplemento='herois_arton'``."""
    from app.games.tormenta.rules.regra_versao_t20 import SUPLEMENTO_HEROIS_ARTON

    origens = lista_origens_v13()
    if suplemento and str(suplemento).strip().lower() == SUPLEMENTO_HEROIS_ARTON:
        origens = origens + lista_origens_herois_arton()
    return sorted(origens, key=lambda x: str(x.get("nome") or "").lower())


def origem_tem_beneficio_fixo(slug_origem: str) -> bool:
    """Origens de Heróis de Arton concedem um benefício único, sem escolha de 2."""
    orig = origem_por_slug(slug_origem)
    return bool(orig and orig.get("beneficio_fixo"))


def _qtd_poderes_escolher(orig: Dict[str, Any]) -> int:
    poderes = list(orig.get("beneficios_poderes") or [])
    bruto = orig.get("poderes_escolher")
    if bruto is None:
        return len(poderes)
    try:
        return max(0, min(len(poderes), int(bruto)))
    except (TypeError, ValueError):
        return len(poderes)


def beneficios_fixos_origem(slug_origem: str) -> List[str]:
    """Benefícios concedidos automaticamente por uma origem de benefício fixo."""
    orig = origem_por_slug(slug_origem)
    if not orig or not orig.get("beneficio_fixo"):
        return []
    out = [f"pericia:{p}" for p in orig.get("beneficios_pericias") or []]
    poderes = list(orig.get("beneficios_poderes") or [])
    if poderes and _qtd_poderes_escolher(orig) == len(poderes):
        out.extend(f"poder:{p}" for p in poderes)
    return out


def normalizar_beneficios_origem(slug_origem: str, beneficios: Any) -> List[str]:
    """Completa `origem_beneficios` com os benefícios automáticos da origem fixa."""
    atuais = [
        str(b or "").strip().lower()
        for b in (beneficios if isinstance(beneficios, list) else [])
        if str(b or "").strip()
    ]
    if not origem_tem_beneficio_fixo(slug_origem):
        return atuais
    out = list(beneficios_fixos_origem(slug_origem))
    vistos = set(out)
    orig = origem_por_slug(slug_origem) or {}
    opcionais = {f"poder:{p}" for p in orig.get("beneficios_poderes") or []}
    limite = _qtd_poderes_escolher(orig)
    escolhidos = 0
    for b in atuais:
        if b in vistos or b not in opcionais or escolhidos >= limite:
            continue
        out.append(b)
        vistos.add(b)
        escolhidos += 1
    return out


def _validar_beneficios_origem_fixa(
    orig: Dict[str, Any], beneficios: List[str]
) -> tuple[bool, str]:
    nome = str(orig.get("nome") or "").strip() or "Origem"
    informados = {str(b or "").strip().lower() for b in beneficios}
    obrigatorios = set(beneficios_fixos_origem(str(orig.get("slug") or "")))
    faltando = obrigatorios - informados
    if faltando:
        return False, f"{nome}: benefícios automáticos ausentes: {sorted(faltando)}."
    poderes = list(orig.get("beneficios_poderes") or [])
    limite = _qtd_poderes_escolher(orig)
    pool_opcional = {f"poder:{p}" for p in poderes} - obrigatorios
    escolhidos = informados & pool_opcional
    if pool_opcional and len(escolhidos) != limite:
        return (
            False,
            f"{nome}: escolha exatamente {limite} poder(es) entre {sorted(pool_opcional)}.",
        )
    desconhecidos = informados - obrigatorios - pool_opcional
    if desconhecidos:
        return (
            False,
            f"{nome}: benefício inválido para a origem: {sorted(desconhecidos)[0]}",
        )
    return True, ""


def validar_beneficios_origem(
    slug_origem: str, beneficios: List[str]
) -> tuple[bool, str]:
    """Valida os benefícios da origem (2 escolhas no core; conjunto fixo em HA)."""
    orig = origem_por_slug(slug_origem)
    if not orig:
        return False, "Origem desconhecida."
    if orig.get("beneficio_fixo"):
        return _validar_beneficios_origem_fixa(orig, beneficios)
    if len(beneficios) != 2:
        return False, "Escolha exatamente 2 benefícios da origem."
    per_pool = {f"pericia:{p}" for p in orig.get("beneficios_pericias") or []}
    pod_pool = {f"poder:{p}" for p in orig.get("beneficios_poderes") or []}
    pu = orig.get("poder_unico")
    if pu:
        pod_pool.add(f"poder:{pu}")
    pool = per_pool | pod_pool
    for b in beneficios:
        key = str(b or "").strip().lower()
        if key not in pool:
            return False, f"Benefício inválido para a origem: {key}"
    return True, ""


def slugs_pericias_de_beneficios_origem(beneficios: Any) -> List[str]:
    """Extrai slugs de perícia de `origem_beneficios` (`pericia:slug`)."""
    out: List[str] = []
    if not isinstance(beneficios, list):
        return out
    seen: set[str] = set()
    for raw in beneficios:
        key = str(raw or "").strip().lower()
        if not key.startswith("pericia:"):
            continue
        slug = key.split(":", 1)[1].strip().lower()
        if slug and slug not in seen:
            seen.add(slug)
            out.append(slug)
    return out


def contar_vagas_pericias_extra_origem(beneficios: Any) -> int:
    return len(slugs_pericias_de_beneficios_origem(beneficios))


def origem_permite_troca_pericia(slug_origem: str) -> bool:
    orig = origem_por_slug(slug_origem)
    if not orig:
        return False
    return bool(orig.get("troca_pericia_treinada"))


def _normalizar_mapa_trocas_pericia(origem_trocas: Any) -> Dict[str, str]:
    if not isinstance(origem_trocas, dict):
        return {}
    out: Dict[str, str] = {}
    for de, para in origem_trocas.items():
        d = str(de or "").strip().lower()
        p = str(para or "").strip().lower()
        if d and p:
            out[d] = p
    return out


def resolver_pericias_origem_efetivas(
    slug_origem: str,
    beneficios: Any,
    treinados: set[str],
    slug_classe: str,
    origem_trocas: Any = None,
) -> tuple[List[str], Dict[str, Any]]:
    """Resolve slugs de perícia a treinar pela origem (com troca se redundante)."""
    from app.games.tormenta.rules.pericias_classe_t20 import (
        config_pericias_classe_v13,
        universo_pericias_classe,
    )

    beneficio_slugs = slugs_pericias_de_beneficios_origem(beneficios)
    trocas = _normalizar_mapa_trocas_pericia(origem_trocas)
    permite = origem_permite_troca_pericia(slug_origem) if slug_origem else False
    cfg = config_pericias_classe_v13(slug_classe)
    universo = universo_pericias_classe(cfg) if cfg else set()

    efetivas: List[str] = []
    redundantes: List[str] = []
    trocas_aplicadas: Dict[str, str] = {}
    ignoradas: List[str] = []

    for slug in beneficio_slugs:
        redundante = bool(universo and slug in treinados and slug in universo)
        if redundante:
            redundantes.append(slug)
            if permite and slug in trocas:
                para = trocas[slug]
                efetivas.append(para)
                trocas_aplicadas[slug] = para
            else:
                ignoradas.append(slug)
        else:
            efetivas.append(slug)

    meta: Dict[str, Any] = {
        "permite_troca": permite,
        "redundantes": redundantes,
        "efetivas": efetivas,
        "trocas_aplicadas": trocas_aplicadas,
        "ignoradas_redundantes": ignoradas,
        "universo_classe": sorted(universo),
    }
    return efetivas, meta


def contar_vagas_pericias_extra_origem_resolvidas(
    slug_origem: str,
    beneficios: Any,
    treinados: set[str],
    slug_classe: str,
    origem_trocas: Any = None,
) -> int:
    """Vagas extras de origem após resolver trocas (redundante sem troca não conta)."""
    efetivas, _ = resolver_pericias_origem_efetivas(
        slug_origem,
        beneficios,
        treinados,
        slug_classe,
        origem_trocas,
    )
    return len(efetivas)


def validar_trocas_pericia_origem(
    slug_origem: str,
    beneficios: Any,
    origem_trocas: Any,
    slug_classe: str,
    pericias: Any,
) -> tuple[bool, str]:
    """Valida mapa ``origem_trocas_pericia`` para origens Heróis de Arton."""
    from app.games.tormenta.rules.pericias_classe_t20 import (
        config_pericias_classe_v13,
        slugs_pericias_treinadas,
        universo_pericias_classe,
    )

    if not slug_origem:
        return True, ""

    beneficio_slugs = slugs_pericias_de_beneficios_origem(beneficios)
    if not beneficio_slugs:
        return True, ""

    trocas = _normalizar_mapa_trocas_pericia(origem_trocas)
    permite = origem_permite_troca_pericia(slug_origem)
    if trocas and not permite:
        return False, "Esta origem não permite trocar perícia já treinada."

    for de in trocas:
        if de not in beneficio_slugs:
            return (
                False,
                f"Troca inválida: '{de}' não é um benefício de perícia escolhido.",
            )

    treinados = slugs_pericias_treinadas(
        pericias if isinstance(pericias, list) else [],
        REGRA_VERSAO_V13,
    )
    efetivas, meta = resolver_pericias_origem_efetivas(
        slug_origem,
        beneficios,
        treinados,
        slug_classe,
        trocas,
    )
    cfg = config_pericias_classe_v13(slug_classe)
    universo = universo_pericias_classe(cfg) if cfg else set()

    for slug in beneficio_slugs:
        if slug not in trocas:
            continue
        if not (universo and slug in treinados and slug in universo):
            return (
                False,
                f"Troca de '{slug.replace('_', ' ')}' só é permitida quando "
                "a perícia já está treinada pela classe.",
            )
        para = trocas[slug]
        if para == slug:
            return False, "A perícia de troca deve ser diferente da original."
        if cfg and para not in universo:
            return (
                False,
                f"Perícia de troca '{para.replace('_', ' ')}' deve ser da "
                "lista de perícias de classe.",
            )
        if para in treinados:
            return (
                False,
                f"Perícia de troca '{para.replace('_', ' ')}' já está treinada.",
            )

    if len(efetivas) != len(set(efetivas)):
        return False, "Perícias efetivas da origem não podem se repetir."

    if meta.get("ignoradas_redundantes") and permite:
        # Redundante sem troca: permitido (benefício não gera vaga extra).
        pass

    return True, ""


def _linha_pericia_padrao(meta: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "nome": str(meta.get("nome", "") or "").strip(),
        "treinado": False,
        "graduacao": 0,
        "outros": 0,
        "somente_treinado": bool(meta.get("somente_treinado")),
        "penalidade_armadura": bool(meta.get("penalidade_armadura")),
    }


def aplicar_pericias_origem_em_lista(
    pericias: Any,
    beneficios: Any,
    *,
    regra_versao: str = REGRA_VERSAO_V13,
    slug_origem: Optional[str] = None,
    slug_classe: Optional[str] = None,
    origem_trocas: Any = None,
) -> List[Dict[str, Any]]:
    """Marca treinado=true nas perícias efetivas do benefício de origem v1.3."""
    from app.games.tormenta.rules.pericias_classe_t20 import slugs_pericias_treinadas

    lista: List[Dict[str, Any]] = (
        [dict(p) for p in pericias if isinstance(p, dict)]
        if isinstance(pericias, list)
        else []
    )
    beneficio_slugs = slugs_pericias_de_beneficios_origem(beneficios)
    if not beneficio_slugs:
        return lista

    treinados = slugs_pericias_treinadas(lista, regra_versao)
    if slug_origem and slug_classe:
        slugs, _ = resolver_pericias_origem_efetivas(
            slug_origem,
            beneficios,
            treinados,
            slug_classe,
            origem_trocas,
        )
    else:
        slugs = beneficio_slugs

    norm_to_idx: Dict[str, int] = {}
    for i, row in enumerate(lista):
        n = _normalizar_nome_pericia(str(row.get("nome", "")))
        if n:
            norm_to_idx[n] = i

    for slug in slugs:
        meta = meta_pericia_por_nome(slug, regra_versao)
        if not meta:
            for row in lista_pericias_com_atributo(regra_versao):
                if str(row.get("slug", "")).lower() == slug:
                    meta = row
                    break
        if not meta:
            continue
        nome = str(meta.get("nome", "") or "").strip()
        key = _normalizar_nome_pericia(nome)
        if not key:
            continue
        if key in norm_to_idx:
            lista[norm_to_idx[key]]["treinado"] = True
        else:
            row = _linha_pericia_padrao(meta)
            row["treinado"] = True
            lista.append(row)
            norm_to_idx[key] = len(lista) - 1
    return lista


def sincronizar_pericias_origem_ficha_json(
    ficha_json: Dict[str, Any]
) -> Dict[str, Any]:
    """Aplica benefícios de origem v1.3 em `ficha_json.pericias`."""
    fj = dict(ficha_json or {})
    if regra_versao_de_ficha(fj) != REGRA_VERSAO_V13:
        return fj
    slug_origem_atual = str(fj.get("origem_slug") or "").strip().lower()
    if origem_tem_beneficio_fixo(slug_origem_atual):
        fj["origem_beneficios"] = normalizar_beneficios_origem(
            slug_origem_atual, fj.get("origem_beneficios")
        )
    beneficios = fj.get("origem_beneficios")
    if not slugs_pericias_de_beneficios_origem(beneficios):
        return fj
    fj["pericias"] = aplicar_pericias_origem_em_lista(
        fj.get("pericias"),
        beneficios,
        regra_versao=REGRA_VERSAO_V13,
        slug_origem=str(fj.get("origem_slug") or "").strip().lower() or None,
        slug_classe=str(fj.get("tormenta_classe_mb_slug") or "").strip().lower()
        or None,
        origem_trocas=fj.get("origem_trocas_pericia"),
    )
    return fj
