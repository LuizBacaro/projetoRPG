#!/usr/bin/env bash
# Instala hooks git locais (.githooks/) com black + isort alinhados ao CI.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

PYTHON="${PYTHON:-python3}"

echo "→ Instalando ferramentas de dev (black, isort, flake8)..."
"$PYTHON" -m pip install -q -r backend/requirements-dev.txt

chmod +x .githooks/pre-commit

echo "→ Ativando hooks em .githooks/ (config local do git)..."
git config core.hooksPath .githooks

echo ""
echo "✅ Pronto. A cada git commit em backend/app ou backend/tests:"
echo "   • black formata os .py staged"
echo "   • isort --profile black ordena imports"
echo ""
echo "   Corrigir tudo manualmente: make format-backend"
echo "   Verificação igual ao CI:      make ci-backend-lint"
