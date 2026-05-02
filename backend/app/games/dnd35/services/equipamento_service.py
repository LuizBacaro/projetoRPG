"""
Service de Equipamento (D&D 3.5)
SRP: lógica de negócio dos equipamentos.

Localização: este módulo pertence ao pacote `app.games.dnd35.services`
porque depende exclusivamente das regras de equipamentos do D&D 3.5.
Existe um shim em `app.services.equipamento_service` que re-exporta as
classes durante a reorganização multi-jogo.
"""

from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app.games.dnd35.models.equipamento import Equipamento, EquipamentoJogador
from app.games.dnd35.ports import EquipamentoCatalogProtocol, EquipamentoJogadorLinksProtocol
from app.games.dnd35.repositories.equipamento_repository import (
    EquipamentoJogadorRepository,
    EquipamentoRepository,
)
from app.games.dnd35.schemas.equipamento import (
    EquipamentoCreate,
    EquipamentoJogadorCreate,
    EquipamentoJogadorListResponse,
)
from app.games.dnd35.models.combatente import Combatente


class EquipamentoService:
    """Serviço de lógica de negócio para equipamentos"""

    def __init__(
        self,
        db: Session,
        *,
        catalog: Optional[EquipamentoCatalogProtocol] = None,
        jogador_links: Optional[EquipamentoJogadorLinksProtocol] = None,
    ):
        self.db = db
        self._catalog = catalog or EquipamentoRepository(db)
        self._jogador = jogador_links or EquipamentoJogadorRepository(db)

    # ========== EQUIPAMENTOS DISPONÍVEIS ==========

    def criar_equipamento(self, equipamento: EquipamentoCreate) -> Equipamento:
        """Cria um novo equipamento"""
        equipamento_existente = (
            self.db.query(Equipamento)
            .filter(Equipamento.nome == equipamento.nome)
            .first()
        )

        if equipamento_existente:
            if equipamento_existente.deleted_at is not None:
                return self._catalog.restaurar_equipamento(
                    equipamento_existente, equipamento
                )
            return equipamento_existente

        return self._catalog.criar_equipamento(equipamento)

    def obter_equipamento(self, equipamento_id: int) -> Optional[Equipamento]:
        """Obtém um equipamento por ID"""
        return self._catalog.obter_equipamento(equipamento_id)

    def listar_todos_equipamentos(
        self, skip: int = 0, limit: int = 100
    ) -> List[Equipamento]:
        """Lista todos os equipamentos disponíveis"""
        return self._catalog.listar_equipamentos(skip, limit)

    def atualizar_equipamento(
        self, equipamento_id: int, equipamento_data: Dict
    ) -> Optional[Equipamento]:
        """Atualiza um equipamento"""
        db_equipamento = self._catalog.obter_equipamento(equipamento_id)

        if not db_equipamento:
            return None

        return self._catalog.atualizar_equipamento(equipamento_id, equipamento_data)

    def deletar_equipamento(self, equipamento_id: int) -> bool:
        """Deleta um equipamento"""
        return self._catalog.deletar_equipamento(equipamento_id)

    # ========== EQUIPAMENTOS DO JOGADOR ==========

    def adicionar_equipamento_jogador(
        self,
        combatente_id: int,
        equipamento_jogador: EquipamentoJogadorCreate,
    ) -> EquipamentoJogadorListResponse:
        """Adiciona um equipamento ao combatente"""
        combatente = (
            self.db.query(Combatente)
            .filter(Combatente.id == combatente_id)
            .first()
        )
        if not combatente:
            raise ValueError(f"Combatente {combatente_id} não encontrado")

        equipamento = self._catalog.obter_equipamento(
            equipamento_jogador.equipamento_id
        )
        if not equipamento:
            raise ValueError(
                f"Equipamento {equipamento_jogador.equipamento_id} não encontrado"
            )

        eq_jogador = self._jogador.adicionar_equipamento(combatente_id, equipamento_jogador)

        return EquipamentoJogadorListResponse(
            id=equipamento.id,
            nome=equipamento.nome,
            descricao=equipamento.descricao,
            pagina_referencia=equipamento.pagina_referencia,
            quantidade=eq_jogador.quantidade,
            categoria=equipamento.categoria,
            subcategoria=equipamento.subcategoria,
            custo=equipamento.custo,
            dano_pequeno=equipamento.dano_pequeno,
            dano_medio=equipamento.dano_medio,
            critico=equipamento.critico,
            alcance_incremento=equipamento.alcance_incremento,
            peso=equipamento.peso,
            tipo_dano=equipamento.tipo_dano,
        )

    def obter_equipamentos_jogador(
        self, combatente_id: int
    ) -> List[EquipamentoJogadorListResponse]:
        """Obtém todos os equipamentos de um combatente com detalhes"""
        equipamentos_jogador = self._jogador.obter_equipamentos_jogador_detalhado(
            combatente_id
        )

        return [
            EquipamentoJogadorListResponse(
                id=eq["equipamento_id"],
                nome=eq["equipamento_nome"],
                descricao=eq["equipamento_descricao"],
                pagina_referencia=eq["equipamento_pagina_referencia"],
                quantidade=eq["jogador_quantidade"],
                categoria=eq.get("equipamento_categoria"),
                subcategoria=eq.get("equipamento_subcategoria"),
                custo=eq.get("equipamento_custo"),
                dano_pequeno=eq.get("equipamento_dano_pequeno"),
                dano_medio=eq.get("equipamento_dano_medio"),
                critico=eq.get("equipamento_critico"),
                alcance_incremento=eq.get("equipamento_alcance_incremento"),
                peso=eq.get("equipamento_peso"),
                tipo_dano=eq.get("equipamento_tipo_dano"),
            )
            for eq in equipamentos_jogador
        ]

    def remover_equipamento_jogador(
        self, combatente_id: int, equipamento_id: int
    ) -> bool:
        """Remove um equipamento do combatente"""
        return self._jogador.remover_equipamento(combatente_id, equipamento_id)

    def atualizar_quantidade_equipamento(
        self,
        combatente_id: int,
        equipamento_id: int,
        quantidade: int,
    ) -> Optional[EquipamentoJogador]:
        """Atualiza a quantidade de um equipamento"""
        if quantidade < 0:
            raise ValueError("Quantidade não pode ser negativa")

        if quantidade == 0:
            self._jogador.remover_equipamento(combatente_id, equipamento_id)
            return None

        return self._jogador.atualizar_quantidade(
            combatente_id, equipamento_id, quantidade
        )
