from sqlalchemy.exc import IntegrityError

from app.shared.core.security import verificar_senha
from app.shared.models.usuario import PerfilUsuario, Usuario
from app.shared.repositories.usuario_repository import UsuarioRepository
from app.shared.startup.admin_default import criar_admin_padrao


def test_criar_admin_padrao_cria_quando_nao_existe(test_db, monkeypatch):
    monkeypatch.setattr(
        "app.shared.startup.admin_default.settings.ADMIN_EMAIL", "admin@arena.test"
    )
    monkeypatch.setattr(
        "app.shared.startup.admin_default.settings.ADMIN_PASSWORD", "SenhaForte123"
    )
    monkeypatch.setattr(
        "app.shared.startup.admin_default.settings.ADMIN_USERNAME", "Admin Teste"
    )

    criar_admin_padrao(test_db)

    admin = test_db.query(Usuario).filter(Usuario.email == "admin@arena.test").first()
    assert admin is not None
    assert admin.perfil == PerfilUsuario.ADMINISTRADOR
    assert admin.nome == "Admin Teste"
    assert verificar_senha("SenhaForte123", admin.senha_hash)


def test_criar_admin_padrao_nao_duplica_em_execucoes_repetidas(test_db, monkeypatch):
    monkeypatch.setattr(
        "app.shared.startup.admin_default.settings.ADMIN_EMAIL", "admin@arena.test"
    )
    monkeypatch.setattr(
        "app.shared.startup.admin_default.settings.ADMIN_PASSWORD", "SenhaForte123"
    )
    monkeypatch.setattr(
        "app.shared.startup.admin_default.settings.ADMIN_USERNAME", "Admin Teste"
    )

    criar_admin_padrao(test_db)
    criar_admin_padrao(test_db)

    total = test_db.query(Usuario).filter(Usuario.email == "admin@arena.test").count()
    assert total == 1


def test_criar_admin_padrao_idempotente_em_race_condition(test_db, monkeypatch):
    monkeypatch.setattr(
        "app.shared.startup.admin_default.settings.ADMIN_EMAIL", "admin@arena.test"
    )
    monkeypatch.setattr(
        "app.shared.startup.admin_default.settings.ADMIN_PASSWORD", "SenhaForte123"
    )
    monkeypatch.setattr(
        "app.shared.startup.admin_default.settings.ADMIN_USERNAME", "Admin Teste"
    )

    def _criar_com_race(self, usuario):
        existente = (
            self.db.query(Usuario).filter(Usuario.email == usuario.email).first()
        )
        if existente is None:
            self.db.add(
                Usuario(
                    perfil=PerfilUsuario.ADMINISTRADOR,
                    nome=usuario.nome,
                    email=usuario.email,
                    senha_hash=usuario.senha_hash,
                    ativo=True,
                    usuario_responsavel="sistema",
                )
            )
            self.db.commit()
        raise IntegrityError(
            "insert into usuarios (...) values (...)", {}, Exception("duplicate key")
        )

    monkeypatch.setattr(UsuarioRepository, "criar", _criar_com_race)

    criar_admin_padrao(test_db)

    total = test_db.query(Usuario).filter(Usuario.email == "admin@arena.test").count()
    assert total == 1
