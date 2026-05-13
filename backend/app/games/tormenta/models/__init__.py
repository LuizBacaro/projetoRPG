"""Modelos SQLAlchemy — Tormenta RPG."""

from app.games.tormenta.models.combate import TormentaCombate
from app.games.tormenta.models.personagem import TormentaPersonagem
from app.games.tormenta.models.talento import TormentaTalento, TormentaTalentoPersonagem
from app.games.tormenta.models.equipamento import TormentaEquipamento, TormentaEquipamentoPersonagem
from app.games.tormenta.models.consumivel import TormentaConsumivel, TormentaConsumivelPersonagem

__all__ = [
    "TormentaCombate",
    "TormentaPersonagem",
    "TormentaTalento",
    "TormentaTalentoPersonagem",
    "TormentaEquipamento",
    "TormentaEquipamentoPersonagem",
    "TormentaConsumivel",
    "TormentaConsumivelPersonagem",
]
