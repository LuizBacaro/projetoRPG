"""Regras de combate MB ligadas à conjuração (concentração, lembretes de SR)."""

from __future__ import annotations

from typing import Any, Dict, Optional

_CHAVE_SESSAO = "tormenta_grimorio_sessao_mb"


def magia_mb_exige_concentracao(meta: Optional[Dict[str, Any]]) -> bool:
    if not meta:
        return False
    dur = str(meta.get("duracao") or "").lower()
    return "concentr" in dur


def ler_concentracao_mb(
    ficha_json: Optional[Dict[str, Any]]
) -> Optional[Dict[str, str]]:
    fj = ficha_json if isinstance(ficha_json, dict) else {}
    sess = fj.get(_CHAVE_SESSAO)
    if not isinstance(sess, dict):
        return None
    slug = str(sess.get("concentracao_magia_slug") or "").strip().lower()
    if not slug:
        return None
    nome = str(sess.get("concentracao_magia_nome") or slug).strip()
    return {"magia_slug": slug, "nome": nome}


def aplicar_concentracao_ao_lancar(
    ficha_json: Optional[Dict[str, Any]],
    *,
    magia_slug: str,
    meta: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    fj = dict(ficha_json or {})
    sess = dict(fj.get(_CHAVE_SESSAO) or {})
    if magia_mb_exige_concentracao(meta):
        nome = str((meta or {}).get("nome") or magia_slug).strip()
        sess["concentracao_magia_slug"] = str(magia_slug).strip().lower()
        sess["concentracao_magia_nome"] = nome
    fj[_CHAVE_SESSAO] = sess
    return fj


def limpar_concentracao_mb(ficha_json: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    fj = dict(ficha_json or {})
    sess = dict(fj.get(_CHAVE_SESSAO) or {})
    sess.pop("concentracao_magia_slug", None)
    sess.pop("concentracao_magia_nome", None)
    fj[_CHAVE_SESSAO] = sess
    return fj


def resistencia_magia_bonus_mb(vinculos: list) -> Optional[int]:
    """MVP: lembrete se há Resistência a magia (ou maior) preparada/ativa na ficha."""
    slugs_bonus = {
        "resistencia_a_magia": 5,
        "resistencia_a_magia_div": 5,
        "resistencia_a_magia_maior": 12,
        "resistencia_a_magia_maior_div": 12,
    }
    best = 0
    for v in vinculos or []:
        if not isinstance(v, dict):
            continue
        pap = str(v.get("papel") or "").strip().lower()
        if pap not in ("preparada", "conhecida"):
            continue
        slug = str(v.get("magia_slug") or "").strip().lower()
        bonus = slugs_bonus.get(slug)
        if bonus and bonus > best:
            best = bonus
    return best if best > 0 else None
