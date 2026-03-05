"""
Router de Autenticação
SRP: apenas rotas de login/logout
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...core.security import verificar_senha, criar_token
from ...repositories.usuario_repository import UsuarioRepository
from ...schemas.auth import LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/login", response_model=TokenResponse)
def login(dados: LoginRequest, db: Session = Depends(get_db)):
    """Autentica o usuário e retorna JWT."""
    repo    = UsuarioRepository(db)
    usuario = repo.buscar_por_email(dados.email)

    # Usuário não encontrado ou senha errada — mesmo erro (segurança)
    if not usuario or not verificar_senha(dados.senha, usuario.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos"
        )

    # Bloqueia usuário inativo (spec item f)
    if not usuario.ativo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo. Contate o administrador."
        )

    token = criar_token({
        "sub":    str(usuario.id),
        "email":  usuario.email,
        "perfil": usuario.perfil.value,
        "nome":   usuario.nome,
    })

    return TokenResponse(access_token=token, usuario=usuario)


@router.post("/logout")
def logout():
    """Logout simbólico — o cliente descarta o token."""
    return {"mensagem": "Logout realizado com sucesso"}