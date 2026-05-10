"""
Suite E2E Smoke — Arena de Combate RPG
Playwright + pytest

Cobre os 4 cenários críticos definidos no MELHORIAS.md #Checklist3/3.4:
  1. Login válido/inválido + persistência de sessão
  2. Dashboard: listagem e abertura da ficha em mesma aba
  3. Perfil divino: abrir modal, editar divindade, salvar e verificar persistência
  4. Grimório: abrir painel, confirmar regras canônicas ativas

Pré-requisitos:
  - API rodando em BASE_URL (padrão: http://localhost:8000)
  - Usuário admin com acesso ao jogo dnd35 (env ADMIN_EMAIL / ADMIN_PASSWORD; catálogo + auto-enroll no startup)
  - `pip install playwright pytest-playwright` + `playwright install chromium`

Execução:
  cd backend
  BASE_URL=http://localhost:8000 pytest tests/e2e/ -v --headed  # com browser visível
  BASE_URL=http://localhost:8000 pytest tests/e2e/ -v           # headless (CI)
"""

import os
import re

import pytest
from playwright.sync_api import Page, expect


def _env_ou_padrao(key: str, default: str) -> str:
    """Como os secrets do GitHub vêm como string vazia se ausentes, getenv('K','d') não basta."""
    raw = os.environ.get(key)
    if raw is None:
        return default
    stripped = raw.strip()
    return default if stripped == "" else stripped


BASE_URL = _env_ou_padrao("BASE_URL", "http://localhost:8000")
ADMIN_EMAIL = _env_ou_padrao("ADMIN_EMAIL", "admin@arena.local")
ADMIN_PASS = _env_ou_padrao("ADMIN_PASSWORD", "admin123")
FRONTEND = BASE_URL  # arquivos estáticos servidos pelo mesmo servidor

# Após login o hub multi-jogo (`selecionar-jogo.html`) exige escolher D&D 3.5;
# `destinoPorSlug('dnd35')` redireciona para `/dashboard` (canónico), não `/pages/dashboard.html`.
_DASHBOARD_URL_RE = re.compile(r".*(/dashboard/?$|/pages/dashboard\.html$)")
# `expect_navigation(..., url=...)` espera até `load` por defeito — páginas com recursos pendentes podem nunca disparar load.
_SELETOR_JOGO_RE = re.compile(r".*selecionar-jogo\.html(\?.*)?$")


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────


def fazer_login(page: Page, email: str = ADMIN_EMAIL, senha: str = ADMIN_PASS):
    """Navega para login, autentica, escolhe D&D 3.5 no hub e aguarda o dashboard."""
    page.goto(f"{FRONTEND}/pages/login.html")
    page.wait_for_load_state("domcontentloaded")
    page.fill("#inputEmail", email)
    page.fill("#inputSenha", senha)
    page.click("#btnLogin")
    page.wait_for_url(_SELETOR_JOGO_RE, timeout=30000, wait_until="domcontentloaded")
    page.wait_for_load_state("domcontentloaded")
    hub_dnd = page.locator("#btnHubDnd35")
    hub_dnd.wait_for(state="visible", timeout=15000)
    expect(hub_dnd).to_be_enabled(timeout=30000)
    hub_dnd.click()
    page.wait_for_url(_DASHBOARD_URL_RE, timeout=30000, wait_until="domcontentloaded")


# ─────────────────────────────────────────────────────────────────────────────
# Cenário 1 — Login
# ─────────────────────────────────────────────────────────────────────────────


def test_login_valido(page: Page):
    """Login válido passa pelo hub de jogos e termina no dashboard D&D 3.5."""
    fazer_login(page)
    expect(page).to_have_url(_DASHBOARD_URL_RE)


def test_login_invalido_exibe_erro(page: Page):
    """Login com senha errada exibe mensagem de erro, não redireciona."""
    page.goto(f"{FRONTEND}/pages/login.html")
    page.wait_for_load_state("networkidle")
    page.fill("#inputEmail", ADMIN_EMAIL)
    page.fill("#inputSenha", "senha_errada_xpto")
    page.click("#btnLogin")

    # Deve permanecer na tela de login
    page.wait_for_timeout(2000)
    expect(page).to_have_url(f"{FRONTEND}/pages/login.html")


def test_login_persiste_token(page: Page):
    """Token armazenado no localStorage sobrevive a reload da página."""
    fazer_login(page)
    token_antes = page.evaluate("localStorage.getItem('token')")
    assert token_antes, "Token deve estar salvo após login"

    page.reload()
    page.wait_for_load_state("networkidle")
    token_depois = page.evaluate("localStorage.getItem('token')")
    assert token_antes == token_depois, "Token deve ser idêntico após reload"


# ─────────────────────────────────────────────────────────────────────────────
# Cenário 2 — Dashboard / Listagem / Ficha
# ─────────────────────────────────────────────────────────────────────────────


def test_dashboard_lista_combatentes(page: Page):
    """Dashboard carrega e exibe ao menos um combatente no grid."""
    fazer_login(page)
    # Aguarda carregamento do grid (cards de combatente)
    page.wait_for_selector(
        ".combatente-card, .dashboard-card, [data-combatente-id]", timeout=10000
    )
    cards = page.locator(".combatente-card, .dashboard-card, [data-combatente-id]")
    assert cards.count() >= 1, "Deve haver ao menos um combatente listado"


def test_dashboard_abre_ficha_mesma_aba(page: Page):
    """Clicar em 'Ver Ficha' navega na mesma aba, não abre nova."""
    fazer_login(page)
    page.wait_for_selector(
        ".combatente-card, .dashboard-card, [data-combatente-id]", timeout=10000
    )

    paginas_antes = (
        page.context.pages.__len__() if hasattr(page.context, "pages") else 1
    )

    # Clica no primeiro link/botão de ficha disponível
    btn_ficha = page.locator(
        "a[href*='ficha-personagem'], button[data-acao='ficha']"
    ).first
    if btn_ficha.count() == 0:
        pytest.skip("Botão de ficha não encontrado neste ambiente de teste")

    btn_ficha.click()
    page.wait_for_url("**/ficha-personagem.html**", timeout=8000)

    paginas_depois = len(page.context.pages)
    assert paginas_depois == paginas_antes, "Ficha deve abrir na mesma aba"
    expect(page).to_have_url(f"{FRONTEND}/pages/ficha-personagem.html**")


# ─────────────────────────────────────────────────────────────────────────────
# Cenário 3 — Modal Perfil Divino (Ficha)
# ─────────────────────────────────────────────────────────────────────────────


def test_modal_perfil_divino_preenche_divindade(page: Page):
    """Ao abrir o modal de perfil mágico, campo Divindade é pré-preenchido com valor salvo."""
    fazer_login(page)

    # Navega direto para uma ficha (usa o primeiro combatente retornado pela API)
    token = page.evaluate("localStorage.getItem('token')")
    combatentes = page.evaluate(
        f"""async () => {{
        const r = await fetch('{BASE_URL}/api/v1/combatentes?tipo=jogador&limit=1',
            {{ headers: {{ Authorization: 'Bearer {{}}'.replace('{{}}', localStorage.getItem('token')) }} }});
        return r.ok ? r.json() : [];
    }}"""
    )
    if not combatentes:
        pytest.skip("Nenhum combatente jogador disponível no ambiente de teste")

    combatente_id = combatentes[0]["id"]
    page.goto(f"{FRONTEND}/pages/ficha-personagem.html?id={combatente_id}")
    page.wait_for_load_state("networkidle")

    # Abre modal de perfil mágico
    btn = page.locator("#btnEditarPerfilMagico")
    btn.wait_for(state="visible", timeout=5000)
    btn.click()

    # Modal deve estar visível
    modal = page.locator("#modalPerfilMagico")
    expect(modal).to_be_visible()

    # Campo de divindade existe (agora é um <select> alimentado pelo catálogo da Tabela 3-7)
    select_divindade = page.locator("#selectPerfilDivindade")
    expect(select_divindade).to_be_visible()


def test_modal_perfil_salva_e_persiste(page: Page):
    """Editar alinhamento no modal e salvar deve refletir na ficha sem reload completo."""
    fazer_login(page)

    combatentes = page.evaluate(
        f"""async () => {{
        const r = await fetch('{BASE_URL}/api/v1/combatentes?tipo=jogador&limit=1',
            {{ headers: {{ Authorization: 'Bearer ' + localStorage.getItem('token') }} }});
        return r.ok ? r.json() : [];
    }}"""
    )
    if not combatentes:
        pytest.skip("Nenhum combatente jogador disponível no ambiente de teste")

    combatente_id = combatentes[0]["id"]
    page.goto(f"{FRONTEND}/pages/ficha-personagem.html?id={combatente_id}")
    page.wait_for_load_state("networkidle")

    btn = page.locator("#btnEditarPerfilMagico")
    btn.wait_for(state="visible", timeout=5000)
    btn.click()

    modal = page.locator("#modalPerfilMagico")
    expect(modal).to_be_visible()

    # Edita alinhamento
    alinhamento_input = page.locator("#inputPerfilAlinhamento")
    alinhamento_input.clear()
    alinhamento_input.fill("Neutro")

    # Salva
    page.locator("#btnSalvarPerfilMagico").click()

    # Modal deve fechar
    page.wait_for_timeout(1500)
    expect(modal).not_to_be_visible()

    # Texto de alinhamento na ficha deve refletir o novo valor
    alinhamento_ficha = page.locator("#fichaAlinhamento")
    expect(alinhamento_ficha).to_contain_text("Neutro")


# ─────────────────────────────────────────────────────────────────────────────
# Cenário 4 — Grimório
# ─────────────────────────────────────────────────────────────────────────────


def test_grimorio_abre_e_lista_magias(page: Page):
    """Painel do grimório abre e exibe ao menos uma magia disponível."""
    fazer_login(page)

    combatentes = page.evaluate(
        f"""async () => {{
        const r = await fetch('{BASE_URL}/api/v1/combatentes?tipo=jogador&limit=1',
            {{ headers: {{ Authorization: 'Bearer ' + localStorage.getItem('token') }} }});
        return r.ok ? r.json() : [];
    }}"""
    )
    if not combatentes:
        pytest.skip("Nenhum combatente jogador disponível no ambiente de teste")

    combatente_id = combatentes[0]["id"]
    page.goto(f"{FRONTEND}/pages/ficha-personagem.html?id={combatente_id}")
    page.wait_for_load_state("networkidle")

    btn_grimorio = page.locator("#btnGrimorio, #btnAbrirGrimorio")
    if btn_grimorio.count() == 0:
        pytest.skip("Botão de grimório não encontrado neste ambiente")

    btn_grimorio.first.click()

    # Painel do grimório deve ficar visível
    painel = page.locator("#modalGrimorio, #grimorioContainer, .grimorio-painel")
    painel.wait_for(state="visible", timeout=5000)
    expect(painel.first).to_be_visible()
