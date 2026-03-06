"""
AtaqueRepository
SRP: acesso a dados de Ataque e MagiaSlot
DIP: depende da abstração Session, não de implementação concreta
"""
from typing import List
from sqlalchemy.orm import Session
from ..models.ataque import Ataque, MagiaSlot


class AtaqueRepository:

    def __init__(self, db: Session):
        self.db = db

    # ── Ataques 

    def listar_por_combatente(self, combatente_id: int) -> List[Ataque]:
        return (self.db.query(Ataque)
                .filter(Ataque.combatente_id == combatente_id)
                .all())

    def criar(self, ataque: Ataque) -> Ataque:
        self.db.add(ataque)
        self.db.commit()
        self.db.refresh(ataque)
        return ataque

    def deletar_por_combatente(self, combatente_id: int) -> None:
        """Remove todos os ataques do combatente (usado no bulk replace)."""
        (self.db.query(Ataque)
         .filter(Ataque.combatente_id == combatente_id)
         .delete())
        self.db.commit()

    def substituir_todos(self, combatente_id: int,
                         ataques_data: list) -> List[Ataque]:
        """Delete + insert atômico — garante consistência."""
        self.deletar_por_combatente(combatente_id)
        novos = []
        for d in ataques_data:
            a = Ataque(combatente_id=combatente_id, **d)
            self.db.add(a)
            novos.append(a)
        self.db.commit()
        for a in novos:
            self.db.refresh(a)
        return novos

    # ── Magias Slots 

    def listar_magias_por_combatente(self, combatente_id: int) -> List[MagiaSlot]:
        return (self.db.query(MagiaSlot)
                .filter(MagiaSlot.combatente_id == combatente_id)
                .order_by(MagiaSlot.nivel)
                .all())

    def deletar_magias_por_combatente(self, combatente_id: int) -> None:
        (self.db.query(MagiaSlot)
         .filter(MagiaSlot.combatente_id == combatente_id)
         .delete())
        self.db.commit()

    def substituir_magias(self, combatente_id: int,
                          slots_data: list) -> List[MagiaSlot]:
        """Delete + insert atômico para slots de magia."""
        self.deletar_magias_por_combatente(combatente_id)
        novos = []
        for d in slots_data:
            s = MagiaSlot(combatente_id=combatente_id, **d)
            self.db.add(s)
            novos.append(s)
        self.db.commit()
        for s in novos:
            self.db.refresh(s)
        return novos

    def atualizar_usados(self, slot_id: int, usados: int) -> MagiaSlot:
        """Atualiza apenas o campo 'usados' de um slot (usado na arena)."""
        slot = self.db.query(MagiaSlot).filter(MagiaSlot.id == slot_id).first()
        if slot:
            slot.usados = max(0, min(usados, slot.total))
            self.db.commit()
            self.db.refresh(slot)
        return slot