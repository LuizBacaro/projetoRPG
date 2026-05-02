"""
Service de armaduras/itens de proteção
SRP: regras de negócio
"""

from typing import Optional

from sqlalchemy.orm import Session

from app.games.dnd35.models.armadura_protecao import ArmaduraProtecao
from app.games.dnd35.ports import ArmaduraProtecaoCatalogProtocol, ArmaduraProtecaoJogadorLinksProtocol
from app.games.dnd35.repositories.armadura_protecao_repository import (
    ArmaduraProtecaoJogadorRepository,
    ArmaduraProtecaoRepository,
)
from app.games.dnd35.schemas.armadura_protecao import (
    ArmaduraProtecaoCreate,
    ArmaduraProtecaoJogadorCreate,
    ArmaduraProtecaoJogadorListResponse,
)
from app.games.dnd35.models.combatente import Combatente


class ArmaduraProtecaoService:
    def __init__(
        self,
        db: Session,
        *,
        catalog: Optional[ArmaduraProtecaoCatalogProtocol] = None,
        jogador_links: Optional[ArmaduraProtecaoJogadorLinksProtocol] = None,
    ):
        self.db = db
        self._catalog = catalog or ArmaduraProtecaoRepository(db)
        self._jogador = jogador_links or ArmaduraProtecaoJogadorRepository(db)

    def criar_item(self, item: ArmaduraProtecaoCreate) -> ArmaduraProtecao:
        existente = self.db.query(ArmaduraProtecao).filter(ArmaduraProtecao.nome == item.nome).first()
        if existente:
            return existente
        return self._catalog.criar_item(item)

    def listar_itens(self, skip: int = 0, limit: int = 100) -> list[ArmaduraProtecao]:
        return self._catalog.listar(skip, limit)

    def obter_item(self, item_id: int) -> Optional[ArmaduraProtecao]:
        return self._catalog.obter_por_id(item_id)

    def adicionar_item_jogador(
        self,
        combatente_id: int,
        payload: ArmaduraProtecaoJogadorCreate,
    ) -> ArmaduraProtecaoJogadorListResponse:
        combatente = self.db.query(Combatente).filter(Combatente.id == combatente_id).first()
        if not combatente:
            raise ValueError(f"Combatente {combatente_id} não encontrado")

        item = self._catalog.obter_por_id(payload.item_id)
        if not item or not item.ativo:
            raise ValueError(f"Item de proteção {payload.item_id} não encontrado")

        self._jogador.adicionar_item(combatente_id, payload)
        self._recalcular_defesas_com_item_protecao(combatente)

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
        itens = self._jogador.listar_detalhado(combatente_id)
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
        removido = self._jogador.remover_item(combatente_id, item_id)
        if not removido:
            return False
        combatente = self.db.query(Combatente).filter(Combatente.id == combatente_id).first()
        if combatente:
            self._recalcular_defesas_com_item_protecao(combatente)
        return True

    def bonus_ca_total(self, combatente_id: int) -> int:
        itens = self._jogador.listar_detalhado(combatente_id)
        return sum(int(row.get("item_bonus_ca") or 0) for row in itens)

    def _recalcular_defesas_com_item_protecao(self, combatente: Combatente) -> None:
        """
        Aplica regra incremental/decremental baseada nos itens atuais:
        - Toque = 10 + mod DES
        - Surpresa = 10 + bônus CA total dos itens
        - CA = 10 + mod DES + bônus CA total dos itens
        """
        des = int(getattr(combatente, "destreza", 10) or 10)
        mod_des = (des - 10) // 2
        bonus_armadura = self.bonus_ca_total(combatente.id)
        combatente.toque = 10 + mod_des
        combatente.surpresa = 10 + bonus_armadura
        combatente.ca = 10 + mod_des + bonus_armadura
        self.db.add(combatente)
        self.db.commit()
        self.db.refresh(combatente)
