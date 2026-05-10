from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from app.games.dnd35.ports.consumiveis import (
    ConsumivelCatalogProtocol,
    ConsumivelJogadorLinksProtocol,
)
from app.games.dnd35.ports.repositories import CombatenteGetByIdProtocol
from app.games.dnd35.repositories.combatente_repository import CombatenteRepository
from app.games.dnd35.repositories.consumivel_repository import (
    ConsumivelJogadorRepository,
    ConsumivelRepository,
)
from app.games.dnd35.schemas.consumivel import (
    ConsumivelCreate,
    ConsumivelJogadorCreate,
    ConsumivelJogadorListResponse,
)
from app.shared.exceptions.custom_exceptions import CombatenteNaoEncontrado


class ConsumivelService:
    def __init__(
        self,
        db: Session,
        *,
        catalog: Optional[ConsumivelCatalogProtocol] = None,
        jogador_links: Optional[ConsumivelJogadorLinksProtocol] = None,
        combatente_repo: Optional[CombatenteGetByIdProtocol] = None,
    ):
        self.db = db
        self._catalog = catalog or ConsumivelRepository(db)
        self._jogador = jogador_links or ConsumivelJogadorRepository(db)
        self._combatente = combatente_repo or CombatenteRepository(db)

    def _verificar_combatente(self, combatente_id: int):
        c = self._combatente.get_by_id(combatente_id)
        if not c:
            raise CombatenteNaoEncontrado(combatente_id)
        return c

    def criar(self, payload: ConsumivelCreate):
        existente = self._catalog.obter_por_nome(payload.nome)
        if existente and existente.deleted_at is None:
            return existente
        if existente and existente.deleted_at is not None:
            existente.deleted_at = None
            existente.ativo = True
            for k, v in payload.model_dump().items():
                setattr(existente, k, v)
            self.db.commit()
            self.db.refresh(existente)
            return existente
        return self._catalog.criar(payload.model_dump())

    def listar(
        self,
        skip: int,
        limit: int,
        tipo: str | None = None,
        categoria: str | None = None,
        busca: str | None = None,
    ):
        return self._catalog.listar(
            skip,
            limit,
            tipo=tipo,
            categoria=categoria,
            busca=busca,
        )

    def obter(self, consumivel_id: int):
        return self._catalog.obter(consumivel_id)

    def deletar(self, consumivel_id: int) -> bool:
        return self._catalog.deletar(consumivel_id)

    def adicionar_jogador(
        self, combatente_id: int, payload: ConsumivelJogadorCreate
    ) -> ConsumivelJogadorListResponse:
        self._verificar_combatente(combatente_id)

        consumivel = self._catalog.obter(payload.consumivel_id)
        if not consumivel:
            raise ValueError(f"Consumível {payload.consumivel_id} não encontrado")

        item = self._jogador.adicionar(
            combatente_id, payload.consumivel_id, payload.quantidade
        )
        return ConsumivelJogadorListResponse(
            id=consumivel.id,
            nome=consumivel.nome,
            descricao=consumivel.descricao,
            pagina_referencia=consumivel.pagina_referencia,
            categoria=consumivel.categoria,
            tipo=consumivel.tipo,
            custo=consumivel.custo,
            peso=consumivel.peso,
            quantidade=item.quantidade,
        )

    def listar_jogador(self, combatente_id: int) -> list[ConsumivelJogadorListResponse]:
        self._verificar_combatente(combatente_id)
        rows = self._jogador.listar_detalhado(combatente_id)
        return [
            ConsumivelJogadorListResponse(
                id=r["consumivel_id"],
                nome=r["consumivel_nome"],
                descricao=r["consumivel_descricao"],
                pagina_referencia=r["consumivel_pagina_referencia"],
                categoria=r["consumivel_categoria"],
                tipo=r["consumivel_tipo"],
                custo=r["consumivel_custo"],
                peso=r["consumivel_peso"],
                quantidade=r["jogador_quantidade"],
            )
            for r in rows
        ]

    def remover_jogador(self, combatente_id: int, consumivel_id: int) -> bool:
        self._verificar_combatente(combatente_id)
        return self._jogador.remover(combatente_id, consumivel_id)
