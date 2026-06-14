"""Regras de combate MB ligadas à conjuração (concentração, resistência à magia)."""

from __future__ import annotations

import re
from typing import Any, Dict, Optional

from app.games.tormenta.rules.atributos_t20 import modificador_atributo_t20
from app.games.tormenta.rules.pericias_t20 import (
    bonus_meio_nivel_t20,
    rolar_teste_pericia,
)

_CHAVE_SESSAO = "tormenta_grimorio_sessao_mb"

_SLUGS_RESISTENCIA_MAGIA_BONUS: Dict[str, int] = {
    "resistencia_a_magia": 4,
    "resistencia_a_magia_div": 4,
    "resistencia_a_magia_maior": 8,
    "resistencia_a_magia_maior_div": 8,
}


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


def ler_resistencia_magia_sessao_mb(
    ficha_json: Optional[Dict[str, Any]],
) -> Optional[int]:
    """Bônus ativo em sessão (após lançar Resistência a magia / maior)."""
    fj = ficha_json if isinstance(ficha_json, dict) else {}
    sess = fj.get(_CHAVE_SESSAO)
    if not isinstance(sess, dict):
        return None
    try:
        bonus = int(sess.get("resistencia_magia_bonus") or 0)
    except (TypeError, ValueError):
        return None
    return bonus if bonus > 0 else None


def aplicar_resistencia_magia_ao_lancar(
    ficha_json: Optional[Dict[str, Any]],
    *,
    magia_slug: str,
) -> Dict[str, Any]:
    """Regista bônus MB (+4/+8) na sessão ao lançar a magia homónima."""
    slug = str(magia_slug or "").strip().lower()
    bonus = _SLUGS_RESISTENCIA_MAGIA_BONUS.get(slug)
    if not bonus:
        return dict(ficha_json or {})
    fj = dict(ficha_json or {})
    sess = dict(fj.get(_CHAVE_SESSAO) or {})
    atual = int(sess.get("resistencia_magia_bonus") or 0)
    if bonus > atual:
        sess["resistencia_magia_bonus"] = bonus
    fj[_CHAVE_SESSAO] = sess
    return fj


def limpar_resistencia_magia_mb(ficha_json: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    fj = dict(ficha_json or {})
    sess = dict(fj.get(_CHAVE_SESSAO) or {})
    sess.pop("resistencia_magia_bonus", None)
    fj[_CHAVE_SESSAO] = sess
    return fj


def resistencia_magia_bonus_mb(vinculos: list) -> Optional[int]:
    """Lembrete: maior bônus entre magias RM preparadas/conhecidas (não substitui sessão ativa)."""
    best = 0
    for v in vinculos or []:
        if not isinstance(v, dict):
            continue
        pap = str(v.get("papel") or "").strip().lower()
        if pap not in ("preparada", "conhecida"):
            continue
        slug = str(v.get("magia_slug") or "").strip().lower()
        bonus = _SLUGS_RESISTENCIA_MAGIA_BONUS.get(slug)
        if bonus and bonus > best:
            best = bonus
    return best if best > 0 else None


def bonus_resistencia_magia_efetivo_mb(
    ficha_json: Optional[Dict[str, Any]],
    vinculos: Optional[list] = None,
) -> int:
    """Prioriza bônus ativo em sessão; senão lembrete de grimório."""
    sess = ler_resistencia_magia_sessao_mb(ficha_json)
    if sess:
        return sess
    lembrete = resistencia_magia_bonus_mb(vinculos or [])
    return int(lembrete or 0)


def cd_teste_resistencia_magia_mb(circulo: int, mod_habilidade_chave: int) -> int:
    """MB p.150–209: CD 10 + nível da magia + mod. habilidade-chave do conjurador."""
    try:
        circ = int(circulo)
    except (TypeError, ValueError):
        circ = 0
    try:
        mod = int(mod_habilidade_chave)
    except (TypeError, ValueError):
        mod = 0
    return 10 + max(0, circ) + mod


def cd_concentracao_por_dano_mb(dano: int) -> int:
    """Manter concentração ao sofrer dano (herança 3.5 / MB): CD 10 + dano recebido."""
    try:
        d = int(dano)
    except (TypeError, ValueError):
        d = 0
    return 10 + max(0, d)


def bonus_manter_concentracao_mb(
    *,
    con_valor: int,
    nivel: int,
    fort_total: Optional[int] = None,
) -> int:
    """
    Bônus no teste para manter concentração.
    Usa fort_total da ficha quando preenchido; senão CON + ½ nível (MB).
    """
    if fort_total is not None:
        try:
            ft = int(fort_total)
        except (TypeError, ValueError):
            ft = None
        else:
            if ft != 0:
                return ft
    mod_con = modificador_atributo_t20(int(con_valor or 10))
    return mod_con + bonus_meio_nivel_t20(int(nivel or 1))


def inferir_tipo_resistencia_mb(texto: Optional[str]) -> Optional[str]:
    """Extrai fortitude | reflexos | vontade de texto MB (ex.: campo resistencia da magia)."""
    t = str(texto or "").lower()
    if not t.strip() or "nenhum" in t:
        return None
    if "fortitude" in t or "fort" in t.split():
        return "fortitude"
    if "reflex" in t or "ref" in t.split():
        return "reflexos"
    if "vontade" in t or "von" in t.split():
        return "vontade"
    return None


def bonus_teste_resistencia_personagem_mb(
    *,
    tipo: str,
    fort_total: int = 0,
    ref_total: int = 0,
    von_total: int = 0,
    bonus_rm: int = 0,
) -> Dict[str, Any]:
    """Monta bônus base + RM para teste contra magia."""
    chave = str(tipo or "").strip().lower()
    mapa = {
        "fortitude": int(fort_total),
        "reflexos": int(ref_total),
        "vontade": int(von_total),
    }
    base = mapa.get(chave, 0)
    rm = max(0, int(bonus_rm or 0))
    return {
        "tipo": chave,
        "bonus_base": base,
        "bonus_resistencia_magia": rm,
        "bonus_total": base + rm,
    }


def rolar_teste_resistencia_magia_mb(
    *,
    tipo: str,
    fort_total: int = 0,
    ref_total: int = 0,
    von_total: int = 0,
    bonus_rm: int = 0,
    cd: int,
    seed: Optional[int] = None,
) -> Dict[str, Any]:
    """Rola 1d20 + bônus de resistência (+ RM) vs CD da magia."""
    partes = bonus_teste_resistencia_personagem_mb(
        tipo=tipo,
        fort_total=fort_total,
        ref_total=ref_total,
        von_total=von_total,
        bonus_rm=bonus_rm,
    )
    teste = rolar_teste_pericia(partes["bonus_total"], int(cd), seed=seed)
    return {
        **partes,
        **teste,
        "passou": bool(teste.get("sucesso")),
    }


def rolar_teste_concentracao_por_dano_mb(
    *,
    dano: int,
    con_valor: int,
    nivel: int,
    fort_total: Optional[int] = None,
    seed: Optional[int] = None,
) -> Dict[str, Any]:
    """Teste automático ao sofrer dano enquanto concentra."""
    dc = cd_concentracao_por_dano_mb(dano)
    bonus = bonus_manter_concentracao_mb(
        con_valor=con_valor, nivel=nivel, fort_total=fort_total
    )
    teste = rolar_teste_pericia(bonus, dc, seed=seed)
    return {
        "dano": int(dano),
        "dc": dc,
        "bonus": bonus,
        **teste,
        "manteve": bool(teste.get("sucesso")),
    }


def processar_concentracao_apos_dano_mb(
    ficha_json: Optional[Dict[str, Any]],
    *,
    dano: int,
    con_valor: int,
    nivel: int,
    fort_total: Optional[int] = None,
    seed: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Se há concentração ativa, rola teste; em falha limpa a sessão.
    Retorna ficha atualizada e metadados do teste.
    """
    conc = ler_concentracao_mb(ficha_json)
    if not conc:
        return {
            "tinha_concentracao": False,
            "concentracao_perdida": False,
            "concentracao_anterior": None,
            "teste": None,
            "ficha_json": dict(ficha_json or {}),
        }

    teste = rolar_teste_concentracao_por_dano_mb(
        dano=dano,
        con_valor=con_valor,
        nivel=nivel,
        fort_total=fort_total,
        seed=seed,
    )
    perdeu = not teste.get("manteve")
    fj = dict(ficha_json or {})
    if perdeu:
        fj = limpar_concentracao_mb(fj)

    return {
        "tinha_concentracao": True,
        "concentracao_perdida": perdeu,
        "concentracao_anterior": conc.get("nome"),
        "teste": teste,
        "ficha_json": fj,
    }


def mod_habilidade_chave_conjurador_mb(
    *,
    classe_slug: str,
    int_valor: int,
    sab_valor: int,
    car_valor: int,
) -> int:
    """INT (mago), SAB (clérigo/druida/ranger), CAR (bardo/feiticeiro/paladino)."""
    slug = str(classe_slug or "").strip().lower()
    if slug in ("mago",):
        return modificador_atributo_t20(int_valor)
    if slug in ("bardo", "feiticeiro", "paladino"):
        return modificador_atributo_t20(car_valor)
    return modificador_atributo_t20(sab_valor)


def normalizar_tipo_resistencia_request(tipo: str) -> str:
    t = re.sub(r"[^a-z]", "", str(tipo or "").strip().lower())
    aliases = {
        "fort": "fortitude",
        "fortitude": "fortitude",
        "ref": "reflexos",
        "reflexos": "reflexos",
        "reflexo": "reflexos",
        "von": "vontade",
        "vontade": "vontade",
    }
    out = aliases.get(t)
    if not out:
        raise ValueError(f"Tipo de resistência inválido: {tipo}")
    return out
