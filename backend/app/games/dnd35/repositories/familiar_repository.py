from sqlalchemy.orm import Session

from app.games.dnd35.models.familiar import Familiar


class FamiliarRepository:
    def __init__(self, db: Session):
        self.db = db

    def obter_por_combatente(self, combatente_id: int) -> Familiar | None:
        return (
            self.db.query(Familiar)
            .filter(Familiar.combatente_id == combatente_id)
            .first()
        )

    def criar(self, entidade: Familiar) -> Familiar:
        self.db.add(entidade)
        self.db.commit()
        self.db.refresh(entidade)
        return entidade

    def atualizar(self, entidade: Familiar) -> Familiar:
        self.db.commit()
        self.db.refresh(entidade)
        return entidade

    def remover(self, entidade: Familiar) -> None:
        self.db.delete(entidade)
        self.db.commit()
