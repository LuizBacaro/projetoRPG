"""Repository do módulo Grimório."""

from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from .base import commit_with_rollback
from ..models.combatente import Combatente
from ..models.grimorio import GrimorioMagia, GrimorioHistoricoTroca, GrimorioNotificacao


class GrimorioRepository:
    def __init__(self, db: Session):
        self.db = db

    def listar(self, combatente_id: int, classe: Optional[str] = None, favorita: Optional[bool] = None):
        query = self.db.query(GrimorioMagia).filter(GrimorioMagia.combatente_id == combatente_id)
        if classe:
            query = query.filter(GrimorioMagia.classe == classe.strip().upper())
        if favorita is not None:
            query = query.filter(GrimorioMagia.favorita == favorita)
        return query.order_by(GrimorioMagia.classe, GrimorioMagia.id).all()

    def listar_historico_troca(self, combatente_id: int, classe: Optional[str] = None, limit: int = 20):
        query = self.db.query(GrimorioHistoricoTroca).filter(
            GrimorioHistoricoTroca.combatente_id == combatente_id
        )
        if classe:
            query = query.filter(GrimorioHistoricoTroca.classe == classe.strip().upper())
        return query.order_by(GrimorioHistoricoTroca.realizada_em.desc()).limit(limit).all()

    def get_item(self, combatente_id: int, magia_id: int, classe: str) -> Optional[GrimorioMagia]:
        return (
            self.db.query(GrimorioMagia)
            .filter(
                GrimorioMagia.combatente_id == combatente_id,
                GrimorioMagia.magia_id == magia_id,
                GrimorioMagia.classe == classe.strip().upper(),
            )
            .first()
        )

    def get_combatente(self, combatente_id: int) -> Optional[Combatente]:
        return self.db.query(Combatente).filter(Combatente.id == combatente_id).first()

    def listar_notificacoes(
        self,
        combatente_id: int,
        *,
        classe: Optional[str] = None,
        apenas_nao_lidas: bool = False,
        limit: int = 30,
    ):
        query = self.db.query(GrimorioNotificacao).filter(
            GrimorioNotificacao.combatente_id == combatente_id
        )
        if classe:
            query = query.filter(GrimorioNotificacao.classe == classe.strip().upper())
        if apenas_nao_lidas:
            query = query.filter(GrimorioNotificacao.lida.is_(False))
        return query.order_by(GrimorioNotificacao.criada_em.desc()).limit(limit).all()

    def get_notificacao(self, notificacao_id: int) -> Optional[GrimorioNotificacao]:
        return self.db.query(GrimorioNotificacao).filter(GrimorioNotificacao.id == notificacao_id).first()

    def get_notificacao_aberta_por_tipo(
        self,
        combatente_id: int,
        classe: str,
        tipo: str,
    ) -> Optional[GrimorioNotificacao]:
        return (
            self.db.query(GrimorioNotificacao)
            .filter(
                GrimorioNotificacao.combatente_id == combatente_id,
                GrimorioNotificacao.classe == classe.strip().upper(),
                GrimorioNotificacao.tipo == tipo.strip().upper(),
                GrimorioNotificacao.lida.is_(False),
            )
            .order_by(GrimorioNotificacao.criada_em.desc())
            .first()
        )

    def create(self, item: GrimorioMagia) -> GrimorioMagia:
        self.db.add(item)
        commit_with_rollback(self.db)
        self.db.refresh(item)
        return item

    def create_notificacao(self, item: GrimorioNotificacao) -> GrimorioNotificacao:
        self.db.add(item)
        commit_with_rollback(self.db)
        self.db.refresh(item)
        return item

    def update(self, item: GrimorioMagia) -> GrimorioMagia:
        commit_with_rollback(self.db)
        self.db.refresh(item)
        return item

    def update_notificacao(self, item: GrimorioNotificacao) -> GrimorioNotificacao:
        commit_with_rollback(self.db)
        self.db.refresh(item)
        return item

    def delete(self, item: GrimorioMagia) -> None:
        self.db.delete(item)
        commit_with_rollback(self.db)

    def delete_notificacao(self, item: GrimorioNotificacao) -> None:
        self.db.delete(item)
        commit_with_rollback(self.db)

    def registrar_troca(self, historico: GrimorioHistoricoTroca) -> GrimorioHistoricoTroca:
        self.db.add(historico)
        commit_with_rollback(self.db)
        self.db.refresh(historico)
        return historico

    def trocar_magia(
        self,
        *,
        item_antigo: GrimorioMagia,
        item_novo: GrimorioMagia,
        historico: GrimorioHistoricoTroca,
    ) -> GrimorioHistoricoTroca:
        self.db.delete(item_antigo)
        self.db.add(item_novo)
        self.db.add(historico)
        commit_with_rollback(self.db)
        self.db.refresh(historico)
        return historico
