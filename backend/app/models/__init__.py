# Importar modelos em ordem para evitar dependências circulares

from .pericia import Pericia, PericiaClasse, PericiaJogador
from .condicao import Condicao
from .combatente_condicao import CombatenteCondicao
from .magia import Magia
from .ataque import Ataque, MagiaSlot, MagiaPreparada
from .equipamento import Equipamento, EquipamentoJogador
from .talento import Talento, TalentoJogador
from .combatente import Combatente
from .usuario import Usuario

__all__ = [
    "Pericia",
    "PericiaClasse",
    "PericiaJogador",
    "Condicao",
    "CombatenteCondicao",
    "Magia",
    "Ataque",
    "MagiaSlot",
    "MagiaPreparada",
    "Equipamento",
    "EquipamentoJogador",
    "Talento",
    "TalentoJogador",
    "Combatente",
    "Usuario",
]
