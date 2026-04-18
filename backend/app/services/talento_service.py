"""
service/talento_service.py
SRP: Lógica de negócio para Talentos
SOLID: Dependency Injection do Repository
"""

from sqlalchemy.orm import Session
from typing import List
from app.repositories.talento_repository import TalentoRepository, TalentoJogadorRepository
from app.schemas.talento import TalentoCreate, TalentoJogadorCreate, TalentoJogadorListResponse


class TalentoService:
    """Lógica de negócio para talentos"""

    def __init__(self, db: Session):
        self.db = db

    def criar_talento(self, talento: TalentoCreate):
        """Cria um novo talento"""
        # Verifica se talento já existe
        talento_existente = TalentoRepository.obter_talento_por_nome(self.db, talento.nome)
        if talento_existente:
            if talento_existente.deleted_at is not None:
                return TalentoRepository.restaurar_talento(self.db, talento_existente, talento)
            return talento_existente
        
        return TalentoRepository.criar_talento(self.db, talento)

    def listar_talentos(self, skip: int = 0, limit: int = 100):
        """Lista todos os talentos"""
        return TalentoRepository.listar_talentos(self.db, skip, limit)

    def adicionar_talento_jogador(self, combatente_id: int, talento_jogador: TalentoJogadorCreate) -> TalentoJogadorListResponse:
        """Adiciona um talento ao combatente e retorna resposta serializada"""
        talento = TalentoRepository.obter_talento(self.db, talento_jogador.talento_id)
        if not talento:
            raise ValueError(f"Talento com ID {talento_jogador.talento_id} não encontrado")

        TalentoJogadorRepository.adicionar_talento(self.db, combatente_id, talento_jogador)
        
        return TalentoJogadorListResponse(
            id=talento.id,
            nome=talento.nome,
            descricao=talento.descricao,
            pagina_referencia=talento.pagina_referencia,
            prerequisitos=talento.prerequisitos,
            secao=talento.secao
        )

    def obter_talentos_jogador(self, combatente_id: int) -> List[TalentoJogadorListResponse]:
        """Obtém todos os talentos de um combatente com detalhes"""
        talentos_jogador = TalentoJogadorRepository.obter_talentos_jogador_detalhado(
            self.db, combatente_id
        )

        return [
            TalentoJogadorListResponse(
                id=tal["talento_id"],
                nome=tal["talento_nome"],
                descricao=tal["talento_descricao"],
                pagina_referencia=tal["talento_pagina_referencia"],
                prerequisitos=tal.get("talento_prerequisitos"),
                secao=tal.get("talento_secao"),
            )
            for tal in talentos_jogador
        ]

    def remover_talento_jogador(self, combatente_id: int, talento_id: int) -> bool:
        """Remove um talento do combatente"""
        return TalentoJogadorRepository.remover_talento(
            self.db, combatente_id, talento_id
        )
