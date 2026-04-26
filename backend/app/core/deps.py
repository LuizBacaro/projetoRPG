"""
deps.py
SRP: Dependências de autenticação/autorização para injeção no FastAPI
SOLID: Dependency Injection — desacoplamento de segurança da lógica
"""
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.requests import Request
from sqlalchemy.orm import Session
from typing import Generator, Optional
import logging

from .config import settings
from .database import SessionLocal
from .security import decodificar_token
from .security_audit import log_security_event
from ..repositories.usuario_repository import UsuarioRepository
from ..models.combatente import Combatente
from ..models.ataque import MagiaSlot
from ..models.usuario import PerfilUsuario

logger = logging.getLogger(__name__)

bearer_scheme = HTTPBearer(
    bearerFormat="JWT",
    scheme_name="JWTBearer",
    description="Informe o token JWT no formato: Bearer <token>",
    auto_error=False,
)


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
    except HTTPException:
        # Erros HTTP esperados (ex.: token inválido/expirado) não são falhas de BD.
        db.rollback()
        raise
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
    credentials: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme),
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
    token = credentials.credentials if credentials else None
    if not token:
        log_security_event(
            "access_token",
            "failure",
            request=request,
            reason="missing_token",
            level=logging.WARNING,
        )
        logger.warning("❌ Tentativa de acesso sem token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token não fornecido",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # ✅ Decodifica token
    payload = decodificar_token(token, settings.SECRET_KEY)
    if payload is None:
        log_security_event(
            "access_token",
            "failure",
            request=request,
            reason="invalid_or_expired_token",
            level=logging.WARNING,
        )
        logger.warning("❌ Tentativa de acesso com token inválido/expirado")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # ✅ Extrai email do token
    email = payload.get("sub")
    if not email:
        log_security_event(
            "access_token",
            "failure",
            request=request,
            reason="missing_subject",
            level=logging.WARNING,
        )
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
        log_security_event(
            "access_token",
            "failure",
            request=request,
            user_email=email,
            reason="user_not_found",
            level=logging.WARNING,
        )
        logger.warning(f"❌ Usuário não encontrado: {email}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )

    if not usuario.ativo:
        log_security_event(
            "access_token",
            "blocked",
            request=request,
            user_email=email,
            reason="inactive_user",
            level=logging.WARNING,
        )
        logger.warning(f"⚠️  Usuário inativo tentou acessar: {email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo"
        )

    logger.info(f"✅ Acesso autorizado: {email}")
    return usuario


def requer_admin(
    request: Request,
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
        log_security_event(
            "rbac_admin",
            "denied",
            request=request,
            user_email=usuario.email,
            reason="insufficient_role",
            level=logging.WARNING,
        )
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
    request: Request,
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
        log_security_event(
            "rbac_mestre_admin",
            "denied",
            request=request,
            user_email=usuario.email,
            reason="insufficient_role",
            level=logging.WARNING,
        )
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
    request: Request,
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
        log_security_event(
            "rbac_jogador",
            "denied",
            request=request,
            user_email=usuario.email,
            reason="insufficient_role",
            level=logging.WARNING,
        )
        logger.warning(f"⚠️  Acesso negado — não é jogador: {usuario.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a jogadores e superiores"
        )
    logger.info(f"✅ Jogador autorizado: {usuario.email}")
    return usuario


def requer_dono_ou_admin_combatente(
    combatente_id: int,
    request: Request,
    usuario=Depends(get_usuario_atual),
    db: Session = Depends(get_db),
) -> "Usuario":
    """Dependency: garante que o usuário é dono do combatente ou admin/mestre."""
    combatente = db.query(Combatente).filter(Combatente.id == combatente_id).first()
    if not combatente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Combatente {combatente_id} não encontrado",
        )

    if usuario.perfil in (PerfilUsuario.ADMINISTRADOR, PerfilUsuario.MESTRE):
        return usuario

    if combatente.dono_id != usuario.id:
        log_security_event(
            "combatente_access",
            "denied",
            request=request,
            user_email=usuario.email,
            target=f"combatente:{combatente_id}",
            reason="not_owner",
            level=logging.WARNING,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para acessar este combatente",
        )

    return usuario


def requer_dono_ou_admin_slot_magia(
    slot_id: int,
    request: Request,
    usuario=Depends(get_usuario_atual),
    db: Session = Depends(get_db),
) -> "Usuario":
    """Dependency: garante acesso por propriedade para endpoints de slot por ID."""
    slot = db.query(MagiaSlot).filter(MagiaSlot.id == slot_id).first()
    if not slot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Slot não encontrado",
        )

    combatente = db.query(Combatente).filter(Combatente.id == slot.combatente_id).first()
    if not combatente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Combatente {slot.combatente_id} não encontrado",
        )

    if usuario.perfil in (PerfilUsuario.ADMINISTRADOR, PerfilUsuario.MESTRE):
        return usuario

    if combatente.dono_id != usuario.id:
        log_security_event(
            "magia_slot_access",
            "denied",
            request=request,
            user_email=usuario.email,
            target=f"slot:{slot_id}",
            reason="not_owner",
            level=logging.WARNING,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para alterar este slot",
        )

    return usuario


def validar_combatentes_do_usuario(
    combatente_ids: list[int],
    usuario,
    db: Session,
) -> None:
    """Valida lista de combatentes para operações em lote (ex.: iniciar combate)."""
    if usuario.perfil in (PerfilUsuario.ADMINISTRADOR, PerfilUsuario.MESTRE):
        return

    ids_unicos = list(set(combatente_ids))
    if not ids_unicos:
        return

    combatentes = (
        db.query(Combatente)
        .filter(Combatente.id.in_(ids_unicos))
        .all()
    )

    encontrados = {c.id for c in combatentes}
    faltantes = [cid for cid in ids_unicos if cid not in encontrados]
    if faltantes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Combatentes não encontrados: {faltantes}",
        )

    sem_acesso = [c.id for c in combatentes if c.dono_id != usuario.id]
    if sem_acesso:
        log_security_event(
            "combatente_batch_access",
            "denied",
            user_email=usuario.email,
            target="combatentes",
            reason="not_owner",
            details={"combatente_ids": sem_acesso},
            level=logging.WARNING,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Sem permissão para os combatentes: {sem_acesso}",
        )