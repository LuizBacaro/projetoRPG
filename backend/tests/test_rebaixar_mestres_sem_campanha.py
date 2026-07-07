"""Script rebaixar_mestres_sem_campanha — dry-run e aplicação."""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.games.dnd35.models.campanha import Campanha
from app.games.gurps.models.campanha import GurpsCampanha
from app.games.tormenta.models.campanha import TormentaCampanha
from app.shared.core.database import Base
from app.shared.core.security import hash_senha
from app.shared.models.usuario import PerfilUsuario, Usuario
from scripts.rebaixar_mestres_sem_campanha import (
    listar_mestres_sem_campanha,
    rebaixar_mestres_sem_campanha,
    usuario_tem_campanha_como_mestre_em_algum_jogo,
)


@pytest.fixture(scope="function")
def rebaixar_mestres_db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        mestre_sem = Usuario(
            perfil=PerfilUsuario.MESTRE,
            nome="Mestre órfão",
            email="mestre.sem@example.com",
            senha_hash=hash_senha("SenhaSegura123"),
            ativo=True,
        )
        mestre_com = Usuario(
            perfil=PerfilUsuario.MESTRE,
            nome="Mestre com mesa",
            email="mestre.com@example.com",
            senha_hash=hash_senha("SenhaSegura123"),
            ativo=True,
        )
        jogador = Usuario(
            perfil=PerfilUsuario.JOGADOR,
            nome="Jogador",
            email="jog@example.com",
            senha_hash=hash_senha("SenhaSegura123"),
            ativo=True,
        )
        admin = Usuario(
            perfil=PerfilUsuario.ADMINISTRADOR,
            nome="Admin",
            email="admin@example.com",
            senha_hash=hash_senha("SenhaSegura123"),
            ativo=True,
        )
        db.add_all([mestre_sem, mestre_com, jogador, admin])
        db.commit()
        db.refresh(mestre_sem)
        db.refresh(mestre_com)

        db.add(
            TormentaCampanha(
                mestre_id=mestre_com.id,
                nome="Mesa T20",
                descricao="",
            )
        )
        db.commit()
        yield SessionLocal, mestre_sem, mestre_com
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def test_usuario_tem_campanha_em_algum_jogo(rebaixar_mestres_db):
    SessionLocal, mestre_sem, mestre_com = rebaixar_mestres_db
    db = SessionLocal()
    try:
        assert usuario_tem_campanha_como_mestre_em_algum_jogo(db, mestre_com.id) is True
        assert (
            usuario_tem_campanha_como_mestre_em_algum_jogo(db, mestre_sem.id) is False
        )
    finally:
        db.close()


def test_listar_mestres_sem_campanha(rebaixar_mestres_db):
    SessionLocal, mestre_sem, _mestre_com = rebaixar_mestres_db
    db = SessionLocal()
    try:
        candidatos = listar_mestres_sem_campanha(db)
        assert len(candidatos) == 1
        assert candidatos[0].usuario_id == mestre_sem.id
        assert candidatos[0].email == mestre_sem.email
    finally:
        db.close()


def test_rebaixar_dry_run_nao_altera_banco(rebaixar_mestres_db, monkeypatch):
    SessionLocal, mestre_sem, _ = rebaixar_mestres_db
    monkeypatch.setattr(
        "scripts.rebaixar_mestres_sem_campanha.SessionLocal",
        SessionLocal,
    )
    candidatos, alterados = rebaixar_mestres_sem_campanha(aplicar=False)
    assert len(candidatos) == 1
    assert alterados == 0

    db = SessionLocal()
    try:
        u = db.query(Usuario).filter(Usuario.id == mestre_sem.id).one()
        assert u.perfil == PerfilUsuario.MESTRE
    finally:
        db.close()


def test_rebaixar_aplicar_persiste_jogador(rebaixar_mestres_db, monkeypatch):
    SessionLocal, mestre_sem, mestre_com = rebaixar_mestres_db
    monkeypatch.setattr(
        "scripts.rebaixar_mestres_sem_campanha.SessionLocal",
        SessionLocal,
    )
    candidatos, alterados = rebaixar_mestres_sem_campanha(aplicar=True)
    assert len(candidatos) == 1
    assert alterados == 1

    db = SessionLocal()
    try:
        orfao = db.query(Usuario).filter(Usuario.id == mestre_sem.id).one()
        com_mesa = db.query(Usuario).filter(Usuario.id == mestre_com.id).one()
        assert orfao.perfil == PerfilUsuario.JOGADOR
        assert orfao.usuario_responsavel == "script:rebaixar_mestres_sem_campanha"
        assert com_mesa.perfil == PerfilUsuario.MESTRE
    finally:
        db.close()


def test_campanha_gurps_ou_dnd35_impede_rebaixamento(rebaixar_mestres_db):
    SessionLocal, mestre_sem, _ = rebaixar_mestres_db
    db = SessionLocal()
    try:
        db.add(
            GurpsCampanha(
                mestre_id=mestre_sem.id,
                nome="Mesa GURPS",
                descricao="",
            )
        )
        db.commit()
        assert listar_mestres_sem_campanha(db) == []

        db.query(GurpsCampanha).delete()
        db.add(
            Campanha(
                mestre_id=mestre_sem.id,
                nome="Mesa D35",
                descricao="",
            )
        )
        db.commit()
        assert listar_mestres_sem_campanha(db) == []
    finally:
        db.close()
