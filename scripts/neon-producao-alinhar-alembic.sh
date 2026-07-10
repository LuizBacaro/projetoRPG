#!/usr/bin/env bash
# ============================================================================
# Alinhar alembic_version no Neon PRODUÇÃO — projetoRPG_Oreon (branch production)
# ============================================================================
#
# CONTEXTO
#   O schema em public já foi criado (guards, deploys antigos, hotfixes SQL).
#   alembic_version está em a7b9d3e1c2f4, mas o banco já tem Tormenta completo.
#
#   NÃO rode `alembic upgrade head` neste banco:
#   - a migration fase_c_schemas_auth_dnd35 moveria tabelas de public → auth/dnd35
#   - várias migrations falhariam com "relation already exists"
#
#   O procedimento seguro aqui é STAMP (registrar head sem reexecutar SQL).
#
# PRÉ-REQUISITOS
#   1. Backup: Neon → Backup & Restore (PITR) ou snapshot manual
#   2. DATABASE_URL do Render (branch production, Oregon us-west-2)
#   3. psql e Python/venv com alembic
#
# USO
#   export DATABASE_URL='postgresql://...neon.../neondb?sslmode=require'
#   ./scripts/neon-producao-alinhar-alembic.sh          # interativo
#   ./scripts/neon-producao-alinhar-alembic.sh --yes    # sem confirmação
#
# ============================================================================

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND="$ROOT/backend"
HEAD_REV="p1q2r3s4t5u6"
AUTO_YES=false

for arg in "$@"; do
  case "$arg" in
    --yes|-y) AUTO_YES=true ;;
    -h|--help)
      sed -n '1,35p' "$0"
      exit 0
      ;;
    *)
      echo "Opção desconhecida: $arg (use --help)" >&2
      exit 1
      ;;
  esac
done

if [[ -z "${DATABASE_URL:-}" ]]; then
  echo "❌ Defina DATABASE_URL (connection string do Neon production)." >&2
  echo "   Copie do Render → Environment → DATABASE_URL" >&2
  exit 1
fi

if [[ "$DATABASE_URL" != postgres://* && "$DATABASE_URL" != postgresql://* ]]; then
  echo "❌ DATABASE_URL deve ser PostgreSQL." >&2
  exit 1
fi

# Aviso se parecer Virginia (projeto antigo) em vez de Oregon
if [[ "$DATABASE_URL" == *"us-east-1"* ]]; then
  echo "⚠️  DATABASE_URL aponta para us-east-1 (Virginia)." >&2
  echo "   Produção atual deve ser projetoRPG_Oreon (us-west-2)." >&2
  if [[ "$AUTO_YES" != true ]]; then
    read -r -p "Continuar mesmo assim? [y/N] " ans
    [[ "$ans" =~ ^[Yy]$ ]] || exit 1
  fi
fi

if ! command -v psql >/dev/null 2>&1; then
  echo "❌ psql não encontrado. Instale postgresql-client." >&2
  exit 1
fi

cd "$BACKEND"

if [[ -d "$ROOT/.venv" ]]; then
  # shellcheck disable=SC1091
  source "$ROOT/.venv/bin/activate"
fi

echo "=== Revisão Alembic (antes) ==="
alembic current || true

echo ""
echo "=== Pre-check SQL ==="
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f "$ROOT/scripts/neon-producao-alembic-precheck.sql"

CURRENT="$(psql "$DATABASE_URL" -tAc 'SELECT version_num FROM alembic_version LIMIT 1' | tr -d '[:space:]')"

if [[ "$CURRENT" == "$HEAD_REV" ]]; then
  echo "✅ alembic_version já está em head ($HEAD_REV). Nada a fazer."
  exit 0
fi

echo ""
echo "Plano: alembic stamp head  ($CURRENT → $HEAD_REV)"
echo "Isso NÃO executa SQL de migration — apenas atualiza alembic_version."
echo ""

if [[ "$AUTO_YES" != true ]]; then
  read -r -p "Confirmar stamp em PRODUÇÃO? [y/N] " ans
  [[ "$ans" =~ ^[Yy]$ ]] || { echo "Cancelado."; exit 1; }
fi

alembic stamp head

echo ""
echo "=== Revisão Alembic (depois) ==="
alembic current

echo ""
echo "=== Smoke opcional (Render) ==="
if command -v curl >/dev/null 2>&1; then
  curl -fsS "https://projetorpg-7ih3.onrender.com/health" | head -c 200 || true
  echo ""
fi

echo ""
echo "✅ Concluído."
echo "   Próximo deploy no Render: Procfile roda 'alembic upgrade head' — deve ser no-op."
echo "   Migrations NOVAS após $HEAD_REV: usar 'alembic upgrade head' normalmente."
