"""Testes do bestiário D&D 3.5 (catálogo + import)."""

from __future__ import annotations

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.dependencies import get_combatente_service, get_file_service
from app.games.dnd35.api.v1 import ataques as ataques_router
from app.games.dnd35.api.v1 import combatentes as combatentes_router
from app.games.dnd35.api.v1 import regras as regras_router
from app.games.dnd35.repositories.combatente_repository import CombatenteRepository
from app.games.dnd35.rules.bestiario_mm35 import (
    lista_bestiario_mm35,
    obter_bestiario_por_slug,
)
from app.games.dnd35.services.combatente_service import CombatenteService
from app.services.file_service import FileService
from app.shared.core.database import Base, get_db
from app.shared.core.deps import get_usuario_atual, requer_dono_ou_admin_combatente
from app.shared.core.security import hash_senha
from app.shared.models.usuario import PerfilUsuario
from app.shared.models.usuario import Usuario as UModel


@pytest.fixture(scope="function")
def bestiario_db():
    import app.models  # noqa: F401

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        mestre = UModel(
            perfil=PerfilUsuario.MESTRE,
            nome="Mestre Bestiario",
            email="mestre.bestiario@example.com",
            senha_hash=hash_senha("SenhaSegura123"),
            ativo=True,
        )
        db.add(mestre)
        db.commit()
        db.refresh(mestre)
        yield SessionLocal, mestre
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def _build_client(SessionLocal, usuario) -> TestClient:
    app = FastAPI()
    app.include_router(regras_router.router, prefix="/api/v1")
    app.include_router(combatentes_router.router, prefix="/api/v1")
    app.include_router(ataques_router.router, prefix="/api/v1")

    def _override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    def override_svc(db=Depends(get_db)):
        return CombatenteService(CombatenteRepository(db), FileService())

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_usuario_atual] = lambda: usuario
    app.dependency_overrides[requer_dono_ou_admin_combatente] = lambda: object()
    app.dependency_overrides[get_file_service] = lambda: FileService()
    app.dependency_overrides[get_combatente_service] = override_svc
    return TestClient(app)


def test_catalogo_lote_inicial():
    rows = lista_bestiario_mm35()
    # Lotes 0–4 (A–Z + animais + insetos + dragões) → mínimo 300
    assert len(rows) >= 300
    goblin = obter_bestiario_por_slug("goblin")
    assert goblin is not None
    assert goblin["ca"] == 15
    assert goblin["toque"] == 12
    assert goblin["surpresa"] == 14
    jovem = obter_bestiario_por_slug("dragao-azul-jovem")
    assert jovem is not None
    assert jovem["especie_pai"] == "dragao-azul"
    assert jovem["categoria_idade"] == "jovem"
    azul_idades = [
        r
        for r in rows
        if r.get("especie_pai") == "dragao-azul" and r.get("categoria_idade")
    ]
    assert len(azul_idades) == 12
    vermelho_adulto = obter_bestiario_por_slug("dragao-vermelho-adulto")
    assert vermelho_adulto is not None
    assert vermelho_adulto["especie_pai"] == "dragao-vermelho"
    assert vermelho_adulto["ca"] >= 20
    abolete = obter_bestiario_por_slug("abolete")
    assert abolete is not None
    assert abolete["ca"] == 16
    assert abolete["pagina_referencia"]
    cao = obter_bestiario_por_slug("cao")
    assert cao is not None
    assert cao["tipo_criatura"] == "Animal"
    assert cao["nd_rotulo"] == "1/3"
    animais = [r for r in rows if r.get("tipo_criatura") == "Animal"]
    assert len(animais) >= 50
    escorpiao = obter_bestiario_por_slug("escorpiao-medio")
    assert escorpiao is not None
    assert escorpiao["tipo_criatura"] == "Inseto"
    insetos = [r for r in rows if r.get("tipo_criatura") == "Inseto"]
    assert len(insetos) >= 30
    pais = [
        r for r in rows if r.get("tipo_criatura") == "Dragão" and r.get("nd") is None
    ]
    assert len(pais) >= 10


def test_get_bestiario_api(bestiario_db):
    SessionLocal, mestre = bestiario_db
    client = _build_client(SessionLocal, mestre)
    r = client.get("/api/v1/dnd35/regras/bestiario", params={"limit": 200})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["total"] >= 300
    assert (
        len(body["itens"]) >= 90
    )  # API limit default may page; request used limit 200
    d = client.get("/api/v1/dnd35/regras/bestiario/goblin")
    assert d.status_code == 200
    assert d.json()["nome"] == "Goblin"
    assert d.json()["ataques"]
    a = client.get("/api/v1/dnd35/regras/bestiario/abolete")
    assert a.status_code == 200
    assert a.json()["nd"] == 7
    anim = client.get(
        "/api/v1/dnd35/regras/bestiario", params={"tipo": "Animal", "limit": 200}
    )
    assert anim.status_code == 200
    assert anim.json()["total"] >= 50
    ins = client.get(
        "/api/v1/dnd35/regras/bestiario", params={"tipo": "Inseto", "limit": 200}
    )
    assert ins.status_code == 200
    assert ins.json()["total"] >= 30
    drag = client.get(
        "/api/v1/dnd35/regras/bestiario", params={"tipo": "Dragão", "limit": 200}
    )
    assert drag.status_code == 200
    assert drag.json()["total"] >= 100
    rv = client.get("/api/v1/dnd35/regras/bestiario/dragao-vermelho-jovem")
    assert rv.status_code == 200
    assert rv.json()["especie_pai"] == "dragao-vermelho"


def test_importar_goblin_mestre(bestiario_db):
    SessionLocal, mestre = bestiario_db
    client = _build_client(SessionLocal, mestre)
    r = client.post(
        "/api/v1/combatentes/importar-bestiario",
        json={"slug": "goblin", "tipo": "monstro"},
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["tipo"] == "monstro"
    assert body["nome"] == "Goblin"
    assert body["hp_maximo"] == 5
    assert body["ca"] == 15
    assert body["toque"] == 12
    assert body["surpresa"] == 14
    assert "Livro dos Monstros" in (body.get("pagina_referencia") or "")
    cid = body["id"]
    atqs = client.get(f"/api/v1/combatentes/{cid}/ataques")
    assert atqs.status_code == 200
    assert len(atqs.json()) >= 1


def test_importar_especie_pai_rejeitada(bestiario_db):
    SessionLocal, mestre = bestiario_db
    client = _build_client(SessionLocal, mestre)
    r = client.post(
        "/api/v1/combatentes/importar-bestiario",
        json={"slug": "dragao-azul"},
    )
    assert r.status_code == 422


def test_importar_dragao_jovem(bestiario_db):
    SessionLocal, mestre = bestiario_db
    client = _build_client(SessionLocal, mestre)
    r = client.post(
        "/api/v1/combatentes/importar-bestiario",
        json={"slug": "dragao-azul-jovem"},
    )
    assert r.status_code == 201, r.text
    assert r.json()["ca"] == 21
