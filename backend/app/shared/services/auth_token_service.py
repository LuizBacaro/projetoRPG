"""
Emissão de JWT access/refresh e serialização do usuário para respostas de auth.
"""

from __future__ import annotations

from datetime import timedelta
from typing import Any, Dict

from ..core.config import settings
from ..core.security import criar_token
from ..models.usuario import Usuario


def usuario_para_dict(usuario: Usuario) -> Dict[str, Any]:
    perfil = usuario.perfil
    if hasattr(perfil, "value"):
        perfil = perfil.value
    return {
        "id": usuario.id,
        "email": usuario.email,
        "nome": usuario.nome,
        "perfil": str(perfil),
        "ativo": usuario.ativo,
    }


def emitir_par_tokens(usuario: Usuario) -> Dict[str, Any]:
    """Retorna access_token, refresh_token e usuario (dict)."""
    access = criar_token(
        data={"sub": usuario.email},
        secret_key=settings.SECRET_KEY,
        expires_delta=timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS),
        token_type="access",
    )
    refresh = criar_token(
        data={"sub": usuario.email},
        secret_key=settings.SECRET_KEY,
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        token_type="refresh",
    )
    return {
        "access_token": access,
        "refresh_token": refresh,
        "token_type": "bearer",
        "usuario": usuario_para_dict(usuario),
    }
