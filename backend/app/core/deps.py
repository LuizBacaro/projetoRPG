"""
deps.py
SRP: Dependências de autenticação/autorização para injeção no FastAPI
SOLID: Dependency Injection — desacoplamento de segurança da lógica
"""
from fastapi import Depends, HTTPException, status
from starlette.requests import Request
from sqlalchemy.orm import Session
from typing import Generator, Optional
import logging

from .config import settings
from .database import SessionLocal
from .security import decodificar_token
from ..repositories.usuario_repository import UsuarioRepository
from ..models.usuario import PerfilUsuario

logger = logging.getLogger(__name__)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency: Fornece sessão do banco de dados para cada request.

    Características:
    - Cria nova sessão por request
    - Garante fechamento mesmo com erro
    - Type hints para IDE support

    Yields:
        Session SQLAlchemy

    Example:
        @app.get("/")
        def minha_rota(db: Session = Depends(get_db)):
            pass
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"❌ Erro na sessão do BD: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


def extrair_token_do_header(request: Request) -> Optional[str]:
    """
    Extrai o token Bearer do header Authorization.

    Args:
        request: Request do FastAPI

    Returns:
        Token ou None se não encontrado

    Example:
        Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
    """
    auth_header = request.headers.get("authorization")
    if not auth_header:
        return None

    partes = auth_header.split()
    if len(partes) != 2 or partes[0].lower() != "bearer":
        return None

    return partes[1]


def get_usuario_atual(
    request: Request,
    db: Session = Depends(get_db)
) -> "Usuario":
    """
    Dependency: Extrai e valida o usuário autenticado do token JWT.

    FLUXO:
    1. Extrai token do header Authorization
    2. Token é decodificado via JWT
    3. Email é extraído do payload
    4. Usuário é buscado no banco
    5. Validações (token válido, usuário existe, está ativo)

    Args:
        request: Request do FastAPI (contém headers)
        db: Sessão do banco de dados

    Returns:
        Objeto Usuario autenticado

    Raises:
        HTTPException 401: Token inválido/expirado/ausente
        HTTPException 404: Usuário não encontrado
        HTTPException 403: Usuário inativo

    Example:
        @app.get("/profile")
        def meu_perfil(usuario = Depends(get_usuario_atual)):
            return {"nome": usuario.nome, "email": usuario.email}
    """
    # ✅ Extrai token do header
    token = extrair_token_do_header(request)
    if not token:
        logger.warning("❌ Tentativa de acesso sem token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token não fornecido",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # ✅ Decodifica token
    payload = decodificar_token(token, settings.SECRET_KEY)
    if payload is None:
        logger.warning("❌ Tentativa de acesso com token inválido/expirado")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # ✅ Extrai email do token
    email = payload.get("sub")
    if not email:
        logger.warning("❌ Token não contém email (sub)")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token não contém email",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # ✅ Busca usuário no banco
    repo = UsuarioRepository(db)
    usuario = repo.buscar_por_email(email)

    if not usuario:
        logger.warning(f"❌ Usuário não encontrado: {email}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )

    if not usuario.ativo:
        logger.warning(f"⚠️  Usuário inativo tentou acessar: {email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo"
        )

    logger.info(f"✅ Acesso autorizado: {email}")
    return usuario


def requer_admin(
    usuario = Depends(get_usuario_atual)
) -> "Usuario":
    """
    Dependency: Valida se o usuário é ADMINISTRADOR.

    Args:
        usuario: Usuário autenticado (via get_usuario_atual)

    Returns:
        Usuario se for admin

    Raises:
        HTTPException 403: Usuário não é administrador
    """
    if usuario.perfil != PerfilUsuario.ADMINISTRADOR:
        logger.warning(
            f"⚠️  Acesso negado — usuário sem permissão admin: {usuario.email}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem acessar este recurso"
        )
    logger.info(f"✅ Admin autorizado: {usuario.email}")
    return usuario


def requer_mestre_ou_admin(
    usuario = Depends(get_usuario_atual)
) -> "Usuario":
    """
    Dependency: Valida se é MESTRE ou ADMINISTRADOR.

    Args:
        usuario: Usuário autenticado

    Returns:
        Usuario se tiver permissão

    Raises:
        HTTPException 403: Sem permissão adequada
    """
    if usuario.perfil not in [
        PerfilUsuario.ADMINISTRADOR,
        PerfilUsuario.MESTRE
    ]:
        logger.warning(
            f"⚠️  Acesso negado — sem permissão mestre/admin: {usuario.email}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas mestres e administradores podem acessar"
        )
    logger.info(f"✅ Mestre/Admin autorizado: {usuario.email}")
    return usuario


def requer_jogador(
    usuario = Depends(get_usuario_atual)
) -> "Usuario":
    """
    Dependency: Valida se é JOGADOR (ou superior).

    Args:
        usuario: Usuário autenticado

    Returns:
        Usuario se for jogador

    Raises:
        HTTPException 403: Não é jogador
    """
    if usuario.perfil not in [
        PerfilUsuario.JOGADOR,
        PerfilUsuario.MESTRE,
        PerfilUsuario.ADMINISTRADOR
    ]:
        logger.warning(f"⚠️  Acesso negado — não é jogador: {usuario.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a jogadores e superiores"
        )
    logger.info(f"✅ Jogador autorizado: {usuario.email}")
    return usuario