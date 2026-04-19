"""
Service de Equipamento
Single Responsibility: Lógica de negócio dos equipamentos
SOLID: Dependency Injection via repository
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.equipamento import Equipamento, EquipamentoJogador
from app.models.combatente import Combatente
from app.schemas.equipamento import (
    EquipamentoCreate, EquipamentoJogadorCreate, EquipamentoJogadorListResponse
)
from app.repositories.equipamento_repository import EquipamentoRepository, EquipamentoJogadorRepository


class EquipamentoService:
    """Serviço de lógica de negócio para equipamentos"""

    def __init__(self, db: Session):
        self.db = db

    # ========== EQUIPAMENTOS DISPONÍVEIS ==========

    def criar_equipamento(self, equipamento: EquipamentoCreate) -> Equipamento:
        """Cria um novo equipamento"""
        # Verificar duplicata
        equipamento_existente = self.db.query(Equipamento).filter(
            Equipamento.nome == equipamento.nome
        ).first()
        
        if equipamento_existente:
            if equipamento_existente.deleted_at is not None:
                return EquipamentoRepository.restaurar_equipamento(self.db, equipamento_existente, equipamento)
            return equipamento_existente
        
        return EquipamentoRepository.criar_equipamento(self.db, equipamento)

    def obter_equipamento(self, equipamento_id: int) -> Optional[Equipamento]:
        """Obtém um equipamento por ID"""
        return EquipamentoRepository.obter_equipamento(self.db, equipamento_id)

    def listar_todos_equipamentos(self, skip: int = 0, limit: int = 100) -> List[Equipamento]:
        """Lista todos os equipamentos disponíveis"""
        return EquipamentoRepository.listar_equipamentos(self.db, skip, limit)

    def atualizar_equipamento(self, equipamento_id: int, equipamento_data: dict) -> Optional[Equipamento]:
        """Atualiza um equipamento"""
        db_equipamento = EquipamentoRepository.obter_equipamento(self.db, equipamento_id)
        
        if not db_equipamento:
            return None
        
        return EquipamentoRepository.atualizar_equipamento(self.db, equipamento_id, equipamento_data)

    def deletar_equipamento(self, equipamento_id: int) -> bool:
        """Deleta um equipamento"""
        return EquipamentoRepository.deletar_equipamento(self.db, equipamento_id)

    # ========== EQUIPAMENTOS DO JOGADOR ==========

    def adicionar_equipamento_jogador(
        self, 
        combatente_id: int, 
        equipamento_jogador: EquipamentoJogadorCreate
    ) -> EquipamentoJogadorListResponse:
        """Adiciona um equipamento ao combatente"""
        # Verificar se combatente existe
        combatente = self.db.query(Combatente).filter(Combatente.id == combatente_id).first()
        if not combatente:
            raise ValueError(f"Combatente {combatente_id} não encontrado")
        
        # Verificar se equipamento existe
        equipamento = EquipamentoRepository.obter_equipamento(self.db, equipamento_jogador.equipamento_id)
        if not equipamento:
            raise ValueError(f"Equipamento {equipamento_jogador.equipamento_id} não encontrado")
        
        eq_jogador = EquipamentoJogadorRepository.adicionar_equipamento(
            self.db, combatente_id, equipamento_jogador
        )
        
        # Retornar com dados do equipamento
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

    def obter_equipamentos_jogador(self, combatente_id: int) -> List[EquipamentoJogadorListResponse]:
        """Obtém todos os equipamentos de um combatente com detalhes"""
        equipamentos_jogador = EquipamentoJogadorRepository.obter_equipamentos_jogador_detalhado(
            self.db, combatente_id
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

    def remover_equipamento_jogador(self, combatente_id: int, equipamento_id: int) -> bool:
        """Remove um equipamento do combatente"""
        return EquipamentoJogadorRepository.remover_equipamento(
            self.db, combatente_id, equipamento_id
        )

    def atualizar_quantidade_equipamento(
        self, 
        combatente_id: int, 
        equipamento_id: int, 
        quantidade: int
    ) -> Optional[EquipamentoJogador]:
        """Atualiza a quantidade de um equipamento"""
        if quantidade < 0:
            raise ValueError("Quantidade não pode ser negativa")
        
        if quantidade == 0:
            # Se quantidade é 0, remove o equipamento
            EquipamentoJogadorRepository.remover_equipamento(self.db, combatente_id, equipamento_id)
            return None
        
        return EquipamentoJogadorRepository.atualizar_quantidade(
            self.db, combatente_id, equipamento_id, quantidade
        )
