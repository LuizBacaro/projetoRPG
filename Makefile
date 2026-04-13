PYTHON ?= python3
NODE   ?= node
BASE_URL ?= http://localhost:8000
SNAPSHOT ?= backend/scripts/generated/personagens_snapshot.json

.PHONY: test test-backend test-frontend test-e2e lint backup-personagens restore-personagens

## Roda toda a suite de testes (backend + frontend)
test: test-backend test-frontend

## Roda apenas os testes de backend (pytest, exclui E2E)
test-backend:
	cd backend && $(PYTHON) -m pytest tests/ -q --tb=short --ignore=tests/e2e

## Roda apenas os testes de frontend (Node.js)
test-frontend:
	cd frontend && $(NODE) test-ficha-perfil-simples.js

## Roda E2E smoke (requer servidor em BASE_URL)
## Uso: make test-e2e BASE_URL=http://localhost:8000
test-e2e:
	cd backend && BASE_URL=$(BASE_URL) $(PYTHON) -m pytest tests/e2e/ -v --tb=short

## Lint básico Python (flake8, se instalado)
lint:
	@command -v flake8 > /dev/null && \
	  cd backend && flake8 app --max-line-length=120 --extend-ignore=E501 || \
	  echo "flake8 não instalado — pulando lint"

## Gera snapshot JSON completo dos personagens do banco configurado em DATABASE_URL
backup-personagens:
	cd backend && $(PYTHON) -m scripts.export_personagens_snapshot --output ../$(SNAPSHOT)

## Restaura snapshot JSON completo dos personagens no banco configurado em DATABASE_URL
## Uso: make restore-personagens SNAPSHOT=backend/scripts/generated/arquivo.json
restore-personagens:
	cd backend && $(PYTHON) -m scripts.restore_personagens_snapshot --input ../$(SNAPSHOT)
