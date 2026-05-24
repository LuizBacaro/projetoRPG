PYTHON ?= python3
NODE   ?= node
BASE_URL ?= http://localhost:8000
SNAPSHOT ?= backend/scripts/generated/personagens_snapshot.json

.PHONY: test test-backend test-frontend test-e2e lint format-backend ci-backend-lint backup-personagens restore-personagens seed-magias pad-magias-dev check-magias-catalogo check-magias-producao dev-magias-paridade

## Roda toda a suite de testes (backend + frontend)
test: test-backend test-frontend

## Roda apenas os testes de backend (pytest, exclui E2E)
test-backend:
	cd backend && $(PYTHON) -m pytest tests/ -q --tb=short --ignore=tests/e2e

## Roda apenas os testes de frontend (Node.js)
test-frontend:
	cd frontend && $(NODE) games/dnd35/test-ficha-perfil-simples.js

## Roda E2E smoke (requer servidor em BASE_URL)
## Uso: make test-e2e BASE_URL=http://localhost:8000
test-e2e:
	cd backend && BASE_URL=$(BASE_URL) $(PYTHON) -m pytest tests/e2e/ -v --tb=short

## Lint básico Python (flake8, se instalado)
lint:
	@command -v flake8 > /dev/null && \
	  cd backend && flake8 app --max-line-length=120 --extend-ignore=E501 || \
	  echo "flake8 não instalado — pulando lint"

## Formata backend (black + isort) — mesmas regras do CI
format-backend:
	cd backend && black app/ tests/ && isort --profile black app/ tests/

## Verificação de lint/format igual ao job GitHub Actions (backend)
ci-backend-lint:
	cd backend && \
	  black --check --diff app/ tests/ && \
	  isort --check-only --diff --profile black app/ tests/ && \
	  flake8 app/ tests/ --max-line-length=120 --extend-ignore=E203,W503,E402,E501,E712,F401,F403,F541,F841

## Gera snapshot JSON completo dos personagens do banco configurado em DATABASE_URL
backup-personagens:
	cd backend && $(PYTHON) -m scripts.export_personagens_snapshot --output ../$(SNAPSHOT)

## Restaura snapshot JSON completo dos personagens no banco configurado em DATABASE_URL
## Uso: make restore-personagens SNAPSHOT=backend/scripts/generated/arquivo.json
restore-personagens:
	cd backend && $(PYTHON) -m scripts.restore_personagens_snapshot --input ../$(SNAPSHOT)

## Popula/sincroniza catálogo PHB de magias D&D 3.5 (grimório, escolas, filtros)
seed-magias:
	cd backend && $(PYTHON) -m scripts.seed_magias --sync

## Padding dev (~1100 magias ativas) para reproduzir volume de produção localmente
pad-magias-dev:
	cd backend && $(PYTHON) -m scripts.pad_magias_catalogo_dev

## Verifica paridade do catálogo (seed + banco)
check-magias-catalogo:
	cd backend && $(PYTHON) -m scripts.check_magias_dnd35_catalogo --db

## Verifica volume próximo de produção (>=1000 magias ativas)
check-magias-producao:
	cd backend && $(PYTHON) -m scripts.check_magias_dnd35_catalogo --db --production-volume

## Seed PHB + padding dev + checagem (fluxo completo de paridade local)
dev-magias-paridade: seed-magias pad-magias-dev check-magias-producao
