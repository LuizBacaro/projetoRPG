#!/usr/bin/env bash
set -euo pipefail

# Valida fluxo de "perícias destacadas para arena":
# 1) Admin consegue marcar destaque_arena=true (HTTP 200)
# 2) Campo aparece em /pericias/{combatente_id}/listar
# 3) Jogador recebe HTTP 403 ao tentar alterar destaque_arena
# 4) (Opcional) reverte destaque_arena para false
#
# Uso:
#   chmod +x scripts/validar_pericias_destaque_arena.sh
#   API_BASE="https://sua-api/api/v1" \
#   ADMIN_EMAIL="admin@email.com" \
#   ADMIN_PASSWORD="senha" \
#   JOGADOR_EMAIL="jogador@email.com" \
#   JOGADOR_PASSWORD="senha" \
#   COMBATENTE_ID=1 \
#   PERICIA_JOGADOR_ID=1 \
#   ./scripts/validar_pericias_destaque_arena.sh
#
# Opcional:
#   REVERTER_NO_FIM=true|false (default: true)

if ! command -v curl >/dev/null 2>&1; then
  echo "❌ curl não encontrado."
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "❌ python3 não encontrado."
  exit 1
fi

: "${API_BASE:?Defina API_BASE (ex: https://sua-api/api/v1)}"
: "${ADMIN_EMAIL:?Defina ADMIN_EMAIL}"
: "${ADMIN_PASSWORD:?Defina ADMIN_PASSWORD}"
: "${JOGADOR_EMAIL:?Defina JOGADOR_EMAIL}"
: "${JOGADOR_PASSWORD:?Defina JOGADOR_PASSWORD}"
: "${COMBATENTE_ID:?Defina COMBATENTE_ID}"
: "${PERICIA_JOGADOR_ID:?Defina PERICIA_JOGADOR_ID}"

REVERTER_NO_FIM="${REVERTER_NO_FIM:-true}"

echo "🔐 Fazendo login como admin..."
ADMIN_LOGIN_JSON="$(curl -sS -X POST "${API_BASE}/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"${ADMIN_EMAIL}\",\"password\":\"${ADMIN_PASSWORD}\"}")"

ADMIN_TOKEN="$(python3 -c 'import json,sys; print(json.loads(sys.stdin.read()).get("access_token",""))' <<<"${ADMIN_LOGIN_JSON}")"
if [[ -z "${ADMIN_TOKEN}" ]]; then
  echo "❌ Não foi possível obter token do admin."
  echo "Resposta: ${ADMIN_LOGIN_JSON}"
  exit 1
fi

echo "🔐 Fazendo login como jogador..."
JOGADOR_LOGIN_JSON="$(curl -sS -X POST "${API_BASE}/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"${JOGADOR_EMAIL}\",\"password\":\"${JOGADOR_PASSWORD}\"}")"

JOGADOR_TOKEN="$(python3 -c 'import json,sys; print(json.loads(sys.stdin.read()).get("access_token",""))' <<<"${JOGADOR_LOGIN_JSON}")"
if [[ -z "${JOGADOR_TOKEN}" ]]; then
  echo "❌ Não foi possível obter token do jogador."
  echo "Resposta: ${JOGADOR_LOGIN_JSON}"
  exit 1
fi

UPDATE_URL="${API_BASE}/pericias/${COMBATENTE_ID}/pericia/${PERICIA_JOGADOR_ID}"
LISTAR_URL="${API_BASE}/pericias/${COMBATENTE_ID}/listar"

echo "✅ [1/4] Admin marcando destaque_arena=true..."
ADMIN_STATUS="$(curl -sS -o /tmp/admin_update_body.json -w "%{http_code}" -X PUT "${UPDATE_URL}" \
  -H "Authorization: Bearer ${ADMIN_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"graduacao":2,"bonus_outros":1,"destaque_arena":true}')"

if [[ "${ADMIN_STATUS}" != "200" ]]; then
  echo "❌ Esperado HTTP 200 para admin, veio ${ADMIN_STATUS}."
  echo "Resposta:"
  cat /tmp/admin_update_body.json
  exit 1
fi
echo "   OK (HTTP 200)"

echo "✅ [2/4] Conferindo destaque_arena na listagem..."
LISTAR_JSON="$(curl -sS "${LISTAR_URL}" -H "Authorization: Bearer ${ADMIN_TOKEN}")"
python3 - <<'PY' <<<"${LISTAR_JSON}"
import json, sys
data = json.loads(sys.stdin.read() or "{}")
pericias = data.get("pericias", [])
if not isinstance(pericias, list):
    print("❌ Resposta de listagem inválida: campo 'pericias' ausente ou inválido.")
    sys.exit(1)
if not any(bool(p.get("destaque_arena")) for p in pericias):
    print("❌ Nenhuma perícia com destaque_arena=true encontrada após atualização.")
    sys.exit(1)
print("   OK (há pelo menos uma perícia destacada)")
PY

echo "✅ [3/4] Jogador tentando alterar destaque_arena (deve falhar com 403)..."
JOGADOR_STATUS="$(curl -sS -o /tmp/jogador_update_body.json -w "%{http_code}" -X PUT "${UPDATE_URL}" \
  -H "Authorization: Bearer ${JOGADOR_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"graduacao":2,"bonus_outros":1,"destaque_arena":false}')"

if [[ "${JOGADOR_STATUS}" != "403" ]]; then
  echo "❌ Esperado HTTP 403 para jogador, veio ${JOGADOR_STATUS}."
  echo "Resposta:"
  cat /tmp/jogador_update_body.json
  exit 1
fi
echo "   OK (HTTP 403)"

if [[ "${REVERTER_NO_FIM}" == "true" ]]; then
  echo "✅ [4/4] Revertendo destaque_arena=false com admin..."
  REV_STATUS="$(curl -sS -o /tmp/admin_revert_body.json -w "%{http_code}" -X PUT "${UPDATE_URL}" \
    -H "Authorization: Bearer ${ADMIN_TOKEN}" \
    -H "Content-Type: application/json" \
    -d '{"graduacao":2,"bonus_outros":1,"destaque_arena":false}')"
  if [[ "${REV_STATUS}" != "200" ]]; then
    echo "❌ Falha ao reverter destaque (HTTP ${REV_STATUS})."
    echo "Resposta:"
    cat /tmp/admin_revert_body.json
    exit 1
  fi
  echo "   OK (revertido)"
else
  echo "ℹ️ REVERTER_NO_FIM=false, sem rollback."
fi

echo ""
echo "🎉 Validação concluída com sucesso."
