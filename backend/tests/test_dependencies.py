from app.core.dependencies import (
    get_combate_repository,
    get_combate_service,
    get_combatente_repository,
    get_combatente_service,
)
from app.games.dnd35.repositories.combate_repository import CombateRepository
from app.games.dnd35.repositories.combatente_repository import CombatenteRepository
from app.games.dnd35.repositories.condicao_repository import CondicaoRepository
from app.games.dnd35.repositories.divindade_custom_repository import (
    DivindadeCustomRepository,
)
from app.games.dnd35.services.combate_service import CombateService
from app.games.dnd35.services.combatente_service import CombatenteService


def test_dependency_factories_reutilizam_objetos_injetados(test_db):
    combatente_repo = get_combatente_repository(test_db)
    combate_repo = get_combate_repository(test_db)
    condicao_repo = CondicaoRepository(test_db)
    divindade_repo = DivindadeCustomRepository(test_db)
    combatente_service = get_combatente_service(
        combatente_repo, condicao_repo, divindade_repo
    )
    combate_service = get_combate_service(combate_repo, combatente_repo)

    assert isinstance(combatente_repo, CombatenteRepository)
    assert isinstance(combate_repo, CombateRepository)
    assert isinstance(combatente_service, CombatenteService)
    assert isinstance(combate_service, CombateService)
    assert combatente_repo.db is test_db
    assert combate_repo.db is test_db
    assert combatente_service.repository is combatente_repo
    assert combate_service.combate_repo is combate_repo
    assert combate_service.combatente_repo is combatente_repo
