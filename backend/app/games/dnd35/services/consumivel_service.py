from sqlalchemy.orm import Session

from app.games.dnd35.models.combatente import Combatente
from app.games.dnd35.repositories.consumivel_repository import (
    ConsumivelJogadorRepository,
    ConsumivelRepository,
)
from app.games.dnd35.schemas.consumivel import (
    ConsumivelCreate,
    ConsumivelJogadorCreate,
    ConsumivelJogadorListResponse,
)


class ConsumivelService:
    def __init__(self, db: Session):
        self.db = db

    def criar(self, payload: ConsumivelCreate):
        existente = ConsumivelRepository.obter_por_nome(self.db, payload.nome)
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
        return ConsumivelRepository.criar(self.db, payload.model_dump())

    def listar(
        self,
        skip: int,
        limit: int,
        tipo: str | None = None,
        categoria: str | None = None,
        busca: str | None = None,
    ):
        return ConsumivelRepository.listar(
            self.db,
            skip,
            limit,
            tipo=tipo,
            categoria=categoria,
            busca=busca,
        )

    def obter(self, consumivel_id: int):
        return ConsumivelRepository.obter(self.db, consumivel_id)

    def deletar(self, consumivel_id: int) -> bool:
        return ConsumivelRepository.deletar(self.db, consumivel_id)

    def adicionar_jogador(
        self, combatente_id: int, payload: ConsumivelJogadorCreate
    ) -> ConsumivelJogadorListResponse:
        combatente = (
            self.db.query(Combatente).filter(Combatente.id == combatente_id).first()
        )
        if not combatente:
            raise ValueError(f"Combatente {combatente_id} não encontrado")

        consumivel = ConsumivelRepository.obter(self.db, payload.consumivel_id)
        if not consumivel:
            raise ValueError(f"Consumível {payload.consumivel_id} não encontrado")

        item = ConsumivelJogadorRepository.adicionar(
            self.db, combatente_id, payload.consumivel_id, payload.quantidade
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
        rows = ConsumivelJogadorRepository.listar_detalhado(self.db, combatente_id)
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
        return ConsumivelJogadorRepository.remover(self.db, combatente_id, consumivel_id)
