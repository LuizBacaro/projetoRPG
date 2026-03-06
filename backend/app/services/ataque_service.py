"""
AtaqueService
SRP: regras de negócio para ataques e slots de magia
"""
from typing import List
from ..repositories.ataque_repository import AtaqueRepository
from ..repositories.combatente_repository import CombatenteRepository
from ..models.ataque import Ataque, MagiaSlot
from ..exceptions.custom_exceptions import CombatenteNaoEncontrado


class AtaqueService:

    def __init__(self, ataque_repo: AtaqueRepository,
                 combatente_repo: CombatenteRepository):
        self.ataque_repo     = ataque_repo
        self.combatente_repo = combatente_repo

    def _verificar_combatente(self, combatente_id: int):
        c = self.combatente_repo.get_by_id(combatente_id)
        if not c:
            raise CombatenteNaoEncontrado(combatente_id)
        return c

    # ── Ataques 

    def listar_ataques(self, combatente_id: int) -> List[Ataque]:
        self._verificar_combatente(combatente_id)
        return self.ataque_repo.listar_por_combatente(combatente_id)

    def salvar_ataques(self, combatente_id: int,
                       ataques_data: list) -> List[Ataque]:
        """Substitui todos os ataques do combatente (bulk replace)."""
        self._verificar_combatente(combatente_id)
        dados = [{"nome": a.nome, "bonus_ataque": a.bonus_ataque,
                  "dano": a.dano, "tipo_dano": a.tipo_dano}
                 for a in ataques_data]
        return self.ataque_repo.substituir_todos(combatente_id, dados)

    # ── Magias 

    def listar_magias(self, combatente_id: int) -> List[MagiaSlot]:
        self._verificar_combatente(combatente_id)
        return self.ataque_repo.listar_magias_por_combatente(combatente_id)

    def salvar_magias(self, combatente_id: int,
                      slots_data: list) -> List[MagiaSlot]:
        """Substitui todos os slots de magia do combatente (bulk replace)."""
        self._verificar_combatente(combatente_id)
        # Filtra apenas níveis com total > 0
        dados = [{"nivel": s.nivel, "total": s.total, "usados": s.usados}
                 for s in slots_data if s.total >= 0]
        return self.ataque_repo.substituir_magias(combatente_id, dados)

    def atualizar_usados(self, slot_id: int, usados: int) -> MagiaSlot:
        """Incrementa/decrementa usados de um slot na arena."""
        return self.ataque_repo.atualizar_usados(slot_id, usados)