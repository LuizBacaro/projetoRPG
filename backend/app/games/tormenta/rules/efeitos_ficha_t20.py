"""Motor de efeitos estruturados na ficha Tormenta 20 (origem, poder, item, relíquia)."""

from __future__ import annotations

import json
import re
import unicodedata
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from app.games.tormenta.rules.origens_t20 import origem_por_slug
from app.games.tormenta.rules.poderes_herois_arton_t20 import poder_por_slug

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_EQUIP_HA_JSON = _DATA_DIR / "equipamentos_herois_arton.json"
_MAGICOS_HA_JSON = _DATA_DIR / "itens_magicos_herois_arton.json"

ALVOS_VALIDOS: Set[str] = {
    "pericia",
    "pv_max",
    "pm_max",
    "defesa",
    "resistencia",
    "iniciativa",
    "carga_espacos",
    "rd",
    "rm",
    "ataque",
    "dano",
    "margem_ameaca",
    "deslocamento_m",
    "penalidade_armadura",
}

QUANDO_VALIDOS: Set[str] = {
    "sempre",
    "condicional",
    "ativo_pm",
    "em_cidade",
    "conduzindo_veiculo",
    "armadura_pesada",
    "arma_duas_maos",
    "arma_martelo_marreta",
    "arma_impacto",
    "grupo_mesmo_poder",
    "vs_criaturas_menores",
    "vs_mortos_vivos",
    "vs_feridos",
    "empunhado",
    "vestido",
}

OPS_VALIDOS: Set[str] = {"soma", "max", "set"}


def _norm_slug(texto: str) -> str:
    s = unicodedata.normalize("NFKD", str(texto or ""))
    s = s.encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "_", s).strip("_")


def _norm_pericia_slug(nome: str) -> str:
    return _norm_slug(nome).replace("_", "")


def normalizar_efeito(
    raw: Dict[str, Any],
    *,
    fonte_tipo: str,
    fonte_slug: str,
    fonte_nome: str = "",
) -> Optional[Dict[str, Any]]:
    if not isinstance(raw, dict):
        return None
    alvo = str(raw.get("alvo") or "").strip().lower()
    if alvo not in ALVOS_VALIDOS:
        return None
    op = str(raw.get("op") or "soma").strip().lower()
    if op not in OPS_VALIDOS:
        op = "soma"
    quando = str(raw.get("quando") or "sempre").strip().lower()
    if quando not in QUANDO_VALIDOS:
        quando = "sempre"
    try:
        valor = int(raw.get("valor") or 0)
    except (TypeError, ValueError):
        valor = 0
    eid = str(raw.get("id") or f"{fonte_slug}_{alvo}_{valor}").strip()
    rotulo = str(raw.get("rotulo") or "").strip()
    if not rotulo:
        rotulo = f"{fonte_nome or fonte_slug}: {alvo}"
    out: Dict[str, Any] = {
        "id": eid[:80],
        "alvo": alvo,
        "op": op,
        "valor": valor,
        "quando": quando,
        "rotulo": rotulo[:200],
        "desvantagem": bool(raw.get("desvantagem")),
        "fonte_tipo": fonte_tipo,
        "fonte_slug": fonte_slug,
        "fonte_nome": fonte_nome or fonte_slug,
    }
    if raw.get("pagina") is not None:
        out["pagina"] = int(raw.get("pagina") or 0)
    if alvo == "pericia":
        ps = str(raw.get("pericia_slug") or raw.get("pericia") or "").strip().lower()
        if ps:
            out["pericia_slug"] = _norm_slug(ps)
    if alvo == "resistencia":
        rs = str(raw.get("resistencia") or raw.get("tipo") or "todas").strip().lower()
        out["resistencia"] = rs
    if alvo == "rd":
        rt = str(raw.get("rd_tipo") or raw.get("tipo") or "todos").strip().lower()
        out["rd_tipo"] = rt
    if raw.get("uso_id"):
        out["uso_id"] = str(raw.get("uso_id")).strip().lower()
    if raw.get("condicao"):
        out["condicao"] = str(raw.get("condicao")).strip()
    return out


def _efeitos_de_lista(
    efeitos: Any,
    *,
    fonte_tipo: str,
    fonte_slug: str,
    fonte_nome: str = "",
) -> List[Dict[str, Any]]:
    if not isinstance(efeitos, list):
        return []
    out: List[Dict[str, Any]] = []
    for raw in efeitos:
        if not isinstance(raw, dict):
            continue
        norm = normalizar_efeito(
            raw,
            fonte_tipo=fonte_tipo,
            fonte_slug=fonte_slug,
            fonte_nome=fonte_nome,
        )
        if norm:
            out.append(norm)
    return out


@lru_cache(maxsize=1)
def _mapa_equip_ha_por_nome() -> Dict[str, Dict[str, Any]]:
    if not _EQUIP_HA_JSON.is_file():
        return {}
    data = json.loads(_EQUIP_HA_JSON.read_text(encoding="utf-8"))
    rows = data.get("itens") or []
    out: Dict[str, Dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        nome = str(row.get("nome") or "").strip()
        if nome:
            out[_norm_slug(nome)] = dict(row)
    return out


@lru_cache(maxsize=1)
def _mapa_magicos_ha_por_nome() -> Dict[str, Dict[str, Any]]:
    if not _MAGICOS_HA_JSON.is_file():
        return {}
    data = json.loads(_MAGICOS_HA_JSON.read_text(encoding="utf-8"))
    rows = data.get("itens") or []
    out: Dict[str, Dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        nome = str(row.get("nome") or "").strip()
        if nome:
            out[_norm_slug(nome)] = dict(row)
    return out


def efeitos_de_origem(slug_origem: str) -> List[Dict[str, Any]]:
    orig = origem_por_slug(slug_origem)
    if not orig:
        return []
    return _efeitos_de_lista(
        orig.get("efeitos"),
        fonte_tipo="origem",
        fonte_slug=str(orig.get("slug") or slug_origem),
        fonte_nome=str(orig.get("nome") or ""),
    )


def efeitos_de_poder(slug_poder: str) -> List[Dict[str, Any]]:
    row = poder_por_slug(slug_poder)
    if not row:
        return []
    return _efeitos_de_lista(
        row.get("efeitos"),
        fonte_tipo="poder",
        fonte_slug=str(row.get("slug") or slug_poder),
        fonte_nome=str(row.get("nome") or ""),
    )


def efeitos_de_item_catalogo(nome: str) -> List[Dict[str, Any]]:
    chave = _norm_slug(nome)
    row = _mapa_equip_ha_por_nome().get(chave) or _mapa_magicos_ha_por_nome().get(chave)
    if not row:
        return []
    slug = str(row.get("slug") or chave)
    return _efeitos_de_lista(
        row.get("efeitos"),
        fonte_tipo="equipamento",
        fonte_slug=slug,
        fonte_nome=str(row.get("nome") or nome),
    )


def _slugs_poderes_ficha(ficha_json: Dict[str, Any]) -> List[str]:
    slugs: List[str] = []
    seen: Set[str] = set()
    for key in (
        "poderes_slugs",
        "talentos_slugs",
    ):
        raw = ficha_json.get(key)
        if isinstance(raw, list):
            for s in raw:
                slug = _norm_slug(s)
                if slug and slug not in seen:
                    seen.add(slug)
                    slugs.append(slug)
    return slugs


def _contexto_ativo(
    quando: str,
    contexto: Optional[Dict[str, Any]],
) -> bool:
    if quando == "sempre":
        return True
    if quando == "ativo_pm":
        return False
    ctx = dict(contexto or {})
    flags = ctx.get("flags") or {}
    if isinstance(flags, dict) and flags.get(quando):
        return True
    if quando == "em_cidade" and ctx.get("em_cidade"):
        return True
    if quando == "conduzindo_veiculo" and ctx.get("conduzindo_veiculo"):
        return True
    if quando == "armadura_pesada" and ctx.get("armadura_pesada"):
        return True
    if quando == "arma_duas_maos" and ctx.get("arma_duas_maos"):
        return True
    if quando == "arma_martelo_marreta" and ctx.get("arma_martelo_marreta"):
        return True
    if quando == "arma_impacto" and ctx.get("arma_impacto"):
        return True
    if quando == "vs_feridos" and ctx.get("vs_feridos"):
        return True
    if quando == "vs_criaturas_menores" and ctx.get("vs_criaturas_menores"):
        return True
    if quando == "vs_mortos_vivos" and ctx.get("vs_mortos_vivos"):
        return True
    if quando == "condicional":
        return bool(ctx.get("condicional_ativo"))
    return False


def _aplicar_valor(
    totais: Dict[str, Any],
    efeito: Dict[str, Any],
) -> None:
    alvo = efeito["alvo"]
    op = efeito.get("op") or "soma"
    valor = int(efeito.get("valor") or 0)
    if alvo == "pericia":
        ps = str(efeito.get("pericia_slug") or "").strip().lower()
        if not ps:
            return
        per_map = totais.setdefault("pericias", {})
        if op == "set":
            per_map[ps] = valor
        else:
            per_map[ps] = int(per_map.get(ps, 0)) + valor
        return
    if alvo == "resistencia":
        rs = str(efeito.get("resistencia") or "todas").lower()
        res_map = totais.setdefault("resistencias", {})
        if op == "set":
            res_map[rs] = valor
        else:
            res_map[rs] = int(res_map.get(rs, 0)) + valor
        return
    if alvo == "rd":
        rt = str(efeito.get("rd_tipo") or "todos").lower()
        rd_map = totais.setdefault("rd", {})
        if op == "set":
            rd_map[rt] = valor
        else:
            rd_map[rt] = int(rd_map.get(rt, 0)) + valor
        return
    if op == "set":
        totais[alvo] = valor
    elif op == "max":
        totais[alvo] = max(int(totais.get(alvo, 0)), valor)
    else:
        totais[alvo] = int(totais.get(alvo, 0)) + valor


def agregar_efeitos_ficha(
    ficha_json: Dict[str, Any],
    *,
    poderes_slugs: Optional[List[str]] = None,
    contexto: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Agrega efeitos de origem, poderes e itens equipados/vestidos.
    Retorna fontes (auditoria), totais (sempre + condicionais ativos) e condicionais pendentes.
    """
    fj = dict(ficha_json or {})
    ctx = dict(contexto or {})
    fontes: List[Dict[str, Any]] = []
    condicionais: List[Dict[str, Any]] = []
    ativos: List[Dict[str, Any]] = []
    totais: Dict[str, Any] = {
        "pv_max": 0,
        "pm_max": 0,
        "defesa": 0,
        "iniciativa": 0,
        "carga_espacos": 0,
        "rm": 0,
        "deslocamento_m": 0,
        "penalidade_armadura": 0,
        "margem_ameaca": 0,
        "ataque": 0,
        "dano": 0,
        "pericias": {},
        "resistencias": {},
        "rd": {},
    }

    def _processar(efeitos: List[Dict[str, Any]]) -> None:
        for ef in efeitos:
            quando = str(ef.get("quando") or "sempre")
            if quando == "ativo_pm":
                ativos.append(ef)
                fontes.append(dict(ef))
                continue
            if _contexto_ativo(quando, ctx):
                _aplicar_valor(totais, ef)
                fontes.append(dict(ef))
            elif quando != "sempre":
                condicionais.append(dict(ef))

    slug_origem = str(fj.get("origem_slug") or "").strip().lower()
    if slug_origem:
        _processar(efeitos_de_origem(slug_origem))
        origem = origem_por_slug(slug_origem)
        if origem:
            for habilidade in origem.get("habilidades_ativas") or []:
                if not isinstance(habilidade, dict) or not habilidade.get("id"):
                    continue
                ativos.append(
                    {
                        **dict(habilidade),
                        "tipo_ativo": "habilidade_origem",
                        "fonte_tipo": "origem",
                        "fonte_slug": slug_origem,
                        "fonte_nome": str(origem.get("nome") or slug_origem),
                        "pagina": int(origem.get("pagina") or 0),
                    }
                )

    slugs_poder = list(poderes_slugs or []) or _slugs_poderes_ficha(fj)
    for ps in slugs_poder:
        _processar(efeitos_de_poder(ps))

    for arm in fj.get("armaduras_protecao") or []:
        if not isinstance(arm, dict):
            continue
        nome = str(arm.get("nome") or "").strip()
        if nome:
            _processar(efeitos_de_item_catalogo(nome))

    for rel in fj.get("reliquias") or []:
        if not isinstance(rel, dict):
            continue
        nome = str(rel.get("nome") or "").strip()
        if nome:
            _processar(efeitos_de_item_catalogo(nome))

    for eq in fj.get("equipamentos_vestidos") or []:
        if not isinstance(eq, dict):
            continue
        nome = str(eq.get("nome") or "").strip()
        if nome:
            _processar(efeitos_de_item_catalogo(nome))

    return {
        "fontes": fontes,
        "totais": totais,
        "condicionais": condicionais,
        "ativos": ativos,
    }


def bonus_pericia_de_efeitos(
    pericia_slug: str,
    agregado: Dict[str, Any],
) -> int:
    ps = _norm_slug(pericia_slug)
    per_map = (agregado.get("totais") or {}).get("pericias") or {}
    return int(per_map.get(ps, 0) or 0)


def habilidades_ativas_de_origem(slug_origem: str) -> List[Dict[str, Any]]:
    orig = origem_por_slug(slug_origem)
    if not orig:
        return []
    raw = orig.get("habilidades_ativas") or []
    if not isinstance(raw, list):
        return []
    out: List[Dict[str, Any]] = []
    for row in raw:
        if isinstance(row, dict) and row.get("nome"):
            out.append(dict(row))
    return out
