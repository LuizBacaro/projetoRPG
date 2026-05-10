"""
Testes unitários para CombatenteService
"""

from unittest.mock import MagicMock, Mock

import pytest


def _mock_repo_db_chain(mock_repository: Mock) -> None:
    """CombatenteService usa repository.db.query(...) para bônus de armadura."""
    mock_repository.db = MagicMock()
    chain = MagicMock()
    mock_repository.db.query.return_value = chain
    chain.join.return_value = chain
    chain.filter.return_value = chain
    chain.all.return_value = []


from app.games.dnd35.models.combatente import Combatente
from app.games.dnd35.services.combatente_service import CombatenteService
from app.shared.exceptions.custom_exceptions import (
    CombatenteNaoEncontrado,
    DadosInvalidos,
)
from app.shared.models.usuario import PerfilUsuario


class TestCombatenteService:
    """Testes para o serviço de combatente"""

    @pytest.fixture
    def mock_repository(self):
        """Mock do repository"""
        mock = Mock()
        _mock_repo_db_chain(mock)
        return mock

    @pytest.fixture
    def mock_file_service(self):
        """Mock do file service"""
        return Mock()

    @pytest.fixture
    def mock_condicao_repository(self):
        """Mock do repository de condições"""
        return Mock()

    @pytest.fixture
    def service(self, mock_repository, mock_file_service):
        """Instância do service com mocks"""
        return CombatenteService(mock_repository, mock_file_service)

    @pytest.fixture
    def service_com_condicoes(
        self, mock_repository, mock_file_service, mock_condicao_repository
    ):
        """Instância do service com integração de condições"""
        return CombatenteService(
            mock_repository, mock_file_service, mock_condicao_repository
        )

    def test_listar_todos(self, service, mock_repository):
        """Testa listagem de todos os combatentes"""
        # Arrange
        combatentes_mock = [
            Combatente(
                id=1,
                nome="Theron",
                tipo="jogador",
                classe="Guerreiro",
                hp_maximo=85,
                hp_atual=85,
                iniciativa=15,
            ),
            Combatente(
                id=2,
                nome="Lyra",
                tipo="jogador",
                classe="Mago",
                hp_maximo=45,
                hp_atual=45,
                iniciativa=18,
            ),
        ]
        mock_repository.get_all.return_value = combatentes_mock

        # Act
        resultado = service.listar_todos()

        # Assert
        assert len(resultado) == 2
        assert resultado[0].nome == "Theron"
        mock_repository.get_all.assert_called_once()

    def test_listar_todos_para_jogador_retorna_apenas_propriedade(
        self, service, mock_repository
    ):
        """Jogador vê apenas seus próprios combatentes, independente do tipo."""

        class _UsuarioDummy:
            perfil = PerfilUsuario.JOGADOR
            id = 42

        # Jogador pode possuir combatentes de vários tipos
        combatentes_mock = [
            Combatente(
                id=1,
                nome="Theron",
                tipo="jogador",
                classe="Guerreiro",
                hp_maximo=85,
                hp_atual=85,
                iniciativa=15,
            ),
            Combatente(
                id=2,
                nome="Famélico",
                tipo="npc",
                classe="Lobo",
                hp_maximo=20,
                hp_atual=20,
                iniciativa=10,
            ),
        ]
        mock_repository.get_by_owner.return_value = combatentes_mock

        # Sem filtro de tipo, retorna todos os combatentes do jogador
        resultado = service.listar_todos(usuario=_UsuarioDummy())

        assert len(resultado) == 2
        mock_repository.get_by_owner.assert_called_once_with(42, skip=0, limit=100)

        # Com filtro de tipo 'npc', retorna apenas npc do jogador
        mock_repository.reset_mock()
        npc_mock = [combatentes_mock[1]]
        mock_repository.get_by_owner_and_tipo.return_value = npc_mock

        resultado_npc = service.listar_todos(usuario=_UsuarioDummy(), tipo="npc")

        assert len(resultado_npc) == 1
        assert resultado_npc[0].tipo == "npc"
        mock_repository.get_by_owner_and_tipo.assert_called_once_with(
            42, "npc", skip=0, limit=100
        )

    def test_obter_por_id_sucesso(self, service, mock_repository):
        """Testa obter combatente por ID - sucesso"""
        # Arrange
        combatente_mock = Combatente(
            id=1,
            nome="Theron",
            tipo="jogador",
            classe="Guerreiro",
            hp_maximo=85,
            hp_atual=85,
            iniciativa=15,
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
        with pytest.raises(CombatenteNaoEncontrado):
            service.obter_por_id(999)

    def test_criar_combatente(self, service, mock_repository, mock_file_service):
        """Testa criação de combatente"""
        # Arrange
        combatente_data = {
            "nome": "Novo Guerreiro",
            "tipo": "jogador",
            "classe": "Guerreiro",
            "hp_maximo": 100,
            "iniciativa": 15,
        }

        combatente_criado = Combatente(id=1, hp_atual=100, **combatente_data)
        mock_repository.create.return_value = combatente_criado
        mock_repository.get_by_id.return_value = combatente_criado

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
            id=1,
            nome="Theron",
            tipo="jogador",
            classe="Guerreiro",
            hp_maximo=85,
            hp_atual=85,
            iniciativa=15,
        )
        mock_repository.get_by_id.return_value = combatente_mock

        # Act
        resultado = service.aplicar_dano(1, 20)

        # Assert
        assert resultado["hp_atual"] == 65
        mock_repository.update.assert_called_once()

    def test_atualizar_hp_jogador_aceita_negativo_ate_menos_dez(
        self, service, mock_repository
    ):
        """Jogador pode descer até -10 (D&D 3.5: morrendo/morto)."""
        combatente_mock = Combatente(
            id=1,
            nome="Theron",
            tipo="jogador",
            classe="Guerreiro",
            hp_maximo=20,
            hp_atual=5,
            iniciativa=10,
        )
        mock_repository.get_by_id.return_value = combatente_mock
        mock_repository.update.return_value = combatente_mock

        service.atualizar_hp(1, -8)
        assert combatente_mock.hp_atual == -8

        # Não desce abaixo de -10 mesmo com input mais negativo
        service.atualizar_hp(1, -50)
        assert combatente_mock.hp_atual == -10

        # Acima de hp_maximo é capado
        service.atualizar_hp(1, 999)
        assert combatente_mock.hp_atual == 20

    def test_atualizar_hp_monstro_clampa_no_zero(self, service, mock_repository):
        """Monstro continua morrendo a 0 — não fica negativo via atualização direta."""
        combatente_mock = Combatente(
            id=2,
            nome="Goblin",
            tipo="monstro",
            classe="Goblin",
            hp_maximo=8,
            hp_atual=4,
            iniciativa=12,
        )
        mock_repository.get_by_id.return_value = combatente_mock
        mock_repository.update.return_value = combatente_mock

        service.atualizar_hp(2, -5)
        assert combatente_mock.hp_atual == 0

    def test_sincronizar_estado_hp_faz_commit_unico(
        self, service_com_condicoes, mock_condicao_repository
    ):
        combatente = Combatente(
            id=1,
            nome="Theron",
            tipo="jogador",
            classe="Guerreiro",
            hp_maximo=85,
            hp_atual=0,
            iniciativa=15,
        )

        mock_condicao_repository.get_by_nome.side_effect = [
            Mock(id=10),
            Mock(id=20),
        ]

        service_com_condicoes._sincronizar_estado_hp(combatente)

        mock_condicao_repository.remover.assert_called_once_with(1, 20, commit=False)
        mock_condicao_repository.aplicar.assert_called_once_with(
            1, 10, duracao_turnos=-1, commit=False
        )
        mock_condicao_repository.commit.assert_called_once()

    def test_cache_id_condicao_evitar_lookup_repetido(
        self, service_com_condicoes, mock_condicao_repository
    ):
        mock_condicao_repository.get_by_nome.return_value = Mock(id=99)

        primeiro = service_com_condicoes._id_condicao("Inconsciente")
        segundo = service_com_condicoes._id_condicao("Inconsciente")

        assert primeiro == 99
        assert segundo == 99
        mock_condicao_repository.get_by_nome.assert_called_once_with("Inconsciente")

    def test_criar_clerigo_exige_exatamente_dois_dominios(
        self, service, mock_repository
    ):
        combatente_data = {
            "nome": "Aela",
            "tipo": "jogador",
            "classe": "Clérigo",
            "dominios": "Bem",
            "hp_maximo": 18,
            "iniciativa": 2,
        }

        with pytest.raises(DadosInvalidos):
            service.criar(combatente_data)

        mock_repository.create.assert_not_called()

    def test_criar_clerigo_sem_dominios_permitido_no_cadastro_inicial(
        self, service, mock_repository
    ):
        combatente_data = {
            "nome": "Luzia",
            "tipo": "jogador",
            "classe": "Clérigo",
            "hp_maximo": 16,
            "iniciativa": 1,
        }

        combatente_criado = Combatente(
            id=2, hp_atual=16, dominios="", **combatente_data
        )
        mock_repository.create.return_value = combatente_criado
        mock_repository.get_by_id.return_value = combatente_criado

        resultado = service.criar(combatente_data)

        assert resultado.id == 2
        assert resultado.dominios == ""

    def test_criar_nao_clerigo_limpa_dominios(self, service, mock_repository):
        combatente_data = {
            "nome": "Brom",
            "tipo": "jogador",
            "classe": "Guerreiro",
            "dominios": "Bem, Proteção",
            "hp_maximo": 20,
            "iniciativa": 1,
        }

        def _create_side_effect(combatente):
            combatente.id = 99
            return combatente

        mock_repository.create.side_effect = _create_side_effect
        mock_repository.get_by_id.side_effect = lambda _id: Combatente(
            id=_id,
            nome="Brom",
            tipo="jogador",
            classe="Guerreiro",
            dominios="",
            hp_maximo=20,
            hp_atual=20,
            iniciativa=1,
        )

        resultado = service.criar(combatente_data)

        assert resultado.dominios == ""

    def test_atualizar_para_clerigo_sem_dominios_permitido_no_fluxo_generico(
        self, service, mock_repository
    ):
        existente = Combatente(
            id=7,
            nome="Nira",
            tipo="jogador",
            classe="Guerreiro",
            dominios="",
            hp_maximo=24,
            hp_atual=24,
            iniciativa=3,
        )

        atualizado = Combatente(
            id=7,
            nome="Nira",
            tipo="jogador",
            classe="Clérigo",
            dominios="",
            hp_maximo=24,
            hp_atual=24,
            iniciativa=3,
        )

        mock_repository.get_by_id.return_value = existente
        mock_repository.update.side_effect = lambda combatente: combatente
        mock_repository.get_by_id.side_effect = [existente, atualizado]

        resultado = service.atualizar(7, {"classe": "Clérigo"})

        assert resultado.classe == "Clérigo"
        assert resultado.dominios == ""

    def test_atualizar_para_nao_clerigo_remove_dominios(self, service, mock_repository):
        existente = Combatente(
            id=11,
            nome="Kael",
            tipo="jogador",
            classe="Clérigo",
            dominios="Bem, Proteção",
            hp_maximo=30,
            hp_atual=30,
            iniciativa=2,
        )

        atualizado = Combatente(
            id=11,
            nome="Kael",
            tipo="jogador",
            classe="Guerreiro",
            dominios="",
            hp_maximo=30,
            hp_atual=30,
            iniciativa=2,
        )

        mock_repository.get_by_id.return_value = existente
        mock_repository.update.side_effect = lambda combatente: combatente
        mock_repository.get_by_id.side_effect = [existente, atualizado]

        resultado = service.atualizar(11, {"classe": "Guerreiro"})

        assert resultado.dominios == ""
