# E2E Playwright — Arena TTRPG

Testes de fumo no browser que validam login, hub multi-jogo, dashboard, ficha e grimório com a API e o frontend no **mesmo origin** (`BASE_URL`, normalmente `http://localhost:8000`).

---

## Onde está o código

| Caminho | Conteúdo |
|---------|----------|
| `backend/tests/e2e/test_smoke.py` | Fluxos UI (login, dashboard, ficha, grimório) |
| `backend/tests/e2e/test_smoke_api.py` | Checks leves via `page.request` (health, OAuth status) |
| `backend/tests/e2e/conftest.py` | Fixtures Playwright (se existir) |

---

## Pré-requisitos locais

```bash
cd backend
python -m pip install -r requirements.txt playwright pytest-playwright
python -m playwright install chromium
```

Variáveis úteis:

| Variável | Padrão | Notas |
|----------|--------|-------|
| `BASE_URL` | `http://localhost:8000` | API + estáticos |
| `ADMIN_EMAIL` | `ci-admin@example.com` | Evitar `*.local` (EmailStr rejeita) |
| `ADMIN_PASSWORD` | `admin123` | Deve existir no banco de teste |

Subir a API antes dos testes (ou usar o mesmo trap do CI):

```bash
export SECRET_KEY="dev-secret-32-chars-minimum!!!!"
export DATABASE_URL="sqlite:///./test_e2e.db"
export STARTUP_RUN_ALEMBIC=0
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BASE_URL=http://localhost:8000 pytest tests/e2e/ -v
```

Com browser visível: `pytest tests/e2e/ -v --headed`.

---

## CI (GitHub Actions)

Job **`E2E Smoke (Playwright)`** em `.github/workflows/ci.yml`:

- Corre em **pull requests** e em push para `develop` ou `feature/salva`.
- Disparo manual: `workflow_dispatch` com input `run_e2e=true`.
- Sobe `uvicorn` no mesmo step que o pytest (evita API morta entre steps).
- Aguarda `GET /health/live` antes dos testes.

---

## Cenários cobertos

1. **Login** — credenciais válidas/inválidas, token em `localStorage`.
2. **Hub** — escolha D&D 3.5 → dashboard.
3. **Dashboard** — tabela de combatentes, abrir ficha na mesma aba.
4. **Ficha** — modal perfil mágico (divindade, alinhamento).
5. **Grimório** — painel em conjurador do seed.
6. **API leve** — `/health/live`, `/api/v1/auth/oauth/google/status`.

---

## Troubleshooting

| Sintoma | Causa provável |
|---------|----------------|
| Timeout em `selecionar-jogo` | Seed sem admin ou catálogo `dnd35` |
| 422 no login | Email inválido (ex. `admin@arena.local`) |
| Ficha não abre modal | `aguardar_ficha_carregar` — controller ainda a inicializar |
| Grimório skipped | Sem conjurador no seed |
| E2E skipped no CI | PR em branch que não dispara o job |

---

## Relacionado

- [docs/dnd35-js-auditoria-2026-06.md](dnd35-js-auditoria-2026-06.md) — débito FE e plano de testes Vitest
- [docs/auth-sessao-oauth.md](auth-sessao-oauth.md) — refresh e OAuth Google
