"""Combate Tormenta 20 — rolagens de iniciativa, ataque e dano; condições v1.3."""

from __future__ import annotations

import random
import re
from typing import Any, Dict, List, Optional, Tuple

from app.games.tormenta.rules.condicoes_t20 import modificadores_de_condicoes

# Ordem T20 Tabela 1-21 (Minúsculo → Colossal).
_ORDEM_TAMANHO: Dict[str, int] = {
    "minusculo": 0,
    "pequeno": 1,
    "medio": 2,
    "grande": 3,
    "enorme": 4,
    "colossal": 5,
}


def ordem_tamanho(slug: Optional[str]) -> int:
    """Índice numérico do tamanho (padrão Médio = 2)."""
    return _ORDEM_TAMANHO.get(str(slug or "medio").strip().lower(), 2)


def ca_bonus_tamanho_combate(
    tamanho_defensor: Optional[str],
    tamanho_atacante: Optional[str],
) -> int:
    """
    Bônus/penalidade de CA por tamanho (T20 Tabela 1-21).
    Pequeno/Minúsculo: +1 vs Médio+; Grande+: −1 vs Médio−.
    """
    od = ordem_tamanho(tamanho_defensor)
    oa = ordem_tamanho(tamanho_atacante)
    if od <= 1 and oa >= 2:
        return 1
    if od >= 3 and oa <= 2:
        return -1
    return 0


def ataque_bonus_tamanho_combate(
    tamanho_atacante: Optional[str],
    tamanho_alvo: Optional[str],
) -> int:
    """Pequeno +1 vs Médio−; Grande+ +1 vs Médio+."""
    oa = ordem_tamanho(tamanho_atacante)
    od = ordem_tamanho(tamanho_alvo)
    if oa <= 1 and od <= 2:
        return 1
    if oa >= 3 and od >= 2:
        return 1
    return 0


def manobra_bonus_tamanho(tamanho: Optional[str]) -> int:
    """Pequeno −4; Grande+ +2 (vs alvos maiores / manobras em geral)."""
    o = ordem_tamanho(tamanho)
    if o <= 1:
        return -4
    if o >= 3:
        return 2
    return 0


def modificadores_tamanho_combate(
    tamanho_atacante: Optional[str],
    tamanho_alvo: Optional[str],
) -> Dict[str, int]:
    """Modificadores contextuais de ataque e CA por tamanho."""
    return {
        "ataque": ataque_bonus_tamanho_combate(tamanho_atacante, tamanho_alvo),
        "ca_defensor": ca_bonus_tamanho_combate(tamanho_alvo, tamanho_atacante),
        "manobra_atacante": manobra_bonus_tamanho(tamanho_atacante),
    }


def expandir_dano_forca_dos_titas(
    rolls: List[int],
    faces: int,
    limite_extras: int,
    *,
    seed: Optional[int] = None,
) -> Tuple[List[int], int]:
    """
    Força dos Titãs (Galokk): dado extra por resultado máximo, até limite = mod. Força.
    """
    if faces < 2 or limite_extras <= 0:
        return list(rolls), sum(rolls)
    rng = random.Random(seed) if seed is not None else random
    all_rolls = list(rolls)
    extras = 0
    i = 0
    while i < len(all_rolls) and extras < limite_extras:
        if all_rolls[i] >= faces:
            extra = rng.randint(1, faces)
            all_rolls.append(extra)
            extras += 1
        i += 1
    return all_rolls, sum(all_rolls)


def rolar_teste_vontade_racial(
    bonus: int,
    dc: int,
    *,
    slug_raca: Optional[str] = None,
    efeito_mental: bool = False,
    seed: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Teste de Vontade; Eiradaan com efeito mental usa pior de 2d20 (Canção da Melancolia).
    """
    rng = random.Random(seed) if seed is not None else random
    raca = str(slug_raca or "").strip().lower()
    melancolia = raca == "eiradaan" and bool(efeito_mental)
    if melancolia:
        d20a = rng.randint(1, 20)
        d20b = rng.randint(1, 20)
        d20 = min(d20a, d20b)
        d20_rolagens = [d20a, d20b]
    else:
        d20 = rng.randint(1, 20)
        d20_rolagens = [d20]
    total = d20 + int(bonus)
    dc_i = int(dc)
    return {
        "d20": d20,
        "d20_rolagens": d20_rolagens,
        "bonus": int(bonus),
        "total": total,
        "dc": dc_i,
        "sucesso": total >= dc_i,
        "falha_critica": d20 == 1,
        "sucesso_critico": d20 == 20,
        "margem": total - dc_i,
        "cancao_melancolia": melancolia,
    }


def modificadores_de_condicoes_mb(
    rotulos: Optional[List[str]],
) -> Dict[str, int]:
    """Alias — delega ao catálogo v1.3 (RF-T05-v13)."""
    return modificadores_de_condicoes(rotulos)


def rolar_dado_formula(
    formula: str, seed: Optional[int] = None
) -> Tuple[int, List[int]]:
    """
    Rola fórmula simples NdM (+/-X opcional).
    Ex.: '1d8', '2d6+3', '1d20'.
    """
    rng = random.Random(seed) if seed is not None else random
    f = str(formula or "").strip().lower().replace(" ", "")
    if not f:
        return 0, []
    m = re.match(r"^(\d+)d(\d+)([+-]\d+)?$", f)
    if not m:
        return 0, []
    n = int(m.group(1))
    faces = int(m.group(2))
    mod = int(m.group(3) or 0)
    rolls = [rng.randint(1, faces) for _ in range(n)]
    return sum(rolls) + mod, rolls


def rolar_iniciativa(
    mod_destreza: int,
    *,
    seed: Optional[int] = None,
) -> Dict[str, Any]:
    rng = random.Random(seed) if seed is not None else random
    d20 = rng.randint(1, 20)
    mod = int(mod_destreza)
    return {"d20": d20, "modificador": mod, "total": d20 + mod}


def rolar_ataque(
    bab: int,
    mod_atributo: int,
    *,
    bonus_arma: int = 0,
    penalidades: int = 0,
    modificador_condicoes: int = 0,
    bonus_tamanho: int = 0,
    ca_alvo: int,
    seed: Optional[int] = None,
) -> Dict[str, Any]:
    rng = random.Random(seed) if seed is not None else random
    d20 = rng.randint(1, 20)
    bonus = (
        int(bab)
        + int(mod_atributo)
        + int(bonus_arma)
        - int(penalidades)
        + int(modificador_condicoes)
        + int(bonus_tamanho)
    )
    total = d20 + bonus
    ca = int(ca_alvo)
    acertou = total >= ca
    ameaca_critica = d20 == 20 or d20 >= 19
    return {
        "d20": d20,
        "bonus": bonus,
        "total": total,
        "ca_alvo": ca,
        "acertou": acertou,
        "ameaca_critica": ameaca_critica,
        "falha_critica": d20 == 1,
        "bonus_tamanho": int(bonus_tamanho),
    }


def rolar_dano(
    formula_dano: str,
    mod_atributo: int = 0,
    *,
    confirmar_critico: bool = False,
    multiplicador_critico: int = 2,
    forca_dos_titas: bool = False,
    limite_dados_extra_forca: int = 0,
    seed: Optional[int] = None,
) -> Dict[str, Any]:
    f = str(formula_dano or "").strip().lower().replace(" ", "")
    m = re.match(r"^(\d+)d(\d+)([+-]\d+)?$", f)
    mod_formula = int(m.group(3) or 0) if m else 0
    faces = int(m.group(2)) if m else 0

    base_roll, rolls = rolar_dado_formula(formula_dano, seed=seed)
    mod = int(mod_atributo)

    if forca_dos_titas and faces >= 2 and limite_dados_extra_forca > 0:
        rolls, soma_dados = expandir_dano_forca_dos_titas(
            rolls,
            faces,
            int(limite_dados_extra_forca),
            seed=None if seed is None else seed + 2,
        )
        base = soma_dados + mod_formula
    else:
        base = base_roll

    total = max(1, base + mod)
    if confirmar_critico:
        extra, rolls2 = rolar_dado_formula(
            formula_dano, seed=None if seed is None else seed + 1
        )
        total = max(1, (base + extra + mod * 2) * (multiplicador_critico // 2))
        rolls = rolls + rolls2
    out: Dict[str, Any] = {
        "formula": formula_dano,
        "rolagens": rolls,
        "modificador": mod,
        "dano": total,
        "critico": confirmar_critico,
    }
    if forca_dos_titas:
        out["forca_dos_titas"] = True
        out["limite_dados_extra_forca"] = int(limite_dados_extra_forca)
    return out
