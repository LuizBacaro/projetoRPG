"""API grimório e magias D&D 5e."""

import pytest
from fastapi import HTTPException

from app.games.dnd5e.models.grimorio import Dnd5eGrimorioMagia
from app.games.dnd5e.models.magia import Dnd5eMagia, Dnd5eMagiaClasse
from app.games.dnd5e.models.personagem import Dnd5ePersonagem
from app.games.dnd5e.repositories.grimorio_repository import Dnd5eGrimorioRepository
from app.games.dnd5e.repositories.magia_repository import Dnd5eMagiaRepository
from app.games.dnd5e.services.grimorio_service import (
    Dnd5eGrimorioService,
    grimorio_item_para_dict,
)
from app.games.dnd5e.services.magia_service import (
    Dnd5eMagiaService,
    magia_para_response,
)
from app.repositories.base import commit_with_rollback
from app.shared.core.database import SessionLocal


def _seed_magia(db, slug="raio-teste", classe="mago", nivel=0):
    magia = db.query(Dnd5eMagia).filter(Dnd5eMagia.slug == slug).first()
    if not magia:
        magia = Dnd5eMagia(
            slug=slug,
            nome="Raio Teste",
            nivel=nivel,
            escola="evocacao",
            tempo_conjuracao="1 ação",
            componentes_verbal=True,
            componentes_somatico=True,
            ativo=True,
        )
        db.add(magia)
        db.flush()
    else:
        magia.nivel = nivel
    ja = (
        db.query(Dnd5eMagiaClasse)
        .filter(
            Dnd5eMagiaClasse.magia_id == magia.id,
            Dnd5eMagiaClasse.classe_slug == classe,
        )
        .first()
    )
    if not ja:
        db.add(
            Dnd5eMagiaClasse(
                magia_id=magia.id, classe_slug=classe, nivel=nivel
            )
        )
        commit_with_rollback(db)
    return magia


def test_grimorio_adicionar_e_listar():
    db = SessionLocal()
    try:
        p = Dnd5ePersonagem(
            tipo="jogador",
            nome="Mago Teste",
            nivel=3,
            ficha_json={"classe_slug": "mago"},
        )
        db.add(p)
        commit_with_rollback(db)
        db.refresh(p)

        magia = _seed_magia(db)
        svc = Dnd5eGrimorioService(
            Dnd5eGrimorioRepository(db), Dnd5eMagiaRepository(db)
        )
        item = svc.adicionar_magia(p.id, magia_id=magia.id, classe="mago")
        assert item.magia_id == magia.id

        total, itens = svc.listar_paginado(p.id, classe="mago")
        assert total >= 1
        payload = grimorio_item_para_dict(itens[0])
        assert payload["magia_nome"] == "Raio Teste"
        assert payload["combatente_id"] == p.id
    finally:
        db.close()


def test_magia_service_listar():
    db = SessionLocal()
    try:
        _seed_magia(db, slug="bola-teste", classe="mago")
        svc = Dnd5eMagiaService(Dnd5eMagiaRepository(db))
        total, rows = svc.listar(classe_slug="mago", nivel=0)
        assert total >= 2
        nomes = {r.nome for r in rows}
        assert "Raio Teste" in nomes
    finally:
        db.close()


def test_grimorio_troca_magia():
    db = SessionLocal()
    try:
        p = Dnd5ePersonagem(
            tipo="jogador",
            nome="Bardo Teste",
            nivel=5,
            ficha_json={"classe_slug": "bardo"},
        )
        db.add(p)
        commit_with_rollback(db)
        db.refresh(p)

        m1 = _seed_magia(db, slug="magia-a", classe="bardo")
        m2 = _seed_magia(db, slug="magia-b", classe="bardo")
        m2.nivel = m1.nivel
        commit_with_rollback(db)

        svc = Dnd5eGrimorioService(
            Dnd5eGrimorioRepository(db), Dnd5eMagiaRepository(db)
        )
        svc.adicionar_magia(p.id, magia_id=m1.id, classe="bardo")
        historico = svc.trocar_magia(
            p.id,
            classe="bardo",
            magia_removida_id=m1.id,
            magia_adicionada_id=m2.id,
        )
        assert historico.magia_adicionada_id == m2.id
        total, itens = svc.listar_paginado(p.id, classe="bardo")
        assert total == 1
        assert itens[0].magia_id == m2.id
    finally:
        db.close()


def test_grimorio_limita_patrulheiro_magias_conhecidas_sem_truques():
    db = SessionLocal()
    try:
        p = Dnd5ePersonagem(
            tipo="jogador",
            nome="Ranger Limite",
            nivel=6,
            ficha_json={"classe_slug": "patrulheiro"},
        )
        db.add(p)
        commit_with_rollback(db)
        db.refresh(p)

        truque = _seed_magia(db, slug="ranger-cantrip", classe="patrulheiro", nivel=0)
        m1 = _seed_magia(db, slug="ranger-l1-a", classe="patrulheiro", nivel=1)
        m2 = _seed_magia(db, slug="ranger-l1-b", classe="patrulheiro", nivel=1)
        m3 = _seed_magia(db, slug="ranger-l1-c", classe="patrulheiro", nivel=1)

        svc = Dnd5eGrimorioService(
            Dnd5eGrimorioRepository(db), Dnd5eMagiaRepository(db)
        )
        svc.adicionar_magia(p.id, magia_id=truque.id, classe="patrulheiro")
        svc.adicionar_magia(p.id, magia_id=m1.id, classe="patrulheiro")
        svc.adicionar_magia(p.id, magia_id=m2.id, classe="patrulheiro")

        with pytest.raises(HTTPException) as exc:
            svc.adicionar_magia(p.id, magia_id=m3.id, classe="patrulheiro")
        assert "limite" in str(exc.value.detail).lower()

        truque2 = _seed_magia(db, slug="ranger-cantrip-2", classe="patrulheiro", nivel=0)
        svc.adicionar_magia(p.id, magia_id=truque2.id, classe="patrulheiro")
        _, itens = svc.listar_paginado(p.id, classe="patrulheiro")
        assert len(itens) == 4
    finally:
        db.close()


def test_grimorio_paladino_sem_limite_conhecidas_no_grimorio():
    db = SessionLocal()
    try:
        p = Dnd5ePersonagem(
            tipo="jogador",
            nome="Paladino Grimorio",
            nivel=6,
            charisma=14,
            ficha_json={"classe_slug": "paladino"},
        )
        db.add(p)
        commit_with_rollback(db)
        db.refresh(p)

        spells = [
            _seed_magia(db, slug=f"pal-spell-{i}", classe="paladino", nivel=1)
            for i in range(4)
        ]
        svc = Dnd5eGrimorioService(
            Dnd5eGrimorioRepository(db), Dnd5eMagiaRepository(db)
        )
        for sp in spells:
            svc.adicionar_magia(p.id, magia_id=sp.id, classe="paladino")
        total, _ = svc.listar_paginado(p.id, classe="paladino")
        assert total == 4
    finally:
        db.close()


def test_grimorio_troca_apenas_uma_por_nivel():
    db = SessionLocal()
    try:
        p = Dnd5ePersonagem(
            tipo="jogador",
            nome="Feiticeiro Teste",
            nivel=4,
            ficha_json={"classe_slug": "feiticeiro"},
        )
        db.add(p)
        commit_with_rollback(db)
        db.refresh(p)

        m1 = _seed_magia(db, slug="truque-a", classe="mago")
        m2 = _seed_magia(db, slug="truque-b", classe="mago")
        m3 = _seed_magia(db, slug="truque-c", classe="mago")

        svc = Dnd5eGrimorioService(
            Dnd5eGrimorioRepository(db), Dnd5eMagiaRepository(db)
        )
        svc.adicionar_magia(p.id, magia_id=m1.id, classe="feiticeiro")
        svc.adicionar_magia(p.id, magia_id=m2.id, classe="feiticeiro")
        svc.trocar_magia(
            p.id,
            classe="feiticeiro",
            magia_removida_id=m1.id,
            magia_adicionada_id=m3.id,
        )
        with pytest.raises(HTTPException) as exc:
            svc.trocar_magia(
                p.id,
                classe="feiticeiro",
                magia_removida_id=m2.id,
                magia_adicionada_id=m1.id,
            )
        assert "neste nível" in str(exc.value.detail).lower()
    finally:
        db.close()
