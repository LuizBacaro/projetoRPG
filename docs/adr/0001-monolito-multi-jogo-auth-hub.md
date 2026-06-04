# ADR 0001 — Monólito FastAPI com Auth Hub e `game_slug` no JWT

**Status:** aceite (implementado)  
**Data:** 2026-06  
**Contexto:** [arquitetura-multi-jogo.md](../arquitetura-multi-jogo.md)

## Contexto

A plataforma precisa de login único e vários sistemas (D&D 3.5, 5e, Tormenta, GURPS) sem misturar regras nem dados de ficha entre jogos.

## Decisão

Manter **um processo FastAPI** e **um PostgreSQL** com:

- **Auth Hub** em `app.shared.*` (`/auth`, `/games`, `/usuarios`, `games_catalog`, `user_game_memberships`).
- **Módulos por jogo** em `app.games.<slug>.*` com rotas prefixadas e guard `requer_game_<slug>` quando `MULTI_GAME_STRICT_MODE=true`.
- **JWT** com claim `game_slug` após `POST /games/selecionar`.
- **Frontend estático** único em `frontend/` + `frontend/games/<slug>/`, seletor em `pages/selecionar-jogo.html`.

A **Fase 5** (apps/backend separados por jogo) fica adiada até haver necessidade operacional (equipes ou deploy independente).

## Consequências

**Positivas**

- Um deploy Render, um Neon, CORS e auth centralizados.
- Menor custo de manutenção para o estágio atual do produto.

**Negativas**

- Cold start e migrations afetam todos os jogos.
- Risco de acoplamento se `shared` importar de `games` (proibido por governança).

## Alternativas consideradas

| Alternativa | Motivo de rejeição (por agora) |
|-------------|--------------------------------|
| Microserviço por jogo | Complexidade de deploy, CORS e dados para time pequeno |
| Banco por jogo já na Fase 1 | Adiado; schema com prefixo/tabelas por jogo no mesmo DB |

## Revisão

Reavaliar quando: tráfego exigir escala independente, ou equipes distintas por `game_slug`.
