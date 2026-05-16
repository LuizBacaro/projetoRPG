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
        "incapacitado",
        "atordoado",
        "cego",
        "agarrado",
        "envenenado",
        "assustado",
        "prostrado",
    }
)


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


def ataque_atinge_ca(
    mod_atributo: int,
    bonus_proficiencia: int,
    ac_alvo: int,
    *,
    rolagem_d20: Optional[int] = None,
    proficiente: bool = True,
    bonus_extra: int = 0,
) -> bool:
    """True se o ataque acerta (total >= CA)."""
    roll = rolagem_d20 if rolagem_d20 is not None else rolar_d20()
    prof = bonus_proficiencia if proficiente else 0
    total = roll + mod_atributo + prof + bonus_extra
    return total >= ac_alvo


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
