# `frontend/games/`

Cada subpasta aqui é um sistema de RPG suportado pela plataforma, com
seu próprio bundle visual: páginas, CSS e JS.

Convenção de slugs (deve casar com `games_catalog.slug` no backend):

- `dnd35/` — Dungeons & Dragons 3.5 (em produção)
- `dnd5e/` — Dungeons & Dragons 5e (em breve)
- `gurps/` — GURPS (em breve)

## Estrutura-alvo de cada jogo

```
frontend/games/<slug>/
    pages/        # HTMLs específicos do jogo (dashboard, ficha, arena, etc.)
    css/          # estilos próprios do jogo
    js/
        services/    # clientes HTTP do backend daquele jogo
        controllers/ # orquestração de UI
```

## Estado atual

- `dnd35/` — bundle em uso: `arena.html`, `pages/` (dashboard, perícias,
  ficha, magias, …), `js/` e `css/`. O `vercel.json` na raiz do repo
  reescreve `/dashboard`, `/arena` e `/pericias` para estes arquivos.
  O shell (`login`, seletor) em `frontend/pages/` também importa assets
  deste pacote (`/games/dnd35/css/...`, `.../js/config/...`). As páginas
  **em breve** (`dnd5e/`, `gurps/`) reutilizam o mesmo
  `/games/dnd35/js/ui/toast.module.js`.
- `dnd5e/em-breve.html` — página de placeholder com identidade visual
  D&D 5e ("Em breve").
- `gurps/em-breve.html` — página de placeholder com identidade visual
  GURPS ("Em breve").

## Como o seletor entra aqui

`pages/selecionar-jogo.html` mapeia cada `slug` ao destino:

| Slug    | Status      | Destino                                |
|---------|-------------|----------------------------------------|
| dnd35   | disponivel  | `/dashboard` (frontend D&D 3.5)        |
| dnd5e   | em_breve    | `/games/dnd5e/em-breve.html`           |
| gurps   | em_breve    | `/games/gurps/em-breve.html`           |

Quando um jogo "em breve" entrar em produção, o destino passa a ser a
`pages/dashboard.html` daquele pacote e o status no catálogo do
backend muda para `disponivel`.
