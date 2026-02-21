"""
Service de Combatente (Business Logic)
Princípio SOLID: SRP - Lógica de negócio de Combatente
"""
from typing import List, Optional, Dict
from ..repositories.combatente_repository import CombatenteRepository
from ..services.file_service import FileService
from ..schemas.combatente import CombatenteCreate, CombatenteUpdate, CombatenteResponse
from ..models.combatente import Combatente
from ..exceptions.custom_exceptions import (
    CombatenteNotFoundError, 
    InvalidHPError,
    CombatenteNaoEncontrado,
    DadosInvalidos
)


class CombatenteService:
    """
    Service contendo lógica de negócio para Combatente
    """
    
    def __init__(self, repository: CombatenteRepository, file_service: FileService):
        self.repository = repository
        self.file_service = file_service
    
    def listar_todos(self, tipo: Optional[str] = None) -> List[Combatente]:
        """Lista todos os combatentes ou filtra por tipo"""
        if tipo:
            return self.repository.get_by_tipo(tipo)
        return self.repository.get_all()
    
    def obter_por_id(self, combatente_id: int) -> Combatente:
        """Obtém um combatente por ID"""
        combatente = self.repository.get_by_id(combatente_id)
        if not combatente:
            raise CombatenteNaoEncontrado(combatente_id)
        return combatente
    
    def criar(self, combatente_data: dict, foto_file=None) -> Combatente:
        """
        Cria um novo combatente
        """
        # Upload de foto se fornecida
        foto_url = None
        if foto_file:
            foto_url = self.file_service.salvar_arquivo(foto_file)
            combatente_data["foto_url"] = foto_url
        
        # Definir HP atual igual ao máximo
        combatente_data["hp_atual"] = combatente_data["hp_maximo"]
        
        # Criar entidade
        combatente = Combatente(**combatente_data)
        return self.repository.create(combatente)
    
    def atualizar(
        self,
        combatente_id: int,
        combatente_data: dict,
        foto_file=None
    ) -> Combatente:
        """
        Atualiza um combatente existente
        """
        combatente = self.obter_por_id(combatente_id)

        # Upload de nova foto SOMENTE se fornecida e válida
        if foto_file and hasattr(foto_file, 'filename') and foto_file.filename:
            if combatente.foto_url:
                self.file_service.deletar_arquivo(combatente.foto_url)
            foto_url = self.file_service.salvar_arquivo(foto_file)
            combatente_data["foto_url"] = foto_url

        # Ajustar HP atual se HP máximo mudou
        if "hp_maximo" in combatente_data and combatente.hp_maximo != combatente_data["hp_maximo"]:
            novo_hp_max = combatente_data["hp_maximo"]
            if "hp_atual" not in combatente_data and combatente.hp_maximo > 0:
                proporcao = combatente.hp_atual / combatente.hp_maximo
                combatente_data["hp_atual"] = int(novo_hp_max * proporcao)

        # ✅ CORRIGIDO: usar 'is not None' cobre int 0 corretamente
        # mas também precisamos aceitar value == 0 (zero é válido)
        for key, value in combatente_data.items():
            if hasattr(combatente, key) and value is not None:
                setattr(combatente, key, value)

        return self.repository.update(combatente)

    
    def deletar(self, combatente_id: int) -> bool:
        """Deleta um combatente"""
        combatente = self.obter_por_id(combatente_id)
        
        # Deletar foto se existir
        if combatente.foto_url:
            self.file_service.deletar_arquivo(combatente.foto_url)
        
        return self.repository.delete(combatente)
    
    def atualizar_hp(self, combatente_id: int, novo_hp: int) -> Combatente:
        """
        Atualiza apenas o HP atual do combatente
        """
        combatente = self.obter_por_id(combatente_id)
        
        # Validar HP
        if novo_hp < 0:
            novo_hp = 0
        elif novo_hp > combatente.hp_maximo:
            novo_hp = combatente.hp_maximo
        
        combatente.hp_atual = novo_hp
        return self.repository.update(combatente)
    
    def atualizar_iniciativa(self, combatente_id: int, nova_iniciativa: int) -> Combatente:
        """
        Atualiza apenas a iniciativa do combatente
        """
        combatente = self.obter_por_id(combatente_id)
        
        if nova_iniciativa < 0:
            nova_iniciativa = 0
        
        combatente.iniciativa = nova_iniciativa
        return self.repository.update(combatente)
    
    # ==================== MÉTODOS DE DANO/CURA ====================
    
    def aplicar_dano(self, combatente_id: int, valor: int) -> Dict:
        """
        Aplica dano a um combatente
        
        Args:
            combatente_id: ID do combatente
            valor: Valor do dano
            
        Returns:
            Dicionário com dados atualizados e mensagem
            
        Raises:
            CombatenteNaoEncontrado: Se combatente não existir
            DadosInvalidos: Se valor for inválido
        """
        # Validar valor
        if valor <= 0:
            raise DadosInvalidos("Valor de dano deve ser maior que zero")
        
        # Buscar combatente usando o método do próprio service
        combatente = self.obter_por_id(combatente_id)
        
        # Calcular novo HP (não pode ser negativo)
        hp_anterior = combatente.hp_atual
        novo_hp = max(0, combatente.hp_atual - valor)
        dano_aplicado = hp_anterior - novo_hp
        
        # Atualizar no banco
        combatente.hp_atual = novo_hp
        self.repository.db.commit()
        self.repository.db.refresh(combatente)
        
        # Gerar mensagem
        if novo_hp == 0:
            mensagem = f"{combatente.nome} foi derrotado! 💀"
        else:
            mensagem = f"{combatente.nome} sofreu {dano_aplicado} de dano"
        
        return {
            "id": combatente.id,
            "nome": combatente.nome,
            "hp_atual": combatente.hp_atual,
            "hp_maximo": combatente.hp_maximo,
            "mensagem": mensagem
        }
    
    def aplicar_cura(self, combatente_id: int, valor: int) -> Dict:
        """
        Aplica cura a um combatente
        
        Args:
            combatente_id: ID do combatente
            valor: Valor da cura
            
        Returns:
            Dicionário com dados atualizados e mensagem
            
        Raises:
            CombatenteNaoEncontrado: Se combatente não existir
            DadosInvalidos: Se valor for inválido
        """
        # Validar valor
        if valor <= 0:
            raise DadosInvalidos("Valor de cura deve ser maior que zero")
        
        # Buscar combatente usando o método do próprio service
        combatente = self.obter_por_id(combatente_id)
        
        # Calcular novo HP (não pode ultrapassar HP máximo)
        hp_anterior = combatente.hp_atual
        novo_hp = min(combatente.hp_maximo, combatente.hp_atual + valor)
        cura_aplicada = novo_hp - hp_anterior
        
        # Atualizar no banco
        combatente.hp_atual = novo_hp
        self.repository.db.commit()
        self.repository.db.refresh(combatente)
        
        # Gerar mensagem
        if cura_aplicada == 0:
            mensagem = f"{combatente.nome} já está com HP máximo"
        else:
            mensagem = f"{combatente.nome} recuperou {cura_aplicada} HP"
        
        return {
            "id": combatente.id,
            "nome": combatente.nome,
            "hp_atual": combatente.hp_atual,
            "hp_maximo": combatente.hp_maximo,
            "mensagem": mensagem
        }