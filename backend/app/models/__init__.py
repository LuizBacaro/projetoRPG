# Importar modelos em ordem para evitar dependências circulares

from .pericia import Pericia, PericiaClasse, PericiaJogador
from .condicao import Condicao
from .combatente_condicao import CombatenteCondicao
from .magia import Magia, MagiaClasse
from .ataque import Ataque, MagiaSlot, MagiaPreparada
from .equipamento import Equipamento, EquipamentoJogador
from .armadura_protecao import ArmaduraProtecao, ArmaduraProtecaoJogador
from .talento import Talento, TalentoJogador
from .combatente import Combatente
from .usuario import Usuario
from .combate import CombateHistorico
from .grimorio import GrimorioMagia, GrimorioHistoricoTroca, GrimorioNotificacao

__all__ = [
    "Pericia",
    "PericiaClasse",
    "PericiaJogador",
    "Condicao",
    "CombatenteCondicao",
    "Magia",
    "MagiaClasse",
    "Ataque",
    "MagiaSlot",
    "MagiaPreparada",
    "Equipamento",
    "EquipamentoJogador",
    "ArmaduraProtecao",
    "ArmaduraProtecaoJogador",
    "Talento",
    "TalentoJogador",
    "Combatente",
    "Usuario",
    "CombateHistorico",
    "GrimorioMagia",
    "GrimorioHistoricoTroca",
    "GrimorioNotificacao",
]
