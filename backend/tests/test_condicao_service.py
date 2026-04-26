"""Testes unitários focados em performance do CondicaoService."""

from unittest.mock import Mock

from app.games.dnd35.services.condicao_service import CondicaoService


class TestCondicaoService:
    def test_decrementar_duracao_todas_commit_unico_quando_ha_mudancas(self):
        condicao_repo = Mock()
        combatente_repo = Mock()
        combatente_repo.get_by_id.return_value = Mock(id=1)

        condicao_repo.get_condicoes_do_combatente.side_effect = [
            [
                {"condicao_id": 10, "nome": "Atordoado", "duracao_turnos": 2},
                {"condicao_id": 11, "nome": "Sangrando", "duracao_turnos": 1},
            ],
            [
                {"condicao_id": 10, "nome": "Atordoado", "duracao_turnos": 1},
            ],
        ]

        service = CondicaoService(condicao_repo, combatente_repo)

        resultado = service.decrementar_duracao_todas(1)

        condicao_repo.atualizar_duracao.assert_called_once_with(1, 10, 1, commit=False)
        condicao_repo.remover.assert_called_once_with(1, 11, commit=False)
        condicao_repo.commit.assert_called_once()
        assert resultado["combatente_id"] == 1
        assert len(resultado["condicoes"]) == 1

    def test_decrementar_duracao_todas_sem_mudanca_nao_commita(self):
        condicao_repo = Mock()
        combatente_repo = Mock()
        combatente_repo.get_by_id.return_value = Mock(id=1)

        condicao_repo.get_condicoes_do_combatente.side_effect = [
            [
                {"condicao_id": 10, "nome": "Invisível", "duracao_turnos": -1},
                {"condicao_id": 11, "nome": "Cego", "duracao_turnos": None},
            ],
            [
                {"condicao_id": 10, "nome": "Invisível", "duracao_turnos": -1},
                {"condicao_id": 11, "nome": "Cego", "duracao_turnos": None},
            ],
        ]

        service = CondicaoService(condicao_repo, combatente_repo)

        service.decrementar_duracao_todas(1)

        condicao_repo.atualizar_duracao.assert_not_called()
        condicao_repo.remover.assert_not_called()
        condicao_repo.commit.assert_not_called()
