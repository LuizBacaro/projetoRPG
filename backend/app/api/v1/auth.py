"""
auth.py
SRP: Rotas de autenticação — login, logout, refresh token
SOLID: Dependency Injection via deps.py
"""
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Optional
import logging

from ...core.config import settings
from ...core.security import (
    hash_senha,
    verificar_senha,
    criar_token,
    decodificar_token,
)
from ...core.security_audit import log_security_event
from ...core.deps import get_db, get_usuario_atual
from ...repositories.usuario_repository import UsuarioRepository
from ...models.usuario import Usuario, PerfilUsuario
from ...models.campanha import Campanha

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/auth",
    tags=["autenticacao"]
)


# ── Schemas Pydantic ─────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    """Schema para requisição de login"""
    email: EmailStr = Field(..., max_length=150, description="Email do usuário")
    senha: str = Field(..., min_length=6, max_length=128, description="Senha do usuário")

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
    refresh_token: Optional[str] = Field(default=None, description="Refresh token para renovação da sessão")
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


class RefreshRequest(BaseModel):
    """Schema para renovação de sessão via refresh token."""
    refresh_token: str = Field(..., min_length=1, max_length=4096, description="Refresh token JWT válido")


class UsuarioResponse(BaseModel):
    """Schema para dados do usuário na resposta"""
    id: int
    email: str
    nome: str
    perfil: str
    ativo: bool

    class Config:
        from_attributes = True


class RegistroRequest(BaseModel):
    """Schema para cadastro público de nova conta."""
    nome: str = Field(..., min_length=1, max_length=100)
    email: EmailStr = Field(..., max_length=150)
    senha: str = Field(..., min_length=6, max_length=128)
    perfil: str = Field(default=PerfilUsuario.JOGADOR.value, pattern="^(jogador|mestre)$")
    campanha_nome: Optional[str] = Field(default=None, max_length=120)


class RegistroResponse(BaseModel):
    """Schema de resposta do cadastro público."""
    id: int
    nome: str
    email: str
    perfil: str
    ativo: bool


# ── Rotas ────────────────────────────────────────────────────────────────────

@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Autenticação de usuário",
    description="Realiza login e retorna access token e refresh token JWT.",
    responses={
        200: {
            "description": "Login efetuado com sucesso",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "<jwt_access_token>",
                        "refresh_token": "<jwt_refresh_token>",
                        "token_type": "bearer",
                        "usuario": {
                            "id": 1,
                            "email": "admin@arena-rpg.com.br",
                            "nome": "Administrador",
                            "perfil": "administrador",
                            "ativo": True,
                        },
                    }
                }
            },
        },
        401: {"description": "Email/senha inválidos"},
        403: {"description": "Usuário inativo"},
    },
)
def login(
    request: Request,
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
        log_security_event(
            "login",
            "failure",
            request=request,
            user_email=credentials.email,
            reason="user_not_found",
            level=logging.WARNING,
        )
        logger.warning(f"❌ Login falhou — email não encontrado: {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # ✅ Verifica senha
    if not verificar_senha(credentials.senha, usuario.senha_hash):
        log_security_event(
            "login",
            "failure",
            request=request,
            user_email=credentials.email,
            reason="bad_password",
            level=logging.WARNING,
        )
        logger.warning(f"❌ Login falhou — senha incorreta: {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # ✅ Valida se usuário está ativo
    if not usuario.ativo:
        log_security_event(
            "login",
            "blocked",
            request=request,
            user_email=credentials.email,
            reason="inactive_user",
            level=logging.WARNING,
        )
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
        expires_delta=timedelta(hours=24),
        token_type="access",
    )
    refresh_token = criar_token(
        data={"sub": usuario.email},
        secret_key=settings.SECRET_KEY,
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        token_type="refresh",
    )

    logger.info(f"✅ Login bem-sucedido: {usuario.email}")
    log_security_event("login", "success", request=request, user_email=usuario.email)

    # ✅ Retorna token + dados do usuário
    return TokenResponse(
        access_token=token,
        refresh_token=refresh_token,
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
def logout(request: Request):
    """
    Endpoint de logout.

    NOTA: JWT é stateless, então logout aqui é apenas para notificar o cliente.
    O cliente deve remover o token do localStorage/sessionStorage.

    Returns:
        Mensagem de confirmação
    """
    logger.info("✅ Logout realizado")
    log_security_event("logout", "success", request=request)
    return {
        "message": "Logout realizado com sucesso. Remova o token do cliente.",
        "status": "success"
    }


@router.post(
    "/registro",
    response_model=RegistroResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastro público de jogador/mestre",
    description="Cria nova conta com perfil jogador ou mestre. Para mestre, exige nome da primeira campanha.",
    responses={
        201: {"description": "Conta criada com sucesso"},
        409: {"description": "E-mail já cadastrado"},
    },
)
def registrar(
    request: Request,
    payload: RegistroRequest,
    db: Session = Depends(get_db),
) -> RegistroResponse:
    repo = UsuarioRepository(db)
    existente = repo.buscar_por_email(payload.email)
    if existente:
        log_security_event(
            "register",
            "failure",
            request=request,
            user_email=payload.email,
            reason="email_already_exists",
            level=logging.WARNING,
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="E-mail já cadastrado",
        )

    perfil_solicitado = payload.perfil.strip().lower()
    perfil = PerfilUsuario.MESTRE if perfil_solicitado == PerfilUsuario.MESTRE.value else PerfilUsuario.JOGADOR
    campanha_nome = (payload.campanha_nome or "").strip()
    if perfil == PerfilUsuario.MESTRE and not campanha_nome:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Nome da campanha é obrigatório para cadastro como mestre",
        )

    novo_usuario = Usuario(
        perfil=perfil,
        nome=payload.nome.strip(),
        email=payload.email.strip().lower(),
        senha_hash=hash_senha(payload.senha),
        ativo=True,
        usuario_responsavel="auto-registro",
    )
    try:
        db.add(novo_usuario)
        db.flush()
        if perfil == PerfilUsuario.MESTRE:
            db.add(
                Campanha(
                    mestre_id=novo_usuario.id,
                    nome=campanha_nome,
                    descricao="Campanha inicial criada no cadastro do mestre.",
                )
            )
        db.commit()
        db.refresh(novo_usuario)
    except Exception:
        db.rollback()
        raise

    usuario = novo_usuario
    log_security_event(
        "register",
        "success",
        request=request,
        user_email=usuario.email,
        target=f"usuario:{usuario.id}",
    )

    return RegistroResponse(
        id=usuario.id,
        nome=usuario.nome,
        email=usuario.email,
        perfil=usuario.perfil.value if hasattr(usuario.perfil, "value") else str(usuario.perfil),
        ativo=usuario.ativo,
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Renovar tokens de autenticação",
    description="Gera novo access token e novo refresh token (token rotation).",
    responses={
        200: {
            "description": "Tokens renovados com sucesso",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "<novo_jwt_access_token>",
                        "refresh_token": "<novo_jwt_refresh_token>",
                        "token_type": "bearer",
                        "usuario": {
                            "id": 1,
                            "email": "admin@arena-rpg.com.br",
                            "nome": "Administrador",
                            "perfil": "administrador",
                            "ativo": True,
                        },
                    }
                }
            },
        },
        401: {"description": "Refresh token inválido/expirado"},
        403: {"description": "Usuário inativo"},
        404: {"description": "Usuário não encontrado"},
    },
)
def refresh(
    request: Request,
    payload: RefreshRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    """Renova a sessão a partir de um refresh token válido."""
    token_payload = decodificar_token(payload.refresh_token, settings.SECRET_KEY)
    if token_payload is None or token_payload.get("type") != "refresh":
        log_security_event(
            "refresh",
            "failure",
            request=request,
            reason="invalid_refresh_token",
            level=logging.WARNING,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    email = token_payload.get("sub")
    if not email:
        log_security_event(
            "refresh",
            "failure",
            request=request,
            reason="missing_subject",
            level=logging.WARNING,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token sem usuário",
            headers={"WWW-Authenticate": "Bearer"},
        )

    repo = UsuarioRepository(db)
    usuario = repo.buscar_por_email(email)

    if not usuario:
        log_security_event(
            "refresh",
            "failure",
            request=request,
            user_email=email,
            reason="user_not_found",
            level=logging.WARNING,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado",
        )

    if not usuario.ativo:
        log_security_event(
            "refresh",
            "blocked",
            request=request,
            user_email=email,
            reason="inactive_user",
            level=logging.WARNING,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo",
        )

    novo_access_token = criar_token(
        data={"sub": usuario.email},
        secret_key=settings.SECRET_KEY,
        expires_delta=timedelta(hours=24),
        token_type="access",
    )
    novo_refresh_token = criar_token(
        data={"sub": usuario.email},
        secret_key=settings.SECRET_KEY,
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        token_type="refresh",
    )

    logger.info(f"✅ Token renovado com sucesso: {usuario.email}")
    log_security_event("refresh", "success", request=request, user_email=usuario.email)

    return TokenResponse(
        access_token=novo_access_token,
        refresh_token=novo_refresh_token,
        token_type="bearer",
        usuario={
            "id": usuario.id,
            "email": usuario.email,
            "nome": usuario.nome,
            "perfil": usuario.perfil,
            "ativo": usuario.ativo,
        },
    )


@router.get(
    "/me",
    response_model=UsuarioResponse,
    summary="Dados do usuário autenticado",
    description="Retorna os dados do usuário atualmente autenticado (requer Bearer JWT).",
    responses={
        200: {
            "description": "Usuário autenticado",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "email": "admin@arena-rpg.com.br",
                        "nome": "Administrador",
                        "perfil": "administrador",
                        "ativo": True,
                    }
                }
            },
        },
        401: {"description": "Token ausente/inválido/expirado"},
        403: {"description": "Usuário inativo"},
        404: {"description": "Usuário não encontrado"},
    },
)
def obter_usuario_atual(
    usuario: Usuario = Depends(get_usuario_atual)
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