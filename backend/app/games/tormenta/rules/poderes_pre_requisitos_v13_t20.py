"""Validação de pré-requisitos de poderes v1.3 (RF-T08g)."""

from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from app.games.tormenta.rules.conjuracao_t20 import lista_regras_conjuracao_por_versao
from app.games.tormenta.rules.pericias_t20 import meta_pericia_por_nome
from app.games.tormenta.rules.proficiencia_arma_t20 import proficiencias_arma_classe
from app.games.tormenta.rules.regra_versao_t20 import (
    REGRA_VERSAO_V13,
    normalizar_regra_versao,
    regra_versao_de_ficha,
)

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_OVERLAY_JSON = _DATA_DIR / "poderes_pre_requisitos_v13_overlay.json"

_ATTR_ALIASES = {
    "for": "for",
    "forca": "for",
    "des": "des",
    "destreza": "des",
    "con": "con",
    "constituicao": "con",
    "int": "int",
    "inteligencia": "int",
    "sab": "sab",
    "sabedoria": "sab",
    "car": "car",
    "carisma": "car",
}

_ATTR_LABEL = {
    "for": "Força",
    "des": "Destreza",
    "con": "Constituição",
    "int": "Inteligência",
    "sab": "Sabedoria",
    "car": "Carisma",
}


def _norm_nome(texto: str) -> str:
    s = unicodedata.normalize("NFKD", str(texto or ""))
    s = s.encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "_", s).strip("_")


_ATTR_RE = re.compile(
    r"\b(for(?:ca)?|des(?:treza)?|con(?:stituicao)?|int(?:eligencia)?|"
    r"sab(?:edoria)?|car(?:isma)?)\s*([+-]?\d+)\b",
    re.IGNORECASE,
)


@dataclass
class PersonagemPoderContext:
    """Snapshot do personagem para validar pré-requisitos de poder."""

    nivel: int = 1
    for_valor: int = 0
    des_valor: int = 0
    con_valor: int = 0
    int_valor: int = 0
    sab_valor: int = 0
    car_valor: int = 0
    ficha_json: Dict[str, Any] = field(default_factory=dict)
    poderes_nomes: List[str] = field(default_factory=list)
    regra_versao: str = REGRA_VERSAO_V13

    def valor_atributo(self, chave: str) -> int:
        m = {
            "for": self.for_valor,
            "des": self.des_valor,
            "con": self.con_valor,
            "int": self.int_valor,
            "sab": self.sab_valor,
            "car": self.car_valor,
        }
        return int(m.get(str(chave or "").lower(), 0))


@lru_cache(maxsize=1)
def _overlay_pre_requisitos_v13() -> Dict[str, List[Dict[str, Any]]]:
    if not _OVERLAY_JSON.is_file():
        return {}
    raw = json.loads(_OVERLAY_JSON.read_text(encoding="utf-8"))
    out: Dict[str, List[Dict[str, Any]]] = {}
    for k, v in (raw.get("overlay_por_nome") or {}).items():
        if isinstance(v, list):
            out[_norm_nome(str(k))] = [dict(x) for x in v if isinstance(x, dict)]
    return out


def _valor_atributo_minimo_bruto(valor_bruto: int, regra_versao: str) -> int:
    """Converte mínimo em texto MB (8–18) para escala v1.3 quando aplicável."""
    v = int(valor_bruto)
    if normalizar_regra_versao(regra_versao) == REGRA_VERSAO_V13 and v >= 8:
        return v - 10
    return v


def _parse_pre_requisitos_texto(
    texto: str,
    *,
    regra_versao: str,
) -> List[Dict[str, Any]]:
    """Fallback: interpreta `prerequisitos` legado do catálogo MB."""
    t = str(texto or "").strip()
    if not t or t in ("—", "-", "n/a", "na"):
        return []
    tl = t.lower()
    out: List[Dict[str, Any]] = []
    if "conjurar magias" in tl or "capacidade de conjurar" in tl:
        out.append({"tipo": "conjura_magias"})
    if "proficiência com a arma" in tl or "proficiencia com a arma" in tl:
        out.append({"tipo": "proficiencia_arma"})
    for m in _ATTR_RE.finditer(t):
        ch_raw = m.group(1).lower()
        ch = _ATTR_ALIASES.get(ch_raw[:3], _ATTR_ALIASES.get(ch_raw))
        if not ch:
            continue
        try:
            val = int(m.group(2))
        except (TypeError, ValueError):
            continue
        out.append(
            {
                "tipo": "atributo_min",
                "atributo": ch,
                "valor": _valor_atributo_minimo_bruto(val, regra_versao),
            }
        )
    return out


def pre_requisitos_de_poder(
    row: Optional[Dict[str, Any]],
    *,
    regra_versao: str = REGRA_VERSAO_V13,
) -> List[Dict[str, Any]]:
    """Lista estruturada de pré-requisitos para um item de catálogo."""
    if not row:
        return []
    rv = normalizar_regra_versao(regra_versao)
    if rv != REGRA_VERSAO_V13:
        return []
    structured = row.get("pre_requisitos_v13")
    if isinstance(structured, list) and structured:
        return [dict(x) for x in structured if isinstance(x, dict)]
    nome = _norm_nome(str(row.get("nome") or ""))
    overlay = _overlay_pre_requisitos_v13().get(nome)
    if overlay:
        return [dict(x) for x in overlay]
    return _parse_pre_requisitos_texto(
        str(row.get("prerequisitos") or ""),
        regra_versao=rv,
    )


def pre_requisitos_por_nome_poder(
    nome: str,
    *,
    regra_versao: str = REGRA_VERSAO_V13,
) -> List[Dict[str, Any]]:
    n = str(nome or "").strip()
    if not n:
        return []
    from app.games.tormenta.rules.poderes_catalogo_v13_t20 import (
        mapa_catalogo_poderes_por_nome,
    )

    m = mapa_catalogo_poderes_por_nome()
    row = m.get(_norm_nome(n)) or m.get(n.lower())
    return pre_requisitos_de_poder(row, regra_versao=regra_versao)


def _poderes_normalizados(ctx: PersonagemPoderContext) -> set[str]:
    out: set[str] = set()
    for raw in ctx.poderes_nomes or []:
        s = str(raw or "").strip()
        if not s:
            continue
        out.add(_norm_nome(s))
        out.add(s.lower())
    return out


def _pericia_treinada(ctx: PersonagemPoderContext, slug_ou_nome: str) -> bool:
    meta = meta_pericia_por_nome(slug_ou_nome, regra_versao=ctx.regra_versao)
    alvo_slug = str(meta.get("slug") or slug_ou_nome).strip().lower()
    alvo_nome = str(meta.get("nome") or slug_ou_nome).strip().lower()
    for row in ctx.ficha_json.get("pericias") or []:
        if not isinstance(row, dict):
            continue
        nome = str(row.get("nome") or row.get("slug") or "").strip().lower()
        slug = str(row.get("slug") or nome).strip().lower()
        if nome != alvo_nome and slug != alvo_slug:
            continue
        if row.get("treinado") is True:
            return True
        grad = row.get("graduacao")
        if grad is not None:
            try:
                if int(grad) > 0:
                    return True
            except (TypeError, ValueError):
                pass
    return False


def _classes_conjuradoras_v13() -> set[str]:
    return {
        str(r.get("slug", "")).strip().lower()
        for r in lista_regras_conjuracao_por_versao(REGRA_VERSAO_V13)
        if str(r.get("modo_conjuracao", "")).lower() != "nao_conjura"
    }


def _personagem_conjura_magias(ctx: PersonagemPoderContext) -> bool:
    fj = ctx.ficha_json or {}
    if fj.get("tormenta_conjuracao_manual_mb") is True:
        return True
    conj_classes = _classes_conjuradoras_v13()
    slug = str(fj.get("tormenta_classe_mb_slug") or "").strip().lower()
    if slug in conj_classes:
        ini = 1
        for row in lista_regras_conjuracao_por_versao(REGRA_VERSAO_V13):
            if str(row.get("slug", "")).lower() == slug:
                ini = int(row.get("conjuracao_inicia_nivel", 1) or 1)
                break
        if int(ctx.nivel or 1) >= ini:
            return True
    linhas = fj.get("multiclasse_v13")
    if isinstance(linhas, list):
        for ln in linhas:
            if not isinstance(ln, dict):
                continue
            s = str(ln.get("slug") or ln.get("classe_slug") or "").strip().lower()
            nv = int(ln.get("nivel") or 0)
            if s in conj_classes and nv >= 1:
                return True
    magias = fj.get("magias_texto") or fj.get("magias_mb_lista")
    if isinstance(magias, list) and magias:
        return True
    if isinstance(magias, str) and magias.strip():
        return True
    return False


def _tem_proficiencia_arma(ctx: PersonagemPoderContext) -> bool:
    fj = ctx.ficha_json or {}
    slug = str(fj.get("tormenta_classe_mb_slug") or "").strip().lower()
    prof = proficiencias_arma_classe(slug or None)
    if prof.get("simples") or prof.get("marcial"):
        return True
    poderes = _poderes_normalizados(ctx)
    for chave in (
        "usar_armas_simples_e_marciais",
        "usar_armas_simples",
        "usar_armas_marciais",
        "proficiencia",
    ):
        if chave in poderes:
            return True
    for raw in ctx.poderes_nomes:
        rl = str(raw or "").lower()
        if "usar armas" in rl or "proficiência" in rl or "proficiencia" in rl:
            return True
    return False


def _falta_descricao(req: Dict[str, Any], ctx: PersonagemPoderContext) -> str:
    tipo = str(req.get("tipo") or "").strip().lower()
    if tipo == "atributo_min":
        ch = str(req.get("atributo") or "").lower()
        min_v = int(req.get("valor") or 0)
        atual = ctx.valor_atributo(ch)
        label = _ATTR_LABEL.get(ch, ch.upper())
        return f"{label} {min_v}+ (atual {atual})"
    if tipo == "nivel_min":
        min_v = int(req.get("valor") or 0)
        return f"nível {min_v}+ (atual {int(ctx.nivel or 1)})"
    if tipo == "pericia_treinada":
        slug = str(req.get("slug") or req.get("nome") or "").strip()
        meta = meta_pericia_por_nome(slug, regra_versao=ctx.regra_versao)
        return f"perícia treinada: {meta.get('nome') or slug}"
    if tipo == "poder":
        slug = str(req.get("slug") or "").strip()
        nome = slug.replace("_", " ").title()
        return f"poder: {nome}"
    if tipo == "conjura_magias":
        return "capacidade de conjurar magias"
    if tipo == "proficiencia_arma":
        return "proficiência com armas"
    return str(req.get("descricao") or tipo or "pré-requisito")


def _atende_requisito(req: Dict[str, Any], ctx: PersonagemPoderContext) -> bool:
    tipo = str(req.get("tipo") or "").strip().lower()
    if tipo == "atributo_min":
        ch = str(req.get("atributo") or "").lower()
        min_v = int(req.get("valor") or 0)
        return ctx.valor_atributo(ch) >= min_v
    if tipo == "nivel_min":
        return int(ctx.nivel or 1) >= int(req.get("valor") or 0)
    if tipo == "pericia_treinada":
        slug = str(req.get("slug") or req.get("nome") or "").strip()
        return _pericia_treinada(ctx, slug)
    if tipo == "poder":
        slug = _norm_nome(str(req.get("slug") or ""))
        poderes = _poderes_normalizados(ctx)
        if slug in poderes:
            return True
        alvo_nome = str(req.get("nome") or "").strip()
        return _norm_nome(alvo_nome) in poderes if alvo_nome else False
    if tipo == "conjura_magias":
        return _personagem_conjura_magias(ctx)
    if tipo == "proficiencia_arma":
        return _tem_proficiencia_arma(ctx)
    return True


def validar_pre_requisitos_poder(
    nome_poder: str,
    ctx: PersonagemPoderContext,
    *,
    incluir_poder_candidato: bool = False,
) -> Dict[str, Any]:
    """
    Valida se o personagem atende pré-requisitos do poder.
    Retorna {valido, faltando[], pre_requisitos[]}.
    """
    rv = normalizar_regra_versao(ctx.regra_versao)
    if rv != REGRA_VERSAO_V13:
        return {"valido": True, "faltando": [], "pre_requisitos": []}

    from app.games.tormenta.rules.poderes_catalogo_v13_t20 import (
        mapa_catalogo_poderes_por_nome,
    )

    m = mapa_catalogo_poderes_por_nome()
    n = str(nome_poder or "").strip()
    row = m.get(_norm_nome(n)) or m.get(n.lower())
    reqs = pre_requisitos_de_poder(row, regra_versao=rv)
    if not reqs:
        return {"valido": True, "faltando": [], "pre_requisitos": []}

    ctx_val = ctx
    if incluir_poder_candidato:
        ctx_val = PersonagemPoderContext(
            nivel=ctx.nivel,
            for_valor=ctx.for_valor,
            des_valor=ctx.des_valor,
            con_valor=ctx.con_valor,
            int_valor=ctx.int_valor,
            sab_valor=ctx.sab_valor,
            car_valor=ctx.car_valor,
            ficha_json=dict(ctx.ficha_json or {}),
            poderes_nomes=list(ctx.poderes_nomes or []) + [n],
            regra_versao=ctx.regra_versao,
        )

    faltando: List[Dict[str, str]] = []
    for req in reqs:
        if not _atende_requisito(req, ctx_val):
            faltando.append(
                {
                    "tipo": str(req.get("tipo") or ""),
                    "descricao": _falta_descricao(req, ctx_val),
                }
            )
    return {
        "valido": len(faltando) == 0,
        "faltando": faltando,
        "pre_requisitos": reqs,
    }


def contexto_poder_de_personagem(
    personagem: Any,
    *,
    poderes_nomes_extra: Optional[Sequence[str]] = None,
) -> PersonagemPoderContext:
    """Monta contexto a partir de `TormentaPersonagem` + vínculos SQL."""
    fj = personagem.ficha_json if isinstance(personagem.ficha_json, dict) else {}
    nomes: List[str] = list(poderes_nomes_extra or [])
    talentos = getattr(personagem, "_poderes_nomes_cache", None)
    if isinstance(talentos, list):
        nomes.extend(talentos)
    return PersonagemPoderContext(
        nivel=int(getattr(personagem, "nivel", 1) or 1),
        for_valor=int(getattr(personagem, "for_valor", 0) or 0),
        des_valor=int(getattr(personagem, "des_valor", 0) or 0),
        con_valor=int(getattr(personagem, "con_valor", 0) or 0),
        int_valor=int(getattr(personagem, "int_valor", 0) or 0),
        sab_valor=int(getattr(personagem, "sab_valor", 0) or 0),
        car_valor=int(getattr(personagem, "car_valor", 0) or 0),
        ficha_json=fj,
        poderes_nomes=nomes,
        regra_versao=regra_versao_de_ficha(fj),
    )


def deve_validar_pre_requisitos_v13(
    *,
    regra_versao: str,
    notas: Optional[str],
) -> bool:
    if normalizar_regra_versao(regra_versao) != REGRA_VERSAO_V13:
        return False
    n = str(notas or "").strip()
    if n.startswith("auto:v13:"):
        return False
    return True
