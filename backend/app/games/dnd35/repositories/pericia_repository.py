"""
Repository de Perícia (D&D 3.5)

Localização: `app.games.dnd35.repositories.pericia_repository`. Shim em
`app.repositories.pericia_repository` durante a reorganização multi-jogo.
"""

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.games.dnd35.models.pericia import Pericia, PericiaClasse, PericiaJogador
from app.games.dnd35.schemas.pericia import (
    PericiaCreate,
    PericiaJogadorCreate,
    PericiaJogadorUpdate,
    PericiaUpdate,
)
from app.repositories.base import (
    apply_not_deleted,
    commit_with_rollback,
    soft_delete_entity,
)


class PericiaRepository:
    """Operações de banco de dados para perícias"""

    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _payload_data(payload, exclude_unset: bool = False) -> dict:
        if hasattr(payload, "model_dump"):
            return payload.model_dump(exclude_unset=exclude_unset)
        if exclude_unset:
            return payload.dict(exclude_unset=True)
        return payload.dict()

    def restaurar_pericia(self, db_pericia: Pericia, pericia: PericiaCreate) -> Pericia:
        db_pericia.deleted_at = None
        for key, value in self._payload_data(pericia).items():
            setattr(db_pericia, key, value)
        commit_with_rollback(self.db)
        self.db.refresh(db_pericia)
        return db_pericia

    def criar_pericia(self, pericia: PericiaCreate) -> Pericia:
        """Cria uma nova perícia"""
        db_pericia = Pericia(**self._payload_data(pericia))
        self.db.add(db_pericia)
        commit_with_rollback(self.db)
        self.db.refresh(db_pericia)
        return db_pericia

    def obter_pericia(self, pericia_id: int):
        """Obtém uma perícia por ID"""
        return (
            apply_not_deleted(self.db.query(Pericia), Pericia)
            .filter(Pericia.id == pericia_id)
            .first()
        )

    def obter_pericia_por_nome(self, nome: str):
        """Obtém uma perícia por nome"""
        return self.db.query(Pericia).filter(Pericia.nome == nome).first()

    def listar_pericias(self, skip: int = 0, limit: int = 100) -> list[Pericia]:
        """Lista todas as perícias com paginação"""
        return (
            apply_not_deleted(self.db.query(Pericia), Pericia)
            .order_by(Pericia.nome.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def listar_pericias_por_atributo(self, atributo: str) -> list[Pericia]:
        """Lista perícias filtradas por atributo"""
        return (
            apply_not_deleted(self.db.query(Pericia), Pericia)
            .filter(Pericia.atributo == atributo)
            .order_by(Pericia.nome.asc())
            .all()
        )

    def listar_pericias_por_tipo(self, tipo: str) -> list[Pericia]:
        """Lista perícias filtradas por tipo"""
        return (
            apply_not_deleted(self.db.query(Pericia), Pericia)
            .filter(Pericia.tipo == tipo)
            .all()
        )

    def listar_pericias_por_classe(self, classe_nome: str) -> list[Pericia]:
        """Lista perícias padrão de uma classe específica"""
        return (
            apply_not_deleted(self.db.query(Pericia), Pericia)
            .join(PericiaClasse, Pericia.id == PericiaClasse.pericia_id)
            .filter(
                PericiaClasse.classe_nome == classe_nome,
                PericiaClasse.is_default == 1,
            )
            .order_by(Pericia.nome.asc())
            .all()
        )

    def obter_custo_pericia(self, pericia_id: int, classe_nome: str) -> int:
        """
        Obtém o custo de uma perícia para uma classe
        Retorna: 1 se é perícia de classe, 2 se é fora da classe
        """
        pericia_classe = (
            self.db.query(PericiaClasse)
            .filter(
                PericiaClasse.pericia_id == pericia_id,
                PericiaClasse.classe_nome == classe_nome,
                PericiaClasse.is_default == 1,
            )
            .first()
        )

        return 1 if pericia_classe else 2

    def obter_custos_pericias(
        self, pericia_ids: list[int], classe_nome: str
    ) -> dict[int, int]:
        """Custos em lote (1 = perícia de classe, 2 = fora da classe)."""
        if not pericia_ids:
            return {}

        pericias_de_classe = {
            pericia_id
            for (pericia_id,) in self.db.query(PericiaClasse.pericia_id)
            .filter(
                PericiaClasse.pericia_id.in_(pericia_ids),
                PericiaClasse.classe_nome == classe_nome,
                PericiaClasse.is_default == 1,
            )
            .all()
        }

        return {
            pericia_id: 1 if pericia_id in pericias_de_classe else 2
            for pericia_id in pericia_ids
        }

    def atualizar_pericia(self, pericia_id: int, pericia: PericiaUpdate):
        """Atualiza uma perícia"""
        db_pericia = (
            apply_not_deleted(self.db.query(Pericia), Pericia)
            .filter(Pericia.id == pericia_id)
            .first()
        )
        if db_pericia:
            for key, value in self._payload_data(pericia, exclude_unset=True).items():
                setattr(db_pericia, key, value)
            commit_with_rollback(self.db)
            self.db.refresh(db_pericia)
        return db_pericia

    def deletar_pericia(self, pericia_id: int) -> bool:
        """Deleta uma perícia"""
        db_pericia = (
            apply_not_deleted(self.db.query(Pericia), Pericia)
            .filter(Pericia.id == pericia_id)
            .first()
        )
        if db_pericia:
            return soft_delete_entity(self.db, db_pericia)
        return False


class PericiaJogadorRepository:
    """Operações de banco de dados para perícias do jogador"""

    def __init__(self, db: Session):
        self.db = db

    def adicionar_pericia(self, pericia_jogador: PericiaJogadorCreate) -> PericiaJogador:
        """Adiciona uma perícia ao jogador"""
        db_pericia_jogador = PericiaJogador(
            **PericiaRepository._payload_data(pericia_jogador)
        )
        self.db.add(db_pericia_jogador)
        commit_with_rollback(self.db)
        self.db.refresh(db_pericia_jogador)
        return db_pericia_jogador

    def obter_pericia_jogador(self, pericia_jogador_id: int):
        """Obtém uma perícia específica do jogador"""
        return (
            self.db.query(PericiaJogador)
            .filter(PericiaJogador.id == pericia_jogador_id)
            .first()
        )

    def listar_pericias_jogador(self, combatente_id: int) -> list[PericiaJogador]:
        """Lista todas as perícias de um combatente"""
        return (
            self.db.query(PericiaJogador)
            .filter(PericiaJogador.combatente_id == combatente_id)
            .all()
        )

    def obter_pericia_jogador_por_nome(self, combatente_id: int, nome_pericia: str):
        """Obtém uma perícia específica do jogador por nome"""
        return (
            self.db.query(PericiaJogador)
            .join(Pericia)
            .filter(
                PericiaJogador.combatente_id == combatente_id,
                Pericia.nome == nome_pericia,
            )
            .first()
        )

    def obter_pericia_jogador_por_ids(self, combatente_id: int, pericia_id: int):
        """Obtém perícia do jogador por combatente_id e pericia_id"""
        return (
            self.db.query(PericiaJogador)
            .filter(
                PericiaJogador.combatente_id == combatente_id,
                PericiaJogador.pericia_id == pericia_id,
            )
            .first()
        )

    def atualizar_pericia_jogador(
        self,
        pericia_jogador_id: int,
        pericia: PericiaJogadorUpdate,
    ):
        """Atualiza uma perícia do jogador"""
        db_pericia_jogador = (
            self.db.query(PericiaJogador)
            .filter(PericiaJogador.id == pericia_jogador_id)
            .first()
        )
        if db_pericia_jogador:
            for key, value in PericiaRepository._payload_data(
                pericia, exclude_unset=True
            ).items():
                setattr(db_pericia_jogador, key, value)
            commit_with_rollback(self.db)
            self.db.refresh(db_pericia_jogador)
        return db_pericia_jogador

    def deletar_pericia_jogador(self, pericia_jogador_id: int) -> bool:
        """Deleta uma perícia do jogador"""
        db_pericia_jogador = (
            self.db.query(PericiaJogador)
            .filter(PericiaJogador.id == pericia_jogador_id)
            .first()
        )
        if db_pericia_jogador:
            self.db.delete(db_pericia_jogador)
            commit_with_rollback(self.db)
            return True
        return False

    def listar_pericias_combatente_com_pericia(
        self, combatente_id: int
    ) -> list[PericiaJogador]:
        """Lista vínculos do combatente com `pericia` eager-loaded e catálogo não deletado."""
        return (
            self.db.query(PericiaJogador)
            .options(joinedload(PericiaJogador.pericia))
            .join(Pericia, Pericia.id == PericiaJogador.pericia_id)
            .filter(
                PericiaJogador.combatente_id == combatente_id,
                Pericia.deleted_at.is_(None),
            )
            .all()
        )

    def persistir_novo_vinculo(self, row: PericiaJogador) -> PericiaJogador:
        self.db.add(row)
        commit_with_rollback(self.db)
        self.db.refresh(row)
        return row

    def contar_pontos_gastos(self, combatente_id: int) -> int:
        """Conta os pontos totais gastos em perícias (incluindo penalidades)"""
        resultado = (
            self.db.query(func.sum(PericiaJogador.custo_total))
            .filter(PericiaJogador.combatente_id == combatente_id)
            .scalar()
        )
        return resultado or 0

    def contar_graduacoes(self, combatente_id: int) -> int:
        """Conta os pontos de graduação (sem penalidades)"""
        resultado = (
            self.db.query(func.sum(PericiaJogador.graduacao))
            .filter(PericiaJogador.combatente_id == combatente_id)
            .scalar()
        )
        return resultado or 0
