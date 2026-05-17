from sqlalchemy.orm import Session

from app.games.dnd35.models.companheiro_animal import CompanheiroAnimal


class CompanheiroAnimalRepository:
    def __init__(self, db: Session):
        self.db = db

    def obter_por_combatente(self, combatente_id: int) -> CompanheiroAnimal | None:
        return (
            self.db.query(CompanheiroAnimal)
            .filter(CompanheiroAnimal.combatente_id == combatente_id)
            .first()
        )

    def criar(self, entidade: CompanheiroAnimal) -> CompanheiroAnimal:
        self.db.add(entidade)
        self.db.commit()
        self.db.refresh(entidade)
        return entidade

    def atualizar(self, entidade: CompanheiroAnimal) -> CompanheiroAnimal:
        self.db.commit()
        self.db.refresh(entidade)
        return entidade

    def remover(self, entidade: CompanheiroAnimal) -> None:
        self.db.delete(entidade)
        self.db.commit()
