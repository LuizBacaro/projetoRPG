from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.equipamentos import router as equipamentos_router
from app.api.v1.magias import router as magias_router
from app.api.v1.pericias import router as pericias_router
from app.core.catalog_cache import catalog_cache
from app.core.database import get_db
from app.core.deps import get_usuario_atual
from app.core.config import settings
from app.services.equipamento_service import EquipamentoService
from app.services.pericia_service import PericiaService


def _with_cache_enabled():
    original = settings.CACHE_ENABLED
    settings.CACHE_ENABLED = True
    return original


def _restore_cache_enabled(original):
    settings.CACHE_ENABLED = original


def test_magias_list_usa_cache_em_requisicoes_iguais(monkeypatch):
    class FakeQuery:
        def __init__(self):
            self.calls = 0

        def filter(self, *args, **kwargs):
            return self

        def count(self):
            return 1

        def order_by(self, *args, **kwargs):
            return self

        def offset(self, *args, **kwargs):
            return self

        def limit(self, *args, **kwargs):
            return self

        def all(self):
            self.calls += 1
            return [
                SimpleNamespace(
                    id=1,
                    nome="Misseis Magicos",
                    nivel=1,
                    classe="MAGO",
                    escola="Evocacao",
                    sub_escola=None,
                    componentes="V,S",
                    alcance="medio",
                    area_efeito=None,
                    duracao="instantanea",
                    tempo_conjuracao="1 acao",
                    dano="1d4+1",
                    teste_resistencia="nenhum",
                    resistencia_magica=False,
                    descricao="Descricao",
                    ativo=True,
                    eh_truque=False,
                    tem_dano=True,
                    data_criacao=None,
                )
            ]

    fake_query = FakeQuery()

    class FakeDB:
        def query(self, *_args, **_kwargs):
            return fake_query

    app = FastAPI()
    app.include_router(magias_router, prefix="/api/v1")

    def _override_get_db():
        yield FakeDB()

    app.dependency_overrides[get_db] = _override_get_db

    original = _with_cache_enabled()
    catalog_cache.clear()
    client = TestClient(app)

    try:
        r1 = client.get("/api/v1/magias", params={"limit": 10})
        r2 = client.get("/api/v1/magias", params={"limit": 10})
    finally:
        _restore_cache_enabled(original)
        catalog_cache.clear()

    assert r1.status_code == 200
    assert r2.status_code == 200
    assert fake_query.calls == 1


def test_pericias_list_usa_cache_em_requisicoes_iguais(monkeypatch):
    called = {"listar": 0}

    def _fake_listar(self, skip=0, limit=100):
        called["listar"] += 1
        return [
            SimpleNamespace(
                id=1,
                nome="Acrobacia",
                descricao="",
                atributo="DES",
                tipo="comum",
                requer_treinamento=0,
                especialidade=None,
                pode_usar_sem_treinamento=1,
                sofre_penalidade_armadura=1,
                pagina_livro=70,
            )
        ]

    monkeypatch.setattr(PericiaService, "listar_todas_pericias", _fake_listar)

    app = FastAPI()
    app.include_router(pericias_router, prefix="/api/v1")

    def _override_get_db():
        yield object()

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_usuario_atual] = lambda: object()

    original = _with_cache_enabled()
    catalog_cache.clear()
    client = TestClient(app)

    try:
        r1 = client.get("/api/v1/pericias", params={"skip": 0, "limit": 10})
        r2 = client.get("/api/v1/pericias", params={"skip": 0, "limit": 10})
    finally:
        _restore_cache_enabled(original)
        catalog_cache.clear()

    assert r1.status_code == 200
    assert r2.status_code == 200
    assert called["listar"] == 1


def test_equipamentos_list_usa_cache_em_requisicoes_iguais(monkeypatch):
    called = {"listar": 0}

    def _fake_listar(self, skip=0, limit=100):
        called["listar"] += 1
        return [
            SimpleNamespace(
                id=1,
                nome="Corda",
                descricao="Corda de canhamo",
                pagina_referencia="PHB p.111",
                ativo=True,
                criado_em=None,
            )
        ]

    monkeypatch.setattr(EquipamentoService, "listar_todos_equipamentos", _fake_listar)

    app = FastAPI()
    app.include_router(equipamentos_router, prefix="/api/v1")

    def _override_get_db():
        yield object()

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_usuario_atual] = lambda: object()

    original = _with_cache_enabled()
    catalog_cache.clear()
    client = TestClient(app)

    try:
        r1 = client.get("/api/v1/equipamentos", params={"skip": 0, "limit": 10})
        r2 = client.get("/api/v1/equipamentos", params={"skip": 0, "limit": 10})
    finally:
        _restore_cache_enabled(original)
        catalog_cache.clear()

    assert r1.status_code == 200
    assert r2.status_code == 200
    assert called["listar"] == 1
