"""
Service de Combate (Business Logic)
Princípio SOLID: SRP - Lógica de negócio de Combate
"""
from typing import List, Dict, Any, Optional  # ← ADICIONAR Optional aqui
from ..repositories.combate_repository import CombateRepository
from ..repositories.combatente_repository import CombatenteRepository
from ..models.combate import Combate
from ..models.combatente import Combatente
from ..exceptions.custom_exceptions import (
    CombateJaAtivoError,
    CombateNotFoundError,
    CombateFinalizadoError
)


class CombateService:
    """
    Service contendo lógica de negócio para Combate
    """
    
    def __init__(
        self, 
        combate_repository: CombateRepository,
        combatente_repository: CombatenteRepository
    ):
        self.combate_repo = combate_repository
        self.combatente_repo = combatente_repository
    
    def iniciar_combate(self, combatente_ids: List[int]) -> Combate:
        """
        Inicia um novo combate com os combatentes selecionados
        """
        # Validar se já existe combate ativo
        if self.combate_repo.existe_combate_ativo():
            raise CombateJaAtivoError("Já existe um combate ativo. Finalize-o antes de iniciar outro.")
        
        # Buscar combatentes
        combatentes = self.combatente_repo.get_by_ids(combatente_ids)
        
        if len(combatentes) != len(combatente_ids):
            raise ValueError("Alguns combatentes não foram encontrados")
        
        # Ordenar por iniciativa
        combatentes_ordenados = self.combatente_repo.ordenar_por_iniciativa(combatentes)
        ids_ordenados = [c.id for c in combatentes_ordenados]
        
        # Criar combate
        combate = Combate(
            combatentes_ids=ids_ordenados,
            turno_atual=0,
            ativo=True
        )
        
        return self.combate_repo.create(combate)
    
    def obter_combate_ativo(self) -> Optional[Combate]:
        """Obtém o combate ativo atual"""
        return self.combate_repo.get_ativo()
    
    def obter_status_combate(self) -> Dict[str, Any]:
        """
        Obtém o status completo do combate ativo
        """
        combate = self.obter_combate_ativo()
        
        if not combate:
            return {"ativo": False, "message": "Nenhum combate ativo"}
        
        combatentes = self.combatente_repo.get_by_ids(combate.combatentes_ids)
        
        return {
            "id": combate.id,
            "combatentes_ids": combate.combatentes_ids,
            "turno_atual": combate.turno_atual,
            "ativo": combate.ativo,
            "combatente_ativo_id": combate.obter_combatente_ativo_id(),
            "combatentes": combatentes
        }
    
    def avancar_turno(self) -> Combate:
        """
        Avança para o próximo turno
        """
        combate = self.obter_combate_ativo()
        
        if not combate:
            raise CombateNotFoundError("Nenhum combate ativo")
        
        # Verificar se todos estão mortos
        combatentes_vivos = self.combatente_repo.get_vivos_by_ids(combate.combatentes_ids)
        
        if len(combatentes_vivos) == 0:
            combate.finalizar()
            self.combate_repo.update(combate)
            raise CombateFinalizadoError("Todos os combatentes estão mortos. Combate finalizado.")
        
        # Avançar turno
        combate.avancar_turno()
        return self.combate_repo.update(combate)
    
    def finalizar_combate(self) -> bool:
        """
        Finaliza o combate ativo
        """
        combate = self.obter_combate_ativo()
        
        if not combate:
            raise CombateNotFoundError("Nenhum combate ativo")
        
        combate.finalizar()
        self.combate_repo.update(combate)
        return True
    
    def resetar_combate(self) -> Dict[str, Any]:
        """
        Reseta todos os combatentes e finaliza o combate
        """
        # Finalizar combate ativo se houver
        try:
            self.finalizar_combate()
        except CombateNotFoundError:
            pass  # Sem combate ativo, OK
        
        # Resetar HP de todos
        count = self.combatente_repo.resetar_todos_hp()
        
        return {
            "message": "Combate resetado com sucesso",
            "combatentes_resetados": count
        }