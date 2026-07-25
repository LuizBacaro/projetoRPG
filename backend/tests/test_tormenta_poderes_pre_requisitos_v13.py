"""Pré-requisitos de poderes v1.3 (RF-T08g)."""

from __future__ import annotations

import pytest

from app.games.tormenta.rules.poderes_catalogo_v13_t20 import (
    mapa_catalogo_poderes_por_nome,
)
from app.games.tormenta.rules.poderes_pre_requisitos_v13_t20 import (
    PersonagemPoderContext,
    pre_requisitos_de_poder,
    pre_requisitos_por_nome_poder,
    validar_pre_requisitos_poder,
)
from app.games.tormenta.schemas.talento_personagem import TormentaTalentoVinculoCreate
from app.games.tormenta.services.personagem_talentos_service import (
    TormentaPersonagemTalentosService,
)
from app.shared.exceptions.custom_exceptions import DadosInvalidos


@pytest.fixture(autouse=True)
def _limpar_cache_catalogo_poderes():
    mapa_catalogo_poderes_por_nome.cache_clear()
    yield
    mapa_catalogo_poderes_por_nome.cache_clear()


def test_overlay_esquiva_exige_des_1():
    reqs = pre_requisitos_por_nome_poder("Esquiva")
    assert any(
        r.get("tipo") == "atributo_min" and r.get("atributo") == "des" for r in reqs
    )


def test_validar_ataque_poderoso_for_insuficiente():
    ctx = PersonagemPoderContext(for_valor=0, regra_versao="v13")
    res = validar_pre_requisitos_poder("Ataque Poderoso", ctx)
    assert res["valido"] is False
    assert any("Força" in f["descricao"] for f in res["faltando"])


def test_validar_ataque_poderoso_ok():
    ctx = PersonagemPoderContext(for_valor=1, regra_versao="v13")
    res = validar_pre_requisitos_poder("Ataque Poderoso", ctx)
    assert res["valido"] is True


def test_validar_ataque_preciso_exige_poder_anterior():
    ctx = PersonagemPoderContext(des_valor=2, regra_versao="v13")
    res = validar_pre_requisitos_poder("Ataque Preciso", ctx)
    assert res["valido"] is False
    assert any(f.get("tipo") == "poder" for f in res["faltando"])


def test_validar_ataque_preciso_ok_com_cadeia():
    ctx = PersonagemPoderContext(
        for_valor=2,
        des_valor=2,
        poderes_nomes=["Ataque Poderoso"],
        regra_versao="v13",
    )
    res = validar_pre_requisitos_poder("Ataque Preciso", ctx)
    assert res["valido"] is True


def test_magia_acelerada_exige_conjurador():
    """v1.3 renomeou 'Conjuração Acelerada' → 'Magia Acelerada' (aprimoramento p.131)."""
    ctx = PersonagemPoderContext(
        nivel=5,
        ficha_json={"tormenta_classe_mb_slug": "guerreiro", "regra_versao": "v13"},
        regra_versao="v13",
    )
    res = validar_pre_requisitos_poder("Magia Acelerada", ctx)
    assert res["valido"] is False
    assert any("conjurar" in f["descricao"].lower() for f in res["faltando"])


def test_magia_acelerada_ok_arcanista():
    ctx = PersonagemPoderContext(
        nivel=3,
        ficha_json={
            "tormenta_classe_mb_slug": "arcanista",
            "arcanista_caminho": "mago",
            "regra_versao": "v13",
        },
        regra_versao="v13",
    )
    res = validar_pre_requisitos_poder("Magia Acelerada", ctx)
    assert res["valido"] is True


def test_parse_texto_mb_des_13_v13():
    row = {"nome": "Teste", "prerequisitos": "Des 13"}
    reqs = pre_requisitos_de_poder(row, regra_versao="v13")
    assert reqs == [{"tipo": "atributo_min", "atributo": "des", "valor": 3}]


def test_preview_service_payload():
    data = TormentaPersonagemTalentosService.preview_validar_pre_requisitos(
        {
            "nome_poder": "Esquiva",
            "regra_versao": "v13",
            "des_valor": 0,
        }
    )
    assert data["valido"] is False
    assert data["nome_poder"] == "Esquiva"


def test_adicionar_vinculo_bloqueia_pre_requisito(test_db):
    from app.games.tormenta.models.personagem import TormentaPersonagem
    from app.shared.core.security import hash_senha
    from app.shared.models.usuario import PerfilUsuario, Usuario

    u1 = Usuario(
        perfil=PerfilUsuario.JOGADOR,
        nome="PreReq User",
        email="prereq_poder@example.com",
        senha_hash=hash_senha("SenhaSegura123"),
        ativo=True,
    )
    test_db.add(u1)
    test_db.commit()
    test_db.refresh(u1)

    p = TormentaPersonagem(
        dono_id=u1.id,
        tipo="jogador",
        nome="Guerreiro Fraco",
        raca="Humano",
        classe_nivel="Guerreiro 1",
        for_valor=0,
        des_valor=0,
        con_valor=0,
        int_valor=0,
        sab_valor=0,
        car_valor=0,
        pv_max=20,
        pv_atual=20,
        pa_max=3,
        pa_atual=3,
        nivel=1,
        ficha_json={"regra_versao": "v13", "tormenta_classe_mb_slug": "guerreiro"},
    )
    test_db.add(p)
    test_db.commit()
    test_db.refresh(p)

    svc = TormentaPersonagemTalentosService(test_db)
    with pytest.raises(DadosInvalidos, match="Pré-requisitos"):
        svc.adicionar_vinculo(
            p.id,
            TormentaTalentoVinculoCreate(nome="Ataque Poderoso", notas=None),
        )

    item = svc.adicionar_vinculo(
        p.id,
        TormentaTalentoVinculoCreate(nome="Sortudo", notas=None),
    )
    assert item.nome == "Sortudo"
