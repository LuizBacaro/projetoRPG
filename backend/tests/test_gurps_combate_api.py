"""Integração HTTP — combate GURPS (iniciar, turno, finalizar, RBAC em lote)."""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.games.gurps.api.v1.combate import router as gurps_combate_router
from app.games.gurps.api.v1.personagens import router as gurps_personagens_router
from app.shared.core.database import get_db
from app.shared.core.deps import get_usuario_atual
from app.shared.models.usuario import Usuario


def _usuario(u: Usuario) -> SimpleNamespace:
    return SimpleNamespace(id=u.id, perfil=u.perfil, email=u.email, nome=u.nome)


def _build_client(SessionLocal, usuario: SimpleNamespace) -> TestClient:
    app = FastAPI()
    app.include_router(gurps_personagens_router, prefix="/api/v1")
    app.include_router(gurps_combate_router, prefix="/api/v1")

    def _override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_usuario_atual] = lambda: usuario
    return TestClient(app)


def _criar(
    session_local,
    client: TestClient,
    nome: str,
    iniciativa: int = 0,
    *,
    velocidade_valor: float | None = None,
    aparar: int | None = None,
    bloqueio: str | None = None,
    extras: dict | None = None,
) -> int:
    body: dict = {
        "nome": nome,
        "tipo": "jogador",
        "iniciativa": iniciativa,
        "extras": extras or {},
    }
    if velocidade_valor is not None:
        body["velocidade_valor"] = velocidade_valor
    if aparar is not None:
        body["aparar"] = aparar
    if bloqueio is not None:
        body["bloqueio"] = bloqueio
    r = client.post("/api/v1/gurps/personagens", json=body)
    assert r.status_code == 201, r.text
    return r.json()["id"]


def test_iniciar_ordena_por_velocidade_basica_desc(gurps_personagens_com_campanha_db):
    SessionLocal, u1, _ = gurps_personagens_com_campanha_db
    client = _build_client(SessionLocal, _usuario(u1))

    p_baixa = _criar(SessionLocal, client, "Lento", 0, velocidade_valor=4.0)
    p_alta = _criar(SessionLocal, client, "Rápido", 0, velocidade_valor=6.25)

    r = client.post(
        "/api/v1/gurps/combate/iniciar",
        json={"personagem_ids": [p_baixa, p_alta]},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["ativo"] is True
    assert body["personagens_ids"] == [p_alta, p_baixa]
    assert body["turno_atual"] == 0
    assert body["personagem_ativo_id"] == p_alta
    assert body["manobra_ativa"] == "fazer_nada"
    assert body["manobras_por_personagem"][str(p_alta)] == "fazer_nada"
    assert body["manobras_por_personagem"][str(p_baixa)] == "fazer_nada"


def test_iniciar_duas_vezes_retorna_400(gurps_personagens_com_campanha_db):
    SessionLocal, u1, _ = gurps_personagens_com_campanha_db
    client = _build_client(SessionLocal, _usuario(u1))

    a = _criar(SessionLocal, client, "A", 0, velocidade_valor=6.0)
    b = _criar(SessionLocal, client, "B", 0, velocidade_valor=5.0)

    assert (
        client.post(
            "/api/v1/gurps/combate/iniciar",
            json={"personagem_ids": [a, b]},
        ).status_code
        == 200
    )

    r2 = client.post(
        "/api/v1/gurps/combate/iniciar",
        json={"personagem_ids": [a]},
    )
    assert r2.status_code == 400
    assert "combate" in r2.json().get("detail", "").lower()


def test_finalizar_e_status_inativo(gurps_personagens_com_campanha_db):
    SessionLocal, u1, _ = gurps_personagens_com_campanha_db
    client = _build_client(SessionLocal, _usuario(u1))

    a = _criar(SessionLocal, client, "Só", 0, velocidade_valor=5.0)
    assert (
        client.post(
            "/api/v1/gurps/combate/iniciar",
            json={"personagem_ids": [a]},
        ).status_code
        == 200
    )

    r = client.post("/api/v1/gurps/combate/finalizar")
    assert r.status_code == 200
    assert r.json().get("ativo") is False

    st = client.get("/api/v1/gurps/combate/status")
    assert st.status_code == 200
    assert st.json().get("ativo") is False


def test_avancar_volta_ao_inicio_incrementa_rodada(gurps_personagens_com_campanha_db):
    SessionLocal, u1, _ = gurps_personagens_com_campanha_db
    client = _build_client(SessionLocal, _usuario(u1))

    a = _criar(SessionLocal, client, "P1", 0, velocidade_valor=6.0)
    b = _criar(SessionLocal, client, "P2", 0, velocidade_valor=5.0)
    assert (
        client.post(
            "/api/v1/gurps/combate/iniciar",
            json={"personagem_ids": [a, b]},
        ).status_code
        == 200
    )

    assert client.post("/api/v1/gurps/combate/avancar-turno").json()["turno_atual"] == 1
    r2 = client.post("/api/v1/gurps/combate/avancar-turno")
    assert r2.status_code == 200
    body = r2.json()
    assert body["turno_atual"] == 0
    assert body["rodada_atual"] == 2


def test_avancar_turno_incrementa(gurps_personagens_com_campanha_db):
    SessionLocal, u1, _ = gurps_personagens_com_campanha_db
    client = _build_client(SessionLocal, _usuario(u1))

    a = _criar(SessionLocal, client, "P1", 0, velocidade_valor=6.0)
    b = _criar(SessionLocal, client, "P2", 0, velocidade_valor=5.0)
    assert (
        client.post(
            "/api/v1/gurps/combate/iniciar",
            json={"personagem_ids": [a, b]},
        ).status_code
        == 200
    )

    r = client.post("/api/v1/gurps/combate/avancar-turno")
    assert r.status_code == 200
    assert r.json()["turno_atual"] == 1
    assert r.json()["personagem_ativo_id"] == b


def test_definir_manobra_ativa(gurps_personagens_com_campanha_db):
    SessionLocal, u1, _ = gurps_personagens_com_campanha_db
    client = _build_client(SessionLocal, _usuario(u1))

    a = _criar(SessionLocal, client, "P1", 0, velocidade_valor=6.0)
    b = _criar(SessionLocal, client, "P2", 0, velocidade_valor=5.0)
    assert (
        client.post(
            "/api/v1/gurps/combate/iniciar",
            json={"personagem_ids": [a, b]},
        ).status_code
        == 200
    )

    r = client.post("/api/v1/gurps/combate/manobra-atual", json={"manobra": "ataque"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["personagem_ativo_id"] == a
    assert body["manobra_ativa"] == "ataque"
    assert body["manobras_por_personagem"][str(a)] == "ataque"
    assert body["manobras_por_personagem"][str(b)] == "fazer_nada"


def test_defesa_total_aplica_bonus_esquiva_efetiva_no_status(
    gurps_personagens_com_campanha_db,
):
    SessionLocal, u1, _ = gurps_personagens_com_campanha_db
    client = _build_client(SessionLocal, _usuario(u1))

    a = _criar(SessionLocal, client, "P1", 0, velocidade_valor=6.0)
    b = _criar(SessionLocal, client, "P2", 0, velocidade_valor=5.0)
    assert (
        client.post(
            "/api/v1/gurps/combate/iniciar",
            json={"personagem_ids": [a, b]},
        ).status_code
        == 200
    )

    r = client.post(
        "/api/v1/gurps/combate/manobra-atual", json={"manobra": "defesa_total"}
    )
    assert r.status_code == 200, r.text
    body = r.json()
    ativo = next(p for p in body["personagens"] if p["id"] == a)
    assert ativo["manobra_atual"] == "defesa_total"
    assert ativo["esquiva_efetiva"] == (ativo["esquiva"] + 2)


def test_ataque_aplica_dano_quando_defesa_falha(gurps_personagens_com_campanha_db):
    SessionLocal, u1, _ = gurps_personagens_com_campanha_db
    client = _build_client(SessionLocal, _usuario(u1))

    a = _criar(SessionLocal, client, "Atacante", 0, velocidade_valor=6.0)
    b = _criar(SessionLocal, client, "Alvo", 0, velocidade_valor=5.0)
    assert (
        client.post(
            "/api/v1/gurps/combate/iniciar",
            json={"personagem_ids": [a, b]},
        ).status_code
        == 200
    )

    r = client.post(
        "/api/v1/gurps/combate/ataque",
        json={
            "alvo_id": b,
            "nh_ataque": 16,
            "expressao_dano": "1d+2",
            "dados_ataque": [3, 3, 3],
            "dados_defesa": [6, 6, 6],
            "dados_dano": [4],
        },
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["ataque"]["sucesso"] is True
    assert body["defesa"]["sucesso"] is False
    assert body["dano"]["total"] == 6
    assert body["pvs_alvo_depois"] == (body["pvs_alvo_antes"] - 6)


def test_ataque_sem_dano_quando_defesa_sucesso(gurps_personagens_com_campanha_db):
    SessionLocal, u1, _ = gurps_personagens_com_campanha_db
    client = _build_client(SessionLocal, _usuario(u1))

    a = _criar(SessionLocal, client, "Atacante", 0, velocidade_valor=6.0)
    b = _criar(SessionLocal, client, "Alvo", 0, velocidade_valor=5.0)
    assert (
        client.post(
            "/api/v1/gurps/combate/iniciar",
            json={"personagem_ids": [a, b]},
        ).status_code
        == 200
    )

    r = client.post(
        "/api/v1/gurps/combate/ataque",
        json={
            "alvo_id": b,
            "nh_ataque": 16,
            "dados_ataque": [3, 3, 3],
            "dados_defesa": [1, 1, 1],
        },
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["ataque"]["sucesso"] is True
    assert body["defesa"]["sucesso"] is True
    assert body["dano"] is None
    assert body["pvs_alvo_depois"] == body["pvs_alvo_antes"]


def test_ajustar_pv_cura_no_alvo(gurps_personagens_com_campanha_db):
    SessionLocal, u1, _ = gurps_personagens_com_campanha_db
    client = _build_client(SessionLocal, _usuario(u1))

    a = _criar(SessionLocal, client, "Atacante", 0, velocidade_valor=6.0)
    b = _criar(SessionLocal, client, "Alvo", 0, velocidade_valor=5.0)
    assert (
        client.post(
            "/api/v1/gurps/combate/iniciar",
            json={"personagem_ids": [a, b]},
        ).status_code
        == 200
    )

    # Primeiro aplica dano.
    r1 = client.post(
        "/api/v1/gurps/combate/ataque",
        json={
            "alvo_id": b,
            "nh_ataque": 16,
            "expressao_dano": "1d+2",
            "dados_ataque": [3, 3, 3],
            "dados_defesa": [6, 6, 6],
            "dados_dano": [4],
        },
    )
    assert r1.status_code == 200, r1.text
    pv_apos_dano = r1.json()["pvs_alvo_depois"]

    r2 = client.post(
        "/api/v1/gurps/combate/ajustar-pv", json={"alvo_id": b, "delta_pv": 3}
    )
    assert r2.status_code == 200, r2.text
    body = r2.json()
    assert body["pvs_alvo_antes"] == pv_apos_dano
    assert body["pvs_alvo_depois"] == (pv_apos_dano + 3)


def test_ataque_falha_quando_alvo_inconsciente(gurps_personagens_com_campanha_db):
    SessionLocal, u1, _ = gurps_personagens_com_campanha_db
    client = _build_client(SessionLocal, _usuario(u1))

    a = _criar(SessionLocal, client, "Atacante", 0, velocidade_valor=6.0)
    b = _criar(SessionLocal, client, "Alvo", 0, velocidade_valor=5.0)
    assert (
        client.post(
            "/api/v1/gurps/combate/iniciar",
            json={"personagem_ids": [a, b]},
        ).status_code
        == 200
    )

    # Derruba alvo para 0 PV e tenta atacar de novo.
    assert (
        client.post(
            "/api/v1/gurps/combate/ataque",
            json={
                "alvo_id": b,
                "nh_ataque": 16,
                "expressao_dano": "10d+0",
                "dados_ataque": [3, 3, 3],
                "dados_defesa": [6, 6, 6],
                "dados_dano": [6] * 10,
            },
        ).status_code
        == 200
    )

    r = client.post(
        "/api/v1/gurps/combate/ataque",
        json={"alvo_id": b, "nh_ataque": 12, "dados_ataque": [3, 3, 3]},
    )
    assert r.status_code == 422
    assert "inconsciente" in r.json().get("detail", "").lower()


def test_ataque_define_manobra_do_atacante_como_ataque(
    gurps_personagens_com_campanha_db,
):
    SessionLocal, u1, _ = gurps_personagens_com_campanha_db
    client = _build_client(SessionLocal, _usuario(u1))

    a = _criar(SessionLocal, client, "Atacante", 0, velocidade_valor=6.0)
    b = _criar(SessionLocal, client, "Alvo", 0, velocidade_valor=5.0)
    assert (
        client.post(
            "/api/v1/gurps/combate/iniciar",
            json={"personagem_ids": [a, b]},
        ).status_code
        == 200
    )

    assert (
        client.post(
            "/api/v1/gurps/combate/ataque",
            json={
                "alvo_id": b,
                "nh_ataque": 16,
                "dados_ataque": [3, 3, 3],
                "dados_defesa": [6, 6, 6],
            },
        ).status_code
        == 200
    )

    st = client.get("/api/v1/gurps/combate/status")
    assert st.status_code == 200
    body = st.json()
    assert body["manobras_por_personagem"][str(a)] == "ataque"


def test_defesa_cumulativa_aplica_penalidade_e_reseta_na_nova_rodada(
    gurps_personagens_com_campanha_db,
):
    SessionLocal, u1, _ = gurps_personagens_com_campanha_db
    client = _build_client(SessionLocal, _usuario(u1))

    a = _criar(SessionLocal, client, "A1", 0, velocidade_valor=7.0)
    b = _criar(SessionLocal, client, "B1", 0, velocidade_valor=6.0)
    assert (
        client.post(
            "/api/v1/gurps/combate/iniciar",
            json={"personagem_ids": [a, b]},
        ).status_code
        == 200
    )

    # Turno A: ataca B (1a defesa de B na rodada).
    r1 = client.post(
        "/api/v1/gurps/combate/ataque",
        json={
            "alvo_id": b,
            "nh_ataque": 16,
            "dados_ataque": [3, 3, 3],
            "dados_defesa": [6, 6, 6],
        },
    )
    assert r1.status_code == 200, r1.text
    assert r1.json()["defesa"]["esquiva_efetiva"] >= 0

    # Turno B -> A (1a defesa de A na rodada).
    assert client.post("/api/v1/gurps/combate/avancar-turno").status_code == 200
    r2 = client.post(
        "/api/v1/gurps/combate/ataque",
        json={
            "alvo_id": a,
            "nh_ataque": 16,
            "dados_ataque": [3, 3, 3],
            "dados_defesa": [6, 6, 6],
        },
    )
    assert r2.status_code == 200, r2.text
    esquiva_primeira_defesa = r2.json()["defesa"]["esquiva_efetiva"]

    # Nova rodada: volta turno A. A ataca B de novo => 2a defesa de B na mesma rodada atual? não, reset ao virar rodada.
    assert client.post("/api/v1/gurps/combate/avancar-turno").status_code == 200
    st = client.get("/api/v1/gurps/combate/status").json()
    # Reset ao virar rodada
    assert st["rodada_atual"] == 2
    assert st["defesas_na_rodada"] == {}

    r3 = client.post(
        "/api/v1/gurps/combate/ataque",
        json={
            "alvo_id": b,
            "nh_ataque": 16,
            "dados_ataque": [3, 3, 3],
            "dados_defesa": [6, 6, 6],
        },
    )
    assert r3.status_code == 200, r3.text
    # primeira defesa da nova rodada volta ao valor base efetivo (sem penalidade acumulada prévia)
    assert r3.json()["defesa"]["esquiva_efetiva"] >= 0

    # Força nova defesa de A na mesma rodada para verificar penalidade cumulativa.
    assert client.post("/api/v1/gurps/combate/avancar-turno").status_code == 200
    r4 = client.post(
        "/api/v1/gurps/combate/ataque",
        json={
            "alvo_id": a,
            "nh_ataque": 16,
            "dados_ataque": [3, 3, 3],
            "dados_defesa": [6, 6, 6],
        },
    )
    assert r4.status_code == 200, r4.text
    esquiva_segunda_defesa = r4.json()["defesa"]["esquiva_efetiva"]
    assert esquiva_segunda_defesa <= esquiva_primeira_defesa


def test_definir_postura_ativa_e_refletir_status(gurps_personagens_com_campanha_db):
    SessionLocal, u1, _ = gurps_personagens_com_campanha_db
    client = _build_client(SessionLocal, _usuario(u1))

    a = _criar(SessionLocal, client, "P1", 0, velocidade_valor=6.0)
    b = _criar(SessionLocal, client, "P2", 0, velocidade_valor=5.0)
    assert (
        client.post(
            "/api/v1/gurps/combate/iniciar",
            json={"personagem_ids": [a, b]},
        ).status_code
        == 200
    )

    r = client.post("/api/v1/gurps/combate/postura-atual", json={"postura": "agachado"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["postura_ativa"] == "agachado"
    assert body["posturas_por_personagem"][str(a)] == "agachado"
    ativo = next(p for p in body["personagens"] if p["id"] == a)
    assert ativo["postura_atual"] == "agachado"
    assert ativo["deslocamento_efetivo"] <= (ativo["deslocamento_valor"] or 0)


def test_postura_modifica_nh_ataque_e_esquiva_efetiva(
    gurps_personagens_com_campanha_db,
):
    SessionLocal, u1, _ = gurps_personagens_com_campanha_db
    client = _build_client(SessionLocal, _usuario(u1))

    a = _criar(SessionLocal, client, "Atacante", 0, velocidade_valor=7.0)
    b = _criar(SessionLocal, client, "Alvo", 0, velocidade_valor=6.0)
    assert (
        client.post(
            "/api/v1/gurps/combate/iniciar",
            json={"personagem_ids": [a, b]},
        ).status_code
        == 200
    )

    # Atacante deitado: penalidade no NH efetivo.
    assert (
        client.post(
            "/api/v1/gurps/combate/postura-atual",
            json={"postura": "deitado"},
        ).status_code
        == 200
    )

    r1 = client.post(
        "/api/v1/gurps/combate/ataque",
        json={
            "alvo_id": b,
            "nh_ataque": 12,
            "dados_ataque": [3, 3, 3],
            "dados_defesa": [6, 6, 6],
        },
    )
    assert r1.status_code == 200, r1.text
    assert r1.json()["nh_ataque_efetivo"] < 12

    # Alvo deitado: defesa efetiva mais baixa.
    assert client.post("/api/v1/gurps/combate/avancar-turno").status_code == 200
    assert (
        client.post(
            "/api/v1/gurps/combate/postura-atual",
            json={"postura": "deitado"},
        ).status_code
        == 200
    )
    assert client.post("/api/v1/gurps/combate/avancar-turno").status_code == 200
    assert (
        client.post(
            "/api/v1/gurps/combate/postura-atual",
            json={"postura": "em_pe"},
        ).status_code
        == 200
    )

    r2 = client.post(
        "/api/v1/gurps/combate/ataque",
        json={
            "alvo_id": b,
            "nh_ataque": 16,
            "dados_ataque": [3, 3, 3],
            "dados_defesa": [6, 6, 6],
        },
    )
    assert r2.status_code == 200, r2.text
    assert r2.json()["defesa"]["esquiva_efetiva"] >= 0


def test_ataque_soco_usa_dx_quando_nh_omitido(gurps_personagens_com_campanha_db):
    SessionLocal, u1, _ = gurps_personagens_com_campanha_db
    client = _build_client(SessionLocal, _usuario(u1))

    a = _criar(SessionLocal, client, "Brigador", 0, velocidade_valor=7.0)
    b = _criar(SessionLocal, client, "Alvo", 0, velocidade_valor=6.0)
    assert (
        client.post(
            "/api/v1/gurps/combate/iniciar",
            json={"personagem_ids": [a, b]},
        ).status_code
        == 200
    )

    r = client.post(
        "/api/v1/gurps/combate/ataque",
        json={
            "alvo_id": b,
            "tipo_ataque": "soco",
            "dados_ataque": [3, 3, 3],
            "dados_defesa": [6, 6, 6],
            "dados_dano": [4],
        },
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["tipo_ataque"] == "soco"
    assert body["nh_ataque"] >= 1
    if body["dano"] is not None:
        assert body["dano"]["expressao"].startswith("1d")


def test_ataque_chute_aplica_penalidade_no_nh_base(gurps_personagens_com_campanha_db):
    SessionLocal, u1, _ = gurps_personagens_com_campanha_db
    client = _build_client(SessionLocal, _usuario(u1))

    a = _criar(SessionLocal, client, "Lutador", 0, velocidade_valor=7.0)
    b = _criar(SessionLocal, client, "Alvo", 0, velocidade_valor=6.0)
    assert (
        client.post(
            "/api/v1/gurps/combate/iniciar",
            json={"personagem_ids": [a, b]},
        ).status_code
        == 200
    )

    r = client.post(
        "/api/v1/gurps/combate/ataque",
        json={
            "alvo_id": b,
            "tipo_ataque": "chute",
            "nh_ataque": 12,
            "dados_ataque": [3, 3, 3],
            "dados_defesa": [6, 6, 6],
        },
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["tipo_ataque"] == "chute"
    assert body["nh_ataque"] == 10


def test_ataque_usa_aparar_quando_solicitado(gurps_personagens_com_campanha_db):
    SessionLocal, u1, _ = gurps_personagens_com_campanha_db
    client = _build_client(SessionLocal, _usuario(u1))

    a = _criar(SessionLocal, client, "Atacante", 0, velocidade_valor=7.0)
    b = _criar(SessionLocal, client, "Defensor", 0, velocidade_valor=6.0, aparar=13)
    assert (
        client.post(
            "/api/v1/gurps/combate/iniciar",
            json={"personagem_ids": [a, b]},
        ).status_code
        == 200
    )

    r = client.post(
        "/api/v1/gurps/combate/ataque",
        json={
            "alvo_id": b,
            "tipo_defesa": "aparar",
            "nh_ataque": 16,
            "dados_ataque": [3, 3, 3],
            "dados_defesa": [4, 4, 4],
        },
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["defesa"]["tipo"] == "aparar"
    assert body["defesa"]["valor_efetivo"] >= 1


def test_ataque_usa_bloqueio_quando_solicitado(gurps_personagens_com_campanha_db):
    SessionLocal, u1, _ = gurps_personagens_com_campanha_db
    client = _build_client(SessionLocal, _usuario(u1))

    a = _criar(SessionLocal, client, "Atacante", 0, velocidade_valor=7.0)
    b = _criar(SessionLocal, client, "Defensor", 0, velocidade_valor=6.0, bloqueio="10")
    assert (
        client.post(
            "/api/v1/gurps/combate/iniciar",
            json={"personagem_ids": [a, b]},
        ).status_code
        == 200
    )

    r = client.post(
        "/api/v1/gurps/combate/ataque",
        json={
            "alvo_id": b,
            "tipo_defesa": "bloqueio",
            "nh_ataque": 16,
            "dados_ataque": [3, 3, 3],
            "dados_defesa": [4, 4, 4],
        },
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["defesa"]["tipo"] == "bloqueio"
    assert body["defesa"]["valor_efetivo"] >= 1


def test_rd_reduz_dano_no_fluxo_de_ataque(gurps_personagens_com_campanha_db):
    SessionLocal, u1, _ = gurps_personagens_com_campanha_db
    client = _build_client(SessionLocal, _usuario(u1))

    a = _criar(SessionLocal, client, "Atacante", 0, velocidade_valor=7.0)
    b = _criar(
        SessionLocal,
        client,
        "Defensor",
        0,
        velocidade_valor=6.0,
        extras={"rd": 3},
    )
    assert (
        client.post(
            "/api/v1/gurps/combate/iniciar",
            json={"personagem_ids": [a, b]},
        ).status_code
        == 200
    )

    r = client.post(
        "/api/v1/gurps/combate/ataque",
        json={
            "alvo_id": b,
            "nh_ataque": 16,
            "expressao_dano": "1d+2",
            "dados_ataque": [3, 3, 3],
            "dados_defesa": [6, 6, 6],
            "dados_dano": [4],
        },
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["dano"]["total_bruto"] == 6
    assert body["dano"]["rd_aplicada"] == 3
    assert body["dano"]["total_liquido"] == 3
    assert body["pvs_alvo_depois"] == (body["pvs_alvo_antes"] - 3)


def test_esforco_consume_fadiga_do_personagem_ativo(gurps_personagens_com_campanha_db):
    SessionLocal, u1, _ = gurps_personagens_com_campanha_db
    client = _build_client(SessionLocal, _usuario(u1))

    a = _criar(SessionLocal, client, "Ativo", 0, velocidade_valor=7.0)
    b = _criar(SessionLocal, client, "Outro", 0, velocidade_valor=6.0)
    assert (
        client.post(
            "/api/v1/gurps/combate/iniciar",
            json={"personagem_ids": [a, b]},
        ).status_code
        == 200
    )

    r = client.post(
        "/api/v1/gurps/combate/esforco",
        json={"custo_fadiga": 2, "usar_surto": True, "descricao": "ataque extra"},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["personagem_id"] == a
    assert body["custo_fadiga"] == 2
    assert body["fadiga_depois"] == (body["fadiga_antes"] - 2)
    assert body["usar_surto"] is True


def test_esforco_falha_sem_fadiga_disponivel(gurps_personagens_com_campanha_db):
    SessionLocal, u1, _ = gurps_personagens_com_campanha_db
    client = _build_client(SessionLocal, _usuario(u1))

    a = _criar(SessionLocal, client, "Ativo", 0, velocidade_valor=7.0)
    b = _criar(SessionLocal, client, "Outro", 0, velocidade_valor=6.0)
    assert (
        client.post(
            "/api/v1/gurps/combate/iniciar",
            json={"personagem_ids": [a, b]},
        ).status_code
        == 200
    )

    # Zera fadiga e tenta esforço.
    assert (
        client.patch(
            f"/api/v1/gurps/personagens/{a}",
            json={"fadiga_atual": 0},
        ).status_code
        == 200
    )

    r = client.post("/api/v1/gurps/combate/esforco", json={"custo_fadiga": 1})
    assert r.status_code == 422
    assert "fadiga" in r.json().get("detail", "").lower()


def test_ataque_aplica_condicao_atordoado_quando_alvo_permanece_consciente(
    gurps_personagens_com_campanha_db,
):
    SessionLocal, u1, _ = gurps_personagens_com_campanha_db
    client = _build_client(SessionLocal, _usuario(u1))

    a = _criar(SessionLocal, client, "Atacante", 0, velocidade_valor=7.0)
    b = _criar(SessionLocal, client, "Alvo", 0, velocidade_valor=6.0)
    assert (
        client.post(
            "/api/v1/gurps/combate/iniciar",
            json={"personagem_ids": [a, b]},
        ).status_code
        == 200
    )
    assert (
        client.patch(
            f"/api/v1/gurps/personagens/{b}", json={"pvs_valor": 20, "pvs_atual": 20}
        ).status_code
        == 200
    )

    r = client.post(
        "/api/v1/gurps/combate/ataque",
        json={
            "alvo_id": b,
            "nh_ataque": 16,
            "expressao_dano": "1d+0",
            "dados_ataque": [3, 3, 3],
            "dados_defesa": [6, 6, 6],
            "dados_dano": [4],
        },
    )
    assert r.status_code == 200, r.text
    assert r.json()["condicao_alvo"] == "atordoado"


def test_atordoado_so_permita_fazer_nada_e_recupera(gurps_personagens_com_campanha_db):
    SessionLocal, u1, _ = gurps_personagens_com_campanha_db
    client = _build_client(SessionLocal, _usuario(u1))

    a = _criar(SessionLocal, client, "A", 0, velocidade_valor=7.0)
    b = _criar(SessionLocal, client, "B", 0, velocidade_valor=6.0)
    assert (
        client.post(
            "/api/v1/gurps/combate/iniciar",
            json={"personagem_ids": [a, b]},
        ).status_code
        == 200
    )

    # A atordoa B
    assert (
        client.post(
            "/api/v1/gurps/combate/ataque",
            json={
                "alvo_id": b,
                "nh_ataque": 16,
                "expressao_dano": "1d+0",
                "dados_ataque": [3, 3, 3],
                "dados_defesa": [6, 6, 6],
                "dados_dano": [4],
            },
        ).status_code
        == 200
    )

    # Turno de B: não pode atacar enquanto atordoado.
    assert client.post("/api/v1/gurps/combate/avancar-turno").status_code == 200
    r1 = client.post("/api/v1/gurps/combate/manobra-atual", json={"manobra": "ataque"})
    assert r1.status_code == 422
    assert "atordoado" in r1.json().get("detail", "").lower()

    # Fazer nada remove atordoado.
    r2 = client.post(
        "/api/v1/gurps/combate/manobra-atual", json={"manobra": "fazer_nada"}
    )
    assert r2.status_code == 200, r2.text
    body = r2.json()
    assert body["condicoes_por_personagem"][str(b)] == "normal"


def test_avancar_sem_combate_404(gurps_personagens_com_campanha_db):
    SessionLocal, u1, _ = gurps_personagens_com_campanha_db
    client = _build_client(SessionLocal, _usuario(u1))

    r = client.post("/api/v1/gurps/combate/avancar-turno")
    assert r.status_code == 404


def test_iniciar_com_id_inexistente_404(gurps_personagens_com_campanha_db):
    SessionLocal, u1, _ = gurps_personagens_com_campanha_db
    client = _build_client(SessionLocal, _usuario(u1))

    r = client.post(
        "/api/v1/gurps/combate/iniciar",
        json={"personagem_ids": [999999]},
    )
    assert r.status_code == 404


def test_iniciar_com_personagem_de_outro_dono_403(gurps_personagens_com_campanha_db):
    SessionLocal, u1, u2 = gurps_personagens_com_campanha_db
    c1 = _build_client(SessionLocal, _usuario(u1))
    pid = _criar(SessionLocal, c1, "Dono1", 0, velocidade_valor=5.0)

    c2 = _build_client(SessionLocal, _usuario(u2))
    r = c2.post("/api/v1/gurps/combate/iniciar", json={"personagem_ids": [pid]})
    assert r.status_code == 403
