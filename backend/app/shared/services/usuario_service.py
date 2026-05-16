"""
UsuarioService
SRP: regras de negócio para usuários
DIP: depende da abstração do repositório
"""

from fastapi import HTTPException, status

from ..core.security import hash_senha, verificar_senha
from ..models.usuario import PerfilUsuario, Usuario
from ..ports import UsuarioRepositoryProtocol
from ..schemas.usuario import UsuarioCreate, UsuarioUpdate


class UsuarioService:
    def __init__(self, repository: UsuarioRepositoryProtocol):
        self.repo = repository

    # ── Regras de negócio ─────────────────────────────────────────────────────

    def _validar_email_unico(self, email: str, excluir_id: int = None) -> None:
        existente = self.repo.buscar_por_email(email)
        if existente and existente.id != excluir_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"E-mail '{email}' já está em uso por outro usuário",
            )

    # ── CRUD ──────────────────────────────────────────────────────────────────

    def listar(
        self, apenas_ativos: bool = False, skip: int = 0, limit: int = 50
    ) -> list[Usuario]:
        return self.repo.listar(apenas_ativos=apenas_ativos, skip=skip, limit=limit)

    def contar(self, apenas_ativos: bool = False) -> int:
        return self.repo.count(apenas_ativos=apenas_ativos)

    def buscar_por_id(self, usuario_id: int) -> Usuario:
        usuario = self.repo.buscar_por_id(usuario_id)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuário {usuario_id} não encontrado",
            )
        return usuario

    def criar(
        self, dados: UsuarioCreate, usuario_responsavel: str = "sistema"
    ) -> Usuario:
        self._validar_email_unico(dados.email)
        usuario = Usuario(
            perfil=dados.perfil,
            nome=dados.nome,
            email=dados.email,
            senha_hash=hash_senha(dados.senha),
            ativo=dados.ativo,
            usuario_responsavel=usuario_responsavel,
        )
        return self.repo.criar(usuario)

    def atualizar(
        self,
        usuario_id: int,
        dados: UsuarioUpdate,
        usuario_responsavel: str = "sistema",
    ) -> Usuario:
        usuario = self.buscar_por_id(usuario_id)

        if not usuario.ativo:
            if dados.ativo is True:
                usuario.ativo = True
                usuario.usuario_responsavel = usuario_responsavel
                return self.repo.atualizar(usuario)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuário inativo só pode ter o status reativado.",
            )

        if dados.email is not None:
            self._validar_email_unico(dados.email, excluir_id=usuario_id)
            usuario.email = dados.email

        if dados.nome is not None:
            usuario.nome = dados.nome
        if dados.perfil is not None:
            usuario.perfil = dados.perfil
        if dados.senha is not None:
            usuario.senha_hash = hash_senha(dados.senha)
        if dados.ativo is not None:
            usuario.ativo = dados.ativo

        usuario.usuario_responsavel = usuario_responsavel
        return self.repo.atualizar(usuario)

    def inativar(
        self, usuario_id: int, usuario_responsavel: str = "sistema"
    ) -> Usuario:
        usuario = self.buscar_por_id(usuario_id)
        usuario.ativo = False
        usuario.usuario_responsavel = usuario_responsavel
        return self.repo.atualizar(usuario)

    def excluir_definitivo(self, usuario_id: int, usuario_solicitante_id: int) -> None:
        usuario = self.buscar_por_id(usuario_id)

        if usuario.id == usuario_solicitante_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não pode excluir o próprio usuário logado",
            )

        if (
            usuario.perfil == PerfilUsuario.ADMINISTRADOR
            and self.repo.contar_admins_ativos() <= 1
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Não é possível excluir o último administrador ativo",
            )

        self.repo.excluir(usuario)
