from sqlalchemy.orm import Session, load_only

from app.games.dnd35.models.companheiro_animal import CompanheiroAnimal
from app.games.dnd35.schema_compat import has_arena_combatente_id

_COLUNAS_SEM_ARENA = (
    CompanheiroAnimal.id,
    CompanheiroAnimal.combatente_id,
    CompanheiroAnimal.especie_slug,
    CompanheiroAnimal.nome,
    CompanheiroAnimal.forca,
    CompanheiroAnimal.destreza,
    CompanheiroAnimal.constituicao,
    CompanheiroAnimal.inteligencia,
    CompanheiroAnimal.sabedoria,
    CompanheiroAnimal.carisma,
    CompanheiroAnimal.bonus_atributos,
    CompanheiroAnimal.hp_atual,
    CompanheiroAnimal.hp_maximo,
    CompanheiroAnimal.ca,
    CompanheiroAnimal.iniciativa,
    CompanheiroAnimal.deslocamento,
    CompanheiroAnimal.truques,
    CompanheiroAnimal.talentos,
    CompanheiroAnimal.pericias,
    CompanheiroAnimal.ataques,
    CompanheiroAnimal.anotacoes,
    CompanheiroAnimal.criado_em,
    CompanheiroAnimal.atualizado_em,
)


class CompanheiroAnimalRepository:
    def __init__(self, db: Session):
        self.db = db

    def _query_base(self):
        q = self.db.query(CompanheiroAnimal)
        if not has_arena_combatente_id(self.db.get_bind()):
            q = q.options(load_only(*_COLUNAS_SEM_ARENA))
        return q

    def obter_por_combatente(self, combatente_id: int) -> CompanheiroAnimal | None:
        return (
            self._query_base()
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
