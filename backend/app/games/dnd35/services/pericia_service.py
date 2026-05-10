"""
Service de Perícia (D&D 3.5)

Localização: `app.games.dnd35.services.pericia_service`. Shim em
`app.services.pericia_service` durante a reorganização multi-jogo.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app.games.dnd35.models.pericia import Pericia, PericiaJogador
from app.games.dnd35.ports.pericias import (
    PericiaJogadorRepositoryProtocol,
    PericiaRepositoryProtocol,
)
from app.games.dnd35.ports.repositories import CombatenteGetByIdProtocol
from app.games.dnd35.repositories.combatente_repository import CombatenteRepository
from app.games.dnd35.repositories.pericia_repository import (
    PericiaJogadorRepository,
    PericiaRepository,
)
from app.games.dnd35.schemas.pericia import (
    PericiaCreate,
    PericiaJogadorCreate,
    PericiaJogadorUpdate,
    PericiaUpdate,
)


class PericiaService:
    """Serviço de lógica de negócio para perícias"""

    def __init__(
        self,
        db: Session,
        *,
        pericia_repository: Optional[PericiaRepositoryProtocol] = None,
        pericia_jogador_repository: Optional[PericiaJogadorRepositoryProtocol] = None,
        combatente_repository: Optional[CombatenteGetByIdProtocol] = None,
    ):
        self.db = db
        self._pericia = pericia_repository or PericiaRepository(db)
        self._pj = pericia_jogador_repository or PericiaJogadorRepository(db)
        self._combatente = combatente_repository or CombatenteRepository(db)

    # ========== PERÍCIAS DISPONÍVEIS ==========

    def criar_pericia(self, pericia: PericiaCreate) -> Pericia:
        """Cria uma nova perícia"""
        pericia_existente = self._pericia.obter_pericia_por_nome(pericia.nome)

        if pericia_existente:
            if pericia_existente.deleted_at is not None:
                return self._pericia.restaurar_pericia(pericia_existente, pericia)
            raise ValueError(f"Perícia '{pericia.nome}' já existe")

        return self._pericia.criar_pericia(pericia)

    def obter_pericia(self, pericia_id: int) -> Optional[Pericia]:
        """Obtém uma perícia por ID"""
        return self._pericia.obter_pericia(pericia_id)

    def listar_todas_pericias(self, skip: int = 0, limit: int = 100) -> List[Pericia]:
        """Lista todas as perícias disponíveis (ordem alfabética — espelha a Tabela 4-3 do livro)."""
        return self._pericia.listar_pericias(skip=skip, limit=limit)

    def listar_pericias_por_atributo(self, atributo: str) -> List[Pericia]:
        """Lista perícias filtradas por atributo (ordem alfabética)."""
        atributos_validos = ["FOR", "DES", "CON", "INT", "SAB", "CAR"]
        if atributo.upper() not in atributos_validos:
            raise ValueError(f"Atributo '{atributo}' inválido")

        return self._pericia.listar_pericias_por_atributo(atributo.upper())

    def listar_pericias_por_classe(self, classe_nome: str) -> List[Pericia]:
        """Lista perícias padrão de uma classe D&D (ordem alfabética)."""
        return self._pericia.listar_pericias_por_classe(classe_nome)

    def atualizar_pericia(
        self, pericia_id: int, pericia: PericiaUpdate
    ) -> Optional[Pericia]:
        """Atualiza uma perícia"""
        return self._pericia.atualizar_pericia(pericia_id, pericia)

    def deletar_pericia(self, pericia_id: int) -> bool:
        """Deleta uma perícia"""
        return self._pericia.deletar_pericia(pericia_id)

    # ========== CÁLCULO DE CUSTOS ==========

    def calcular_custo_pericia(self, pericia_id: int, classe_nome: str) -> int:
        """
        Calcula o custo de uma perícia para uma classe
        Retorna: 1 se é perícia de classe, 2 se é fora da classe
        """
        return self._pericia.obter_custo_pericia(pericia_id, classe_nome)

    def obter_custos_pericias(
        self, pericia_ids: List[int], classe_nome: str
    ) -> Dict[int, int]:
        """Busca em lote os custos das perícias para uma classe."""
        return self._pericia.obter_custos_pericias(pericia_ids, classe_nome)

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
        combatente = self._combatente.get_by_id(combatente_id)

        if not combatente:
            raise ValueError(f"Combatente com ID {combatente_id} não existe")

        pericia = self._pericia.obter_pericia(pericia_jogador.pericia_id)

        if not pericia:
            raise ValueError(f"Perícia com ID {pericia_jogador.pericia_id} não existe")

        pericia_existente = self._pj.obter_pericia_jogador_por_ids(
            combatente_id, pericia_jogador.pericia_id
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
            destaque_arena=1 if bool(pericia_jogador.destaque_arena) else 0,
        )

        return self._pj.persistir_novo_vinculo(db_pericia_jogador)

    def obter_pericia_jogador(
        self, pericia_jogador_id: int
    ) -> Optional[PericiaJogador]:
        """Obtém uma perícia específica do jogador"""
        return self._pj.obter_pericia_jogador(pericia_jogador_id)

    def listar_pericias_combatente(self, combatente_id: int) -> List[PericiaJogador]:
        """Lista todas as perícias de um combatente"""
        return self._pj.listar_pericias_combatente_com_pericia(combatente_id)

    def atualizar_pericia_jogador(
        self,
        pericia_jogador_id: int,
        pericia: PericiaJogadorUpdate,
    ) -> Optional[PericiaJogador]:
        """Atualiza uma perícia do jogador"""
        return self._pj.atualizar_pericia_jogador(pericia_jogador_id, pericia)

    def deletar_pericia_jogador(self, pericia_jogador_id: int) -> bool:
        """Deleta uma perícia do jogador"""
        return self._pj.deletar_pericia_jogador(pericia_jogador_id)

    def obter_estatisticas_pericias(self, combatente_id: int) -> dict:
        """Obtém estatísticas de perícias do combatente"""
        pericias = self.listar_pericias_combatente(combatente_id)

        pontos_gastos_total = sum(p.custo_total for p in pericias)
        pontos_apenas_graduacao = sum(p.graduacao for p in pericias)

        combatente = self._combatente.get_by_id(combatente_id)

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
