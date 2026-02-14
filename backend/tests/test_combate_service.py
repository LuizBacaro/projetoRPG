"""
Testes unitários para CombateService
"""
import pytest
from unittest.mock import Mock
from app.services.combate_service import CombateService
from app.models.combate import Combate
from app.models.combatente import Combatente
from app.exceptions.custom_exceptions import CombateJaAtivoError, CombateNotFoundError


class TestCombateService:
    """Testes para o serviço de combate"""
    
    @pytest.fixture
    def mock_combate_repo(self):
        """Mock do combate repository"""
        return Mock()
    
    @pytest.fixture
    def mock_combatente_repo(self):
        """Mock do combatente repository"""
        return Mock()
    
    @pytest.fixture
    def service(self, mock_combate_repo, mock_combatente_repo):
        """Instância do service com mocks"""
        return CombateService(mock_combate_repo, mock_combatente_repo)
    
    def test_iniciar_combate_sucesso(self, service, mock_combate_repo, mock_combatente_repo):
        """Testa iniciar combate - sucesso"""
        # Arrange
        combatentes = [
            Combatente(id=1, nome="Theron", tipo="jogador", classe="Guerreiro", hp_maximo=85, hp_atual=85, iniciativa=15),
            Combatente(id=2, nome="Lyra", tipo="jogador", classe="Mago", hp_maximo=45, hp_atual=45, iniciativa=18)
        ]
        
        mock_combate_repo.existe_combate_ativo.return_value = False
        mock_combatente_repo.get_by_ids.return_value = combatentes
        mock_combatente_repo.ordenar_por_iniciativa.return_value = sorted(combatentes, key=lambda c: c.iniciativa, reverse=True)
        
        combate_criado = Combate(id=1, combatentes_ids=[2, 1], turno_atual=0, ativo=True)
        mock_combate_repo.create.return_value = combate_criado
        
        # Act
        resultado = service.iniciar_combate([1, 2])
        
        # Assert
        assert resultado.ativo == True
        assert resultado.combatentes_ids == [2, 1]  # Ordenado por iniciativa (Lyra 18, Theron 15)
        mock_combate_repo.create.assert_called_once()
    
    def test_iniciar_combate_ja_ativo(self, service, mock_combate_repo):
        """Testa iniciar combate quando já existe um ativo"""
        # Arrange
        mock_combate_repo.existe_combate_ativo.return_value = True
        
        # Act & Assert
        with pytest.raises(CombateJaAtivoError):
            service.iniciar_combate([1, 2])
    
    def test_avancar_turno(self, service, mock_combate_repo, mock_combatente_repo):
        """Testa avanço de turno"""
        # Arrange
        combate_mock = Combate(id=1, combatentes_ids=[1, 2, 3], turno_atual=0, ativo=True)
        mock_combate_repo.get_ativo.return_value = combate_mock
        
        combatentes_vivos = [
            Combatente(id=1, nome="C1", tipo="jogador", classe="G", hp_maximo=50, hp_atual=30, iniciativa=15),
            Combatente(id=2, nome="C2", tipo="jogador", classe="M", hp_maximo=40, hp_atual=20, iniciativa=12)
        ]
        mock_combatente_repo.get_vivos_by_ids.return_value = combatentes_vivos
        mock_combate_repo.update.return_value = combate_mock
        
        # Act
        resultado = service.avancar_turno()
        
        # Assert
        assert resultado.turno_atual == 1
        mock_combate_repo.update.assert_called_once()
    
    def test_finalizar_combate(self, service, mock_combate_repo):
        """Testa finalização de combate"""
        # Arrange
        combate_mock = Combate(id=1, combatentes_ids=[1, 2], turno_atual=0, ativo=True)
        mock_combate_repo.get_ativo.return_value = combate_mock
        
        # Act
        resultado = service.finalizar_combate()
        
        # Assert
        assert resultado == True
        mock_combate_repo.update.assert_called_once()