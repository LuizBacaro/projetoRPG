"""Equipamentos automáticos v1.3 — origem e kit inicial."""

from app.games.tormenta.rules.equipamentos_ficha_v13_t20 import (
    listar_equipamentos_sync_v13,
    nota_auto_equip_v13,
)
from app.games.tormenta.rules.kit_inicial_v13_t20 import (
    itens_kit_inicial_v13,
    opcoes_kit_inicial_v13,
)
from app.games.tormenta.rules.origens_t20 import resolver_itens_origem_v13
from app.games.tormenta.services.personagem_equipamentos_service import (
    TormentaPersonagemEquipamentosService,
)


def test_resolver_itens_origem_acolito():
    itens = resolver_itens_origem_v13("acolito")
    assert "Símbolo sagrado de madeira" in itens


def test_resolver_itens_origem_escolha_artista():
    itens = resolver_itens_origem_v13(
        "artista", {"origem_itens_escolha": {"artista": "disfarce"}}
    )
    assert itens == ["Kit de disfarce"]


def test_listar_equipamentos_sync_origem_e_kit():
    rows = listar_equipamentos_sync_v13(
        {
            "regra_versao": "v13",
            "nivel": 1,
            "origem_slug": "acolito",
            "tormenta_classe_mb_slug": "guerreiro",
            "kit_inicial_v13": {
                "arma_simples": "Adaga",
                "arma_marcial": "Espada longa",
                "armadura": "Armadura de couro",
                "escudo": True,
            },
        }
    )
    notas = {r["notas"] for r in rows}
    assert (
        nota_auto_equip_v13("origem", "acolito_0_simbolo_sagrado_de_madeira") in notas
    )
    assert any(r["nome"] == "Mochila" for r in rows)
    assert any(r["nome"] == "Espada longa" for r in rows)


def test_kit_arcanista_sem_armadura():
    itens = itens_kit_inicial_v13(
        {
            "regra_versao": "v13",
            "nivel": 1,
            "tormenta_classe_mb_slug": "arcanista",
            "kit_inicial_v13": {
                "arma_simples": "Cajado",
                "armadura": "Armadura de couro",
            },
        }
    )
    nomes = [i["nome"] for i in itens]
    assert "Mochila" in nomes
    assert not any("Armadura" in n for n in nomes)


def test_opcoes_kit_guerreiro():
    op = opcoes_kit_inicial_v13("guerreiro")
    assert op["arma_marcial"] is True
    assert op["armadura_pesada_opcao"] is True


def test_sincronizar_equipamentos_automaticos_v13(test_db):
    from app.games.tormenta.models.personagem import TormentaPersonagem
    from app.shared.core.security import hash_senha
    from app.shared.models.usuario import PerfilUsuario, Usuario

    u1 = Usuario(
        perfil=PerfilUsuario.JOGADOR,
        nome="Sync Equip User",
        email="sync_equip@example.com",
        senha_hash=hash_senha("SenhaSegura123"),
        ativo=True,
    )
    test_db.add(u1)
    test_db.commit()
    test_db.refresh(u1)

    ent = TormentaPersonagem(
        dono_id=u1.id,
        tipo="jogador",
        nome="Sync Equip",
        raca="Humano",
        classe_nivel="Guerreiro 1",
        for_valor=2,
        des_valor=1,
        con_valor=2,
        int_valor=0,
        sab_valor=0,
        car_valor=0,
        pv_max=20,
        pv_atual=20,
        pa_max=3,
        pa_atual=3,
        ca=12,
        nivel=1,
        ficha_json={
            "regra_versao": "v13",
            "origem_slug": "acolito",
            "tormenta_classe_mb_slug": "guerreiro",
            "kit_inicial_v13": {
                "arma_simples": "Adaga",
                "armadura": "Armadura de couro",
            },
        },
    )
    test_db.add(ent)
    test_db.commit()
    test_db.refresh(ent)

    svc = TormentaPersonagemEquipamentosService(test_db)
    fj = dict(ent.ficha_json or {})
    fj["nivel"] = 1
    res = svc.sincronizar_equipamentos_automaticos_v13(ent.id, fj)
    assert res["vinculos_criados"] >= 2

    itens = svc.listar_por_personagem(ent.id)
    assert len(itens) >= 2
    assert any("símbolo" in i.nome.lower() for i in itens)
    assert any(i.notas and i.notas.startswith("auto:v13:") for i in itens)
