"""
Testes unitários para CombatenteService
"""
import pytest
from unittest.mock import Mock, MagicMock
from app.services.combatente_service import CombatenteService
from app.models.combatente import Combatente
from app.exceptions.custom_exceptions import CombatenteNotFoundError


class TestCombatenteService:
    """Testes para o serviço de combatente"""
    
    @pytest.fixture
    def mock_repository(self):
        """Mock do repository"""
        return Mock()
    
    @pytest.fixture
    def mock_file_service(self):
        """Mock do file service"""
        return Mock()
    
    @pytest.fixture
    def service(self, mock_repository, mock_file_service):
        """Instância do service com mocks"""
        return CombatenteService(mock_repository, mock_file_service)
    
    def test_listar_todos(self, service, mock_repository):
        """Testa listagem de todos os combatentes"""
        # Arrange
        combatentes_mock = [
            Combatente(id=1, nome="Theron", tipo="jogador", classe="Guerreiro", hp_maximo=85, hp_atual=85, iniciativa=15),
            Combatente(id=2, nome="Lyra", tipo="jogador", classe="Mago", hp_maximo=45, hp_atual=45, iniciativa=18)
        ]
        mock_repository.get_all.return_value = combatentes_mock
        
        # Act
        resultado = service.listar_todos()
        
        # Assert
        assert len(resultado) == 2
        assert resultado[0].nome == "Theron"
        mock_repository.get_all.assert_called_once()
    
    def test_obter_por_id_sucesso(self, service, mock_repository):
        """Testa obter combatente por ID - sucesso"""
        # Arrange
        combatente_mock = Combatente(
            id=1, nome="Theron", tipo="jogador", classe="Guerreiro",
            hp_maximo=85, hp_atual=85, iniciativa=15
        )
        mock_repository.get_by_id.return_value = combatente_mock
        
        # Act
        resultado = service.obter_por_id(1)
        
        # Assert
        assert resultado.nome == "Theron"
        mock_repository.get_by_id.assert_called_once_with(1)
    
    def test_obter_por_id_nao_encontrado(self, service, mock_repository):
        """Testa obter combatente por ID - não encontrado"""
        # Arrange
        mock_repository.get_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(CombatenteNotFoundError):
            service.obter_por_id(999)
    
    def test_criar_combatente(self, service, mock_repository, mock_file_service):
        """Testa criação de combatente"""
        # Arrange
        combatente_data = {
            "nome": "Novo Guerreiro",
            "tipo": "jogador",
            "classe": "Guerreiro",
            "hp_maximo": 100,
            "iniciativa": 15
        }
        
        combatente_criado = Combatente(id=1, hp_atual=100, **combatente_data)
        mock_repository.create.return_value = combatente_criado
        
        # Act
        resultado = service.criar(combatente_data)
        
        # Assert
        assert resultado.id == 1
        assert resultado.nome == "Novo Guerreiro"
        assert resultado.hp_atual == resultado.hp_maximo
        mock_repository.create.assert_called_once()
    
    def test_aplicar_dano(self, service, mock_repository):
        """Testa aplicação de dano"""
        # Arrange
        combatente_mock = Combatente(
            id=1, nome="Theron", tipo="jogador", classe="Guerreiro",
            hp_maximo=85, hp_atual=85, iniciativa=15
        )
        mock_repository.get_by_id.return_value = combatente_mock
        mock_repository.update.return_value = combatente_mock
        
        # Act
        resultado = service.aplicar_dano(1, 20)
        
        # Assert
        assert resultado.hp_atual == 65
        mock_repository.update.assert_called_once()