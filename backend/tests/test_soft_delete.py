from app.games.dnd35.models.combatente import Combatente
from app.games.dnd35.models.equipamento import Equipamento, EquipamentoJogador
from app.games.dnd35.models.pericia import Pericia
from app.games.dnd35.repositories.combatente_repository import CombatenteRepository
from app.games.dnd35.services.equipamento_service import EquipamentoService
from app.games.dnd35.services.pericia_service import PericiaService


def test_combatente_repository_soft_delete_remove_da_listagem(test_db):
    combatente = Combatente(
        nome="Brom",
        tipo="jogador",
        classe="Guerreiro",
        hp_maximo=22,
        hp_atual=22,
        iniciativa=1,
    )
    test_db.add(combatente)
    test_db.commit()

    repository = CombatenteRepository(test_db)

    assert repository.delete(combatente) is True
    assert combatente.deleted_at is not None
    assert repository.get_by_id(combatente.id) is None
    assert repository.get_all() == []


def test_pericia_service_soft_delete_oculta_pericia(test_db):
    service = PericiaService(test_db)
    pericia = service.criar_pericia(
        type(
            "PericiaPayload",
            (),
            {
                "nome": "Diplomacia",
                "descricao": "Teste social",
                "atributo": "CAR",
                "tipo": "comum",
                "especialidade": None,
                "requer_treinamento": 0,
                "pode_usar_sem_treinamento": 1,
                "sofre_penalidade_armadura": 0,
                "pagina_livro": None,
                "dict": lambda self: {
                    "nome": "Diplomacia",
                    "descricao": "Teste social",
                    "atributo": "CAR",
                    "tipo": "comum",
                    "especialidade": None,
                    "requer_treinamento": 0,
                    "pode_usar_sem_treinamento": 1,
                    "sofre_penalidade_armadura": 0,
                    "pagina_livro": None,
                },
            },
        )()
    )

    assert service.deletar_pericia(pericia.id) is True
    assert service.obter_pericia(pericia.id) is None
    assert service.listar_todas_pericias() == []


def test_equipamento_service_reativa_registro_soft_deleted(test_db):
    equipamento = Equipamento(
        nome="Corda",
        descricao="Velha",
        pagina_referencia="PHB p.128",
        ativo=True,
    )
    equipamento.soft_delete()
    equipamento.ativo = False
    test_db.add(equipamento)
    test_db.commit()

    service = EquipamentoService(test_db)
    payload = type(
        "EquipamentoPayload",
        (),
        {
            "nome": "Corda",
            "descricao": "Nova",
            "pagina_referencia": "PHB p.128",
            "dict": lambda self: {
                "nome": "Corda",
                "descricao": "Nova",
                "pagina_referencia": "PHB p.128",
            },
        },
    )()

    restaurado = service.criar_equipamento(payload)

    assert restaurado.id == equipamento.id
    assert restaurado.deleted_at is None
    assert restaurado.ativo is True
    assert service.listar_todos_equipamentos() == [restaurado]


def test_equipamento_relationship_bidirecional_funciona_sem_warning(test_db):
    equipamento = Equipamento(
        nome="Adaga", descricao="Arma", pagina_referencia="PHB p.120"
    )
    combatente = Combatente(
        nome="Kara",
        tipo="jogador",
        classe="Ladina",
        hp_maximo=18,
        hp_atual=18,
        iniciativa=3,
    )
    test_db.add_all([equipamento, combatente])
    test_db.flush()

    vinculo = EquipamentoJogador(
        combatente_id=combatente.id, equipamento=equipamento, quantidade=1
    )
    test_db.add(vinculo)
    test_db.commit()

    assert equipamento.combatentes[0].id == vinculo.id
