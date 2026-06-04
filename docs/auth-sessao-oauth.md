# Autenticação — sessão JWT, refresh e Google OAuth

## Tokens (padrão)

| Token | Duração | Config |
|-------|---------|--------|
| Access (JWT) | **24 h** | `ACCESS_TOKEN_EXPIRE_HOURS=24` |
| Refresh | **7 dias** | `REFRESH_TOKEN_EXPIRE_DAYS=7` |

## Frontend

- `frontend/js/shared/auth-session.js` — warm-up `/health/live`, refresh silencioso, retry de login em 503.
- `frontend/pages/login.html` — tenta refresh ao abrir; login com retry; botão Google se configurado.
- `frontend/pages/oauth-callback.html` — troca `exchange` por JWT via `POST /auth/oauth/exchange`.
- `AuthService.tentarRenovarToken()` — em 401 nas APIs, renova uma vez e repete o pedido.

## OAuth Google (opcional)

1. Criar credencial OAuth 2.0 (Web) no Google Cloud.
2. Definir **Authorized redirect URI**:
   - `{ORIGEM_DA_API}/api/v1/auth/oauth/google/callback`
3. No Render (ou `.env` local):
   - `GOOGLE_OAUTH_CLIENT_ID`
   - `GOOGLE_OAUTH_CLIENT_SECRET`
   - `FRONTEND_BASE_URL` (ex.: `https://arena-de-combate-rpg.com.br`)

Contas só Google não têm `senha_hash`; login por e-mail/senha retorna mensagem para usar Google.

## Lentidão em produção

OAuth **não** remove cold start do Render. O warm-up e o retry no login tratam 503 e serviço dormindo. Manter cron em `GET /health` a cada 10 min.
