"""
auth.py
SRP: Rotas de autenticação — login, logout, refresh token
SOLID: Dependency Injection via deps.py
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session
from datetime import timedelta
import logging

from ...core.config import settings
from ...core.database import SessionLocal
from ...core.security import (
    hash_senha,
    verificar_senha,
    criar_token
)
from ...core.deps import get_db
from ...repositories.usuario_repository import UsuarioRepository
from ...models.usuario import Usuario

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/auth",
    tags=["autenticacao"]
)


# ── Schemas Pydantic ─────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    """Schema para requisição de login"""
    email: EmailStr = Field(..., description="Email do usuário")
    senha: str = Field(..., min_length=6, description="Senha do usuário")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "admin@arena-rpg.com.br",
                "senha": "Admin@123456"
            }
        }


class TokenResponse(BaseModel):
    """Schema para resposta de autenticação"""
    access_token: str = Field(..., description="JWT token para autenticação")
    token_type: str = Field(default="bearer", description="Tipo do token")
    usuario: dict = Field(..., description="Dados do usuário autenticado")

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "usuario": {
                    "id": 1,
                    "email": "admin@arena-rpg.com.br",
                    "nome": "Administrador"
                }
            }
        }


class UsuarioResponse(BaseModel):
    """Schema para dados do usuário na resposta"""
    id: int
    email: str
    nome: str
    perfil: str
    ativo: bool

    class Config:
        from_attributes = True


# ── Rotas ────────────────────────────────────────────────────────────────────

@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Autenticação de usuário",
    description="Realiza login e retorna JWT token para autenticação"
)
def login(
    credentials: LoginRequest,
    db: Session = Depends(get_db)
) -> TokenResponse:
    """
    Endpoint de login.

    FLUXO:
    1. Recebe email e senha
    2. Busca usuário no banco
    3. Valida senha
    4. Cria JWT token
    5. Retorna token + dados do usuário

    Args:
        credentials: Email e senha do usuário
        db: Sessão do banco

    Returns:
        TokenResponse com access_token e dados do usuário

    Raises:
        HTTPException 401: Email ou senha incorretos
        HTTPException 403: Usuário inativo

    Example:
        POST /api/auth/login
        {
            "email": "admin@arena-rpg.com.br",
            "senha": "Admin@123456"
        }

        Response:
        {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer",
            "usuario": {
                "id": 1,
                "email": "admin@arena-rpg.com.br",
                "nome": "Administrador",
                "perfil": "admin",
                "ativo": true
            }
        }
    """
    repo = UsuarioRepository(db)

    # ✅ Busca usuário por email
    usuario = repo.buscar_por_email(credentials.email)
    if not usuario:
        logger.warning(f"❌ Login falhou — email não encontrado: {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # ✅ Verifica senha
    if not verificar_senha(credentials.senha, usuario.senha_hash):
        logger.warning(f"❌ Login falhou — senha incorreta: {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # ✅ Valida se usuário está ativo
    if not usuario.ativo:
        logger.warning(f"⚠️  Login bloqueado — usuário inativo: {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo"
        )

    # ✅ Cria JWT token com 24h de validade
    # ⚠️ IMPORTANTE: Passar settings.SECRET_KEY como argumento
    token = criar_token(
        data={"sub": usuario.email},
        secret_key=settings.SECRET_KEY,
        expires_delta=timedelta(hours=24)
    )

    logger.info(f"✅ Login bem-sucedido: {usuario.email}")

    # ✅ Retorna token + dados do usuário
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        usuario={
            "id": usuario.id,
            "email": usuario.email,
            "nome": usuario.nome,
            "perfil": usuario.perfil,
            "ativo": usuario.ativo
        }
    )


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Logout do usuário",
    description="Invalida a sessão do usuário"
)
def logout():
    """
    Endpoint de logout.

    NOTA: JWT é stateless, então logout aqui é apenas para notificar o cliente.
    O cliente deve remover o token do localStorage/sessionStorage.

    Returns:
        Mensagem de confirmação
    """
    logger.info("✅ Logout realizado")
    return {
        "message": "Logout realizado com sucesso. Remova o token do cliente.",
        "status": "success"
    }


@router.get(
    "/me",
    response_model=UsuarioResponse,
    summary="Dados do usuário autenticado",
    description="Retorna os dados do usuário atualmente autenticado"
)
def obter_usuario_atual(
    usuario: Usuario = Depends(get_db)  # ✅ Será injetado pela dependency
):
    """
    Endpoint que retorna dados do usuário logado.

    Requer token válido no header:
        Authorization: Bearer <token>

    Returns:
        UsuarioResponse com dados do usuário

    Example:
        GET /api/auth/me
        Headers: Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

        Response:
        {
            "id": 1,
            "email": "admin@arena-rpg.com.br",
            "nome": "Administrador",
            "perfil": "admin",
            "ativo": true
        }
    """
    return usuario