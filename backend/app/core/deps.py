"""
deps.py
SRP: Dependências de autenticação/autorização para injeção no FastAPI
SOLID: Dependency Injection — desacoplamento de segurança da lógica
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from sqlalchemy.orm import Session
from typing import Generator
import logging

from .config import settings
from .database import SessionLocal
from .security import decodificar_token
from ..repositories.usuario_repository import UsuarioRepository
from ..models.usuario import PerfilUsuario

logger = logging.getLogger(__name__)

# ── Security Scheme ──────────────────────────────────────────────────────────
security = HTTPBearer()


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


def get_usuario_atual(
    credentials: HTTPAuthCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> "Usuario":
    """
    Dependency: Extrai e valida o usuário autenticado do token JWT.

    FLUXO:
    1. HTTPBearer extrai o token do header Authorization
    2. Token é decodificado via JWT
    3. Email é extraído do payload
    4. Usuário é buscado no banco
    5. Validações (token válido, usuário existe, está ativo)

    Args:
        credentials: Bearer token via HTTPBearer
        db: Sessão do banco de dados

    Returns:
        Objeto Usuario autenticado

    Raises:
        HTTPException 401: Token inválido/expirado
        HTTPException 404: Usuário não encontrado
        HTTPException 403: Usuário inativo

    Example:
        @app.get("/profile")
        def meu_perfil(usuario = Depends(get_usuario_atual)):
            return {"nome": usuario.nome, "email": usuario.email}
    """
    token = credentials.credentials

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

    FLUXO:
    1. Chama get_usuario_atual (autentica)
    2. Verifica se perfil = ADMINISTRADOR
    3. Retorna usuário ou lança exceção 403

    Args:
        usuario: Usuário autenticado (via get_usuario_atual)

    Returns:
        Usuario se for admin

    Raises:
        HTTPException 403: Usuário não é administrador

    Example:
        @app.delete("/usuarios/{id}")
        def deletar_usuario(id: int, admin = Depends(requer_admin)):
            # apenas admins chegam aqui
            pass
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

    FLUXO:
    1. Chama get_usuario_atual (autentica)
    2. Verifica se perfil ∈ [ADMINISTRADOR, MESTRE]
    3. Retorna usuário ou lança exceção 403

    Args:
        usuario: Usuário autenticado

    Returns:
        Usuario se tiver permissão

    Raises:
        HTTPException 403: Sem permissão adequada

    Example:
        @app.post("/combates")
        def criar_combate(combate: dict, mestre = Depends(requer_mestre_ou_admin)):
            # apenas mestres e admins chegam aqui
            pass
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

    Example:
        @app.get("/personagens")
        def listar_personagens(jogador = Depends(requer_jogador)):
            pass
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