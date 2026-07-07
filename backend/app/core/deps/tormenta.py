"""Factories de injeção — domínio Tormenta."""

from fastapi import Depends
from sqlalchemy.orm import Session

from app.games.tormenta.repositories.campanha_repository import (
    TormentaCampanhaRepository,
)
from app.games.tormenta.repositories.campanha_solicitacao_repository import (
    TormentaCampanhaSolicitacaoRepository,
)
from app.games.tormenta.repositories.combate_repository import TormentaCombateRepository
from app.games.tormenta.repositories.personagem_repository import (
    TormentaPersonagemRepository,
)
from app.games.tormenta.repositories.sessao_campanha_repository import (
    TormentaSessaoCampanhaRepository,
)
from app.games.tormenta.services.campanha_service import TormentaCampanhaService
from app.games.tormenta.services.campanha_solicitacao_service import (
    TormentaCampanhaSolicitacaoService,
)
from app.games.tormenta.services.combate_service import TormentaCombateService
from app.games.tormenta.services.personagem_consumiveis_service import (
    TormentaPersonagemConsumiveisService,
)
from app.games.tormenta.services.personagem_equipamentos_service import (
    TormentaPersonagemEquipamentosService,
)
from app.games.tormenta.services.personagem_inventario_legado_service import (
    TormentaPersonagemInventarioLegadoService,
)
from app.games.tormenta.services.personagem_magias_service import (
    TormentaPersonagemMagiasService,
)
from app.games.tormenta.services.personagem_service import TormentaPersonagemService
from app.games.tormenta.services.personagem_talentos_service import (
    TormentaPersonagemTalentosService,
)
from app.games.tormenta.services.sessao_campanha_service import (
    TormentaSessaoCampanhaService,
)
from app.shared.core.database import get_db
from app.shared.core.deps import get_usuario_atual
from app.shared.models.usuario import Usuario


def get_tormenta_personagem_repository(
    db: Session = Depends(get_db),
) -> TormentaPersonagemRepository:
    return TormentaPersonagemRepository(db)


def get_tormenta_personagem_service(
    repository: TormentaPersonagemRepository = Depends(
        get_tormenta_personagem_repository
    ),
) -> TormentaPersonagemService:
    return TormentaPersonagemService(repository)


def get_tormenta_personagem_talentos_service(
    db: Session = Depends(get_db),
) -> TormentaPersonagemTalentosService:
    return TormentaPersonagemTalentosService(db)


def get_tormenta_personagem_magias_service(
    db: Session = Depends(get_db),
) -> TormentaPersonagemMagiasService:
    return TormentaPersonagemMagiasService(db)


def get_tormenta_personagem_progressao_service(
    db: Session = Depends(get_db),
):
    from app.games.tormenta.services.personagem_progressao_service import (
        TormentaPersonagemProgressaoService,
    )

    return TormentaPersonagemProgressaoService(db)


def get_tormenta_personagem_equipamentos_service(
    db: Session = Depends(get_db),
) -> TormentaPersonagemEquipamentosService:
    return TormentaPersonagemEquipamentosService(db)


def get_tormenta_personagem_consumiveis_service(
    db: Session = Depends(get_db),
) -> TormentaPersonagemConsumiveisService:
    return TormentaPersonagemConsumiveisService(db)


def get_tormenta_personagem_inventario_legado_service(
    db: Session = Depends(get_db),
) -> TormentaPersonagemInventarioLegadoService:
    return TormentaPersonagemInventarioLegadoService(db)


def get_tormenta_combate_service(
    usuario: Usuario = Depends(get_usuario_atual),
    db: Session = Depends(get_db),
) -> TormentaCombateService:
    return TormentaCombateService(
        TormentaCombateRepository(db),
        TormentaPersonagemRepository(db),
        usuario.id,
    )


def get_tormenta_campanha_repository(
    db: Session = Depends(get_db),
) -> TormentaCampanhaRepository:
    return TormentaCampanhaRepository(db)


def get_tormenta_sessao_campanha_repository(
    db: Session = Depends(get_db),
) -> TormentaSessaoCampanhaRepository:
    return TormentaSessaoCampanhaRepository(db)


def get_tormenta_campanha_solicitacao_repository(
    db: Session = Depends(get_db),
) -> TormentaCampanhaSolicitacaoRepository:
    return TormentaCampanhaSolicitacaoRepository(db)


def get_tormenta_campanha_solicitacao_service(
    solicitacao_repository: TormentaCampanhaSolicitacaoRepository = Depends(
        get_tormenta_campanha_solicitacao_repository
    ),
    campanha_repository: TormentaCampanhaRepository = Depends(
        get_tormenta_campanha_repository
    ),
    personagem_repository: TormentaPersonagemRepository = Depends(
        get_tormenta_personagem_repository
    ),
) -> TormentaCampanhaSolicitacaoService:
    return TormentaCampanhaSolicitacaoService(
        solicitacao_repository, campanha_repository, personagem_repository
    )


def get_tormenta_campanha_service(
    campanha_repository: TormentaCampanhaRepository = Depends(
        get_tormenta_campanha_repository
    ),
    personagem_repository: TormentaPersonagemRepository = Depends(
        get_tormenta_personagem_repository
    ),
) -> TormentaCampanhaService:
    return TormentaCampanhaService(campanha_repository, personagem_repository)


def get_tormenta_sessao_campanha_service(
    sessao_repository: TormentaSessaoCampanhaRepository = Depends(
        get_tormenta_sessao_campanha_repository
    ),
    campanha_repository: TormentaCampanhaRepository = Depends(
        get_tormenta_campanha_repository
    ),
) -> TormentaSessaoCampanhaService:
    return TormentaSessaoCampanhaService(sessao_repository, campanha_repository)
