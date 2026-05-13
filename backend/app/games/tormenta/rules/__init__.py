"""Regras de jogo Tormenta 20 (puros Python, sem I/O de rede)."""

from app.games.tormenta.rules.atributos_t20 import (
    custo_total_compra_seis_atributos,
    custo_valor_atributo_compra,
    lista_custos_compra,
    lista_pericias_com_atributo,
    modificador_atributo_t20,
    pontos_iniciais_compra,
)
from app.games.tormenta.rules.racas_t20 import lista_racas_mb

__all__ = [
    "modificador_atributo_t20",
    "custo_valor_atributo_compra",
    "custo_total_compra_seis_atributos",
    "pontos_iniciais_compra",
    "lista_custos_compra",
    "lista_pericias_com_atributo",
    "lista_racas_mb",
]
