# Modelos SQLAlchemy — ordem importa para ForeignKeys.
# Hub global: `usuario`, `game`. D&D 3.5: `app.games.dnd35.models`.

from app.games.dnd35.models.armadura_protecao import (
    ArmaduraProtecao,
    ArmaduraProtecaoJogador,
)
from app.games.dnd35.models.ataque import Ataque, MagiaPreparada, MagiaSlot
from app.games.dnd35.models.campanha import Campanha
from app.games.dnd35.models.combate import Combate, CombateHistorico
from app.games.dnd35.models.combatente import Combatente
from app.games.dnd35.models.combatente_condicao import CombatenteCondicao
from app.games.dnd35.models.condicao import Condicao
from app.games.dnd35.models.consumivel import Consumivel, ConsumivelJogador
from app.games.dnd35.models.divindade_custom import DivindadeCustom
from app.games.dnd35.models.equipamento import Equipamento, EquipamentoJogador
from app.games.dnd35.models.grimorio import (
    GrimorioHistoricoTroca,
    GrimorioMagia,
    GrimorioNotificacao,
)
from app.games.dnd35.models.magia import Magia, MagiaClasse
from app.games.dnd35.models.pericia import Pericia, PericiaClasse, PericiaJogador
from app.games.dnd35.models.sessao_campanha import SessaoCampanha
from app.games.dnd35.models.talento import Talento, TalentoJogador
from app.games.gurps.models.campanha import GurpsCampanha
from app.games.gurps.models.catalogo_ficha import (
    GurpsCatalogoFichaDesvantagem,
    GurpsCatalogoFichaPericia,
    GurpsCatalogoFichaVantagem,
)
from app.games.gurps.models.combate import GurpsCombate
from app.games.gurps.models.personagem import (
    GurpsPersonagem,
    GurpsPersonagemDesvantagem,
    GurpsPersonagemPericia,
    GurpsPersonagemVantagem,
)
from app.games.gurps.models.sessao_campanha import GurpsSessaoCampanha
from app.games.tormenta.models.personagem import TormentaPersonagem
from app.shared.models.game import Game, UserGameMembership
from app.shared.models.usuario import PerfilUsuario, Usuario

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
    "Consumivel",
    "ConsumivelJogador",
    "Combatente",
    "Usuario",
    "PerfilUsuario",
    "Combate",
    "CombateHistorico",
    "GrimorioMagia",
    "GrimorioHistoricoTroca",
    "GrimorioNotificacao",
    "DivindadeCustom",
    "Campanha",
    "SessaoCampanha",
    "Game",
    "UserGameMembership",
    "GurpsCampanha",
    "GurpsSessaoCampanha",
    "GurpsCombate",
    "GurpsPersonagem",
    "GurpsPersonagemVantagem",
    "GurpsPersonagemDesvantagem",
    "GurpsPersonagemPericia",
    "GurpsCatalogoFichaVantagem",
    "GurpsCatalogoFichaDesvantagem",
    "GurpsCatalogoFichaPericia",
    "TormentaPersonagem",
]
