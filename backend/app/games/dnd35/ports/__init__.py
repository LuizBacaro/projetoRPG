from app.games.dnd35.ports.armaduras import (
    ArmaduraProtecaoCatalogProtocol,
    ArmaduraProtecaoJogadorLinksProtocol,
)
from app.games.dnd35.ports.ataques import AtaqueRepositoryProtocol, CombatenteRepositoryForAtaqueProtocol
from app.games.dnd35.ports.campanhas import CampanhaRepositoryProtocol, SessaoCampanhaRepositoryProtocol
from app.games.dnd35.ports.consumiveis import ConsumivelCatalogProtocol, ConsumivelJogadorLinksProtocol
from app.games.dnd35.ports.condicoes import CondicaoRepositoryProtocol
from app.games.dnd35.ports.divindade_custom import DivindadeCustomRepositoryProtocol
from app.games.dnd35.ports.grimorio import GrimorioRepositoryProtocol
from app.games.dnd35.ports.equipamentos import (
    EquipamentoCatalogProtocol,
    EquipamentoJogadorLinksProtocol,
)
from app.games.dnd35.ports.magia_preparada import MagiaPreparadaRepositoryProtocol
from app.games.dnd35.ports.magias import MagiaCriacaoParaImportProtocol, MagiaRepositoryProtocol
from app.games.dnd35.ports.pericias import (
    PericiaCatalogRestoreProtocol,
    PericiaJogadorRepositoryProtocol,
    PericiaRepositoryProtocol,
)
from app.games.dnd35.ports.talentos import TalentoCatalogProtocol, TalentoJogadorLinksProtocol
from app.games.dnd35.ports.repositories import (
    CombatenteGetByIdProtocol,
    CombatenteRepositoryForCombateProtocol,
    CombatenteRepositoryProtocol,
    CombateRepositoryProtocol,
)

__all__ = [
    "ArmaduraProtecaoCatalogProtocol",
    "ArmaduraProtecaoJogadorLinksProtocol",
    "AtaqueRepositoryProtocol",
    "CampanhaRepositoryProtocol",
    "CombatenteGetByIdProtocol",
    "CombatenteRepositoryForAtaqueProtocol",
    "CombatenteRepositoryForCombateProtocol",
    "CombatenteRepositoryProtocol",
    "CombateRepositoryProtocol",
    "CondicaoRepositoryProtocol",
    "ConsumivelCatalogProtocol",
    "ConsumivelJogadorLinksProtocol",
    "DivindadeCustomRepositoryProtocol",
    "EquipamentoCatalogProtocol",
    "EquipamentoJogadorLinksProtocol",
    "GrimorioRepositoryProtocol",
    "MagiaCriacaoParaImportProtocol",
    "MagiaPreparadaRepositoryProtocol",
    "MagiaRepositoryProtocol",
    "PericiaCatalogRestoreProtocol",
    "PericiaJogadorRepositoryProtocol",
    "PericiaRepositoryProtocol",
    "SessaoCampanhaRepositoryProtocol",
    "TalentoCatalogProtocol",
    "TalentoJogadorLinksProtocol",
]
