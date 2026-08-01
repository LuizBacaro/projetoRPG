"""Catálogo e ativação de poderes v1.3."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import pytest

from app.games.tormenta.rules.poderes_catalogo_v13_t20 import (
    categoria_v13_de_item,
    custo_pm_de_item,
    enriquecer_item_catalogo_poder,
    metadados_poder_por_nome,
)
from app.games.tormenta.services.personagem_talentos_service import (
    TormentaPersonagemTalentosService,
)
from app.shared.exceptions.custom_exceptions import DadosInvalidos


def test_catalogo_poderes_v13_volume_e_amostras():
    """Cap. 2 v1.3 — ~162 poderes nas 5 categorias de catálogo (+ concedidos/tormenta)."""
    path = (
        Path(__file__).resolve().parents[1]
        / "app"
        / "games"
        / "tormenta"
        / "data"
        / "talentos_mb_catalogo.json"
    )
    data = json.loads(path.read_text(encoding="utf-8"))
    itens = data.get("itens") or []
    assert 150 <= len(itens) <= 180, len(itens)
    cats = Counter(
        str(r.get("categoria_v13") or "") for r in itens if isinstance(r, dict)
    )
    assert cats.get("combate", 0) >= 40
    assert cats.get("destino", 0) >= 20
    assert cats.get("magia", 0) >= 8
    assert cats.get("concedido", 0) >= 70
    assert cats.get("tormenta", 0) >= 20
    nomes = {str(r.get("nome") or "") for r in itens if isinstance(r, dict)}
    for amostra in (
        "Acuidade com Arma",
        "Surto Heroico",
        "Sortudo",
        "Êxtase da Loucura",
    ):
        assert amostra in nomes, amostra


def test_lista_talentos_mb_sem_fragmentos_de_proficiencia():
    """Catálogo runtime = JSON Cap. 2; sem split de talentos_adicionais (adaga/machado)."""
    from app.games.tormenta.rules.catalogo_t20 import lista_talentos_mb_catalogo

    rows = lista_talentos_mb_catalogo()
    assert len(rows) == 162
    nomes = {str(r.get("nome") or "").strip().lower() for r in rows}
    for bad in (
        "adaga",
        "machado)",
        "bordão",
        "dardo",
        "funda",
        "usar armas (clava",
        "médias e pesadas)",
        "shuriken)",
    ):
        assert bad not in nomes, bad
    assert not any(n.startswith("usar armas") for n in nomes)
    assert not any(n.startswith("usar armaduras") for n in nomes)


def test_categoria_v13_combate():
    assert (
        categoria_v13_de_item({"categoria": "Combate", "secao": "Ataque"}) == "combate"
    )


def test_categoria_v13_concedido_por_nota():
    assert (
        categoria_v13_de_item(
            {"categoria": "Geral"},
            notas="auto:v13:concedido:coragem_total",
        )
        == "concedido"
    )


def test_custo_pm_parse_descricao():
    row = {
        "descricao_resumo": "Conjurar como movimento (+2 PM; MB).",
    }
    assert custo_pm_de_item(row) == 2


def test_metadados_magia_acelerada_v13():
    """v1.3 renomeou 'Conjuração Acelerada' → 'Magia Acelerada' (aprimoramento, +4 PM)."""
    meta = metadados_poder_por_nome("Magia Acelerada")
    assert meta["categoria_v13"] == "magia"
    assert meta["custo_pm"] == 4


def test_ativar_poder_debita_pm(test_db):
    from app.games.tormenta.models.personagem import TormentaPersonagem
    from app.games.tormenta.models.talento import (
        TormentaTalento,
        TormentaTalentoPersonagem,
    )
    from app.shared.core.security import hash_senha
    from app.shared.models.usuario import PerfilUsuario, Usuario

    u1 = Usuario(
        perfil=PerfilUsuario.JOGADOR,
        nome="Poder PM User",
        email="poder_pm@example.com",
        senha_hash=hash_senha("SenhaSegura123"),
        ativo=True,
    )
    test_db.add(u1)
    test_db.commit()
    test_db.refresh(u1)

    ent = TormentaPersonagem(
        dono_id=u1.id,
        tipo="jogador",
        nome="Magia Acel",
        raca="Humano",
        classe_nivel="Arcanista 5",
        for_valor=0,
        des_valor=0,
        con_valor=0,
        int_valor=2,
        sab_valor=0,
        car_valor=0,
        pv_max=20,
        pv_atual=20,
        pa_max=10,
        pa_atual=10,
        ca=12,
        nivel=5,
        ficha_json={"regra_versao": "v13"},
    )
    test_db.add(ent)
    test_db.commit()
    test_db.refresh(ent)

    tal = TormentaTalento(
        nome="Magia Acelerada",
        origem_catalogo_mb=True,
    )
    test_db.add(tal)
    test_db.commit()
    test_db.refresh(tal)

    vinc = TormentaTalentoPersonagem(
        personagem_id=ent.id,
        talento_id=tal.id,
    )
    test_db.add(vinc)
    test_db.commit()
    test_db.refresh(vinc)

    svc = TormentaPersonagemTalentosService(test_db)
    res = svc.ativar_poder_com_pm(ent.id, vinc.id)
    assert res.custo_pm == 4
    assert res.pa_atual_antes == 10
    assert res.pa_atual_depois == 6

    test_db.refresh(ent)
    assert ent.pa_atual == 6


def test_ativar_poder_sem_pm_rejeita(test_db):
    from app.games.tormenta.models.personagem import TormentaPersonagem
    from app.games.tormenta.models.talento import (
        TormentaTalento,
        TormentaTalentoPersonagem,
    )
    from app.shared.core.security import hash_senha
    from app.shared.models.usuario import PerfilUsuario, Usuario

    u1 = Usuario(
        perfil=PerfilUsuario.JOGADOR,
        nome="Poder Pass User",
        email="poder_pass@example.com",
        senha_hash=hash_senha("SenhaSegura123"),
        ativo=True,
    )
    test_db.add(u1)
    test_db.commit()
    test_db.refresh(u1)

    ent = TormentaPersonagem(
        dono_id=u1.id,
        tipo="jogador",
        nome="Esquiva",
        raca="Humano",
        classe_nivel="Guerreiro 1",
        for_valor=0,
        des_valor=2,
        con_valor=0,
        int_valor=0,
        sab_valor=0,
        car_valor=0,
        pv_max=20,
        pv_atual=20,
        pa_max=3,
        pa_atual=3,
        ca=12,
        nivel=1,
        ficha_json={"regra_versao": "v13"},
    )
    test_db.add(ent)
    test_db.commit()
    test_db.refresh(ent)

    tal = TormentaTalento(nome="Esquiva", origem_catalogo_mb=True)
    test_db.add(tal)
    test_db.commit()
    test_db.refresh(tal)

    vinc = TormentaTalentoPersonagem(personagem_id=ent.id, talento_id=tal.id)
    test_db.add(vinc)
    test_db.commit()
    test_db.refresh(vinc)

    svc = TormentaPersonagemTalentosService(test_db)
    with pytest.raises(DadosInvalidos, match="custo PM"):
        svc.ativar_poder_com_pm(ent.id, vinc.id)
