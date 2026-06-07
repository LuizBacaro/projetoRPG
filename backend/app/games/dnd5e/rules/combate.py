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
    is_critico: bool = False


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
        acerto = total >= ac_alvo or roll == 20
    is_critico = mods.critico_automatico or roll == 20
    return ResultadoAtaque(
        rolagem=roll,
        rolagem_secundaria=roll2,
        total=total,
        acerto=acerto,
        vantagem=vant,
        desvantagem=desv,
        critico_automatico=mods.critico_automatico,
        acerto_automatico=mods.acerto_automatico,
        is_critico=is_critico,
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


@dataclass
class ResultadoTesteMorte:
    death_failures: int
    death_successes: int
    hp_atual: int
    status: StatusVida


def _status_vida_de_valor(valor: Optional[str | StatusVida]) -> Optional[StatusVida]:
    if valor is None:
        return None
    if isinstance(valor, StatusVida):
        return valor
    try:
        return StatusVida(str(valor).strip().lower())
    except ValueError:
        return None


def aplicar_teste_morte(
    hp: int,
    death_failures: int,
    death_successes: int,
    rolagem_d20: int,
) -> ResultadoTesteMorte:
    """PHB: 1=falha extra; 20=recupera 1 PV; ≥10=sucesso; senão falha."""
    hp_atual = max(0, int(hp))
    if hp_atual > 0:
        return ResultadoTesteMorte(0, 0, hp_atual, StatusVida.VIVO)

    falhas = max(0, int(death_failures))
    sucessos = max(0, int(death_successes))
    roll = int(rolagem_d20)

    if roll == 20:
        return ResultadoTesteMorte(0, 0, 1, StatusVida.VIVO)
    if roll == 1:
        falhas += 2
    elif roll >= 10:
        sucessos += 1
    else:
        falhas += 1

    status = verificar_morte(0, falhas, sucessos)
    return ResultadoTesteMorte(falhas, sucessos, 0, status)


@dataclass
class ResultadoDanoHp:
    hp_atual: int
    death_failures: int
    death_successes: int
    status: StatusVida
    morte_instantanea: bool = False


def aplicar_dano_hp(
    hp_atual: int,
    hp_max: int,
    death_failures: int,
    death_successes: int,
    dano: int,
    *,
    is_critico: bool = False,
    status_vida: Optional[str | StatusVida] = None,
) -> ResultadoDanoHp:
    """Aplica dano com regras PHB: morte instantânea, falhas em 0 PV, queda de estabilizado."""
    hp = max(0, int(hp_atual))
    hp_max = max(1, int(hp_max))
    dano = max(0, int(dano))
    falhas = max(0, int(death_failures))
    sucessos = max(0, int(death_successes))
    status_atual = _status_vida_de_valor(status_vida)

    if status_atual == StatusVida.MORTO or falhas >= 3:
        return ResultadoDanoHp(hp, falhas, sucessos, StatusVida.MORTO)

    incremento_falha = 2 if is_critico else 1

    if hp > 0:
        if dano >= hp:
            restante = dano - hp
            if restante >= hp_max:
                return ResultadoDanoHp(0, falhas, sucessos, StatusVida.MORTO, True)
            return ResultadoDanoHp(0, 0, 0, StatusVida.INCONSCIENTE)
        return ResultadoDanoHp(hp - dano, falhas, sucessos, StatusVida.VIVO)

    if status_atual == StatusVida.ESTABILIZADO:
        falhas = incremento_falha
        sucessos = 0
    else:
        falhas += incremento_falha

    if falhas >= 3:
        return ResultadoDanoHp(0, falhas, sucessos, StatusVida.MORTO)
    return ResultadoDanoHp(0, falhas, sucessos, StatusVida.INCONSCIENTE)


@dataclass
class ResultadoEstabilizar:
    death_failures: int
    death_successes: int
    status: StatusVida
    rolagem: Optional[int] = None
    total_medicina: Optional[int] = None
    sucesso: bool = True


def estabilizar_combatente(
    hp_atual: int,
    *,
    metodo: str = "medicina",
    mod_medicina: int = 0,
    rolagem_d20: Optional[int] = None,
    rng: Optional[Callable[[int, int], int]] = None,
) -> ResultadoEstabilizar:
    """Estabiliza combatente a 0 PV (Medicina CD 10 ou magia/efeito)."""
    if hp_atual > 0:
        raise ValueError("Só é possível estabilizar com 0 PV")

    m = (metodo or "medicina").strip().lower()
    if m == "magia":
        return ResultadoEstabilizar(0, 3, StatusVida.ESTABILIZADO, sucesso=True)

    roll = int(rolagem_d20) if rolagem_d20 is not None else rolar_d20(rng=rng)
    total = roll + int(mod_medicina)
    if total < 10:
        return ResultadoEstabilizar(
            death_failures=0,
            death_successes=0,
            status=StatusVida.INCONSCIENTE,
            rolagem=roll,
            total_medicina=total,
            sucesso=False,
        )
    return ResultadoEstabilizar(
        0,
        3,
        StatusVida.ESTABILIZADO,
        rolagem=roll,
        total_medicina=total,
        sucesso=True,
    )


def registrar_teste_morte(
    combatente: Combatente,
    rolagem_d20: int,
) -> StatusVida:
    """Atualiza falhas/sucessos de morte (1d20: 1=falha extra, 20=recupera 1 PV)."""
    resultado = aplicar_teste_morte(
        combatente.hp,
        combatente.death_failures,
        combatente.death_successes,
        rolagem_d20,
    )
    combatente.death_failures = resultado.death_failures
    combatente.death_successes = resultado.death_successes
    combatente.hp = resultado.hp_atual
    return resultado.status


def ordenar_chave_iniciativa(
    iniciativa: int,
    dex_mod: int,
    nome: str = "",
) -> tuple[int, int, str]:
    """Empate: maior DES mod; depois nome (ordem estável)."""
    return (-int(iniciativa), -int(dex_mod), (nome or "").lower())


@dataclass
class EconomiaTurno:
    """Economia de ações PHB (resumo de mesa)."""

    acao_usada: bool = False
    bonus_acao_usada: bool = False
    movimento_usado_metros: float = 0.0
    reacao_usada: bool = False
    velocidade_metros: float = 9.0

    def as_dict(self) -> dict:
        return {
            "acao_usada": self.acao_usada,
            "bonus_acao_usada": self.bonus_acao_usada,
            "movimento_usado_metros": self.movimento_usado_metros,
            "reacao_usada": self.reacao_usada,
            "velocidade_metros": self.velocidade_metros,
        }


def economia_turno_de_dict(data: Optional[dict]) -> EconomiaTurno:
    if not isinstance(data, dict):
        return EconomiaTurno()
    return EconomiaTurno(
        acao_usada=bool(data.get("acao_usada")),
        bonus_acao_usada=bool(data.get("bonus_acao_usada")),
        movimento_usado_metros=float(data.get("movimento_usado_metros") or 0),
        reacao_usada=bool(data.get("reacao_usada")),
        velocidade_metros=float(data.get("velocidade_metros") or 9),
    )


def reset_economia_turno(*, velocidade_metros: float = 9.0) -> EconomiaTurno:
    return EconomiaTurno(velocidade_metros=velocidade_metros)


def gastar_acao_turno(
    economia: EconomiaTurno,
    tipo: str,
    *,
    metros: float = 0.0,
) -> EconomiaTurno:
    """Registra gasto de ação/movimento/reação; levanta ValueError se inválido."""
    t = (tipo or "").strip().lower()
    out = EconomiaTurno(
        acao_usada=economia.acao_usada,
        bonus_acao_usada=economia.bonus_acao_usada,
        movimento_usado_metros=economia.movimento_usado_metros,
        reacao_usada=economia.reacao_usada,
        velocidade_metros=economia.velocidade_metros,
    )
    if t == "reset":
        return reset_economia_turno(velocidade_metros=out.velocidade_metros)
    if t == "acao":
        if out.acao_usada:
            raise ValueError("Ação padrão já usada neste turno")
        out.acao_usada = True
        return out
    if t == "bonus_acao":
        if out.bonus_acao_usada:
            raise ValueError("Ação bônus já usada neste turno")
        out.bonus_acao_usada = True
        return out
    if t == "reacao":
        if out.reacao_usada:
            raise ValueError("Reação já usada nesta rodada")
        out.reacao_usada = True
        return out
    if t == "movimento":
        delta = max(0.0, float(metros))
        if out.movimento_usado_metros + delta > out.velocidade_metros + 0.01:
            raise ValueError("Movimento excede a velocidade do turno")
        out.movimento_usado_metros += delta
        return out
    raise ValueError(f"Tipo de ação inválido: {tipo}")


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

    def aplicar_dano(
        self,
        combatente_id: str,
        dano: int,
        *,
        is_critico: bool = False,
        status_vida: Optional[str | StatusVida] = None,
    ) -> ResultadoDanoHp:
        alvo = next(
            (c for c in self.combatentes if c.combatente_id == combatente_id), None
        )
        if alvo is None:
            raise ValueError("Combatente nao encontrado")
        status_atual = status_vida or verificar_morte(
            alvo.hp, alvo.death_failures, alvo.death_successes
        )
        resultado = aplicar_dano_hp(
            alvo.hp,
            alvo.max_hp,
            alvo.death_failures,
            alvo.death_successes,
            dano,
            is_critico=is_critico,
            status_vida=status_atual,
        )
        alvo.hp = resultado.hp_atual
        alvo.death_failures = resultado.death_failures
        alvo.death_successes = resultado.death_successes
        return resultado
