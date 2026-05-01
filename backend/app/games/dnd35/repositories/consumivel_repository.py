from sqlalchemy import and_, or_
from sqlalchemy.orm import Session, aliased

from app.games.dnd35.models.consumivel import Consumivel, ConsumivelJogador
from app.repositories.base import (
    apply_not_deleted,
    commit_with_rollback,
    soft_delete_entity,
)


class ConsumivelRepository:
    @staticmethod
    def criar(db: Session, payload: dict) -> Consumivel:
        obj = Consumivel(**payload)
        db.add(obj)
        commit_with_rollback(db)
        db.refresh(obj)
        return obj

    @staticmethod
    def obter(db: Session, consumivel_id: int) -> Consumivel | None:
        return (
            apply_not_deleted(db.query(Consumivel), Consumivel)
            .filter(Consumivel.id == consumivel_id)
            .first()
        )

    @staticmethod
    def obter_por_nome(db: Session, nome: str) -> Consumivel | None:
        return db.query(Consumivel).filter(Consumivel.nome == nome).first()

    @staticmethod
    def listar(
        db: Session,
        skip: int,
        limit: int,
        tipo: str | None = None,
        categoria: str | None = None,
        busca: str | None = None,
    ) -> list[Consumivel]:
        query = (
            apply_not_deleted(db.query(Consumivel), Consumivel)
            .filter(Consumivel.ativo == True)  # noqa: E712
        )

        tipo_norm = (tipo or "").strip().lower()
        categoria_norm = (categoria or "").strip().lower()
        busca_norm = (busca or "").strip()

        if tipo_norm:
            query = query.filter(Consumivel.tipo.ilike(tipo_norm))

        if categoria_norm:
            query = query.filter(Consumivel.categoria.ilike(f"%{categoria_norm}%"))

        if busca_norm:
            termo = f"%{busca_norm}%"
            query = query.filter(
                or_(
                    Consumivel.nome.ilike(termo),
                    Consumivel.descricao.ilike(termo),
                    Consumivel.categoria.ilike(termo),
                    Consumivel.tipo.ilike(termo),
                    Consumivel.custo.ilike(termo),
                    Consumivel.pagina_referencia.ilike(termo),
                )
            )

        return query.order_by(Consumivel.nome.asc()).offset(skip).limit(limit).all()

    @staticmethod
    def deletar(db: Session, consumivel_id: int) -> bool:
        item = ConsumivelRepository.obter(db, consumivel_id)
        if not item:
            return False
        return soft_delete_entity(db, item)


class ConsumivelJogadorRepository:
    @staticmethod
    def adicionar(
        db: Session, combatente_id: int, consumivel_id: int, quantidade: int
    ) -> ConsumivelJogador:
        existente = (
            db.query(ConsumivelJogador)
            .filter(
                and_(
                    ConsumivelJogador.combatente_id == combatente_id,
                    ConsumivelJogador.consumivel_id == consumivel_id,
                )
            )
            .first()
        )
        if existente:
            existente.quantidade += quantidade
            commit_with_rollback(db)
            db.refresh(existente)
            return existente

        obj = ConsumivelJogador(
            combatente_id=combatente_id,
            consumivel_id=consumivel_id,
            quantidade=quantidade,
        )
        db.add(obj)
        commit_with_rollback(db)
        db.refresh(obj)
        return obj

    @staticmethod
    def listar_detalhado(db: Session, combatente_id: int) -> list[dict]:
        cj = aliased(ConsumivelJogador, name="cj")
        c = aliased(Consumivel, name="c")
        rows = (
            db.query(
                cj.consumivel_id.label("consumivel_id"),
                cj.quantidade.label("jogador_quantidade"),
                c.nome.label("consumivel_nome"),
                c.descricao.label("consumivel_descricao"),
                c.pagina_referencia.label("consumivel_pagina_referencia"),
                c.categoria.label("consumivel_categoria"),
                c.tipo.label("consumivel_tipo"),
                c.custo.label("consumivel_custo"),
                c.peso.label("consumivel_peso"),
            )
            .join(c, c.id == cj.consumivel_id)
            .filter(cj.combatente_id == combatente_id, c.deleted_at.is_(None))
            .order_by(c.nome.asc())
            .all()
        )
        return [dict(r._mapping) for r in rows]

    @staticmethod
    def remover(db: Session, combatente_id: int, consumivel_id: int) -> bool:
        obj = (
            db.query(ConsumivelJogador)
            .filter(
                and_(
                    ConsumivelJogador.combatente_id == combatente_id,
                    ConsumivelJogador.consumivel_id == consumivel_id,
                )
            )
            .first()
        )
        if not obj:
            return False
        db.delete(obj)
        commit_with_rollback(db)
        return True
