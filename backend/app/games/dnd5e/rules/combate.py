"""Combate D&D 5E — iniciativa, ataques, dano, condições, morte (Cap. 9)."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, List, Optional, Sequence

from app.games.dnd5e.rules.dados import rolar_d20, rolar_dado


class StatusVida(str, Enum):
    VIVO = "vivo"
    INCONSCIENTE = "inconsciente"
    MORTO = "morto"
    ESTABILIZADO = "estabilizado"


CONDICOES_PADRAO = frozenset(
    {
        "agarrado",
        "assustado",
        "atordoado",
        "cego",
        "enfeiticado",
        "envenenado",
        "exausto",
        "incapacitado",
        "inconsciente",
        "invisivel",
        "paralisado",
        "petrificado",
        "prostrado",
        "surdo",
    }
)

CONDICOES_NOMES: dict[str, str] = {
    "agarrado": "Agarrado",
    "assustado": "Assustado",
    "atordoado": "Atordoado",
    "cego": "Cego",
    "enfeiticado": "Enfeitiçado",
    "envenenado": "Envenenado",
    "exausto": "Exausto",
    "incapacitado": "Incapacitado",
    "inconsciente": "Inconsciente",
    "invisivel": "Invisível",
    "paralisado": "Paralisado",
    "petrificado": "Petrificado",
    "prostrado": "Prostrado",
    "surdo": "Surdo",
}


def normalizar_condicao_slug(condicao: str) -> str:
    """Slug estável para comparação (minúsculas, sem acentos extras)."""
    return (
        (condicao or "")
        .strip()
        .lower()
        .replace(" ", "_")
        .replace("ç", "c")
        .replace("ã", "a")
        .replace("á", "a")
        .replace("é", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ú", "u")
    )


def _conjunto_condicoes(condicoes: Optional[Sequence[str]]) -> set[str]:
    return {normalizar_condicao_slug(c) for c in (condicoes or ()) if c}


@dataclass
class ModificadoresAtaque:
    """Vantagem/desvantagem e efeitos especiais derivados de condições PHB (resumo)."""

    vantagem: bool = False
    desvantagem: bool = False
    acerto_automatico: bool = False
    critico_automatico: bool = False

    def rolagem_efetiva(self) -> tuple[bool, bool]:
        """Cancela vantagem e desvantagem simultâneos (PHB)."""
        if self.vantagem and self.desvantagem:
            return False, False
        return self.vantagem, self.desvantagem


def resumo_modificadores_ataque(
    condicoes_atacante: Optional[Sequence[str]] = None,
    condicoes_alvo: Optional[Sequence[str]] = None,
    *,
    corpo_a_corpo: bool = True,
) -> ModificadoresAtaque:
    """Deriva modificadores de ataque a partir das condições (Cap. 9 — resumo de mesa)."""
    at = _conjunto_condicoes(condicoes_atacante)
    al = _conjunto_condicoes(condicoes_alvo)
    mod = ModificadoresAtaque()

    if at & {"cego", "envenenado", "atordoado", "assustado"}:
        mod.desvantagem = True
    if "exausto" in at:
        mod.desvantagem = True

    if al & {"atordoado", "inconsciente", "paralisado", "cego"}:
        mod.vantagem = True
    if "prostrado" in al:
        if corpo_a_corpo:
            mod.vantagem = True
        else:
            mod.desvantagem = True

    if "incapacitado" in al and corpo_a_corpo:
        mod.acerto_automatico = True
        mod.critico_automatico = True

    return mod


@dataclass
class ArmaCombate:
    """Arma simplificada para cálculo de dano."""

    nome: str = "arma"
    dano: str = "1d8"  # expressão NdM
    tipo: str = "corpo_a_corpo"  # corpo_a_corpo | distancia


@dataclass
class Combatente:
    combatente_id: str
    nome: str
    hp: int
    max_hp: int
    ac: int
    dex_mod: int = 0
    str_mod: int = 0
    proficiencia_bonus: int = 2
    armas: List[ArmaCombate] = field(default_factory=list)
    condicoes: List[str] = field(default_factory=list)
    death_failures: int = 0
    death_successes: int = 0
    iniciativa_rolagem: int = 0

    def tem_condicao(self, condicao: str) -> bool:
        return condicao.lower() in {c.lower() for c in self.condicoes}


def calcular_iniciativa(
    dex_mod: int,
    *,
    rolagem_d20: Optional[int] = None,
    rng: Optional[Callable[[int, int], int]] = None,
) -> int:
    """Iniciativa = 1d20 + modificador de Destreza."""
    roll = rolagem_d20 if rolagem_d20 is not None else rolar_d20(rng)
    return roll + dex_mod


def rolar_d20_ataque(
    *,
    vantagem: bool = False,
    desvantagem: bool = False,
    rolagem_forcada: Optional[int] = None,
    rng: Optional[Callable[[int, int], int]] = None,
) -> tuple[int, Optional[int]]:
    """Retorna (d20 usado, d20 descartado ou None)."""
    if rolagem_forcada is not None:
        return rolagem_forcada, None
    if vantagem and desvantagem:
        return rolar_d20(rng), None
    if vantagem:
        r1, r2 = rolar_d20(rng), rolar_d20(rng)
        return max(r1, r2), min(r1, r2)
    if desvantagem:
        r1, r2 = rolar_d20(rng), rolar_d20(rng)
        return min(r1, r2), max(r1, r2)
    return rolar_d20(rng), None


def ataque_atinge_ca(
    mod_atributo: int,
    bonus_proficiencia: int,
    ac_alvo: int,
    *,
    rolagem_d20: Optional[int] = None,
    proficiente: bool = True,
    bonus_extra: int = 0,
    vantagem: bool = False,
    desvantagem: bool = False,
    acerto_automatico: bool = False,
) -> bool:
    """True se o ataque acerta (total >= CA ou acerto automático por condição)."""
    if acerto_automatico:
        return True
    roll, _ = rolar_d20_ataque(
        vantagem=vantagem,
        desvantagem=desvantagem,
        rolagem_forcada=rolagem_d20,
    )
    prof = bonus_proficiencia if proficiente else 0
    total = roll + mod_atributo + prof + bonus_extra
    return total >= ac_alvo


@dataclass
class ResultadoAtaque:
    rolagem: int
    rolagem_secundaria: Optional[int]
    total: int
    acerto: bool
    vantagem: bool
    desvantagem: bool
    critico_automatico: bool
    acerto_automatico: bool


def resolver_ataque(
    mod_atributo: int,
    bonus_proficiencia: int,
    ac_alvo: int,
    *,
    rolagem_d20: Optional[int] = None,
    proficiente: bool = True,
    bonus_extra: int = 0,
    condicoes_atacante: Optional[Sequence[str]] = None,
    condicoes_alvo: Optional[Sequence[str]] = None,
    corpo_a_corpo: bool = True,
    rng: Optional[Callable[[int, int], int]] = None,
) -> ResultadoAtaque:
    """Resolve ataque com modificadores de condição e vantagem/desvantagem."""
    mods = resumo_modificadores_ataque(
        condicoes_atacante,
        condicoes_alvo,
        corpo_a_corpo=corpo_a_corpo,
    )
    vant, desv = mods.rolagem_efetiva()
    roll, roll2 = rolar_d20_ataque(
        vantagem=vant,
        desvantagem=desv,
        rolagem_forcada=rolagem_d20,
        rng=rng,
    )
    prof = bonus_proficiencia if proficiente else 0
    total = roll + mod_atributo + prof + bonus_extra
    if mods.acerto_automatico:
        acerto = True
    else:
        acerto = total >= ac_alvo
    return ResultadoAtaque(
        rolagem=roll,
        rolagem_secundaria=roll2,
        total=total,
        acerto=acerto,
        vantagem=vant,
        desvantagem=desv,
        critico_automatico=mods.critico_automatico,
        acerto_automatico=mods.acerto_automatico,
    )


def calcular_dano(
    arma: ArmaCombate | str,
    mod_atributo: int,
    is_critico: bool = False,
    *,
    rng: Optional[Callable[[int, int], int]] = None,
) -> int:
    """Dano = dados da arma (+ dobro dos dados em crítico) + mod; mínimo 1."""
    expressao = arma.dano if isinstance(arma, ArmaCombate) else str(arma)
    if is_critico:
        # 2× os dados de dano
        parts = expressao.lower().split("d")
        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
            n, faces = int(parts[0]), int(parts[1])
            expressao = f"{n * 2}d{faces}"
    dano_dados = rolar_dado(expressao, rng=rng)
    total = dano_dados + mod_atributo
    return max(1, total)


def verificar_morte(
    hp: int,
    death_failures: int = 0,
    death_successes: int = 0,
) -> StatusVida:
    """HP > 0: vivo; 0 com 3 sucessos: estabilizado; 3 falhas: morto; senão inconsciente."""
    if hp > 0:
        return StatusVida.VIVO
    if death_successes >= 3:
        return StatusVida.ESTABILIZADO
    if death_failures >= 3:
        return StatusVida.MORTO
    return StatusVida.INCONSCIENTE


def registrar_teste_morte(
    combatente: Combatente,
    rolagem_d20: int,
) -> StatusVida:
    """Atualiza falhas/sucessos de morte (1d20: 1=falha extra, 20=2 sucessos)."""
    if combatente.hp > 0:
        combatente.death_failures = 0
        combatente.death_successes = 0
        return StatusVida.VIVO

    if rolagem_d20 == 1:
        combatente.death_failures += 2
    elif rolagem_d20 == 20:
        combatente.death_successes += 2
    elif rolagem_d20 >= 10:
        combatente.death_successes += 1
    else:
        combatente.death_failures += 1

    return verificar_morte(
        combatente.hp,
        combatente.death_failures,
        combatente.death_successes,
    )


@dataclass
class RodadaCombate:
    """Ordem de iniciativa e turno atual."""

    combatentes: List[Combatente] = field(default_factory=list)
    rodada_atual: int = 1
    indice_turno: int = 0

    def ordenar_por_iniciativa(
        self,
        rolagens: Optional[dict[str, int]] = None,
        rng: Optional[Callable[[int, int], int]] = None,
    ) -> List[Combatente]:
        """Rola iniciativa (ou usa rolagens fixas) e ordena: maior primeiro; empate = DEX mod."""
        rolagens = rolagens or {}
        for c in self.combatentes:
            roll = rolagens.get(c.combatente_id)
            c.iniciativa_rolagem = calcular_iniciativa(
                c.dex_mod, rolagem_d20=roll, rng=rng
            )
        self.combatentes.sort(
            key=lambda x: (x.iniciativa_rolagem, x.dex_mod), reverse=True
        )
        self.indice_turno = 0
        return list(self.combatentes)

    @property
    def ordem_iniciativa(self) -> List[Combatente]:
        return list(self.combatentes)

    @property
    def turno_atual(self) -> Optional[Combatente]:
        if not self.combatentes:
            return None
        return self.combatentes[self.indice_turno % len(self.combatentes)]

    def avancar_turno(self) -> Optional[Combatente]:
        if not self.combatentes:
            return None
        self.indice_turno += 1
        if self.indice_turno >= len(self.combatentes):
            self.indice_turno = 0
            self.rodada_atual += 1
        return self.turno_atual

    def aplicar_dano(self, combatente_id: str, dano: int) -> StatusVida:
        alvo = next(
            (c for c in self.combatentes if c.combatente_id == combatente_id), None
        )
        if alvo is None:
            raise ValueError("Combatente nao encontrado")
        alvo.hp = max(0, alvo.hp - dano)
        if alvo.hp == 0:
            alvo.death_failures = 0
            alvo.death_successes = 0
        return verificar_morte(alvo.hp, alvo.death_failures, alvo.death_successes)
