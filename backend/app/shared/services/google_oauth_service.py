"""
Fluxo OAuth 2.0 / OpenID com Google (sem SessionMiddleware).
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import httpx
from sqlalchemy.orm import Session

from ..core.config import settings
from ..models.usuario import PerfilUsuario, Usuario
from ..repositories.usuario_repository import UsuarioRepository
from .auth_token_service import emitir_par_tokens

logger = logging.getLogger(__name__)

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://openidconnect.googleapis.com/v1/userinfo"


def google_oauth_habilitado() -> bool:
    return bool(
        settings.GOOGLE_OAUTH_CLIENT_ID.strip()
        and settings.GOOGLE_OAUTH_CLIENT_SECRET.strip()
    )


def resolver_frontend_base_url() -> str:
    explicit = (settings.FRONTEND_BASE_URL or "").strip().rstrip("/")
    if explicit:
        return explicit
    for origin in settings.ALLOWED_ORIGINS:
        o = (origin or "").strip().rstrip("/")
        if not o or o == "*":
            continue
        if "arena-de-combate-rpg" in o or "localhost" in o or "127.0.0.1" in o:
            return o
    return "http://127.0.0.1:8000"


def montar_redirect_uri(api_base: str) -> str:
    base = api_base.rstrip("/")
    return f"{base}{settings.API_V1_PREFIX}/auth/oauth/google/callback"


def url_autorizacao_google(*, redirect_uri: str, state: str) -> str:
    params = {
        "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "access_type": "online",
        "prompt": "select_account",
    }
    return f"{GOOGLE_AUTH_URL}?{urlencode(params)}"


def _trocar_codigo_por_tokens(code: str, redirect_uri: str) -> Dict[str, Any]:
    with httpx.Client(timeout=20.0) as client:
        token_res = client.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
                "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            },
        )
        token_res.raise_for_status()
        token_data = token_res.json()
        access = token_data.get("access_token")
        if not access:
            raise ValueError("Google não retornou access_token")
        user_res = client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access}"},
        )
        user_res.raise_for_status()
        return user_res.json()


def obter_ou_criar_usuario_google(db: Session, userinfo: Dict[str, Any]) -> Usuario:
    sub = (userinfo.get("sub") or "").strip()
    email = (userinfo.get("email") or "").strip().lower()
    nome = (userinfo.get("name") or userinfo.get("given_name") or email).strip()
    if not sub or not email:
        raise ValueError("Perfil Google incompleto (sub/email)")

    repo = UsuarioRepository(db)
    por_oauth = (
        db.query(Usuario)
        .filter(
            Usuario.oauth_provider == "google",
            Usuario.oauth_subject == sub,
        )
        .first()
    )
    if por_oauth:
        return por_oauth

    por_email = repo.buscar_por_email(email)
    if por_email:
        if not por_email.oauth_subject:
            por_email.oauth_provider = "google"
            por_email.oauth_subject = sub
            return repo.atualizar(por_email)
        if por_email.oauth_subject != sub:
            raise ValueError(
                "E-mail já vinculado a outra conta Google. Use o login original."
            )
        return por_email

    novo = Usuario(
        perfil=PerfilUsuario.JOGADOR,
        nome=nome[:100] or email,
        email=email,
        senha_hash=None,
        oauth_provider="google",
        oauth_subject=sub,
        ativo=True,
        usuario_responsavel="oauth-google",
    )
    return repo.criar(novo)


def processar_callback_google(
    db: Session, *, code: str, redirect_uri: str
) -> Dict[str, Any]:
    userinfo = _trocar_codigo_por_tokens(code, redirect_uri)
    if not userinfo.get("email_verified", True):
        raise ValueError("E-mail Google não verificado")
    usuario = obter_ou_criar_usuario_google(db, userinfo)
    if not usuario.ativo:
        raise ValueError("Usuário inativo")
    return emitir_par_tokens(usuario)
