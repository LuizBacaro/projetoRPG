"""
Service de Usuário
SRP: lógica de negócio de usuário (sem acesso direto ao banco)
DIP: depende da abstração do repositório
"""
from fastapi import HTTPException, status
from passlib.context import CryptContext
from ..models.usuario import Usuario, PerfilUsuario
from ..repositories.usuario_repository import UsuarioRepository
from ..schemas.usuario import UsuarioCreate, UsuarioUpdate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UsuarioService:

    def __init__(self, repository: UsuarioRepository):
        self.repo = repository

    # ── Helpers de senha ──────────────────────────────────────────────────────

    def _hash_senha(self, senha: str) -> str:
        return pwd_context.hash(senha)

    def _verificar_senha(self, senha: str, hash_: str) -> bool:
        return pwd_context.verify(senha, hash_)

    # ── Regras de negócio ─────────────────────────────────────────────────────

    def _validar_email_unico(self, email: str, excluir_id: int = None) -> None:
        existente = self.repo.buscar_por_email(email)
        if existente and existente.id != excluir_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"E-mail '{email}' já está em uso por outro usuário"
            )

    def _garantir_ativo(self, usuario: Usuario) -> None:
        """Usuário inativo não pode ser alterado (exceto o próprio status)."""
        if not usuario.ativo:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuário inativo não pode ser alterado. Reative-o primeiro."
            )

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
        self._validar_email_unico(dados.email)

        usuario = Usuario(
            perfil              = dados.perfil,
            nome                = dados.nome,
            email               = dados.email,
            senha_hash          = self._hash_senha(dados.senha),
            ativo               = True,
            usuario_responsavel = usuario_responsavel,
        )
        return self.repo.criar(usuario)

    def atualizar(self, usuario_id: int, dados: UsuarioUpdate, usuario_responsavel: str = "sistema") -> Usuario:
        usuario = self.buscar_por_id(usuario_id)

        # Permite alterar apenas o status se estiver inativo
        if not usuario.ativo:
            if dados.ativo is True:
                usuario.ativo               = True
                usuario.usuario_responsavel = usuario_responsavel
                return self.repo.atualizar(usuario)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuário inativo só pode ter o status reativado."
            )

        if dados.email is not None:
            self._validar_email_unico(dados.email, excluir_id=usuario_id)
            usuario.email = dados.email

        if dados.nome   is not None: usuario.nome   = dados.nome
        if dados.perfil is not None: usuario.perfil = dados.perfil
        if dados.senha  is not None: usuario.senha_hash = self._hash_senha(dados.senha)
        if dados.ativo  is not None: usuario.ativo  = dados.ativo

        usuario.usuario_responsavel = usuario_responsavel
        return self.repo.atualizar(usuario)

    def inativar(self, usuario_id: int, usuario_responsavel: str = "sistema") -> Usuario:
        """Exclusão lógica via status = Inativo."""
        usuario = self.buscar_por_id(usuario_id)
        usuario.ativo               = False
        usuario.usuario_responsavel = usuario_responsavel
        return self.repo.atualizar(usuario)