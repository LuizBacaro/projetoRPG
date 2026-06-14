# Comandos úteis — Arena TTRPG

Referência rápida para desenvolvimento local, qualidade de código, testes, banco e deploy.  
Todos os comandos `make` devem ser executados na **raiz do repositório**, salvo indicação em contrário.

---

## 1. Setup inicial (primeira vez)

```bash
# Clone e entre no projeto
git clone https://github.com/LuizBacaro/projetoRPG.git
cd projetoRPG

# Ambiente virtual Python (recomendado na raiz do repo)
python3 -m venv .venv
source .venv/bin/activate          # Linux/macOS
# .venv\Scripts\activate           # Windows

# Dependências do backend
pip install -r backend/requirements.txt

# Ferramentas de dev (black, isort, flake8 — mesmas versões do CI)
pip install -r backend/requirements-dev.txt

# Variáveis de ambiente
cp backend/.env.example backend/.env
# Edite backend/.env: DATABASE_URL, SECRET_KEY, ADMIN_EMAIL, ADMIN_PASSWORD, etc.

# Hook git (black + isort antes de cada commit) — uma vez por clone
make install-hooks
```

---

## 2. Servidor local

```bash
# Ativar o venv (se ainda não estiver ativo)
source .venv/bin/activate

# Subir API + frontend estático (mesmo origin em dev)
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

| URL | Descrição |
|-----|-----------|
| http://127.0.0.1:8000 | Login (redireciona para `/pages/login.html`) |
| http://127.0.0.1:8000/docs | Swagger / OpenAPI |
| http://127.0.0.1:8000/pages/selecionar-jogo.html | Hub de jogos (após login) |
| http://127.0.0.1:8000/health/live | Health check (sem migrations) |

**Login local:** com `ADMIN_EMAIL` e `ADMIN_PASSWORD` no `.env`, o admin é criado no primeiro startup.

**Banco SQLite (dev simples):** no `.env`:

```env
DATABASE_URL=sqlite:///./rpg_arena.db
```

---

## 3. Qualidade de código (backend)

Evita falhas no CI por `black`, `isort` ou `flake8`. Detalhes: [normas-qualidade-backend-ci.md](normas-qualidade-backend-ci.md).

| Comando | O que faz |
|---------|-----------|
| `make format-backend` | Corrige formatação (`black` + `isort --profile black`) em `backend/app/` e `backend/tests/` |
| `make pre-commit-run` | Formata tudo e valida black/isort (simula o hook em massa) |
| `make ci-backend-lint` | Verificação **igual ao CI**: black, isort e flake8 (só checa, não altera) |
| `make install-hooks` | Instala hook git em `.githooks/` (black + isort nos `.py` staged) |

Equivalente manual (dentro de `backend/`):

```bash
cd backend
black app/ tests/
isort --profile black app/ tests/
black --check app/ tests/
isort --check-only --profile black app/ tests/
flake8 app/ tests/ --max-line-length=120 --extend-ignore=E203,W503,E402,E501,E712,F401,F403,F541,F841
```

**Antes de cada push** com alterações em `backend/**/*.py`:

```bash
make ci-backend-lint
```

---

## 4. Testes

```bash
# Tudo (backend + smoke frontend D&D 3.5)
make test

# Só backend (pytest, exclui E2E)
make test-backend

# Só frontend (Node — perfil simples D&D 3.5)
make test-frontend

# E2E Playwright (API precisa estar rodando)
make test-e2e
# ou: make test-e2e BASE_URL=http://localhost:8000
```

Testes por módulo (exemplos):

```bash
cd backend

# D&D 5e
pytest tests/test_dnd5e_*.py -q

# D&D 3.5 — um ficheiro
pytest tests/test_combatentes_api.py -v

# Com cobertura
pytest tests/ -v --cov=app --ignore=tests/e2e
```

E2E com servidor em background:

```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BASE_URL=http://localhost:8000 pytest tests/e2e/ -v
```

Ver também: [e2e-playwright-arena.md](e2e-playwright-arena.md).

---

## 5. Banco de dados e migrations (Alembic)

Comandos a partir de `backend/` (onde está `alembic.ini`). O Alembic usa `DATABASE_URL` do ambiente.

```bash
cd backend
source ../.venv/bin/activate

# Estado atual
python3 -m alembic current

# Ver heads
python3 -m alembic heads

# Aplicar todas as migrations
python3 -m alembic upgrade head

# Nova migration (após alterar models)
python3 -m alembic revision --autogenerate -m "descricao_curta"
```

Instruções completas: [.github/instructions/migrations.instructions.md](../.github/instructions/migrations.instructions.md).

---

## 6. Seeds e catálogos (D&D 3.5)

```bash
# Sincronizar catálogo PHB de magias
make seed-magias

# Padding dev (~1100 magias) para paridade com produção
make pad-magias-dev

# Verificar catálogo no banco
make check-magias-catalogo

# Verificar volume tipo produção (>= 1000 magias)
make check-magias-producao

# Fluxo completo: seed + padding + checagem
make dev-magias-paridade
```

Seeds manuais (alternativa):

```bash
cd backend
python -m scripts.seed_magias
python -m scripts.seed_pericias
python -m scripts.seed_equipamentos
```

---

## 7. Backup e restore de personagens

```bash
# Exportar snapshot JSON (usa DATABASE_URL do ambiente)
make backup-personagens
# ou com caminho customizado:
make backup-personagens SNAPSHOT=backend/scripts/generated/meu_backup.json

# Restaurar em banco já migrado
make restore-personagens SNAPSHOT=backend/scripts/generated/meu_backup.json

# Com Neon/Postgres em produção — prefixe DATABASE_URL:
DATABASE_URL="postgresql://..." make backup-personagens
DATABASE_URL="postgresql://..." make restore-personagens
```

Restore com sobrescrita (script direto):

```bash
cd backend
python3 -m scripts.restore_personagens_snapshot \
  --input ../backend/scripts/generated/meu_backup.json \
  --replace-existing
```

---

## 8. D&D 5e — spellcasting (TypeScript)

Quando alterar ficheiros em `frontend/games/dnd5e/spellcasting/`:

```bash
cd frontend/games/dnd5e/spellcasting
npm ci
npm run build
npm test
```

O bundle gerado vai para `frontend/games/dnd5e/js/spellcasting/`. Revise o diff antes do commit.

---

## 9. Deploy e smoke (produção)

| Recurso | Onde |
|---------|------|
| Checklist pré-deploy | [PRE_DEPLOY_CHECKLIST.md](../PRE_DEPLOY_CHECKLIST.md) |
| Smoke pós-deploy | [runbook-deploy-smoke.md](runbook-deploy-smoke.md) |
| Curl de health | [smoke-pos-deploy-curl.md](smoke-pos-deploy-curl.md) |
| Pipeline CI/CD | [passo-a-passo-ci-cd.md](../passo-a-passo-ci-cd.md) |

Health em produção:

```bash
curl -sS https://projetorpg-7ih3.onrender.com/health/live
```

---

## 10. Resumo — fluxo típico do dia a dia

```bash
# 1. Ativar ambiente
source .venv/bin/activate

# 2. Subir servidor (terminal separado)
cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 3. Depois de editar Python no backend
make format-backend          # ou deixar o hook fazer no commit
make test-backend            # testes rápidos
make ci-backend-lint         # antes do push (igual ao CI)

# 4. Commit (com hook instalado)
git add ...
git commit -m "sua mensagem"   # black/isort rodam nos .py staged
git push
```

---

## Documentos relacionados

- [normas-qualidade-backend-ci.md](normas-qualidade-backend-ci.md) — black, isort, flake8
- [README.md](../README.md) — visão geral e setup
- [AGENTS.md](../AGENTS.md) — governança para agentes e contribuidores
- [auth-sessao-oauth.md](auth-sessao-oauth.md) — JWT e Google OAuth
