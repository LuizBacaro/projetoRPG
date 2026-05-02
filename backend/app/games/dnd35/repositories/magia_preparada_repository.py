"""Persistência de magias preparadas e reset de slots (D&D 3.5)."""

from __future__ import annotations

from typing import List, Optional

from sqlalchemy.orm import Session

from app.games.dnd35.models.ataque import MagiaPreparada, MagiaSlot


class MagiaPreparadaRepository:
    def __init__(self, db: Session):
        self.db = db

    def listar_por_combatente(self, combatente_id: int) -> List[MagiaPreparada]:
        return (
            self.db.query(MagiaPreparada)
            .filter(MagiaPreparada.combatente_id == combatente_id)
            .all()
        )

    def obter_por_combatente_e_magia(
        self, combatente_id: int, magia_id: int
    ) -> Optional[MagiaPreparada]:
        return (
            self.db.query(MagiaPreparada)
            .filter(
                MagiaPreparada.combatente_id == combatente_id,
                MagiaPreparada.magia_id == magia_id,
            )
            .first()
        )

    def obter_por_id(self, preparada_id: int) -> Optional[MagiaPreparada]:
        return (
            self.db.query(MagiaPreparada).filter(MagiaPreparada.id == preparada_id).first()
        )

    def commit_refresh(self, registro: MagiaPreparada) -> MagiaPreparada:
        self.db.commit()
        self.db.refresh(registro)
        atualizado = self.obter_por_id(registro.id)
        return atualizado or registro

    def add_commit_refresh(self, nova: MagiaPreparada) -> MagiaPreparada:
        self.db.add(nova)
        self.db.commit()
        self.db.refresh(nova)
        carregada = self.obter_por_id(nova.id)
        return carregada or nova

    def delete(self, registro: MagiaPreparada) -> None:
        self.db.delete(registro)
        self.db.commit()

    def delete_all_por_combatente(self, combatente_id: int) -> int:
        return (
            self.db.query(MagiaPreparada)
            .filter(MagiaPreparada.combatente_id == combatente_id)
            .delete()
        )

    def reset_slots_usados(self, combatente_id: int) -> None:
        self.db.query(MagiaSlot).filter(MagiaSlot.combatente_id == combatente_id).update(
            {"usados": 0}
        )

    def commit(self) -> None:
        self.db.commit()
