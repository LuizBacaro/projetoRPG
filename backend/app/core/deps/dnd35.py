"""Factories de injeção — domínio D&D 3.5."""

from fastapi import Depends
from sqlalchemy.orm import Session

from app.games.dnd35.repositories.armadura_protecao_repository import (
    ArmaduraProtecaoJogadorRepository,
    ArmaduraProtecaoRepository,
)
from app.games.dnd35.repositories.campanha_repository import CampanhaRepository
from app.games.dnd35.repositories.combate_repository import CombateRepository
from app.games.dnd35.repositories.combatente_repository import CombatenteRepository
from app.games.dnd35.repositories.companheiro_animal_repository import (
    CompanheiroAnimalRepository,
)
from app.games.dnd35.repositories.condicao_repository import CondicaoRepository
from app.games.dnd35.repositories.consumivel_repository import (
    ConsumivelJogadorRepository,
    ConsumivelRepository,
)
from app.games.dnd35.repositories.divindade_custom_repository import (
    DivindadeCustomRepository,
)
from app.games.dnd35.repositories.equipamento_repository import (
    EquipamentoJogadorRepository,
    EquipamentoRepository,
)
from app.games.dnd35.repositories.grimorio_repository import GrimorioRepository
from app.games.dnd35.repositories.magia_repository import MagiaRepository
from app.games.dnd35.repositories.pericia_repository import (
    PericiaJogadorRepository,
    PericiaRepository,
)
from app.games.dnd35.repositories.sessao_campanha_repository import (
    SessaoCampanhaRepository,
)
from app.games.dnd35.repositories.talento_repository import (
    TalentoJogadorRepository,
    TalentoRepository,
)
from app.games.dnd35.services.armadura_protecao_service import ArmaduraProtecaoService
from app.games.dnd35.services.campanha_service import CampanhaService
from app.games.dnd35.services.combate_service import CombateService
from app.games.dnd35.services.combatente_service import CombatenteService
from app.games.dnd35.services.companheiro_animal_service import CompanheiroAnimalService
from app.games.dnd35.services.condicao_service import CondicaoService
from app.games.dnd35.services.consumivel_service import ConsumivelService
from app.games.dnd35.services.equipamento_service import EquipamentoService
from app.games.dnd35.services.grimorio_service import GrimorioService
from app.games.dnd35.services.magia_import_service import MagiaImportService
from app.games.dnd35.services.magia_service import MagiaService
from app.games.dnd35.services.pericia_service import PericiaService
from app.games.dnd35.services.sessao_campanha_service import SessaoCampanhaService
from app.games.dnd35.services.talento_service import TalentoService
from app.shared.core.database import get_db

from .file_storage import get_file_service


def get_combatente_repository(db: Session = Depends(get_db)) -> CombatenteRepository:
    return CombatenteRepository(db)


def get_combate_repository(db: Session = Depends(get_db)) -> CombateRepository:
    return CombateRepository(db)


def get_magia_repository(db: Session = Depends(get_db)) -> MagiaRepository:
    return MagiaRepository(db)


def get_grimorio_repository(db: Session = Depends(get_db)) -> GrimorioRepository:
    return GrimorioRepository(db)


def get_campanha_repository(db: Session = Depends(get_db)) -> CampanhaRepository:
    return CampanhaRepository(db)


def get_sessao_campanha_repository(
    db: Session = Depends(get_db),
) -> SessaoCampanhaRepository:
    return SessaoCampanhaRepository(db)


def get_condicao_repository(db: Session = Depends(get_db)) -> CondicaoRepository:
    return CondicaoRepository(db)


def get_divindade_custom_repository(
    db: Session = Depends(get_db),
) -> DivindadeCustomRepository:
    return DivindadeCustomRepository(db)


def get_pericia_repository(db: Session = Depends(get_db)) -> PericiaRepository:
    return PericiaRepository(db)


def get_pericia_jogador_repository(
    db: Session = Depends(get_db),
) -> PericiaJogadorRepository:
    return PericiaJogadorRepository(db)


def get_companheiro_animal_repository(
    db: Session = Depends(get_db),
) -> CompanheiroAnimalRepository:
    return CompanheiroAnimalRepository(db)


def get_consumivel_repository(db: Session = Depends(get_db)) -> ConsumivelRepository:
    return ConsumivelRepository(db)


def get_consumivel_jogador_repository(
    db: Session = Depends(get_db),
) -> ConsumivelJogadorRepository:
    return ConsumivelJogadorRepository(db)


def get_equipamento_repository(db: Session = Depends(get_db)) -> EquipamentoRepository:
    return EquipamentoRepository(db)


def get_equipamento_jogador_repository(
    db: Session = Depends(get_db),
) -> EquipamentoJogadorRepository:
    return EquipamentoJogadorRepository(db)


def get_armadura_protecao_repository(
    db: Session = Depends(get_db),
) -> ArmaduraProtecaoRepository:
    return ArmaduraProtecaoRepository(db)


def get_armadura_protecao_jogador_repository(
    db: Session = Depends(get_db),
) -> ArmaduraProtecaoJogadorRepository:
    return ArmaduraProtecaoJogadorRepository(db)


def get_talento_repository(db: Session = Depends(get_db)) -> TalentoRepository:
    return TalentoRepository(db)


def get_talento_jogador_repository(
    db: Session = Depends(get_db),
) -> TalentoJogadorRepository:
    return TalentoJogadorRepository(db)


def get_combatente_service(
    repository: CombatenteRepository = Depends(get_combatente_repository),
    condicao_repo: CondicaoRepository = Depends(get_condicao_repository),
    divindade_custom_repo: DivindadeCustomRepository = Depends(
        get_divindade_custom_repository
    ),
) -> CombatenteService:
    file_service = get_file_service()
    return CombatenteService(
        repository,
        file_service,
        condicao_repo,
        divindade_custom_repo,
    )


def get_pericia_service(
    db: Session = Depends(get_db),
    pericia_repository: PericiaRepository = Depends(get_pericia_repository),
    pericia_jogador_repository: PericiaJogadorRepository = Depends(
        get_pericia_jogador_repository
    ),
    combatente_repository: CombatenteRepository = Depends(get_combatente_repository),
) -> PericiaService:
    return PericiaService(
        db,
        pericia_repository=pericia_repository,
        pericia_jogador_repository=pericia_jogador_repository,
        combatente_repository=combatente_repository,
    )


def get_companheiro_animal_service(
    db: Session = Depends(get_db),
    repo: CompanheiroAnimalRepository = Depends(get_companheiro_animal_repository),
    combatente_repository: CombatenteRepository = Depends(get_combatente_repository),
) -> CompanheiroAnimalService:
    return CompanheiroAnimalService(
        db,
        repo=repo,
        combatente_repo=combatente_repository,
    )


def get_consumivel_service(
    db: Session = Depends(get_db),
    consumivel_catalog: ConsumivelRepository = Depends(get_consumivel_repository),
    consumivel_jogador: ConsumivelJogadorRepository = Depends(
        get_consumivel_jogador_repository
    ),
    combatente_repository: CombatenteRepository = Depends(get_combatente_repository),
) -> ConsumivelService:
    return ConsumivelService(
        db,
        catalog=consumivel_catalog,
        jogador_links=consumivel_jogador,
        combatente_repo=combatente_repository,
    )


def get_equipamento_service(
    db: Session = Depends(get_db),
    equipamento_catalog: EquipamentoRepository = Depends(get_equipamento_repository),
    equipamento_jogador: EquipamentoJogadorRepository = Depends(
        get_equipamento_jogador_repository
    ),
) -> EquipamentoService:
    return EquipamentoService(
        db,
        catalog=equipamento_catalog,
        jogador_links=equipamento_jogador,
    )


def get_armadura_protecao_service(
    db: Session = Depends(get_db),
    armadura_catalog: ArmaduraProtecaoRepository = Depends(
        get_armadura_protecao_repository
    ),
    armadura_jogador: ArmaduraProtecaoJogadorRepository = Depends(
        get_armadura_protecao_jogador_repository
    ),
) -> ArmaduraProtecaoService:
    return ArmaduraProtecaoService(
        db,
        catalog=armadura_catalog,
        jogador_links=armadura_jogador,
    )


def get_talento_service(
    db: Session = Depends(get_db),
    talento_catalog: TalentoRepository = Depends(get_talento_repository),
    talento_jogador: TalentoJogadorRepository = Depends(get_talento_jogador_repository),
) -> TalentoService:
    return TalentoService(
        db,
        catalog=talento_catalog,
        jogador_links=talento_jogador,
    )


def get_combate_service(
    combate_repo: CombateRepository = Depends(get_combate_repository),
    combatente_repo: CombatenteRepository = Depends(get_combatente_repository),
) -> CombateService:
    return CombateService(combate_repo, combatente_repo)


def get_magia_service(
    repository: MagiaRepository = Depends(get_magia_repository),
) -> MagiaService:
    return MagiaService(repository)


def get_magia_import_service(
    magia_service: MagiaService = Depends(get_magia_service),
) -> MagiaImportService:
    return MagiaImportService(magia_service)


def get_grimorio_service(
    grimorio_repository: GrimorioRepository = Depends(get_grimorio_repository),
    magia_repository: MagiaRepository = Depends(get_magia_repository),
) -> GrimorioService:
    return GrimorioService(grimorio_repository, magia_repository)


def get_campanha_service(
    campanha_repository: CampanhaRepository = Depends(get_campanha_repository),
    combatente_repository: CombatenteRepository = Depends(get_combatente_repository),
) -> CampanhaService:
    return CampanhaService(campanha_repository, combatente_repository)


def get_sessao_campanha_service(
    sessao_repository: SessaoCampanhaRepository = Depends(
        get_sessao_campanha_repository
    ),
    campanha_repository: CampanhaRepository = Depends(get_campanha_repository),
) -> SessaoCampanhaService:
    return SessaoCampanhaService(sessao_repository, campanha_repository)


def get_condicao_service(db: Session = Depends(get_db)) -> CondicaoService:
    condicao_repo = CondicaoRepository(db)
    combatente_repo = CombatenteRepository(db)
    return CondicaoService(condicao_repo, combatente_repo)
