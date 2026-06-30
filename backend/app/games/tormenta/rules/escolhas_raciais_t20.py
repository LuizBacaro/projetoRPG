"""Escolhas raciais v1.3 — Lefou, Qareen, Dahllan, Golem, Kliren, Osteon, Sereia, Sílfide (RF-T02-v13)."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from app.games.tormenta.rules.regra_versao_t20 import (
    REGRA_VERSAO_V13,
    normalizar_regra_versao,
)

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_ESCOLHAS_JSON = _DATA_DIR / "escolhas_raciais_v13.json"

_TIPO_FLAGS: Dict[str, str] = {
    "deformidade": "escolhe_lefou_deformidade",
    "ascendencia_magia": "escolhe_qareen_ascendencia",
    "magias_fixas": "magias_inatas_v13",
    "memoria_postuma": "escolhe_osteon_memoria",
}

_TIPO_SLUG_FLAGS: Dict[Tuple[str, str], str] = {
    ("magias_escolha", "sereia_tritao"): "escolhe_sereia_magias",
    ("magias_escolha", "silfide"): "escolhe_silfide_magias",
    ("fonte_elemental_poder", "golem"): "escolhe_golem_fonte",
    ("hibrido_vanguardista", "kliren"): "escolhe_kliren_hibrido",
}

_RACA_NOME: Dict[str, str] = {
    "sereia_tritao": "Sereia/Tritão",
    "silfide": "Sílfide",
    "golem": "Golem",
    "kliren": "Kliren",
}


@lru_cache(maxsize=1)
def _carregar_escolhas() -> Dict[str, Any]:
    if not _ESCOLHAS_JSON.is_file():
        return {"racas": {}}
    return json.loads(_ESCOLHAS_JSON.read_text(encoding="utf-8"))


def racas_com_escolhas_v13() -> List[str]:
    racas = _carregar_escolhas().get("racas") or {}
    if not isinstance(racas, dict):
        return []
    return sorted(str(k).strip().lower() for k in racas if str(k).strip())


def flag_escolha_por_tipo(tipo: str, slug: str = "") -> Optional[str]:
    s = str(slug or "").strip().lower()
    t = str(tipo or "").strip()
    key = (t, s)
    if key in _TIPO_SLUG_FLAGS:
        return _TIPO_SLUG_FLAGS[key]
    return _TIPO_FLAGS.get(t)


def escolhas_por_raca(
    slug: str, regra_versao: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    if normalizar_regra_versao(regra_versao) != REGRA_VERSAO_V13:
        return None
    s = str(slug or "").strip().lower()
    if not s:
        return None
    row = (_carregar_escolhas().get("racas") or {}).get(s)
    if not isinstance(row, dict):
        return None
    return dict(row)


def _norm_pericias(raw: Optional[List[str]]) -> List[str]:
    out: List[str] = []
    seen: set[str] = set()
    for item in raw or []:
        n = str(item or "").strip()
        if not n:
            continue
        key = n.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(n)
    return out


def _norm_magias(raw: Optional[List[str]]) -> List[str]:
    out: List[str] = []
    seen: set[str] = set()
    for item in raw or []:
        s = str(item or "").strip().lower()
        if not s or s in seen:
            continue
        seen.add(s)
        out.append(s)
    return out


def _nome_raca(slug: str) -> str:
    return _RACA_NOME.get(slug, slug.replace("_", " ").title())


def _validar_magias_escolha(
    cfg: Dict[str, Any],
    slug_raca: str,
    picks: List[str],
) -> List[str]:
    erros: List[str] = []
    nome = _nome_raca(slug_raca)
    qtd = int(cfg.get("escolhas_qtd", 2) or 2)
    opcoes = {
        str(m.get("slug"))
        for m in (cfg.get("magias_opcoes") or [])
        if isinstance(m, dict)
    }
    if len(picks) < qtd:
        erros.append(f"{nome}: escolha {qtd} magia(s).")
    if len(picks) > qtd:
        erros.append(f"{nome}: no máximo {qtd} magia(s).")
    for slug_m in picks:
        if slug_m not in opcoes:
            erros.append(f"{nome}: magia inválida ({slug_m}).")
    return erros


def validar_escolhas_raciais_v13(
    slug_raca: str,
    *,
    lefou_deformidade_modo: Optional[str] = None,
    lefou_deformidade_pericias: Optional[List[str]] = None,
    lefou_deformidade_poder_slug: Optional[str] = None,
    qareen_ascendencia: Optional[str] = None,
    qareen_magia_slug: Optional[str] = None,
    golem_fonte_elemental: Optional[str] = None,
    golem_poder_geral_slug: Optional[str] = None,
    kliren_pericia: Optional[str] = None,
    kliren_oficio: Optional[str] = None,
    osteon_memoria_modo: Optional[str] = None,
    osteon_memoria_pericia: Optional[str] = None,
    osteon_memoria_poder_slug: Optional[str] = None,
    sereia_magias: Optional[List[str]] = None,
    silfide_magias: Optional[List[str]] = None,
) -> Tuple[bool, List[str]]:
    """Valida escolhas obrigatórias por raça v1.3."""
    s = str(slug_raca or "").strip().lower()
    cfg = escolhas_por_raca(s, REGRA_VERSAO_V13)
    if not cfg:
        return True, []

    erros: List[str] = []
    tipo = str(cfg.get("tipo") or "")

    if tipo == "deformidade":
        modos = {
            str(m.get("slug")) for m in (cfg.get("modos") or []) if isinstance(m, dict)
        }
        modo = str(lefou_deformidade_modo or "duas_pericias").strip().lower()
        if modo not in modos:
            erros.append("Lefou: modo de deformidade inválido.")
            return False, erros
        modo_row = next(
            (m for m in (cfg.get("modos") or []) if str(m.get("slug")) == modo),
            None,
        )
        slots = int((modo_row or {}).get("slots_pericia", 0) or 0)
        per = _norm_pericias(lefou_deformidade_pericias)
        if len(per) < slots:
            erros.append(f"Lefou: informe {slots} perícia(s) para deformidade.")
        if len(per) > slots:
            erros.append(f"Lefou: no máximo {slots} perícia(s) para deformidade.")
        if modo == "pericia_poder_tormenta":
            pod = str(lefou_deformidade_poder_slug or "").strip()
            if not pod:
                erros.append("Lefou: informe o poder da Tormenta (deformidade).")

    elif tipo == "ascendencia_magia":
        asc_slugs = {
            str(a.get("slug"))
            for a in (cfg.get("ascendencias") or [])
            if isinstance(a, dict)
        }
        asc = str(qareen_ascendencia or "").strip().lower()
        if asc not in asc_slugs:
            erros.append("Qareen: escolha a ascendência elementar.")
        mag = str(qareen_magia_slug or "").strip()
        if not mag:
            erros.append("Qareen: escolha a magia de 1º círculo (Tatuagem Mística).")

    elif tipo == "fonte_elemental_poder":
        fontes = {
            str(f.get("slug")) for f in (cfg.get("fontes") or []) if isinstance(f, dict)
        }
        fonte = str(golem_fonte_elemental or "").strip().lower()
        if fonte not in fontes:
            erros.append("Golem: escolha a Fonte Elemental.")
        if not str(golem_poder_geral_slug or "").strip():
            erros.append("Golem: informe o poder geral (Propósito de Criação).")

    elif tipo == "hibrido_vanguardista":
        if not str(kliren_pericia or "").strip():
            erros.append("Kliren: informe a perícia do Híbrido.")
        if not str(kliren_oficio or "").strip():
            erros.append("Kliren: informe a especialidade de Ofício (Vanguardista).")

    elif tipo == "memoria_postuma":
        modos = {
            str(m.get("slug")) for m in (cfg.get("modos") or []) if isinstance(m, dict)
        }
        modo = str(osteon_memoria_modo or "").strip().lower()
        if modo not in modos:
            erros.append("Osteon: escolha Memória Póstuma (perícia ou poder geral).")
        elif modo == "pericia":
            if not str(osteon_memoria_pericia or "").strip():
                erros.append("Osteon: informe a perícia da Memória Póstuma.")
        elif modo == "poder_geral":
            if not str(osteon_memoria_poder_slug or "").strip():
                erros.append("Osteon: informe o poder geral da Memória Póstuma.")

    elif tipo == "magias_escolha":
        picks = _norm_magias(sereia_magias if s == "sereia_tritao" else silfide_magias)
        erros.extend(_validar_magias_escolha(cfg, s, picks))

    return len(erros) == 0, erros


def aplicar_escolhas_ao_preview(
    preview: Dict[str, Any],
    slug_raca: str,
    *,
    regra_versao: Optional[str] = None,
    lefou_deformidade_modo: Optional[str] = None,
    lefou_deformidade_pericias: Optional[List[str]] = None,
    qareen_ascendencia: Optional[str] = None,
    golem_fonte_elemental: Optional[str] = None,
    kliren_pericia: Optional[str] = None,
    kliren_oficio: Optional[str] = None,
    osteon_memoria_modo: Optional[str] = None,
    osteon_memoria_pericia: Optional[str] = None,
    sereia_magias: Optional[List[str]] = None,
    silfide_magias: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Mescla bônus mecânicos das escolhas raciais no preview de traços."""
    if normalizar_regra_versao(regra_versao) != REGRA_VERSAO_V13:
        return preview

    s = str(slug_raca or "").strip().lower()
    cfg = escolhas_por_raca(s, REGRA_VERSAO_V13)
    if not cfg:
        return preview

    out = dict(preview)
    per_map = dict(out.get("pericias_bonus") or {})
    rd_map = dict(out.get("reducao_dano") or {})
    imun_map = dict(out.get("imunidades_dano") or {})
    magias: List[str] = list(out.get("magias_inatas") or [])
    resumo: List[str] = list(out.get("escolhas_resumo") or [])
    per_treinadas: List[str] = list(out.get("pericias_treinadas_escolha") or [])
    tipo = str(cfg.get("tipo") or "")

    if tipo == "deformidade":
        bonus = int(cfg.get("bonus_pericia", 2) or 2)
        modo = str(lefou_deformidade_modo or "duas_pericias").strip().lower()
        for nome in _norm_pericias(lefou_deformidade_pericias):
            per_map[nome] = int(per_map.get(nome, 0) or 0) + bonus
            resumo.append(f"{nome} +{bonus} (Deformidade)")
        if modo == "pericia_poder_tormenta":
            resumo.append("1 poder da Tormenta (Deformidade)")

    elif tipo == "ascendencia_magia":
        asc = str(qareen_ascendencia or "").strip().lower()
        for row in cfg.get("ascendencias") or []:
            if not isinstance(row, dict):
                continue
            if str(row.get("slug")) != asc:
                continue
            rd_tipo = str(row.get("rd_tipo") or "").strip().lower()
            rd_val = int(row.get("rd_valor", 0) or 0)
            if rd_tipo and rd_val:
                rd_map[rd_tipo] = int(rd_map.get(rd_tipo, 0) or 0) + rd_val
                resumo.append(f"RD {rd_val} ({row.get('rotulo', asc)})")
            break

    elif tipo == "fonte_elemental_poder":
        fonte = str(golem_fonte_elemental or "").strip().lower()
        for row in cfg.get("fontes") or []:
            if not isinstance(row, dict):
                continue
            if str(row.get("slug")) != fonte:
                continue
            im_tipo = str(row.get("imunidade_tipo") or "").strip().lower()
            if im_tipo:
                imun_map[im_tipo] = True
                resumo.append(f"Imune a {im_tipo} ({row.get('rotulo', fonte)})")
            break
        resumo.append("1 poder geral (Propósito de Criação)")

    elif tipo == "hibrido_vanguardista":
        per = str(kliren_pericia or "").strip()
        if per:
            per_treinadas.append(per)
            resumo.append(f"Treinado: {per} (Híbrido)")
        oficio = str(kliren_oficio or "").strip()
        bonus_of = int(cfg.get("bonus_oficio", 2) or 2)
        if oficio:
            per_map["Ofício"] = int(per_map.get("Ofício", 0) or 0) + bonus_of
            resumo.append(f"Ofício ({oficio}) +{bonus_of} (Vanguardista)")

    elif tipo == "magias_fixas":
        for row in cfg.get("magias_inatas") or []:
            if not isinstance(row, dict):
                continue
            slug_m = str(row.get("slug") or "").strip()
            if slug_m and slug_m not in magias:
                magias.append(slug_m)
        if magias:
            resumo.append("Magias inatas raciais")

    elif tipo == "memoria_postuma":
        modo = str(osteon_memoria_modo or "").strip().lower()
        if modo == "pericia":
            per = str(osteon_memoria_pericia or "").strip()
            if per:
                per_treinadas.append(per)
                resumo.append(f"Treinado: {per} (Memória Póstuma)")
        elif modo == "poder_geral":
            resumo.append("1 poder geral (Memória Póstuma)")

    elif tipo == "magias_escolha":
        picks = _norm_magias(sereia_magias if s == "sereia_tritao" else silfide_magias)
        for slug_m in picks:
            if slug_m not in magias:
                magias.append(slug_m)
        if picks:
            op_map = {
                str(o.get("slug")): str(o.get("nome", o.get("slug")))
                for o in (cfg.get("magias_opcoes") or [])
                if isinstance(o, dict)
            }
            labels = [op_map.get(slug_m, slug_m) for slug_m in picks]
            titulo = "Canção dos Mares" if s == "sereia_tritao" else "Magia das Fadas"
            resumo.append(f"{titulo}: {', '.join(labels)}")

    out["pericias_bonus"] = per_map
    out["reducao_dano"] = rd_map
    out["imunidades_dano"] = imun_map
    out["magias_inatas"] = magias
    out["escolhas_resumo"] = resumo
    out["pericias_treinadas_escolha"] = per_treinadas
    return out


def magias_inatas_raca_v13(slug_raca: str) -> List[str]:
    cfg = escolhas_por_raca(slug_raca, REGRA_VERSAO_V13)
    if not cfg:
        return []
    tipo = str(cfg.get("tipo") or "")
    if tipo == "magias_fixas":
        out: List[str] = []
        for row in cfg.get("magias_inatas") or []:
            if isinstance(row, dict):
                slug_m = str(row.get("slug") or "").strip()
                if slug_m:
                    out.append(slug_m)
        return out
    return []
