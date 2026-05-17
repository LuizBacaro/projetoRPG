from sqlalchemy.orm import Session, load_only

from app.games.dnd35.models.familiar import Familiar
from app.games.dnd35.schema_compat import has_arena_combatente_id, has_familiares_table

_COLUNAS_FAMILIAR_SEM_ARENA = (
    Familiar.id,
    Familiar.combatente_id,
    Familiar.especie_slug,
    Familiar.nome,
    Familiar.nivel_mestre,
    Familiar.inteligencia,
    Familiar.armadura_natural_bonus,
    Familiar.hp_atual,
    Familiar.hp_maximo,
    Familiar.ca,
    Familiar.bonus_mestre,
    Familiar.habilidades_especiais,
    Familiar.anotacoes,
    Familiar.criado_em,
    Familiar.atualizado_em,
)


class FamiliarRepository:
    def __init__(self, db: Session):
        self.db = db

    def obter_por_combatente(self, combatente_id: int) -> Familiar | None:
        if not has_familiares_table(self.db.get_bind()):
            return None
        q = self.db.query(Familiar)
        if not has_arena_combatente_id(self.db.get_bind()):
            q = q.options(load_only(*_COLUNAS_FAMILIAR_SEM_ARENA))
        return q.filter(Familiar.combatente_id == combatente_id).first()

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
