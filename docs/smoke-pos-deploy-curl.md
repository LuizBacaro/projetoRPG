# Coleção curl — smoke pós-deploy (5 min)

## Preparação

```bash
export API_BASE_URL="https://projetorpg-7ih3.onrender.com"
export ADMIN_EMAIL="<admin_email>"
export ADMIN_PASSWORD="<admin_password>"
```

## 1) Docs

```bash
curl -i "$API_BASE_URL/api/docs"
```

Esperado: `HTTP/1.1 200`.

## 2) Login

```bash
LOGIN_RESP=$(curl -sS -X POST "$API_BASE_URL/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$ADMIN_EMAIL\",
    \"senha\": \"$ADMIN_PASSWORD\"
  }")

echo "$LOGIN_RESP"
```

Esperado: JSON com `access_token` e `refresh_token`.

## 3) Extrair tokens

```bash
ACCESS_TOKEN=$(printf '%s' "$LOGIN_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('access_token',''))")
REFRESH_TOKEN=$(printf '%s' "$LOGIN_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('refresh_token',''))")

echo "ACCESS_TOKEN size: ${#ACCESS_TOKEN}"
echo "REFRESH_TOKEN size: ${#REFRESH_TOKEN}"
```

## 4) Refresh

```bash
curl -i -X POST "$API_BASE_URL/api/v1/auth/refresh" \
  -H "Content-Type: application/json" \
  -d "{
    \"refresh_token\": \"$REFRESH_TOKEN\"
  }"
```

Esperado: `HTTP 200`.

## 5) Catálogo de jogos autenticado

```bash
curl -i "$API_BASE_URL/api/v1/games" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

Esperado: `HTTP 200`.

## 6) Selecionar jogo D&D 3.5

```bash
SELECT_RESP=$(curl -sS -X POST "$API_BASE_URL/api/v1/games/selecionar" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"game_slug":"dnd35"}')

echo "$SELECT_RESP"
```

Esperado: JSON com novo `access_token` e `game_slug: "dnd35"`.

## 7) Extrair token com jogo

```bash
GAME_ACCESS_TOKEN=$(printf '%s' "$SELECT_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('access_token',''))")
echo "GAME_ACCESS_TOKEN size: ${#GAME_ACCESS_TOKEN}"
```

## 8) Rota crítica D&D (combatentes)

```bash
curl -i "$API_BASE_URL/api/v1/combatentes" \
  -H "Authorization: Bearer $GAME_ACCESS_TOKEN"
```

Esperado: `HTTP 200` (ou payload válido sem 500).

## 9) Alternativa rota crítica (campanhas)

```bash
curl -i "$API_BASE_URL/api/v1/campanhas" \
  -H "Authorization: Bearer $GAME_ACCESS_TOKEN"
```

Esperado: `HTTP 200` (ou payload válido sem 500).

## 10) Check rápido sem token (controle)

```bash
curl -i "$API_BASE_URL/api/v1/auth/me"
curl -i "$API_BASE_URL/api/v1/games"
```

Esperado: `HTTP 401` com detalhe de token ausente.

