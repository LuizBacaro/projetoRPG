"""Modelos SQLAlchemy — Tormenta RPG."""

from app.games.tormenta.models.campanha import TormentaCampanha, TormentaSessaoCampanha
from app.games.tormenta.models.combate import TormentaCombate
from app.games.tormenta.models.consumivel import (
    TormentaConsumivel,
    TormentaConsumivelPersonagem,
)
from app.games.tormenta.models.equipamento import (
    TormentaEquipamento,
    TormentaEquipamentoPersonagem,
)
from app.games.tormenta.models.magia_personagem import TormentaMagiaPersonagem
from app.games.tormenta.models.personagem import TormentaPersonagem
from app.games.tormenta.models.talento import TormentaTalento, TormentaTalentoPersonagem

__all__ = [
    "TormentaCampanha",
    "TormentaSessaoCampanha",
    "TormentaCombate",
    "TormentaPersonagem",
    "TormentaTalento",
    "TormentaTalentoPersonagem",
    "TormentaEquipamento",
    "TormentaEquipamentoPersonagem",
    "TormentaConsumivel",
    "TormentaConsumivelPersonagem",
    "TormentaMagiaPersonagem",
]
