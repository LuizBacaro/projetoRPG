"""
conftest.py — E2E Smoke Suite
Configura browser Playwright e disponibiliza fixtures PAGE / CONTEXT reutilizáveis.

BASE_URL pode ser sobrescrito via variável de ambiente, útil para CI:
  BASE_URL=https://staging.example.com pytest tests/e2e/ -v
"""

import os
from typing import Generator

import pytest
from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright


def _env_ou_padrao(key: str, default: str) -> str:
    raw = os.environ.get(key)
    if raw is None:
        return default
    stripped = raw.strip()
    return default if stripped == "" else stripped


BASE_URL = _env_ou_padrao("BASE_URL", "http://localhost:8000")
HEADLESS = (
    os.getenv("E2E_HEADLESS", "1") != "0"
)  # headless por padrão; E2E_HEADLESS=0 para visual


@pytest.fixture(scope="session")
def browser_instance() -> Generator[Browser, None, None]:
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=HEADLESS)
        yield browser
        browser.close()


@pytest.fixture(scope="function")
def context(browser_instance: Browser) -> Generator[BrowserContext, None, None]:
    ctx = browser_instance.new_context(
        base_url=BASE_URL,
        viewport={"width": 1280, "height": 800},
        locale="pt-BR",
        ignore_https_errors=True,
    )
    yield ctx
    ctx.close()


@pytest.fixture(scope="function")
def page(context: BrowserContext) -> Generator[Page, None, None]:
    p = context.new_page()
    yield p
    p.close()
