"""
Service de Talento (D&D 3.5)

Localização: `app.games.dnd35.services.talento_service`. Shim em
`app.services.talento_service` durante a reorganização multi-jogo.
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.games.dnd35.ports import TalentoCatalogProtocol, TalentoJogadorLinksProtocol
from app.games.dnd35.repositories.talento_repository import (
    TalentoJogadorRepository,
    TalentoRepository,
)
from app.games.dnd35.schemas.talento import (
    TalentoCreate,
    TalentoJogadorCreate,
    TalentoJogadorListResponse,
)


class TalentoService:
    """Lógica de negócio para talentos"""

    def __init__(
        self,
        db: Session,
        *,
        catalog: Optional[TalentoCatalogProtocol] = None,
        jogador_links: Optional[TalentoJogadorLinksProtocol] = None,
    ):
        self.db = db
        self._catalog = catalog or TalentoRepository(db)
        self._jogador = jogador_links or TalentoJogadorRepository(db)

    def criar_talento(self, talento: TalentoCreate):
        """Cria um novo talento"""
        talento_existente = self._catalog.obter_talento_por_nome(talento.nome)
        if talento_existente:
            if talento_existente.deleted_at is not None:
                return self._catalog.restaurar_talento(talento_existente, talento)
            return talento_existente

        return self._catalog.criar_talento(talento)

    def listar_talentos(self, skip: int = 0, limit: int = 100):
        """Lista todos os talentos"""
        return self._catalog.listar_talentos(skip, limit)

    def adicionar_talento_jogador(
        self,
        combatente_id: int,
        talento_jogador: TalentoJogadorCreate,
    ) -> TalentoJogadorListResponse:
        """Adiciona um talento ao combatente e retorna resposta serializada"""
        talento = self._catalog.obter_talento(talento_jogador.talento_id)
        if not talento:
            raise ValueError(
                f"Talento com ID {talento_jogador.talento_id} não encontrado"
            )

        self._jogador.adicionar_talento(combatente_id, talento_jogador)

        return TalentoJogadorListResponse(
            id=talento.id,
            nome=talento.nome,
            descricao=talento.descricao,
            pagina_referencia=talento.pagina_referencia,
            prerequisitos=talento.prerequisitos,
            secao=talento.secao,
        )

    def obter_talentos_jogador(
        self, combatente_id: int
    ) -> List[TalentoJogadorListResponse]:
        """Obtém todos os talentos de um combatente com detalhes"""
        talentos_jogador = self._jogador.obter_talentos_jogador_detalhado(combatente_id)

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

    def remover_talento_jogador(
        self, combatente_id: int, talento_id: int
    ) -> bool:
        """Remove um talento do combatente"""
        return self._jogador.remover_talento(combatente_id, talento_id)
