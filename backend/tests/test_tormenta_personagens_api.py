"""Integração HTTP — personagens Tormenta (CRUD básico)."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.dependencies import get_file_service
from app.games.tormenta.api.v1.personagens import router as tormenta_personagens_router
from app.services.file_service import FileService
from app.shared.core.database import get_db
from app.shared.core.deps import get_usuario_atual
from app.shared.models.usuario import Usuario


@pytest.fixture(scope="function")
def tormenta_personagens_db():
    """SQLite em memória: dois jogadores + um mestre (monstro sem validação de compra)."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.pool import StaticPool

    import app.models  # noqa: F401
    from app.shared.core.database import Base
    from app.shared.core.security import hash_senha
    from app.shared.models.usuario import PerfilUsuario
    from app.shared.models.usuario import Usuario as UModel

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        u1 = UModel(
            perfil=PerfilUsuario.JOGADOR,
            nome="Tormenta Um",
            email="tormenta1@example.com",
            senha_hash=hash_senha("SenhaSegura123"),
            ativo=True,
        )
        u2 = UModel(
            perfil=PerfilUsuario.JOGADOR,
            nome="Tormenta Dois",
            email="tormenta2@example.com",
            senha_hash=hash_senha("SenhaSegura123"),
            ativo=True,
        )
        u_mestre = UModel(
            perfil=PerfilUsuario.MESTRE,
            nome="Tormenta Mestre",
            email="tormenta.mestre@example.com",
            senha_hash=hash_senha("SenhaSegura123"),
            ativo=True,
        )
        db.add_all([u1, u2, u_mestre])
        db.commit()
        db.refresh(u1)
        db.refresh(u2)
        db.refresh(u_mestre)
        yield SessionLocal, u1, u2, u_mestre
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def _build_client(
    SessionLocal, usuario: SimpleNamespace, file_service=None
) -> TestClient:
    app = FastAPI()
    app.include_router(tormenta_personagens_router, prefix="/api/v1")

    def _override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_usuario_atual] = lambda: usuario
    if file_service is not None:
        app.dependency_overrides[get_file_service] = lambda: file_service
    return TestClient(app)


def _usuario(u: Usuario) -> SimpleNamespace:
    return SimpleNamespace(id=u.id, perfil=u.perfil, email=u.email, nome=u.nome)


_T20_JOG_BASE20 = {
    "for_valor": 8,
    "des_valor": 8,
    "con_valor": 8,
    "int_valor": 18,
    "sab_valor": 8,
    "car_valor": 18,
}


def _t20_post_jogador_json(**kwargs) -> dict:
    """POST mínimo tipo jogador com compra MB = 20 pontos (atributos + ficha_json alinhados)."""
    ficha_extra = kwargs.pop("ficha_json", None) or {}
    body = {"tipo": "jogador", **_T20_JOG_BASE20.copy()}
    body.update(kwargs)
    if "pv_max" in body and "pv_atual" not in body:
        body["pv_atual"] = body["pv_max"]
    fj = {**ficha_extra}
    fj["atributos_compra"] = {
        "for": body["for_valor"],
        "des": body["des_valor"],
        "con": body["con_valor"],
        "int": body["int_valor"],
        "sab": body["sab_valor"],
        "car": body["car_valor"],
    }
    body["ficha_json"] = fj
    return body


def test_criar_mago_mb_preenche_pontos_de_magia(tormenta_personagens_db):
    """Classe conjuradora MB + atributos na criação → pa_max/pa_atual pela regra do livro."""
    SessionLocal, u1, *_ = tormenta_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))
    r = client.post(
        "/api/v1/tormenta/personagens",
        json=_t20_post_jogador_json(
            nome="Arcanus",
            nivel=1,
            classe_nivel="Mago 1",
            pv_max=6,
            pv_atual=6,
            ficha_json={"tormenta_classe_mb_slug": "mago"},
        ),
    )
    assert r.status_code == 201
    body = r.json()
    assert body["pa_max"] == 5
    assert body["pa_atual"] == 5


def test_patch_mago_mb_sobe_nivel_atualiza_pm(tormenta_personagens_db):
    """PATCH nível + atributos mantém PM MB alinhado ao livro."""
    SessionLocal, u1, *_ = tormenta_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))
    rid = client.post(
        "/api/v1/tormenta/personagens",
        json=_t20_post_jogador_json(
            nome="Arcanus2",
            nivel=1,
            classe_nivel="Mago 1",
            pv_max=6,
            pv_atual=6,
            ficha_json={"tormenta_classe_mb_slug": "mago"},
        ),
    ).json()["id"]
    r2 = client.patch(
        f"/api/v1/tormenta/personagens/{rid}",
        json={"nivel": 2},
    )
    assert r2.status_code == 200
    assert r2.json()["pa_max"] == 8
    assert r2.json()["pa_atual"] == 8


def test_patch_paladino_abaixo_do_5_sem_pm(tormenta_personagens_db):
    SessionLocal, u1, *_ = tormenta_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))
    rid = client.post(
        "/api/v1/tormenta/personagens",
        json=_t20_post_jogador_json(
            nome="Luz",
            nivel=4,
            classe_nivel="Paladino 4",
            for_valor=8,
            des_valor=8,
            con_valor=10,
            int_valor=16,
            sab_valor=12,
            car_valor=18,
            pv_max=10,
            pv_atual=10,
            ficha_json={"tormenta_classe_mb_slug": "paladino"},
        ),
    ).json()["id"]
    b = client.get(f"/api/v1/tormenta/personagens/{rid}").json()
    assert b["pa_max"] == 0
    r5 = client.patch(f"/api/v1/tormenta/personagens/{rid}", json={"nivel": 5})
    assert r5.status_code == 200
    # 1 PM + SAB mod (+1) no 5º, sem níveis extras além do inicial
    assert r5.json()["pa_max"] == 2


def test_get_sincroniza_pm_mb_quando_banco_estava_zerado(tormenta_personagens_db):
    """GET detalhe reaplica regra MB de PM e persiste se o banco estiver defasado (ex.: ficha antiga)."""
    from app.games.tormenta.models.personagem import TormentaPersonagem

    SessionLocal, u1, *_ = tormenta_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))
    rid = client.post(
        "/api/v1/tormenta/personagens",
        json=_t20_post_jogador_json(
            nome="Cura",
            nivel=1,
            classe_nivel="Clérigo 1",
            for_valor=8,
            des_valor=8,
            con_valor=8,
            int_valor=16,
            sab_valor=14,
            car_valor=18,
            pv_max=8,
            pv_atual=8,
            ficha_json={"tormenta_classe_mb_slug": "clerigo"},
        ),
    ).json()["id"]
    db = SessionLocal()
    try:
        ent = db.get(TormentaPersonagem, rid)
        ent.pa_max = 0
        ent.pa_atual = 0
        db.commit()
    finally:
        db.close()
    b = client.get(f"/api/v1/tormenta/personagens/{rid}").json()
    # 1 PM + mod SAB(14) +2 + 0 níveis extras × 3
    assert b["pa_max"] == 3
    assert b["pa_atual"] == 3


def test_guerreiro_post_e_lista(tormenta_personagens_db):
    SessionLocal, u1, *_ = tormenta_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))
    r = client.post(
        "/api/v1/tormenta/personagens",
        json=_t20_post_jogador_json(
            nome="Arthas",
            nivel=3,
            classe_nivel="Guerreiro 3",
            ficha_json={
                "pericias": [
                    {
                        "nome": "Luta",
                        "graduacao": 2,
                        "outros": 0,
                        "somente_treinado": False,
                    }
                ]
            },
        ),
    )
    assert r.status_code == 201
    body = r.json()
    assert body["nome"] == "Arthas"
    assert body["ficha_json"]["pericias"][0]["nome"] == "Luta"

    r2 = client.get("/api/v1/tormenta/personagens")
    assert r2.status_code == 200
    assert len(r2.json()) >= 1


def test_post_foto_atualiza_foto_url(tormenta_personagens_db, monkeypatch, tmp_path):
    SessionLocal, u1, *_ = tormenta_personagens_db
    monkeypatch.setattr("app.services.file_service.settings.CLOUDINARY_CLOUD_NAME", "")
    monkeypatch.setattr("app.services.file_service.settings.CLOUDINARY_API_KEY", "")
    monkeypatch.setattr("app.services.file_service.settings.CLOUDINARY_API_SECRET", "")
    monkeypatch.setattr("app.services.file_service.settings.UPLOADS_DIR", tmp_path)
    monkeypatch.setattr("app.services.file_service.settings.MAX_FILE_SIZE", 1024 * 1024)
    monkeypatch.setattr(
        "app.services.file_service.settings.ALLOWED_EXTENSIONS", {".png"}
    )
    client = _build_client(SessionLocal, _usuario(u1), FileService())
    rid = client.post(
        "/api/v1/tormenta/personagens",
        json=_t20_post_jogador_json(nome="ComFoto"),
    ).json()["id"]
    png = b"\x89PNG\r\n\x1a\n" + (b"\x00" * 32)
    r = client.post(
        f"/api/v1/tormenta/personagens/{rid}/foto",
        files={"foto": ("retrato.png", BytesIO(png), "image/png")},
    )
    assert r.status_code == 200, r.text
    url = r.json().get("foto_url")
    assert url
    assert "/uploads/" in url or url.startswith("http")
    r2 = client.get(f"/api/v1/tormenta/personagens/{rid}")
    assert r2.json()["foto_url"] == url
    assert (tmp_path / Path(url).name).is_file()


def test_patch_foto_url(tormenta_personagens_db):
    SessionLocal, u1, *_ = tormenta_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))
    rid = client.post(
        "/api/v1/tormenta/personagens",
        json=_t20_post_jogador_json(nome="ComFoto"),
    ).json()["id"]
    url = "https://example.com/retrato.png"
    r = client.patch(
        f"/api/v1/tormenta/personagens/{rid}",
        json={"foto_url": url},
    )
    assert r.status_code == 200
    assert r.json()["foto_url"] == url
    r2 = client.get(f"/api/v1/tormenta/personagens/{rid}")
    assert r2.json()["foto_url"] == url


def test_patch_ficha_json(tormenta_personagens_db):
    SessionLocal, u1, *_ = tormenta_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))
    rid = client.post(
        "/api/v1/tormenta/personagens",
        json=_t20_post_jogador_json(nome="Beta"),
    ).json()["id"]
    r = client.patch(
        f"/api/v1/tormenta/personagens/{rid}",
        json={"ficha_json": {"notas": "teste"}},
    )
    assert r.status_code == 200
    assert r.json()["ficha_json"]["notas"] == "teste"


def test_post_rejeita_pericias_mb_invalidas(tormenta_personagens_db):
    SessionLocal, u1, *_ = tormenta_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))
    r = client.post(
        "/api/v1/tormenta/personagens",
        json=_t20_post_jogador_json(
            nome="PericiasRuim",
            nivel=1,
            ficha_json={
                "tormenta_classe_mb_slug": "mago",
                "pericias": [
                    {"nome": "Conhecimento", "treinado": True, "graduacao": 5},
                ],
            },
        ),
    )
    assert r.status_code in (400, 422)
    detail = r.json().get("detail", "")
    if isinstance(detail, list):
        detail = str(detail)
    assert "gradua" in detail.lower()


def test_delete(tormenta_personagens_db):
    SessionLocal, u1, *_ = tormenta_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))
    rid = client.post(
        "/api/v1/tormenta/personagens",
        json=_t20_post_jogador_json(nome="Gamma"),
    ).json()["id"]
    d = client.delete(f"/api/v1/tormenta/personagens/{rid}")
    assert d.status_code == 204
    g = client.get(f"/api/v1/tormenta/personagens/{rid}")
    assert g.status_code == 404


def test_criar_jogador_com_atributos_compra_excede_orcamento(tormenta_personagens_db):
    SessionLocal, u1, *_ = tormenta_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))
    r = client.post(
        "/api/v1/tormenta/personagens",
        json={
            "nome": "Invalido",
            "tipo": "jogador",
            "for_valor": 10,
            "des_valor": 10,
            "con_valor": 10,
            "int_valor": 10,
            "sab_valor": 10,
            "car_valor": 10,
            "ficha_json": {
                "atributos_compra": {
                    "for": 18,
                    "des": 18,
                    "con": 18,
                    "int": 18,
                    "sab": 18,
                    "car": 18,
                }
            },
        },
    )
    assert r.status_code == 422
    d = r.json().get("detail", "").lower()
    assert "ultrapassar" in d or "20" in d


def test_criar_jogador_compra_menos_de_20_rejeita(tormenta_personagens_db):
    SessionLocal, u1, *_ = tormenta_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))
    r = client.post(
        "/api/v1/tormenta/personagens",
        json={
            "nome": "RascunhoInvalido",
            "tipo": "jogador",
            "for_valor": 10,
            "des_valor": 10,
            "con_valor": 10,
            "int_valor": 10,
            "sab_valor": 10,
            "car_valor": 10,
            "ficha_json": {
                "atributos_compra": {
                    "for": 10,
                    "des": 10,
                    "con": 10,
                    "int": 10,
                    "sab": 10,
                    "car": 10,
                },
            },
        },
    )
    assert r.status_code == 422
    d = r.json().get("detail", "").lower()
    assert "20" in d and ("obrigatorio" in d or "gastar" in d or "gasto" in d)


def test_criar_monstro_dez_em_todos_ok(tormenta_personagens_db):
    SessionLocal, _, _, u_mestre = tormenta_personagens_db
    client = _build_client(SessionLocal, _usuario(u_mestre))
    r = client.post(
        "/api/v1/tormenta/personagens",
        json={
            "nome": "Bicho",
            "tipo": "monstro",
            "for_valor": 10,
            "des_valor": 10,
            "con_valor": 10,
            "int_valor": 10,
            "sab_valor": 10,
            "car_valor": 10,
        },
    )
    assert r.status_code == 201
    assert r.json()["for_valor"] == 10


def test_patch_jogador_atributos_compra_ultrapassa_rejeita(tormenta_personagens_db):
    SessionLocal, u1, *_ = tormenta_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))
    rid = client.post(
        "/api/v1/tormenta/personagens",
        json=_t20_post_jogador_json(nome="Heroi"),
    ).json()["id"]
    r = client.patch(
        f"/api/v1/tormenta/personagens/{rid}",
        json={
            "ficha_json": {
                "atributos_compra": {
                    "for": 18,
                    "des": 18,
                    "con": 18,
                    "int": 18,
                    "sab": 18,
                    "car": 18,
                }
            }
        },
    )
    assert r.status_code == 422
    assert "ultrapassar" in r.json().get("detail", "").lower()


def test_talentos_crud_e_get_personagem_inclui_lista(tormenta_personagens_db):
    SessionLocal, u1, *_ = tormenta_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))
    rid = client.post(
        "/api/v1/tormenta/personagens",
        json=_t20_post_jogador_json(nome="ComTalentos"),
    ).json()["id"]
    nome_unico = "Talento Teste API Único XYZ"
    r_add = client.post(
        f"/api/v1/tormenta/personagens/{rid}/talentos",
        json={"nome": nome_unico},
    )
    assert r_add.status_code == 201, r_add.text
    body = r_add.json()
    assert body["nome"] == nome_unico
    vid = body["id"]

    r_dup = client.post(
        f"/api/v1/tormenta/personagens/{rid}/talentos",
        json={"nome": nome_unico},
    )
    assert r_dup.status_code == 409

    r_get = client.get(f"/api/v1/tormenta/personagens/{rid}")
    assert r_get.status_code == 200
    tlist = r_get.json().get("talentos") or []
    assert len(tlist) == 1
    assert tlist[0]["nome"] == nome_unico

    r_list = client.get(f"/api/v1/tormenta/personagens/{rid}/talentos")
    assert r_list.status_code == 200
    assert len(r_list.json()) == 1

    d = client.delete(f"/api/v1/tormenta/personagens/{rid}/talentos/{vid}")
    assert d.status_code == 204
    r_empty = client.get(f"/api/v1/tormenta/personagens/{rid}")
    assert (r_empty.json().get("talentos") or []) == []


def test_magias_crud_e_get_personagem_inclui_lista(tormenta_personagens_db):
    SessionLocal, u1, *_ = tormenta_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))
    rid = client.post(
        "/api/v1/tormenta/personagens",
        json=_t20_post_jogador_json(nome="ComMagias"),
    ).json()["id"]
    pr = client.patch(
        f"/api/v1/tormenta/personagens/{rid}",
        json={"nivel": 3, "ficha_json": {"tormenta_classe_mb_slug": "mago"}},
    )
    assert pr.status_code == 200, pr.text
    assert pr.json().get("grimorio_mb_permitido") is True
    r_add = client.post(
        f"/api/v1/tormenta/personagens/{rid}/magias",
        json={"magia_slug": "stub_truque_arc", "papel": "grimorio"},
    )
    assert r_add.status_code == 201, r_add.text
    body = r_add.json()
    assert body["magia_slug"] == "stub_truque_arc"
    assert body["papel"] == "grimorio"
    assert body.get("nome")
    vid = body["id"]

    r_dup = client.post(
        f"/api/v1/tormenta/personagens/{rid}/magias",
        json={"magia_slug": "stub_truque_arc", "papel": "grimorio"},
    )
    assert r_dup.status_code == 409

    r_bad = client.post(
        f"/api/v1/tormenta/personagens/{rid}/magias",
        json={"magia_slug": "slug_inexistente_xyz", "papel": "grimorio"},
    )
    assert r_bad.status_code == 422

    r_add2 = client.post(
        f"/api/v1/tormenta/personagens/{rid}/magias",
        json={"magia_slug": "stub_truque_arc", "papel": "preparada"},
    )
    assert r_add2.status_code == 201

    r_get = client.get(f"/api/v1/tormenta/personagens/{rid}")
    assert r_get.status_code == 200
    mlist = r_get.json().get("magias") or []
    assert len(mlist) == 2

    r_list = client.get(f"/api/v1/tormenta/personagens/{rid}/magias")
    assert r_list.status_code == 200
    assert len(r_list.json()) == 2

    d = client.delete(f"/api/v1/tormenta/personagens/{rid}/magias/{vid}")
    assert d.status_code == 204
    r_empty = client.get(f"/api/v1/tormenta/personagens/{rid}")
    assert len(r_empty.json().get("magias") or []) == 1


def test_magias_bloqueia_guerreiro_sem_conjuracao_manual(tormenta_personagens_db):
    SessionLocal, u1, *_ = tormenta_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))
    rid = client.post(
        "/api/v1/tormenta/personagens",
        json=_t20_post_jogador_json(nome="GerrMag", nivel=5),
    ).json()["id"]
    client.patch(
        f"/api/v1/tormenta/personagens/{rid}",
        json={"ficha_json": {"tormenta_classe_mb_slug": "guerreiro"}},
    )
    r_get = client.get(f"/api/v1/tormenta/personagens/{rid}")
    assert r_get.json().get("grimorio_mb_permitido") is False
    r_add = client.post(
        f"/api/v1/tormenta/personagens/{rid}/magias",
        json={"magia_slug": "stub_truque_arc", "papel": "conhecida"},
    )
    assert r_add.status_code == 422


def test_magias_paladino_so_apos_nivel_5_mb(tormenta_personagens_db):
    SessionLocal, u1, *_ = tormenta_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))
    rid = client.post(
        "/api/v1/tormenta/personagens",
        json=_t20_post_jogador_json(nome="PalMag", nivel=4),
    ).json()["id"]
    client.patch(
        f"/api/v1/tormenta/personagens/{rid}",
        json={"ficha_json": {"tormenta_classe_mb_slug": "paladino"}},
    )
    assert (
        client.get(f"/api/v1/tormenta/personagens/{rid}")
        .json()
        .get("grimorio_mb_permitido")
        is False
    )
    r_low = client.post(
        f"/api/v1/tormenta/personagens/{rid}/magias",
        json={"magia_slug": "stub_truque_arc", "papel": "conhecida"},
    )
    assert r_low.status_code == 422
    client.patch(f"/api/v1/tormenta/personagens/{rid}", json={"nivel": 5})
    assert (
        client.get(f"/api/v1/tormenta/personagens/{rid}")
        .json()
        .get("grimorio_mb_permitido")
        is True
    )
    r_ok = client.post(
        f"/api/v1/tormenta/personagens/{rid}/magias",
        json={"magia_slug": "stub_truque_arc", "papel": "preparada"},
    )
    assert r_ok.status_code == 201, r_ok.text


def test_magias_paladino_nivel_conjurador_mb_libera_antes_do_nivel_total(
    tormenta_personagens_db,
):
    SessionLocal, u1, *_ = tormenta_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))
    rid = client.post(
        "/api/v1/tormenta/personagens",
        json=_t20_post_jogador_json(nome="PalOverride", nivel=4),
    ).json()["id"]
    client.patch(
        f"/api/v1/tormenta/personagens/{rid}",
        json={
            "ficha_json": {
                "tormenta_classe_mb_slug": "paladino",
                "tormenta_nivel_conjurador_mb": 5,
            }
        },
    )
    assert (
        client.get(f"/api/v1/tormenta/personagens/{rid}")
        .json()
        .get("grimorio_mb_permitido")
        is True
    )
    r_add = client.post(
        f"/api/v1/tormenta/personagens/{rid}/magias",
        json={"magia_slug": "stub_truque_arc", "papel": "preparada"},
    )
    assert r_add.status_code == 201, r_add.text


def test_magias_mago_rejeita_papel_conhecida(tormenta_personagens_db):
    SessionLocal, u1, *_ = tormenta_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))
    rid = client.post(
        "/api/v1/tormenta/personagens",
        json=_t20_post_jogador_json(nome="MagoPapel", nivel=3),
    ).json()["id"]
    client.patch(
        f"/api/v1/tormenta/personagens/{rid}",
        json={"ficha_json": {"tormenta_classe_mb_slug": "mago"}},
    )
    r = client.post(
        f"/api/v1/tormenta/personagens/{rid}/magias",
        json={"magia_slug": "stub_truque_arc", "papel": "conhecida"},
    )
    assert r.status_code == 422


def test_magias_conjuracao_manual_permite_guerreiro(tormenta_personagens_db):
    SessionLocal, u1, *_ = tormenta_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))
    rid = client.post(
        "/api/v1/tormenta/personagens",
        json=_t20_post_jogador_json(nome="GuerMag", nivel=3),
    ).json()["id"]
    client.patch(
        f"/api/v1/tormenta/personagens/{rid}",
        json={
            "ficha_json": {
                "tormenta_classe_mb_slug": "guerreiro",
                "tormenta_conjuracao_manual_mb": True,
            }
        },
    )
    r_add = client.post(
        f"/api/v1/tormenta/personagens/{rid}/magias",
        json={"magia_slug": "stub_truque_arc", "papel": "conhecida"},
    )
    assert r_add.status_code == 201, r_add.text


def test_magias_feiticeiro_limite_conhecidas_circulo_1(tormenta_personagens_db):
    SessionLocal, u1, *_ = tormenta_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))
    rid = client.post(
        "/api/v1/tormenta/personagens",
        json=_t20_post_jogador_json(nome="FetLim", nivel=1),
    ).json()["id"]
    client.patch(
        f"/api/v1/tormenta/personagens/{rid}",
        json={"ficha_json": {"tormenta_classe_mb_slug": "feiticeiro"}},
    )
    for slug in ("stub_1_circulo_arc", "alarme"):
        r = client.post(
            f"/api/v1/tormenta/personagens/{rid}/magias",
            json={"magia_slug": slug, "papel": "conhecida"},
        )
        assert r.status_code == 201, r.text
    r3 = client.post(
        f"/api/v1/tormenta/personagens/{rid}/magias",
        json={"magia_slug": "animar_corda", "papel": "conhecida"},
    )
    assert r3.status_code == 422


def test_magias_bardo_troca_conhecida_nivel_5(tormenta_personagens_db):
    SessionLocal, u1, *_ = tormenta_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))
    rid = client.post(
        "/api/v1/tormenta/personagens",
        json=_t20_post_jogador_json(nome="BardoTroca", nivel=5),
    ).json()["id"]
    client.patch(
        f"/api/v1/tormenta/personagens/{rid}",
        json={"ficha_json": {"tormenta_classe_mb_slug": "bardo"}},
    )
    client.post(
        f"/api/v1/tormenta/personagens/{rid}/magias",
        json={"magia_slug": "stub_1_circulo_arc", "papel": "conhecida"},
    ).raise_for_status()
    r = client.post(
        f"/api/v1/tormenta/personagens/{rid}/magias/trocar",
        json={
            "magia_slug_removida": "stub_1_circulo_arc",
            "magia_slug_nova": "alarme",
        },
    )
    assert r.status_code == 200, r.text
    assert r.json()["nova_slug"] == "alarme"
    prev = client.get(f"/api/v1/tormenta/personagens/{rid}/magias/conhecidas-preview")
    assert prev.status_code == 200
    assert prev.json()["bardo_pode_trocar"] is True


def test_migrar_talentos_mb_lista_do_json(tormenta_personagens_db):
    SessionLocal, u1, *_ = tormenta_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))
    rid = client.post(
        "/api/v1/tormenta/personagens",
        json=_t20_post_jogador_json(nome="MigrarTal"),
    ).json()["id"]
    client.patch(
        f"/api/v1/tormenta/personagens/{rid}",
        json={
            "ficha_json": {
                "talentos_mb_lista": [
                    {"nome": "Talento Migra A"},
                    {"nome": "Talento Migra A"},
                    {"nome": "Talento Migra B"},
                ]
            }
        },
    )
    r = client.post(f"/api/v1/tormenta/personagens/{rid}/talentos/migrar-do-json")
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["vinculos_criados"] == 2
    assert data["ignorados_duplicados"] == 1
    names = {
        x["nome"]
        for x in client.get(f"/api/v1/tormenta/personagens/{rid}/talentos").json()
    }
    assert names == {"Talento Migra A", "Talento Migra B"}


def test_importar_inventario_legado_remove_json(tormenta_personagens_db):
    SessionLocal, u1, *_ = tormenta_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))
    rid = client.post(
        "/api/v1/tormenta/personagens",
        json=_t20_post_jogador_json(nome="Legado"),
    ).json()["id"]
    client.patch(
        f"/api/v1/tormenta/personagens/{rid}",
        json={
            "ficha_json": {
                "talentos_mb_lista": [{"nome": "Talento Único Legado"}],
                "equipamentos": [{"item": "Espada de Teste", "qtd": "2"}],
            }
        },
    )
    r = client.post(f"/api/v1/tormenta/personagens/{rid}/inventario/importar-legado")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["talentos_criados"] >= 1
    assert body["equipamentos_criados"] >= 1
    p = client.get(f"/api/v1/tormenta/personagens/{rid}").json()
    fj = p.get("ficha_json") or {}
    assert "talentos_mb_lista" not in fj
    assert "equipamentos" not in fj
    assert len(p.get("talentos") or []) >= 1
    assert len(p.get("equipamentos") or []) >= 1


def test_equipamentos_post_e_get(tormenta_personagens_db):
    SessionLocal, u1, *_ = tormenta_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))
    rid = client.post(
        "/api/v1/tormenta/personagens",
        json=_t20_post_jogador_json(nome="Eq"),
    ).json()["id"]
    r = client.post(
        f"/api/v1/tormenta/personagens/{rid}/equipamentos",
        json={"nome": "Item API Equip Único", "quantidade": 3},
    )
    assert r.status_code == 201, r.text
    assert r.json()["quantidade"] == 3
    lst = client.get(f"/api/v1/tormenta/personagens/{rid}/equipamentos").json()
    assert len(lst) == 1
    vid = lst[0]["id"]
    p = client.patch(
        f"/api/v1/tormenta/personagens/{rid}/equipamentos/{vid}",
        json={"quantidade": 5},
    )
    assert p.status_code == 200
    assert p.json()["quantidade"] == 5


def _mago_rid(client, *, nivel=1):
    rid = client.post(
        "/api/v1/tormenta/personagens",
        json=_t20_post_jogador_json(nome=f"MagoC{nivel}", nivel=nivel),
    ).json()["id"]
    client.patch(
        f"/api/v1/tormenta/personagens/{rid}",
        json={"ficha_json": {"tormenta_classe_mb_slug": "mago"}},
    )
    return rid


def test_mago_grimorio_limite_aprendizado_nivel_1(tormenta_personagens_db):
    SessionLocal, u1, *_ = tormenta_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))
    rid = _mago_rid(client, nivel=1)
    slugs = [
        "stub_1_circulo_arc",
        "alarme",
        "animar_corda",
        "apagar",
        "sono",
        "suportar_elementos",
        "toque_chocante",
    ]
    for slug in slugs:
        r = client.post(
            f"/api/v1/tormenta/personagens/{rid}/magias",
            json={"magia_slug": slug, "papel": "grimorio"},
        )
        assert r.status_code == 201, r.text
    excede = client.post(
        f"/api/v1/tormenta/personagens/{rid}/magias",
        json={"magia_slug": "toque_macabro", "papel": "grimorio"},
    )
    assert excede.status_code == 422
    assert "livro" in excede.json()["detail"].lower()


def test_mago_preparada_exige_grimorio_e_teto(tormenta_personagens_db):
    SessionLocal, u1, *_ = tormenta_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))
    rid = _mago_rid(client, nivel=3)
    sem_livro = client.post(
        f"/api/v1/tormenta/personagens/{rid}/magias",
        json={"magia_slug": "alarme", "papel": "preparada"},
    )
    assert sem_livro.status_code == 422
    client.post(
        f"/api/v1/tormenta/personagens/{rid}/magias",
        json={"magia_slug": "alarme", "papel": "grimorio"},
    )
    ok = client.post(
        f"/api/v1/tormenta/personagens/{rid}/magias",
        json={"magia_slug": "alarme", "papel": "preparada"},
    )
    assert ok.status_code == 201, ok.text


def test_mago_lancar_exige_preparada_ou_grimorio(tormenta_personagens_db):
    SessionLocal, u1, *_ = tormenta_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))
    rid = _mago_rid(client, nivel=3)
    client.post(
        f"/api/v1/tormenta/personagens/{rid}/magias",
        json={"magia_slug": "alarme", "papel": "grimorio"},
    )
    falha = client.post(
        f"/api/v1/tormenta/personagens/{rid}/magias/lancar",
        json={"magia_slug": "alarme"},
    )
    assert falha.status_code == 422
    client.post(
        f"/api/v1/tormenta/personagens/{rid}/magias",
        json={"magia_slug": "alarme", "papel": "preparada"},
    )
    ok = client.post(
        f"/api/v1/tormenta/personagens/{rid}/magias/lancar",
        json={"magia_slug": "alarme"},
    )
    assert ok.status_code == 200, ok.text


def test_mago_lancar_truque_com_grimorio(tormenta_personagens_db):
    SessionLocal, u1, *_ = tormenta_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))
    rid = _mago_rid(client, nivel=1)
    client.post(
        f"/api/v1/tormenta/personagens/{rid}/magias",
        json={"magia_slug": "stub_truque_arc", "papel": "grimorio"},
    )
    r = client.post(
        f"/api/v1/tormenta/personagens/{rid}/magias/lancar",
        json={"magia_slug": "stub_truque_arc"},
    )
    assert r.status_code == 200, r.text
    assert r.json()["custo_pm"] == 0


def test_mago_limpar_preparadas(tormenta_personagens_db):
    SessionLocal, u1, *_ = tormenta_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))
    rid = _mago_rid(client, nivel=3)
    client.post(
        f"/api/v1/tormenta/personagens/{rid}/magias",
        json={"magia_slug": "alarme", "papel": "grimorio"},
    )
    client.post(
        f"/api/v1/tormenta/personagens/{rid}/magias",
        json={"magia_slug": "alarme", "papel": "preparada"},
    )
    prev = client.get(f"/api/v1/tormenta/personagens/{rid}/magias/preparadas-preview")
    assert prev.status_code == 200
    assert prev.json()["preparadas_usadas"] == 1
    limp = client.post(f"/api/v1/tormenta/personagens/{rid}/magias/limpar-preparadas")
    assert limp.status_code == 200
    assert limp.json()["removidas"] == 1
    prev2 = client.get(f"/api/v1/tormenta/personagens/{rid}/magias/preparadas-preview")
    assert prev2.json()["preparadas_usadas"] == 0


def test_subir_nivel_preview_e_aplicar_mago(tormenta_personagens_db):
    SessionLocal, u1, *_ = tormenta_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))
    rid = client.post(
        "/api/v1/tormenta/personagens",
        json=_t20_post_jogador_json(
            nome="SubNv",
            nivel=1,
            pv_max=7,
            pv_atual=7,
            ficha_json={"tormenta_classe_mb_slug": "mago"},
        ),
    ).json()["id"]
    prev = client.get(
        f"/api/v1/tormenta/personagens/{rid}/subir-nivel-preview",
        params={"nivel_alvo": 2},
    )
    assert prev.status_code == 200, prev.text
    body = prev.json()
    assert body["permitido"] is True
    assert body["nivel_alvo"] == 2
    assert body["magias_livro_ganho"] == 2
    assert body["pa_ganho"] == 3

    aplic = client.post(
        f"/api/v1/tormenta/personagens/{rid}/subir-nivel",
        json={"aplicar_ganhos_vida": True},
    )
    assert aplic.status_code == 200, aplic.text
    res = aplic.json()
    assert res["personagem"]["nivel"] == 2
    assert res["personagem"]["pv_max"] == body["pv_max_novo"]
    assert res["personagem"]["pa_max"] == body["pa_max_novo"]
    assert res["personagem"]["pv_atual"] == body["pv_max_novo"]
    assert res["personagem"]["ficha_json"].get("habilidade_classe_mb")


def test_clerigo_preparada_e_lancar_truque_divino(tormenta_personagens_db):
    SessionLocal, u1, *_ = tormenta_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))
    rid_resp = client.post(
        "/api/v1/tormenta/personagens",
        json=_t20_post_jogador_json(
            nome="ClerPrep",
            nivel=3,
            divindade="Lena, Deusa da Vida",
            ficha_json={
                "tormenta_classe_mb_slug": "clerigo",
                "tormenta_divindade_mb_slug": "lena",
            },
        ),
    )
    assert rid_resp.status_code == 201, rid_resp.text
    rid = rid_resp.json()["id"]
    r_grim = client.post(
        f"/api/v1/tormenta/personagens/{rid}/magias",
        json={"magia_slug": "alarme", "papel": "grimorio"},
    )
    assert r_grim.status_code == 422
    r_rep = client.post(
        f"/api/v1/tormenta/personagens/{rid}/magias",
        json={"magia_slug": "stub_1_circulo_div", "papel": "conhecida"},
    )
    assert r_rep.status_code == 201, r_rep.text
    r_prep = client.post(
        f"/api/v1/tormenta/personagens/{rid}/magias",
        json={"magia_slug": "stub_1_circulo_div", "papel": "preparada"},
    )
    assert r_prep.status_code == 201, r_prep.text
    prev = client.get(f"/api/v1/tormenta/personagens/{rid}/magias/preparadas-preview")
    assert prev.status_code == 200
    assert prev.json()["preparadas_usadas"] == 1
    assert prev.json()["preparadas_max"] == 2
    rep_prev = client.get(
        f"/api/v1/tormenta/personagens/{rid}/magias/repertorio-preview"
    )
    assert rep_prev.status_code == 200
    assert rep_prev.json()["repertorio_usadas"] == 1
    r_lanc_tr = client.post(
        f"/api/v1/tormenta/personagens/{rid}/magias/lancar",
        json={"magia_slug": "virtude"},
    )
    assert r_lanc_tr.status_code == 200, r_lanc_tr.text
    assert r_lanc_tr.json()["truque_devocao"] is True
    assert r_lanc_tr.json()["custo_pm"] == 0
    r_lanc_circ = client.post(
        f"/api/v1/tormenta/personagens/{rid}/magias/lancar",
        json={"magia_slug": "stub_1_circulo_div"},
    )
    assert r_lanc_circ.status_code == 200, r_lanc_circ.text
    assert r_lanc_circ.json()["custo_pm"] == 1


def test_magias_migrar_texto_limpa_ficha_apos_sincronizar(tormenta_personagens_db):
    SessionLocal, _, _, u_mestre = tormenta_personagens_db
    client = _build_client(SessionLocal, _usuario(u_mestre))
    r = client.post(
        "/api/v1/tormenta/personagens",
        json=_t20_post_jogador_json(
            nome="Mago Sync Magias",
            ficha_json={
                "tormenta_classe_mb_slug": "mago",
                "magias_texto": "Mísseis mágicos",
            },
        ),
    )
    assert r.status_code == 201, r.text
    rid = r.json()["id"]
    mig = client.post(f"/api/v1/tormenta/personagens/{rid}/magias/migrar-do-json")
    assert mig.status_code == 200, mig.text
    data = mig.json()
    assert data["vinculos_criados"] >= 1
    assert data["magias_texto_restante"] == ""
    got = client.get(f"/api/v1/tormenta/personagens/{rid}")
    fj = got.json().get("ficha_json") or {}
    assert not str(fj.get("magias_texto") or "").strip()
    mig2 = client.post(f"/api/v1/tormenta/personagens/{rid}/magias/migrar-do-json")
    assert mig2.status_code == 200
    assert mig2.json()["vinculos_criados"] == 0
