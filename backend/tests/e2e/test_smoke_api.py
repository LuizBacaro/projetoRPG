"""
E2E leve — endpoints JSON sem fluxo completo de UI.
Complementa test_smoke.py (Playwright).
"""

import os

from playwright.sync_api import Page


def _env_ou_padrao(key: str, default: str) -> str:
    raw = os.environ.get(key)
    if raw is None:
        return default
    stripped = raw.strip()
    return default if stripped == "" else stripped


BASE_URL = _env_ou_padrao("BASE_URL", "http://localhost:8000")
FRONTEND = BASE_URL


def test_health_live(page: Page):
    """API responde no probe usado pelo Render."""
    res = page.request.get(f"{BASE_URL}/health/live")
    assert res.ok, res.text()


def test_oauth_google_status(page: Page):
    """Status OAuth expõe google_enabled (CI sem credenciais → false)."""
    res = page.request.get(f"{BASE_URL}/api/v1/auth/oauth/google/status")
    assert res.ok, res.text()
    data = res.json()
    assert "google_enabled" in data
    assert isinstance(data["google_enabled"], bool)
    assert data.get("frontend_callback_path") == "/pages/oauth-callback.html"


def test_pagina_login_carrega(page: Page):
    """Formulário de login renderiza sem autenticação prévia."""
    page.goto(f"{FRONTEND}/pages/login.html")
    page.wait_for_load_state("domcontentloaded")
    assert page.locator("#inputEmail").is_visible()
    assert page.locator("#inputSenha").is_visible()
    assert page.locator("#btnLogin").is_visible()
