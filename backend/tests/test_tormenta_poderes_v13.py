"""Poderes automáticos v1.3 — sync SQL."""

from app.games.tormenta.rules.poderes_ficha_v13_t20 import (
    listar_poderes_sync_v13,
    nome_poder_por_slug_v13,
    nota_auto_poder_v13,
    slugs_poderes_de_beneficios_origem,
)
from app.games.tormenta.services.personagem_talentos_service import (
    TormentaPersonagemTalentosService,
)


def test_slugs_poderes_de_beneficios_origem():
    assert slugs_poderes_de_beneficios_origem(["pericia:cura", "poder:medicina"]) == [
        "medicina"
    ]


def test_nome_poder_por_slug_v13():
    assert nome_poder_por_slug_v13("lobo_solitario") == "Lobo Solitario"


def test_listar_poderes_sync_origem_e_concedido():
    rows = listar_poderes_sync_v13(
        {
            "regra_versao": "v13",
            "origem_beneficios": ["pericia:cura", "poder:medicina"],
            "poder_concedido_slug": "coragem_total",
        }
    )
    notas = {r["notas"] for r in rows}
    assert nota_auto_poder_v13("origem", "medicina") in notas
    assert nota_auto_poder_v13("concedido", "coragem_total") in notas


def test_listar_poderes_sync_versatil():
    rows = listar_poderes_sync_v13(
        {
            "regra_versao": "v13",
            "humano_versatil": "pericia_poder",
            "humano_versatil_poder_slug": "sortudo",
        }
    )
    assert len(rows) == 1
    assert rows[0]["slug"] == "sortudo"


def test_sincronizar_poderes_automaticos_v13(test_db):
    from app.games.tormenta.models.personagem import TormentaPersonagem
    from app.shared.core.security import hash_senha
    from app.shared.models.usuario import PerfilUsuario, Usuario

    u1 = Usuario(
        perfil=PerfilUsuario.JOGADOR,
        nome="Sync Poder User",
        email="sync_poder@example.com",
        senha_hash=hash_senha("SenhaSegura123"),
        ativo=True,
    )
    test_db.add(u1)
    test_db.commit()
    test_db.refresh(u1)

    ent = TormentaPersonagem(
        dono_id=u1.id,
        tipo="jogador",
        nome="Sync Poder",
        raca="Humano",
        classe_nivel="Bárbaro 1",
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
            "origem_beneficios": ["pericia:cura", "poder:medicina"],
        },
    )
    test_db.add(ent)
    test_db.commit()
    test_db.refresh(ent)

    svc = TormentaPersonagemTalentosService(test_db)
    res = svc.sincronizar_poderes_automaticos_v13(ent.id, ent.ficha_json)
    assert res["vinculos_criados"] == 1

    itens = svc.listar_por_personagem(ent.id)
    assert len(itens) == 1
    assert "medicina" in itens[0].nome.lower() or itens[0].nome == "Medicina"
    assert itens[0].notas and itens[0].notas.startswith("auto:v13:")
