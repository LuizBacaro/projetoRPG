#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"
ADMIN_EMAIL="${ADMIN_EMAIL:-admin@arena-rpg.com.br}"
ADMIN_PASSWORD="${ADMIN_PASSWORD:-admin123}"

check_url() {
    local url="$1"
    local code
    code=$(curl -s -o /tmp/projeto_rpg_smoke_body.txt -w "%{http_code}" "$url")
    echo "$code $url"
}

echo "=== Smoke HTTP: paginas e health ==="
check_url "$BASE_URL/pages/login.html"
check_url "$BASE_URL/pages/dashboard.html"
check_url "$BASE_URL/arena"
check_url "$BASE_URL/pages/ficha-personagem.html?id=1"
check_url "$BASE_URL/pages/pericias.html?id=1"
check_url "$BASE_URL/pages/usuarios.html"
check_url "$BASE_URL/favicon.ico"
check_url "$BASE_URL/health"

echo "=== Smoke HTTP: autenticacao ==="
LOGIN_JSON=$(curl -s -X POST "$BASE_URL/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$ADMIN_EMAIL\",\"senha\":\"$ADMIN_PASSWORD\"}")

TOKEN=$(echo "$LOGIN_JSON" | sed -n 's/.*"access_token":"\([^"]*\)".*/\1/p')
if [[ -z "$TOKEN" ]]; then
    echo "LOGIN_FAIL $ADMIN_EMAIL"
    echo "$LOGIN_JSON" | head -c 300
    echo
    exit 1
fi

echo "LOGIN_OK $ADMIN_EMAIL"
ME_CODE=$(curl -s -o /tmp/projeto_rpg_smoke_me.txt -w "%{http_code}" \
  "$BASE_URL/api/v1/auth/me" \
  -H "Authorization: Bearer $TOKEN")
echo "$ME_CODE $BASE_URL/api/v1/auth/me"

echo "=== Smoke HTTP finalizado ==="
