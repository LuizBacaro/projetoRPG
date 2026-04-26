---
name: arena-ttrpg-architecture
description: >-
  Descreve a arquitetura de deploy e integração do projeto Arena TTRPG (FastAPI,
  frontend estático, Vercel, Render, CORS, rotas). Usar ao trabalhar em deploy,
  API cross-origin, vercel.json, login/dashboard/arena, ou erros 404/CORS em produção.
---

# Arena TTRPG — arquitetura e deploy

## Visão geral

- **Backend:** FastAPI em `backend/app/main.py`, prefixo API `settings.API_V1_PREFIX` (tipicamente `/api/v1`).
- **Frontend:** HTML/CSS/JS em `frontend/` (vanilla, ES modules onde indicado).
- **Produção típica:** site estático no **Vercel** + API no **Render** (`https://projetorpg-7ih3.onrender.com` no código de origem da API). Dois hosts → **CORS obrigatório** para chamadas do browser à API.
- **Dev local:** mesmo host que o uvicorn (`window.location.origin`) para a API; sem CORS entre origens diferentes se front e back forem o mesmo origin.

## Origem da API no browser (`getApiUrl`)

- Lógica canónica: `frontend/games/dnd35/js/config/api.config.js` — `BASE_URL` = origin local só em **localhost / 127.0.0.1 / ::1 / *.localhost**; caso contrário usa a origem do **Render** + `/api/v1`.
- Páginas com **scripts clássicos** que rodam antes de módulos (ex.: `pages/dashboard.html`) carregam **`/js/config/api-url-global.js`** primeiro para definir `window.getApiUrl` síncrono; depois pode importar `api.config.js` como módulo para resiliência do `fetch`.
- **Não** sobrescrever `window.getApiUrl` com `window.location.origin + '/api/v1'` em produção: isso aponta para o **Vercel**, onde `/api/*` não existe → 404.

## Vercel (`vercel.json`)

- `outputDirectory`: `frontend`; build mínimo (`echo 'static'`).
- **Rewrites** alinham atalhos do FastAPI local com ficheiros reais:
  - `/dashboard` → `/games/dnd35/pages/dashboard.html`
  - `/pericias` → `/games/dnd35/pages/pericias.html`
  - `/arena` → `/games/dnd35/arena.html`
- Bundle D&D 3.5 em `frontend/games/dnd35/` (servido em `/games/dnd35/...`).
- Shell global: `frontend/pages/login.html`, `selecionar-jogo.html` e stubs de redirect em `/pages/*.html`.

## Backend: rotas de página vs API

- `main.py` serve `/`, `/dashboard`, `/arena`, `/pericias` e monta estáticos em `/games/dnd35` a partir de `frontend/games/dnd35/` quando se usa só o uvicorn.
- Na Internet, com front no Vercel, essas rotas “bonitas” no FastAPI **não** são vistas pelo utilizador do site; no Vercel os **rewrites** cumprem o mesmo papel.

## CORS (produção)

- `ALLOWED_ORIGINS` no `.env` do Render deve incluir `https://www.arena-de-combate-rpg.com.br` e `https://arena-de-combate-rpg.com.br` (e previews `https://*.vercel.app` se necessário).
- **`allow_headers` no `CORSMiddleware`** deve incluir cabeçalhos usados pelo front (ex.: **`If-Match`** na Arena para combate). Se faltar, o **preflight OPTIONS** falha com status não OK e o browser reporta erro de CORS genérico.
- **`RateLimitMiddleware`:** não deve limitar **`OPTIONS`** (preflight); caso contrário 429 pode ser devolvido **sem** headers CORS e o browser bloqueia.

## Padrões a preservar

- Autenticação: JWT no `localStorage`; serviços usam `Authorization` onde aplicável.
- `getApiUrl('/...')` para todos os endpoints da API v1.

## Catálogo de talentos (LdJ)

- **Planilha:** `Tabela_5-1_Talentos_LdJ.xlsx` → gerar JSON com `python processar_talentos_excel.py` → **`talentos_importacao_limpo.json`** (commit no git).
- **Startup:** `inicializar_talentos` **sincroniza sempre** com esse JSON (upsert + soft-delete de legado não usado em fichas), como equipamentos. Após deploy no Render, reiniciar o serviço aplica o catálogo novo.
- **Caminho do JSON:** raiz do repo ou, em alternativa, `backend/talentos_importacao_limpo.json`.
- **CLI manual (opcional):** `python scripts/importar_talentos_catalogo_json.py [--remover-legado]`.
- Listagem na API: `order_by(nome)`.

## Referência rápida de ficheiros

| Área | Caminhos |
|------|----------|
| API routers | `backend/app/api/v1/*.py` |
| Config / CORS | `backend/app/main.py`, `backend/app/core/config.py` |
| Rate limit | `backend/app/core/rate_limit.py` |
| Config front API | `frontend/js/shared/render-api-origin.js` (origem Render), `frontend/games/dnd35/js/config/api.config.js`, `api-url-global.js` (IIFE legado — manter URL alinhada ao shared) |
| Arena (If-Match) | `frontend/games/dnd35/js/controllers/ArenaController.js` |
| Catálogo talentos | `talentos_importacao_limpo.json`, `backend/app/core/talentos_catalog_seed.py`, `backend/scripts/importar_talentos_catalogo_json.py` |
