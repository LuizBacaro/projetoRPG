"""Domar Criatura — regra da classe Treinador (Heróis de Arton v1.1, p.20)."""

from __future__ import annotations

from typing import Dict

# Tabela de dano psíquico não-letal por nível de Treinador (p.20)
# nivel → dado (ex.: "2d8")
_DANO_POR_NIVEL: Dict[int, str] = {
    2: "2d8",
    6: "4d8",
    10: "6d8",
    14: "8d8",
    18: "10d8",
}

# Duração do controle por nível: 5: cena, 8: dia (antes: 1 rodada)
_DURACAO_CONTROLE: Dict[int, str] = {
    2: "instantaneo",
    5: "cena",
    8: "dia",
}


def dano_domar_por_nivel(nivel_treinador: int) -> str:
    """Dados de dano psíquico não-letal para Domar Criatura no nível dado.

    Retorna a string de dados correspondente (ex. ``"4d8"``).
    Antes do nível 2, retorna ``"0"``.
    """
    try:
        nv = max(1, int(nivel_treinador))
    except (TypeError, ValueError):
        nv = 1
    resultado = "0"
    for nivel_limiar, dado in sorted(_DANO_POR_NIVEL.items()):
        if nv >= nivel_limiar:
            resultado = dado
    return resultado


def duracao_controle_por_nivel(nivel_treinador: int) -> str:
    """Duração do controle de criatura rendida (``instantaneo`` | ``cena`` | ``dia``)."""
    try:
        nv = max(1, int(nivel_treinador))
    except (TypeError, ValueError):
        nv = 1
    duracao = "instantaneo"
    for nivel_limiar, dur in sorted(_DURACAO_CONTROLE.items()):
        if nv >= nivel_limiar:
            duracao = dur
    return duracao


def dano_domar(nivel_treinador: int) -> str:
    """Alias de ``dano_domar_por_nivel`` (contrato HA-2)."""
    return dano_domar_por_nivel(nivel_treinador)


def resolver_domar(
    teste_adestramento: int,
    teste_vontade_criatura: int,
    nivel_treinador: int,
) -> Dict[str, object]:
    """Resolve uma tentativa de Domar Criatura.

    O Treinador rola Adestramento oposto à Vontade da criatura.
    - Sucesso: criatura recebe dano psíquico não-letal conforme nível.
    - Criatura a 0 PV: rende-se (flag ``rendida=True``).
    - A partir do nível 5: pode controlar criatura rendida gastando PM = ND dela.

    Retorna um dict com: ``sucesso``, ``dado_dano``, ``duracao_controle``,
    ``pode_controlar`` (nível ≥ 5), ``rendida`` (controle da UI — backend não
    sabe os PV atuais, apenas se o teste passou).
    """
    sucesso = teste_adestramento > teste_vontade_criatura
    dado = dano_domar_por_nivel(nivel_treinador)
    duracao = duracao_controle_por_nivel(nivel_treinador)
    pode_controlar = nivel_treinador >= 5

    return {
        "sucesso": sucesso,
        "dado_dano": dado,
        "duracao_controle": duracao,
        "pode_controlar": pode_controlar,
    }
