"""
Service de Perícia (D&D 3.5)

Localização: `app.games.dnd35.services.pericia_service`. Shim em
`app.services.pericia_service` durante a reorganização multi-jogo.
"""

from typing import Dict, List, Optional

from sqlalchemy.orm import Session, joinedload

from app.games.dnd35.models.pericia import Pericia, PericiaClasse, PericiaJogador
from app.games.dnd35.repositories.pericia_repository import PericiaRepository
from app.games.dnd35.schemas.pericia import (
    PericiaCreate,
    PericiaJogadorCreate,
    PericiaJogadorUpdate,
    PericiaUpdate,
)
from app.models.combatente import Combatente
from app.repositories.base import (
    apply_not_deleted,
    commit_with_rollback,
    soft_delete_entity,
)


class PericiaService:
    """Serviço de lógica de negócio para perícias"""

    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _payload_data(payload, exclude_unset: bool = False) -> dict:
        if hasattr(payload, "model_dump"):
            return payload.model_dump(exclude_unset=exclude_unset)
        if exclude_unset:
            return payload.dict(exclude_unset=True)
        return payload.dict()

    # ========== PERÍCIAS DISPONÍVEIS ==========

    def criar_pericia(self, pericia: PericiaCreate) -> Pericia:
        """Cria uma nova perícia"""
        pericia_existente = (
            self.db.query(Pericia).filter(Pericia.nome == pericia.nome).first()
        )

        if pericia_existente:
            if pericia_existente.deleted_at is not None:
                return PericiaRepository.restaurar_pericia(
                    self.db, pericia_existente, pericia
                )
            raise ValueError(f"Perícia '{pericia.nome}' já existe")

        db_pericia = Pericia(**self._payload_data(pericia))
        self.db.add(db_pericia)
        commit_with_rollback(self.db)
        self.db.refresh(db_pericia)
        return db_pericia

    def obter_pericia(self, pericia_id: int) -> Optional[Pericia]:
        """Obtém uma perícia por ID"""
        return (
            apply_not_deleted(self.db.query(Pericia), Pericia)
            .filter(Pericia.id == pericia_id)
            .first()
        )

    def listar_todas_pericias(
        self, skip: int = 0, limit: int = 100
    ) -> List[Pericia]:
        """Lista todas as perícias disponíveis (ordem alfabética — espelha a Tabela 4-3 do livro)."""
        return (
            apply_not_deleted(self.db.query(Pericia), Pericia)
            .order_by(Pericia.nome.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def listar_pericias_por_atributo(self, atributo: str) -> List[Pericia]:
        """Lista perícias filtradas por atributo (ordem alfabética)."""
        atributos_validos = ["FOR", "DES", "CON", "INT", "SAB", "CAR"]
        if atributo.upper() not in atributos_validos:
            raise ValueError(f"Atributo '{atributo}' inválido")

        return (
            apply_not_deleted(self.db.query(Pericia), Pericia)
            .filter(Pericia.atributo == atributo.upper())
            .order_by(Pericia.nome.asc())
            .all()
        )

    def listar_pericias_por_classe(self, classe_nome: str) -> List[Pericia]:
        """Lista perícias padrão de uma classe D&D (ordem alfabética)."""
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

    def atualizar_pericia(
        self, pericia_id: int, pericia: PericiaUpdate
    ) -> Optional[Pericia]:
        """Atualiza uma perícia"""
        db_pericia = (
            apply_not_deleted(self.db.query(Pericia), Pericia)
            .filter(Pericia.id == pericia_id)
            .first()
        )

        if not db_pericia:
            return None

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

        if not db_pericia:
            return False

        return soft_delete_entity(self.db, db_pericia)

    # ========== CÁLCULO DE CUSTOS ==========

    def calcular_custo_pericia(self, pericia_id: int, classe_nome: str) -> int:
        """
        Calcula o custo de uma perícia para uma classe
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
        self, pericia_ids: List[int], classe_nome: str
    ) -> Dict[int, int]:
        """Busca em lote os custos das perícias para uma classe."""
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

    def calcular_custo_total_graduacao(
        self,
        pericia_id: int,
        classe_nome: str,
        pontos_a_adicionar: int = 1,
    ) -> int:
        """
        Calcula o custo total em pontos de perícia
        Para adicionar N pontos a uma perícia
        """
        custo_por_ponto = self.calcular_custo_pericia(pericia_id, classe_nome)
        return custo_por_ponto * pontos_a_adicionar

    # ========== PERÍCIAS DO JOGADOR ==========

    def adicionar_pericia_jogador(
        self,
        combatente_id: int,
        pericia_jogador: PericiaJogadorCreate,
    ) -> PericiaJogador:
        """Adiciona uma perícia ao jogador"""
        combatente = (
            self.db.query(Combatente)
            .filter(
                Combatente.id == combatente_id,
                Combatente.deleted_at.is_(None),
            )
            .first()
        )

        if not combatente:
            raise ValueError(f"Combatente com ID {combatente_id} não existe")

        pericia = (
            apply_not_deleted(self.db.query(Pericia), Pericia)
            .filter(Pericia.id == pericia_jogador.pericia_id)
            .first()
        )

        if not pericia:
            raise ValueError(
                f"Perícia com ID {pericia_jogador.pericia_id} não existe"
            )

        pericia_existente = (
            self.db.query(PericiaJogador)
            .filter(
                PericiaJogador.combatente_id == combatente_id,
                PericiaJogador.pericia_id == pericia_jogador.pericia_id,
            )
            .first()
        )

        if pericia_existente:
            raise ValueError("Jogador já possui essa perícia")

        atributo_map = {
            "FOR": "forca",
            "DES": "destreza",
            "CON": "constituicao",
            "INT": "inteligencia",
            "SAB": "sabedoria",
            "CAR": "carisma",
        }

        atributo_nome = atributo_map.get(pericia.atributo, "forca")

        modificador = combatente.calcular_modificador(atributo_nome)

        custo_total = self.calcular_custo_total_graduacao(
            pericia_jogador.pericia_id,
            combatente.classe,
            pericia_jogador.graduacao,
        )

        db_pericia_jogador = PericiaJogador(
            combatente_id=combatente_id,
            pericia_id=pericia_jogador.pericia_id,
            graduacao=pericia_jogador.graduacao,
            custo_total=custo_total,
            modificador_atributo=float(modificador),
            bonus_outros=pericia_jogador.bonus_outros or 0,
        )

        self.db.add(db_pericia_jogador)
        commit_with_rollback(self.db)
        self.db.refresh(db_pericia_jogador)

        return db_pericia_jogador

    def obter_pericia_jogador(
        self, pericia_jogador_id: int
    ) -> Optional[PericiaJogador]:
        """Obtém uma perícia específica do jogador"""
        return (
            self.db.query(PericiaJogador)
            .filter(PericiaJogador.id == pericia_jogador_id)
            .first()
        )

    def listar_pericias_combatente(
        self, combatente_id: int
    ) -> List[PericiaJogador]:
        """Lista todas as perícias de um combatente"""
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

    def atualizar_pericia_jogador(
        self,
        pericia_jogador_id: int,
        pericia: PericiaJogadorUpdate,
    ) -> Optional[PericiaJogador]:
        """Atualiza uma perícia do jogador"""
        db_pericia_jogador = (
            self.db.query(PericiaJogador)
            .filter(PericiaJogador.id == pericia_jogador_id)
            .first()
        )

        if not db_pericia_jogador:
            return None

        for key, value in self._payload_data(pericia, exclude_unset=True).items():
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

        if not db_pericia_jogador:
            return False

        self.db.delete(db_pericia_jogador)
        commit_with_rollback(self.db)
        return True

    def obter_estatisticas_pericias(self, combatente_id: int) -> dict:
        """Obtém estatísticas de perícias do combatente"""
        pericias = self.listar_pericias_combatente(combatente_id)

        pontos_gastos_total = sum(p.custo_total for p in pericias)
        pontos_apenas_graduacao = sum(p.graduacao for p in pericias)

        combatente = (
            self.db.query(Combatente)
            .filter(
                Combatente.id == combatente_id,
                Combatente.deleted_at.is_(None),
            )
            .first()
        )

        if not combatente:
            raise ValueError(f"Combatente {combatente_id} não encontrado")

        nivel = combatente.nivel
        pontos_disponiveis = max(0, (3 * nivel) - pontos_gastos_total)

        return {
            "total_pericias": len(pericias),
            "pontos_gastos_total": pontos_gastos_total,
            "pontos_apenas_graduacao": pontos_apenas_graduacao,
            "pontos_disponiveis": pontos_disponiveis,
            "pericias": pericias,
        }
