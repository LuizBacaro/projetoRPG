from fastapi import Response

from app.api.v1.magias import listar_magias
from app.models.magia import Magia, MagiaClasse
from app.models.usuario import PerfilUsuario, Usuario
from app.repositories.usuario_repository import UsuarioRepository


def test_listar_magias_aplica_paginacao_e_headers(test_db):
    test_db.add_all(
        [
            Magia(nome="Armadura Arcana", nivel=1, classe="MAGO", ativo=True),
            Magia(nome="Sono", nivel=1, classe="MAGO", ativo=True),
            Magia(nome="Mísseis Mágicos", nivel=1, classe="MAGO", ativo=True),
        ]
    )
    test_db.commit()

    response = Response()

    resultado = listar_magias(
        classe=None,
        nivel=None,
        escola=None,
        nome=None,
        componentes=None,
        dominio=None,
        ativo=None,
        sort_by=None,
        sort_dir="asc",
        skip=1,
        limit=1,
        response=response,
        db=test_db,
    )

    assert len(resultado) == 1
    assert response.headers["x-total-count"] == "3"
    assert response.headers["x-skip"] == "1"
    assert response.headers["x-limit"] == "1"


def test_listar_magias_filtra_classe_com_acento_sqlite(test_db):
    """
    SQLite upper('Clérigo') não vira CLERIGO; o repositório deve comparar com normalização Python.
    """
    m = Magia(nome="Cura Ferimentos Leves", nivel=1, classe="CLERIGO", ativo=True)
    test_db.add(m)
    test_db.flush()
    test_db.add(MagiaClasse(magia_id=m.id, classe="Clérigo", nivel=1))
    test_db.commit()

    response = Response()
    resultado = listar_magias(
        classe="CLERIGO",
        nivel=None,
        escola=None,
        nome=None,
        componentes=None,
        dominio=None,
        ativo=None,
        sort_by=None,
        sort_dir="asc",
        skip=0,
        limit=50,
        response=response,
        db=test_db,
    )

    assert len(resultado) == 1
    item = resultado[0]
    nome = item["nome"] if isinstance(item, dict) else item.nome
    assert nome == "Cura Ferimentos Leves"


def test_usuario_repository_lista_e_conta_com_paginacao(test_db):
    test_db.add_all(
        [
            Usuario(perfil=PerfilUsuario.ADMINISTRADOR, nome="Ana", email="ana@example.com", senha_hash="hash", ativo=True),
            Usuario(perfil=PerfilUsuario.JOGADOR, nome="Bruno", email="bruno@example.com", senha_hash="hash", ativo=True),
            Usuario(perfil=PerfilUsuario.JOGADOR, nome="Caio", email="caio@example.com", senha_hash="hash", ativo=False),
        ]
    )
    test_db.commit()

    repository = UsuarioRepository(test_db)

    usuarios = repository.listar(apenas_ativos=True, skip=0, limit=1)

    assert len(usuarios) == 1
    assert usuarios[0].ativo is True
    assert repository.count(apenas_ativos=True) == 2