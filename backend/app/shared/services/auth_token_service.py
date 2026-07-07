"""
Emissão de JWT access/refresh e serialização do usuário para respostas de auth.
"""

from __future__ import annotations

from datetime import timedelta
from typing import Any, Dict, Optional

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


def _claims_jogo(
    game_slug: Optional[str],
    perfil_no_jogo: Optional[str],
) -> Dict[str, Any]:
    slug = (game_slug or "").strip().lower()
    if not slug:
        return {}
    claims: Dict[str, Any] = {"game_slug": slug}
    perfil = (perfil_no_jogo or "").strip()
    if perfil:
        claims["perfil_no_jogo"] = perfil
        claims["profile"] = perfil
    return claims


def emitir_par_tokens(
    usuario: Usuario,
    *,
    game_slug: Optional[str] = None,
    perfil_no_jogo: Optional[str] = None,
) -> Dict[str, Any]:
    """Retorna access_token, refresh_token e usuario (dict)."""
    jogo = _claims_jogo(game_slug, perfil_no_jogo)
    access = criar_token(
        data={"sub": usuario.email, **jogo},
        secret_key=settings.SECRET_KEY,
        expires_delta=timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS),
        token_type="access",
    )
    refresh = criar_token(
        data={"sub": usuario.email, **jogo},
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
