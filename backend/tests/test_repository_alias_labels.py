from app.games.dnd35.models.combatente import Combatente
from app.games.dnd35.models.combatente_condicao import CombatenteCondicao
from app.games.dnd35.models.condicao import Condicao
from app.games.dnd35.models.equipamento import Equipamento
from app.games.dnd35.models.talento import Talento
from app.games.dnd35.repositories.condicao_repository import CondicaoRepository
from app.games.dnd35.repositories.equipamento_repository import (
    EquipamentoJogadorRepository,
)
from app.games.dnd35.repositories.talento_repository import TalentoJogadorRepository
from app.games.dnd35.schemas.equipamento import EquipamentoJogadorCreate
from app.games.dnd35.schemas.talento import TalentoJogadorCreate
from app.games.dnd35.services.equipamento_service import EquipamentoService
from app.games.dnd35.services.talento_service import TalentoService


def _criar_combatente(test_db):
    combatente = Combatente(
        nome="Teste",
        tipo="jogador",
        classe="Mago",
        hp_maximo=20,
        hp_atual=20,
        iniciativa=1,
    )
    test_db.add(combatente)
    test_db.commit()
    test_db.refresh(combatente)
    return combatente


def test_equipamento_service_lista_com_alias_labels(test_db):
    combatente = _criar_combatente(test_db)
    equipamento = Equipamento(
        nome="Mochila", descricao="Couro", pagina_referencia="PHB p.101", ativo=True
    )
    test_db.add(equipamento)
    test_db.commit()
    test_db.refresh(equipamento)

    EquipamentoJogadorRepository(test_db).adicionar_equipamento(
        combatente.id,
        EquipamentoJogadorCreate(equipamento_id=equipamento.id, quantidade=2),
    )

    service = EquipamentoService(test_db)
    itens = service.obter_equipamentos_jogador(combatente.id)

    assert len(itens) == 1
    assert itens[0].id == equipamento.id
    assert itens[0].nome == "Mochila"
    assert itens[0].quantidade == 2


def test_talento_service_lista_com_alias_labels(test_db):
    combatente = _criar_combatente(test_db)
    talento = Talento(
        nome="Iniciativa Aprimorada",
        descricao="+4 iniciativa",
        pagina_referencia="PHB p.95",
        ativo=True,
    )
    test_db.add(talento)
    test_db.commit()
    test_db.refresh(talento)

    TalentoJogadorRepository(test_db).adicionar_talento(
        combatente.id,
        TalentoJogadorCreate(talento_id=talento.id),
    )

    service = TalentoService(test_db)
    itens = service.obter_talentos_jogador(combatente.id)

    assert len(itens) == 1
    assert itens[0].id == talento.id
    assert itens[0].nome == "Iniciativa Aprimorada"


def test_condicao_repository_join_com_labels_explicitas(test_db):
    combatente = _criar_combatente(test_db)
    condicao = Condicao(nome="Cego", efeito="Penalidade pesada")
    test_db.add(condicao)
    test_db.commit()
    test_db.refresh(condicao)

    test_db.add(
        CombatenteCondicao(
            combatente_id=combatente.id,
            condicao_id=condicao.id,
            duracao_turnos=3,
        )
    )
    test_db.commit()

    repo = CondicaoRepository(test_db)
    itens = repo.get_condicoes_do_combatente(combatente.id)

    assert len(itens) == 1
    assert itens[0]["condicao_id"] == condicao.id
    assert itens[0]["nome"] == "Cego"
    assert itens[0]["duracao_turnos"] == 3
