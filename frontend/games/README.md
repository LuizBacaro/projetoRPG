# `frontend/games/`

Cada subpasta é um sistema de RPG (`game_slug` = pasta), com páginas, CSS e JS próprios.

**Fonte de verdade do status no produto:** `games_catalog.status` no backend (`backend/app/shared/startup/game_catalog.py`), sincronizado no startup. O seletor (`frontend/pages/selecionar-jogo.html`) lê a API `/api/v1/games`.

## Slugs

| Slug | Pasta | Status no catálogo (2026-06) | Maturidade |
|------|--------|------------------------------|------------|
| `dnd35` | `dnd35/` | **disponivel** | Produção — dashboard, ficha, arena, grimório |
| `dnd5e` | `dnd5e/` | **disponivel** | Ficha, dashboard e arena; backend com catálogos 5e |
| `tormenta` | `tormenta/` | **disponivel** | Ficha MB, dashboard, grimório/API de regras |
| `gurps` | `gurps/` | **disponivel** | Dashboard, ficha, combate Lite |

Páginas `em-breve.html` permanecem como fallback quando o catálogo marcar `em_breve` ou `manutencao`.

## Estrutura-alvo

```
frontend/games/<slug>/
    pages/           # dashboard, ficha, arena, …
    css/
    js/
        services/
        controllers/
```

## Rewrites Vercel (raiz `vercel.json`)

| Rota pública | Destino |
|--------------|---------|
| `/dashboard`, `/arena`, `/pericias` | `dnd35/` |
| `/dnd5e/dashboard`, `/dnd5e/ficha`, `/dnd5e/arena` | `dnd5e/pages/` |
| `/tormenta/dashboard` | `tormenta/pages/dashboard.html` |

## Seletor pós-login

`frontend/pages/selecionar-jogo.html` — função `destinoPorSlug()`:

| Slug | Destino (status `disponivel`) |
|------|-------------------------------|
| `dnd35` | `/dashboard` |
| `dnd5e` | `/games/dnd5e/pages/dashboard.html` |
| `tormenta` | `/games/tormenta/pages/dashboard.html` |
| `gurps` | `/games/gurps/pages/dashboard.html` |

## Build D&D 5e — conjuração (TypeScript)

O subpacote `dnd5e/spellcasting/` compila para `dnd5e/js/spellcasting/`. **`node_modules/` não é versionado** — ver [dnd5e/spellcasting/README.md](dnd5e/spellcasting/README.md).

## Matriz requisitos × código

Gerar com: `python3 scripts/generate_requisitos_cobertura_matrix.py` → [docs/requisitos-cobertura-matrix.md](../../docs/requisitos-cobertura-matrix.md).
