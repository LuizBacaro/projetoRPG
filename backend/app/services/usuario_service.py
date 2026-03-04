"""
UsuarioService
SRP: regras de negócio para usuários
"""
from passlib.context import CryptContext
from fastapi import HTTPException, status
from ..repositories.usuario_repository import UsuarioRepository
from ..schemas.usuario import UsuarioCreate, UsuarioUpdate
from ..models.usuario import Usuario

# bcrypt 4.x não tem __about__ — usar schemes alternativos como fallback
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12
)


class UsuarioService:

    def __init__(self, repository: UsuarioRepository):
        self.repo = repository

    # ── Hash ──────────────────────────────────────────────────────────────────

    def _hash_senha(self, senha: str) -> str:
        # bcrypt limita a 72 bytes — trunca preventivamente
        return pwd_context.hash(senha[:72])

    def _verificar_senha(self, senha: str, hash_: str) -> bool:
        return pwd_context.verify(senha[:72], hash_)

    # ── CRUD ──────────────────────────────────────────────────────────────────

    def listar(self, apenas_ativos: bool = False) -> list[Usuario]:
        return self.repo.listar(apenas_ativos=apenas_ativos)

    def buscar_por_id(self, usuario_id: int) -> Usuario:
        usuario = self.repo.buscar_por_id(usuario_id)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuário {usuario_id} não encontrado"
            )
        return usuario

    def criar(self, dados: UsuarioCreate, usuario_responsavel: str = "sistema") -> Usuario:
        # Verifica e-mail duplicado
        if self.repo.buscar_por_email(dados.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="E-mail já cadastrado"
            )

        usuario = Usuario(
            perfil              = dados.perfil,
            nome                = dados.nome,
            email               = dados.email,
            senha_hash          = self._hash_senha(dados.senha),
            ativo               = dados.ativo,
            usuario_responsavel = usuario_responsavel,
        )
        return self.repo.criar(usuario)

    def atualizar(
        self,
        usuario_id: int,
        dados: UsuarioUpdate,
        usuario_responsavel: str = "sistema"
    ) -> Usuario:
        usuario = self.buscar_por_id(usuario_id)

        # Verifica e-mail duplicado (se mudou)
        if dados.email and dados.email != usuario.email:
            if self.repo.buscar_por_email(dados.email):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="E-mail já cadastrado"
                )

        # Aplica apenas os campos enviados
        if dados.perfil is not None:
            usuario.perfil = dados.perfil
        if dados.nome is not None:
            usuario.nome = dados.nome
        if dados.email is not None:
            usuario.email = dados.email
        if dados.senha is not None:
            usuario.senha_hash = self._hash_senha(dados.senha)
        if dados.ativo is not None:
            usuario.ativo = dados.ativo

        usuario.usuario_responsavel = usuario_responsavel
        return self.repo.atualizar(usuario)

    def inativar(self, usuario_id: int, usuario_responsavel: str = "sistema") -> Usuario:
        usuario = self.buscar_por_id(usuario_id)
        usuario.ativo               = False
        usuario.usuario_responsavel = usuario_responsavel
        return self.repo.atualizar(usuario)