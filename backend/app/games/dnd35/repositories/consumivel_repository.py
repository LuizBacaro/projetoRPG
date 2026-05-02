from sqlalchemy import and_, or_
from sqlalchemy.orm import Session, aliased

from app.games.dnd35.models.consumivel import Consumivel, ConsumivelJogador
from app.repositories.base import (
    apply_not_deleted,
    commit_with_rollback,
    soft_delete_entity,
)


def _variantes_texto_unicode_para_filtro(valor: str) -> list[str]:
    """
    Gera variantes de capitalização em Python (Unicode-aware).
    SQLite compara ILIKE/LIKE sem folding correto fora de ASCII — ex.: 'óleo' não
    casa com coluna 'Óleo'. Igualdade exata com variantes resolve dev/prod.
    """
    s = (valor or "").strip()
    if not s:
        return []
    candidatos = {s, s.title(), s.capitalize(), s.upper()}
    return [c for c in candidatos if c]


class ConsumivelRepository:
    def __init__(self, db: Session):
        self.db = db

    def criar(self, payload: dict) -> Consumivel:
        obj = Consumivel(**payload)
        self.db.add(obj)
        commit_with_rollback(self.db)
        self.db.refresh(obj)
        return obj

    def obter(self, consumivel_id: int) -> Consumivel | None:
        return (
            apply_not_deleted(self.db.query(Consumivel), Consumivel)
            .filter(Consumivel.id == consumivel_id)
            .first()
        )

    def obter_por_nome(self, nome: str) -> Consumivel | None:
        return self.db.query(Consumivel).filter(Consumivel.nome == nome).first()

    def listar(
        self,
        skip: int,
        limit: int,
        tipo: str | None = None,
        categoria: str | None = None,
        busca: str | None = None,
    ) -> list[Consumivel]:
        query = (
            apply_not_deleted(self.db.query(Consumivel), Consumivel)
            .filter(Consumivel.ativo == True)  # noqa: E712
        )

        tipo_norm = (tipo or "").strip().lower()
        categoria_norm = (categoria or "").strip().lower()
        busca_norm = (busca or "").strip()

        if tipo_norm:
            query = query.filter(
                or_(
                    *[
                        Consumivel.tipo == v
                        for v in _variantes_texto_unicode_para_filtro(tipo_norm)
                    ]
                )
            )

        if categoria_norm:
            query = query.filter(
                or_(
                    *[
                        Consumivel.categoria.ilike(f"%{v}%")
                        for v in _variantes_texto_unicode_para_filtro(categoria_norm)
                    ]
                )
            )

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

    def deletar(self, consumivel_id: int) -> bool:
        item = self.obter(consumivel_id)
        if not item:
            return False
        return soft_delete_entity(self.db, item)


class ConsumivelJogadorRepository:
    def __init__(self, db: Session):
        self.db = db

    def adicionar(
        self, combatente_id: int, consumivel_id: int, quantidade: int
    ) -> ConsumivelJogador:
        existente = (
            self.db.query(ConsumivelJogador)
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
            commit_with_rollback(self.db)
            self.db.refresh(existente)
            return existente

        obj = ConsumivelJogador(
            combatente_id=combatente_id,
            consumivel_id=consumivel_id,
            quantidade=quantidade,
        )
        self.db.add(obj)
        commit_with_rollback(self.db)
        self.db.refresh(obj)
        return obj

    def listar_detalhado(self, combatente_id: int) -> list[dict]:
        cj = aliased(ConsumivelJogador, name="cj")
        c = aliased(Consumivel, name="c")
        rows = (
            self.db.query(
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

    def remover(self, combatente_id: int, consumivel_id: int) -> bool:
        obj = (
            self.db.query(ConsumivelJogador)
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
        self.db.delete(obj)
        commit_with_rollback(self.db)
        return True
