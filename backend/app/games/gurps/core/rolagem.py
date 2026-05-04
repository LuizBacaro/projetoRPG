"""Utilitários de rolagem GURPS 4e (3d6)."""

from __future__ import annotations

import random
import re
from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class ResultadoTeste3d6:
    dados: List[int]
    total: int
    nivel_efetivo: int
    sucesso: bool
    margem: int
    sucesso_decisivo: bool
    falha_critica: bool


@dataclass(frozen=True)
class ExpressaoDano:
    quantidade_dados: int
    modificador: int


@dataclass(frozen=True)
class ResultadoDano:
    expressao: str
    dados_rolados: List[int]
    quantidade_dados: int
    modificador: int
    total_sem_modificador: int
    total: int


_DANO_RE = re.compile(r"^\s*(\d+)d(?:\s*([+-])\s*(\d+))?\s*$", re.IGNORECASE)


def parse_expressao_dano(expressao: str) -> ExpressaoDano:
    m = _DANO_RE.match(str(expressao or ""))
    if not m:
        raise ValueError("expressao de dano inválida; use formato Nd, Nd+M ou Nd-M")
    qtd = int(m.group(1))
    if qtd <= 0:
        raise ValueError("quantidade de dados deve ser maior que zero")
    sinal = m.group(2)
    mag = int(m.group(3)) if m.group(3) is not None else 0
    mod = -mag if sinal == "-" else mag
    return ExpressaoDano(quantidade_dados=qtd, modificador=mod)


def rolar_dano(
    expressao: str,
    rng: Optional[random.Random] = None,
    dados_forcados: Optional[List[int]] = None,
) -> ResultadoDano:
    parsed = parse_expressao_dano(expressao)
    if dados_forcados is not None:
        if len(dados_forcados) != parsed.quantidade_dados or any(
            (d < 1 or d > 6) for d in dados_forcados
        ):
            raise ValueError("dados_forcados incompatíveis com a expressão de dano")
        dados = list(dados_forcados)
    else:
        r = rng if rng is not None else random.Random()
        dados = [r.randint(1, 6) for _ in range(parsed.quantidade_dados)]
    subtotal = int(sum(dados))
    total = subtotal + parsed.modificador
    return ResultadoDano(
        expressao=expressao,
        dados_rolados=dados,
        quantidade_dados=parsed.quantidade_dados,
        modificador=parsed.modificador,
        total_sem_modificador=subtotal,
        total=total,
    )


def calcular_nivel_efetivo(nh_base: int, modificadores: Optional[List[int]] = None) -> int:
    return int(nh_base) + int(sum(modificadores or []))


def _is_sucesso_decisivo(total: int, nivel_efetivo: int) -> bool:
    # GURPS 4e: 3-4 sempre; 5 com NH 15+; 6 com NH 16+.
    if total <= 4:
        return True
    if total == 5 and nivel_efetivo >= 15:
        return True
    if total == 6 and nivel_efetivo >= 16:
        return True
    return False


def _is_falha_critica(total: int, nivel_efetivo: int) -> bool:
    # GURPS 4e: 18 sempre; 17 para NH <= 15; 16 para NH <= 6.
    if total == 18:
        return True
    if total == 17 and nivel_efetivo <= 15:
        return True
    if total == 16 and nivel_efetivo <= 6:
        return True
    return False


def avaliar_teste_3d6(
    nivel_efetivo: int,
    dados: Optional[List[int]] = None,
    rng: Optional[random.Random] = None,
) -> ResultadoTeste3d6:
    if dados is None:
        r = rng if rng is not None else random.Random()
        dados = [r.randint(1, 6), r.randint(1, 6), r.randint(1, 6)]
    if len(dados) != 3 or any((d < 1 or d > 6) for d in dados):
        raise ValueError("dados deve conter exatamente 3 valores entre 1 e 6")

    total = int(sum(dados))
    sucesso = total <= nivel_efetivo
    margem = (nivel_efetivo - total) if sucesso else (total - nivel_efetivo)
    sucesso_decisivo = _is_sucesso_decisivo(total, nivel_efetivo)
    falha_critica = _is_falha_critica(total, nivel_efetivo)

    return ResultadoTeste3d6(
        dados=list(dados),
        total=total,
        nivel_efetivo=nivel_efetivo,
        sucesso=sucesso,
        margem=margem,
        sucesso_decisivo=sucesso_decisivo,
        falha_critica=falha_critica,
    )

