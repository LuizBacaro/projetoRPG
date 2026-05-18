"""Repository — grimório `dnd5e_grimorio_magias`."""

from __future__ import annotations

from typing import Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app.games.dnd5e.models.grimorio import (
    Dnd5eGrimorioHistoricoTroca,
    Dnd5eGrimorioMagia,
    Dnd5eGrimorioNotificacao,
)
from app.games.dnd5e.models.personagem import Dnd5ePersonagem
from app.games.dnd5e.models.magia import Dnd5eMagia
from app.repositories.base import commit_with_rollback


class Dnd5eGrimorioRepository:
    def __init__(self, db: Session):
        self.db = db

    def _base_query(self, personagem_id: int):
        return (
            self.db.query(Dnd5eGrimorioMagia)
            .options(joinedload(Dnd5eGrimorioMagia.magia))
            .filter(Dnd5eGrimorioMagia.personagem_id == personagem_id)
        )

    def listar_paginado(
        self,
        personagem_id: int,
        *,
        classe: Optional[str] = None,
        favorita: Optional[bool] = None,
        nome: Optional[str] = None,
        nivel: Optional[int] = None,
        escola: Optional[str] = None,
        skip: int = 0,
        limit: Optional[int] = None,
    ) -> tuple[int, list[Dnd5eGrimorioMagia]]:
        query = self._base_query(personagem_id)
        if classe:
            query = query.filter(
                Dnd5eGrimorioMagia.classe == classe.strip().lower()
            )
        if favorita is not None:
            query = query.filter(Dnd5eGrimorioMagia.favorita == favorita)

        precisa_join = any(v is not None for v in (nome, nivel, escola))
        if precisa_join:
            query = query.join(Dnd5eGrimorioMagia.magia)
            if nome:
                termo = f"%{nome.strip()}%"
                query = query.filter(
                    or_(
                        Dnd5eMagia.nome.ilike(termo),
                        Dnd5eMagia.descricao.ilike(termo),
                        Dnd5eGrimorioMagia.anotacoes.ilike(termo),
                    )
                )
            if nivel is not None:
                query = query.filter(Dnd5eMagia.nivel == nivel)
            if escola:
                query = query.filter(Dnd5eMagia.escola.ilike(escola.strip()))

        total = query.count()
        query = query.order_by(Dnd5eGrimorioMagia.classe, Dnd5eGrimorioMagia.id)
        if skip:
            query = query.offset(skip)
        if limit is not None:
            query = query.limit(limit)
        return total, query.all()

    def obter_item(
        self, personagem_id: int, magia_id: int, classe: str
    ) -> Optional[Dnd5eGrimorioMagia]:
        return (
            self._base_query(personagem_id)
            .filter(
                Dnd5eGrimorioMagia.magia_id == magia_id,
                Dnd5eGrimorioMagia.classe == classe.strip().lower(),
            )
            .first()
        )

    def adicionar(self, item: Dnd5eGrimorioMagia) -> Dnd5eGrimorioMagia:
        self.db.add(item)
        commit_with_rollback(self.db)
        self.db.refresh(item)
        return item

    def atualizar(self, item: Dnd5eGrimorioMagia) -> Dnd5eGrimorioMagia:
        commit_with_rollback(self.db)
        self.db.refresh(item)
        return item

    def remover(self, item: Dnd5eGrimorioMagia) -> None:
        self.db.delete(item)
        commit_with_rollback(self.db)

    def obter_personagem(self, personagem_id: int) -> Optional[Dnd5ePersonagem]:
        return (
            self.db.query(Dnd5ePersonagem)
            .filter(Dnd5ePersonagem.id == personagem_id)
            .first()
        )

    def listar_historico_troca(
        self, personagem_id: int, *, classe: Optional[str] = None, limit: int = 20
    ) -> list[Dnd5eGrimorioHistoricoTroca]:
        query = self.db.query(Dnd5eGrimorioHistoricoTroca).filter(
            Dnd5eGrimorioHistoricoTroca.personagem_id == personagem_id
        )
        if classe:
            query = query.filter(
                Dnd5eGrimorioHistoricoTroca.classe == classe.strip().lower()
            )
        return (
            query.order_by(Dnd5eGrimorioHistoricoTroca.realizada_em.desc())
            .limit(limit)
            .all()
        )

    def listar_notificacoes(
        self,
        personagem_id: int,
        *,
        classe: Optional[str] = None,
        apenas_nao_lidas: bool = False,
        limit: int = 30,
    ) -> list[Dnd5eGrimorioNotificacao]:
        query = self.db.query(Dnd5eGrimorioNotificacao).filter(
            Dnd5eGrimorioNotificacao.personagem_id == personagem_id
        )
        if classe:
            query = query.filter(
                Dnd5eGrimorioNotificacao.classe == classe.strip().lower()
            )
        if apenas_nao_lidas:
            query = query.filter(Dnd5eGrimorioNotificacao.lida.is_(False))
        return (
            query.order_by(Dnd5eGrimorioNotificacao.criada_em.desc()).limit(limit).all()
        )

    def get_notificacao(self, notificacao_id: int) -> Optional[Dnd5eGrimorioNotificacao]:
        return (
            self.db.query(Dnd5eGrimorioNotificacao)
            .filter(Dnd5eGrimorioNotificacao.id == notificacao_id)
            .first()
        )

    def get_notificacao_aberta_por_tipo(
        self, personagem_id: int, classe: str, tipo: str
    ) -> Optional[Dnd5eGrimorioNotificacao]:
        return (
            self.db.query(Dnd5eGrimorioNotificacao)
            .filter(
                Dnd5eGrimorioNotificacao.personagem_id == personagem_id,
                Dnd5eGrimorioNotificacao.classe == classe.strip().lower(),
                Dnd5eGrimorioNotificacao.tipo == tipo.strip().upper(),
                Dnd5eGrimorioNotificacao.lida.is_(False),
            )
            .order_by(Dnd5eGrimorioNotificacao.criada_em.desc())
            .first()
        )

    def create_notificacao(
        self, item: Dnd5eGrimorioNotificacao
    ) -> Dnd5eGrimorioNotificacao:
        self.db.add(item)
        commit_with_rollback(self.db)
        self.db.refresh(item)
        return item

    def update_notificacao(
        self, item: Dnd5eGrimorioNotificacao
    ) -> Dnd5eGrimorioNotificacao:
        commit_with_rollback(self.db)
        self.db.refresh(item)
        return item

    def delete_notificacao(self, item: Dnd5eGrimorioNotificacao) -> None:
        self.db.delete(item)
        commit_with_rollback(self.db)

    def registrar_troca(
        self,
        *,
        item_antigo: Dnd5eGrimorioMagia,
        item_novo: Dnd5eGrimorioMagia,
        historico: Dnd5eGrimorioHistoricoTroca,
    ) -> Dnd5eGrimorioHistoricoTroca:
        self.db.delete(item_antigo)
        self.db.add(item_novo)
        self.db.add(historico)
        commit_with_rollback(self.db)
        self.db.refresh(historico)
        return historico
