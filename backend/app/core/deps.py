"""
Dependências FastAPI
SRP: injeção do usuário autenticado nas rotas protegidas
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from .database import get_db
from .security import decodificar_token
from ..repositories.usuario_repository import UsuarioRepository
from ..models.usuario import Usuario

bearer = HTTPBearer()


def get_usuario_atual(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db)
) -> Usuario:
    """Valida JWT e retorna o usuário logado."""
    token   = credentials.credentials
    payload = decodificar_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado"
        )

    usuario_id = int(payload.get("sub", 0))
    usuario    = UsuarioRepository(db).buscar_por_id(usuario_id)

    if not usuario or not usuario.ativo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado ou inativo"
        )

    return usuario


def requer_admin(usuario: Usuario = Depends(get_usuario_atual)) -> Usuario:
    """Garante que o usuário logado é Administrador."""
    if usuario.perfil.value != "administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a Administradores"
        )
    return usuario


def requer_mestre(usuario: Usuario = Depends(get_usuario_atual)) -> Usuario:
    """Garante que o usuário logado é Mestre ou Administrador."""
    if usuario.perfil.value not in ("mestre", "administrador"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a Mestres e Administradores"
        )
    return usuario