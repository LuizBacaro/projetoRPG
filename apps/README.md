# `apps/` — visão multi-repo (evolução)

Este diretório documenta a **estrutura-alvo** quando Auth Hub e cada jogo
forem **repositórios ou pastas deployáveis independentes** (reverse proxy,
CI/CD e BDs separados). **Hoje o código continua no monólito** (`backend/`,
`frontend/`); nada aqui é obrigatório para desenvolvimento local.

## Mapa: plano → código atual

| Alvo (serviço / pasta) | Responsabilidade | Onde vive hoje (abr/2026) |
|------------------------|------------------|---------------------------|
| **Auth Hub** | Login, refresh, registro, catálogo de jogos, memberships, JWT global | `backend/app/api/v1/auth.py`, `games.py`, `usuarios.py`; `app/core/*`; `app/models/{usuario,game}.py`; `app/services/game_service.py` |
| **Game D&D 3.5** | Regras PHB 3.5, combate, ficha, magias, campanhas, … | `backend/app/games/dnd35/`; rotas montadas em `app.main` + shims residuais em `app/api/v1/*` (ver [docs/fase-a-inventario-routers.md](../docs/fase-a-inventario-routers.md)) |
| **Game D&D 5e** | Reservado | `backend/app/games/dnd5e/` (casca); `frontend/games/dnd5e/em-breve.html` |
| **Game GURPS** | Reservado | `backend/app/games/gurps/` (casca); `frontend/games/gurps/em-breve.html` |
| **Frontend shell** | Login global + seletor de jogo + assets partilhados | `frontend/pages/login.html`, `selecionar-jogo.html`, `js/services/AuthService.js`, `css/layout.css` |

## Fases do plano (resumo)

1. **Fase 1 — Auth + catálogo + seleção de jogo:** entregue no monólito
   (`games_catalog`, `user_game_memberships`, `GET/POST /api/v1/games`, redirect
   pós-login). Ver [docs/arquitetura-multi-jogo.md](../docs/arquitetura-multi-jogo.md).
2. **Fase 2 — Guard e trust no JWT:** `game_slug`, `requer_game_dnd35`, modo
   estrito; mesmo processo FastAPI.
3. **Fase 3 — Shell no frontend:** páginas globais + `frontend/games/dnd35/`
   para o bundle do jogo.
4. **Fase 4 — Permissões por jogo:** `perfil_no_jogo` + UI admin de memberships.
5. **Fase 5 — Deploy multi-app:** extrair para `apps/auth-hub`, `apps/game-dnd35`,
   etc.; ver secção 5 em `docs/arquitetura-multi-jogo.md`.

## Próximo passo físico (quando for prioridade)

1. Copiar ou mover `backend/` para `apps/game-dnd35/backend` com o mesmo
   `Dockerfile`/entrypoint; apontar `DATABASE_URL` do jogo.
2. Extrair rotas e modelos de hub para `apps/auth-hub` com BD própria ou
   schema `auth` (ver [docs/roteiro-melhorias-arquitetura.md](../docs/roteiro-melhorias-arquitetura.md)).
3. Gateway: mesmo domínio, prefixos `/api/v1/auth` → auth-hub,
   `/api/v1/combatentes` → game-dnd35 (ou subdomínios).

Não editar ficheiros de plano em `.cursor/plans/` a partir daqui — este README
é a fonte de verdade **no repositório** para o estado e o alvo.
