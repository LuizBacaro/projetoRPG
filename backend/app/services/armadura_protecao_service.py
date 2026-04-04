"""
Service de armaduras/itens de proteção
SRP: regras de negócio
"""

from typing import Optional

from sqlalchemy.orm import Session

from app.models.combatente import Combatente
from app.models.armadura_protecao import ArmaduraProtecao
from app.repositories.armadura_protecao_repository import (
    ArmaduraProtecaoJogadorRepository,
    ArmaduraProtecaoRepository,
)
from app.schemas.armadura_protecao import (
    ArmaduraProtecaoCreate,
    ArmaduraProtecaoJogadorCreate,
    ArmaduraProtecaoJogadorListResponse,
)


class ArmaduraProtecaoService:
    def __init__(self, db: Session):
        self.db = db

    def criar_item(self, item: ArmaduraProtecaoCreate) -> ArmaduraProtecao:
        existente = self.db.query(ArmaduraProtecao).filter(ArmaduraProtecao.nome == item.nome).first()
        if existente:
            return existente
        return ArmaduraProtecaoRepository.criar_item(self.db, item)

    def listar_itens(self, skip: int = 0, limit: int = 100) -> list[ArmaduraProtecao]:
        return ArmaduraProtecaoRepository.listar(self.db, skip, limit)

    def obter_item(self, item_id: int) -> Optional[ArmaduraProtecao]:
        return ArmaduraProtecaoRepository.obter_por_id(self.db, item_id)

    def adicionar_item_jogador(
        self,
        combatente_id: int,
        payload: ArmaduraProtecaoJogadorCreate,
    ) -> ArmaduraProtecaoJogadorListResponse:
        combatente = self.db.query(Combatente).filter(Combatente.id == combatente_id).first()
        if not combatente:
            raise ValueError(f"Combatente {combatente_id} não encontrado")

        item = ArmaduraProtecaoRepository.obter_por_id(self.db, payload.item_id)
        if not item or not item.ativo:
            raise ValueError(f"Item de proteção {payload.item_id} não encontrado")

        ArmaduraProtecaoJogadorRepository.adicionar_item(self.db, combatente_id, payload)

        return ArmaduraProtecaoJogadorListResponse(
            id=item.id,
            nome=item.nome,
            tipo=item.tipo,
            bonus_ca=item.bonus_ca,
            des_max=item.des_max,
            penalidade=item.penalidade,
            falha_arcana=item.falha_arcana,
            deslocamento=item.deslocamento,
            peso=item.peso,
            propriedades_especiais=item.propriedades_especiais,
        )

    def listar_itens_jogador(self, combatente_id: int) -> list[ArmaduraProtecaoJogadorListResponse]:
        itens = ArmaduraProtecaoJogadorRepository.listar_detalhado(self.db, combatente_id)
        return [
            ArmaduraProtecaoJogadorListResponse(
                id=row["item_id"],
                nome=row["item_nome"],
                tipo=row["item_tipo"],
                bonus_ca=row["item_bonus_ca"],
                des_max=row["item_des_max"],
                penalidade=row["item_penalidade"],
                falha_arcana=row["item_falha_arcana"],
                deslocamento=row["item_deslocamento"],
                peso=row["item_peso"],
                propriedades_especiais=row["item_propriedades_especiais"],
            )
            for row in itens
        ]

    def remover_item_jogador(self, combatente_id: int, item_id: int) -> bool:
        return ArmaduraProtecaoJogadorRepository.remover_item(self.db, combatente_id, item_id)

    def bonus_ca_total(self, combatente_id: int) -> int:
        itens = ArmaduraProtecaoJogadorRepository.listar_detalhado(self.db, combatente_id)
        return sum(int(row.get("item_bonus_ca") or 0) for row in itens)
