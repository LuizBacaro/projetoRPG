"""Factories de injeção — domínio Tormenta."""

from fastapi import Depends
from sqlalchemy.orm import Session

from app.games.tormenta.repositories.combate_repository import TormentaCombateRepository
from app.games.tormenta.repositories.personagem_repository import TormentaPersonagemRepository
from app.games.tormenta.services.personagem_consumiveis_service import TormentaPersonagemConsumiveisService
from app.games.tormenta.services.personagem_equipamentos_service import TormentaPersonagemEquipamentosService
from app.games.tormenta.services.personagem_inventario_legado_service import (
    TormentaPersonagemInventarioLegadoService,
)
from app.games.tormenta.services.combate_service import TormentaCombateService
from app.games.tormenta.services.personagem_service import TormentaPersonagemService
from app.games.tormenta.services.personagem_magias_service import TormentaPersonagemMagiasService
from app.games.tormenta.services.personagem_talentos_service import TormentaPersonagemTalentosService
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
