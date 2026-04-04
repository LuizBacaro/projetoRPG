from app.models.combatente import Combatente
from app.models.pericia import Pericia, PericiaClasse, PericiaJogador
from app.services.pericia_service import PericiaService


def test_obter_custos_pericias_em_lote(test_db):
    pericia_classe = Pericia(
        nome="Ouvir",
        atributo="SAB",
        tipo="comum",
    )
    pericia_fora = Pericia(
        nome="Blefar",
        atributo="CAR",
        tipo="comum",
    )
    test_db.add_all([pericia_classe, pericia_fora])
    test_db.flush()

    test_db.add(
        PericiaClasse(
            pericia_id=pericia_classe.id,
            classe_nome="Bardo",
            is_default=1,
        )
    )
    test_db.commit()

    service = PericiaService(test_db)

    custos = service.obter_custos_pericias(
        [pericia_classe.id, pericia_fora.id],
        "Bardo",
    )

    assert custos == {
        pericia_classe.id: 1,
        pericia_fora.id: 2,
    }


def test_listar_pericias_combatente_carrega_pericia_relacionada(test_db):
    combatente = Combatente(
        nome="Aramil",
        tipo="jogador",
        classe="Mago",
        nivel=3,
        hp_maximo=18,
        hp_atual=18,
        forca=8,
        destreza=14,
        constituicao=12,
        inteligencia=16,
        sabedoria=10,
        carisma=11,
    )
    pericia = Pericia(
        nome="Concentração",
        atributo="CON",
        tipo="comum",
    )
    test_db.add_all([combatente, pericia])
    test_db.flush()

    test_db.add(
        PericiaJogador(
            combatente_id=combatente.id,
            pericia_id=pericia.id,
            graduacao=2,
            custo_total=2,
            modificador_atributo=1,
            bonus_outros=0,
        )
    )
    test_db.commit()

    service = PericiaService(test_db)

    pericias = service.listar_pericias_combatente(combatente.id)

    assert len(pericias) == 1
    assert pericias[0].pericia.nome == "Concentração"
    assert "pericia" not in pericias[0].__dict__.get("_sa_instance_state").unloaded