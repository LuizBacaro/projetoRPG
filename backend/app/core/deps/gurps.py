"""Factories de injeção — domínio GURPS."""

from fastapi import Depends
from sqlalchemy.orm import Session

from app.games.gurps.repositories.campanha_repository import GurpsCampanhaRepository
from app.games.gurps.repositories.campanha_solicitacao_repository import (
    GurpsCampanhaSolicitacaoRepository,
)
from app.games.gurps.repositories.combate_repository import GurpsCombateRepository
from app.games.gurps.repositories.personagem_repository import GurpsPersonagemRepository
from app.games.gurps.repositories.sessao_campanha_repository import (
    GurpsSessaoCampanhaRepository,
)
from app.games.gurps.services.campanha_service import GurpsCampanhaService
from app.games.gurps.services.campanha_solicitacao_service import (
    GurpsCampanhaSolicitacaoService,
)
from app.games.gurps.services.combate_service import GurpsCombateService
from app.games.gurps.services.personagem_service import GurpsPersonagemService
from app.games.gurps.services.sessao_campanha_service import GurpsSessaoCampanhaService
from app.shared.core.database import get_db


def get_gurps_personagem_repository(
    db: Session = Depends(get_db),
) -> GurpsPersonagemRepository:
    return GurpsPersonagemRepository(db)


def get_gurps_campanha_repository(
    db: Session = Depends(get_db),
) -> GurpsCampanhaRepository:
    return GurpsCampanhaRepository(db)


def get_gurps_sessao_campanha_repository(
    db: Session = Depends(get_db),
) -> GurpsSessaoCampanhaRepository:
    return GurpsSessaoCampanhaRepository(db)


def get_gurps_combate_repository(
    db: Session = Depends(get_db),
) -> GurpsCombateRepository:
    return GurpsCombateRepository(db)


def get_gurps_personagem_service(
    repository: GurpsPersonagemRepository = Depends(get_gurps_personagem_repository),
) -> GurpsPersonagemService:
    return GurpsPersonagemService(repository)


def get_gurps_campanha_service(
    campanha_repository: GurpsCampanhaRepository = Depends(
        get_gurps_campanha_repository
    ),
    personagem_repository: GurpsPersonagemRepository = Depends(
        get_gurps_personagem_repository
    ),
) -> GurpsCampanhaService:
    return GurpsCampanhaService(campanha_repository, personagem_repository)


def get_gurps_sessao_campanha_service(
    sessao_repository: GurpsSessaoCampanhaRepository = Depends(
        get_gurps_sessao_campanha_repository
    ),
    campanha_repository: GurpsCampanhaRepository = Depends(
        get_gurps_campanha_repository
    ),
) -> GurpsSessaoCampanhaService:
    return GurpsSessaoCampanhaService(sessao_repository, campanha_repository)


def get_gurps_campanha_solicitacao_repository(
    db: Session = Depends(get_db),
) -> GurpsCampanhaSolicitacaoRepository:
    return GurpsCampanhaSolicitacaoRepository(db)


def get_gurps_campanha_solicitacao_service(
    solicitacao_repository: GurpsCampanhaSolicitacaoRepository = Depends(
        get_gurps_campanha_solicitacao_repository
    ),
    campanha_repository: GurpsCampanhaRepository = Depends(
        get_gurps_campanha_repository
    ),
    personagem_repository: GurpsPersonagemRepository = Depends(
        get_gurps_personagem_repository
    ),
) -> GurpsCampanhaSolicitacaoService:
    return GurpsCampanhaSolicitacaoService(
        solicitacao_repository, campanha_repository, personagem_repository
    )


def get_gurps_combate_service(
    combate_repo: GurpsCombateRepository = Depends(get_gurps_combate_repository),
    personagem_repo: GurpsPersonagemRepository = Depends(
        get_gurps_personagem_repository
    ),
) -> GurpsCombateService:
    return GurpsCombateService(combate_repo, personagem_repo)
