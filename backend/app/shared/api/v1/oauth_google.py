"""
Rotas OAuth Google — autorização, callback e troca de código para tokens JWT.
"""

from __future__ import annotations

import logging
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ...core.config import settings
from ...core.deps import get_db
from ...core.security_audit import log_security_event
from ...services.auth_token_service import emitir_par_tokens
from ...services.google_oauth_service import (
    google_oauth_habilitado,
    montar_redirect_uri,
    processar_callback_google,
    resolver_frontend_base_url,
    url_autorizacao_google,
)
from ...services.oauth_exchange_store import (
    consumir_exchange_code,
    consumir_oauth_state,
    criar_exchange_code,
    criar_oauth_state,
)
from .auth import TokenResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth/oauth", tags=["autenticacao-oauth"])


class OAuthStatusResponse(BaseModel):
    google_enabled: bool
    frontend_callback_path: str = "/pages/oauth-callback.html"


class OAuthExchangeRequest(BaseModel):
    exchange_code: str = Field(..., min_length=8, max_length=256)


def _api_base_from_request(request: Request) -> str:
    return str(request.base_url).rstrip("/")


@router.get("/google/status", response_model=OAuthStatusResponse)
def oauth_google_status() -> OAuthStatusResponse:
    return OAuthStatusResponse(google_enabled=google_oauth_habilitado())


@router.get("/google/authorize")
def oauth_google_authorize(request: Request):
    if not google_oauth_habilitado():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Login com Google não configurado no servidor",
        )
    redirect_uri = montar_redirect_uri(_api_base_from_request(request))
    state = criar_oauth_state()
    url = url_autorizacao_google(redirect_uri=redirect_uri, state=state)
    return RedirectResponse(url=url, status_code=status.HTTP_302_FOUND)


@router.get("/google/callback")
def oauth_google_callback(
    request: Request,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    db: Session = Depends(get_db),
):
    frontend = resolver_frontend_base_url()
    callback_page = f"{frontend}/pages/oauth-callback.html"

    if error:
        log_security_event(
            "oauth_google",
            "failure",
            request=request,
            reason=error,
            level=logging.WARNING,
        )
        q = urlencode({"oauth_error": error})
        return RedirectResponse(f"{callback_page}?{q}", status_code=302)

    if not code or not state or not consumir_oauth_state(state):
        q = urlencode({"oauth_error": "state_invalido"})
        return RedirectResponse(f"{callback_page}?{q}", status_code=302)

    redirect_uri = montar_redirect_uri(_api_base_from_request(request))
    try:
        tokens = processar_callback_google(db, code=code, redirect_uri=redirect_uri)
        exchange = criar_exchange_code(
            tokens, ttl_seconds=settings.OAUTH_EXCHANGE_TTL_SECONDS
        )
        log_security_event(
            "oauth_google",
            "success",
            request=request,
            user_email=tokens["usuario"].get("email"),
        )
        q = urlencode({"exchange": exchange})
        return RedirectResponse(f"{callback_page}?{q}", status_code=302)
    except Exception as exc:
        logger.warning("OAuth Google callback falhou: %s", exc)
        log_security_event(
            "oauth_google",
            "failure",
            request=request,
            reason=str(exc)[:120],
            level=logging.WARNING,
        )
        q = urlencode({"oauth_error": "falha_autenticacao"})
        return RedirectResponse(f"{callback_page}?{q}", status_code=302)


@router.post("/exchange", response_model=TokenResponse)
def oauth_exchange_tokens(payload: OAuthExchangeRequest):
    """Troca código único (pós-redirect) por JWT — evita tokens na URL."""
    data = consumir_exchange_code(payload.exchange_code)
    if not data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Código de troca inválido ou expirado",
        )
    return TokenResponse(**data)
