# `backend/app/games/gurps/` — GURPS

Backend do sistema **GURPS** na plataforma multi-jogo.

## API (`/api/v1/gurps/...`)

| Prefixo | Descrição |
|--------|-----------|
| `/gurps/personagens` | CRUD da ficha (atributos, vantagens, desvantagens, perícias, totais de pontos). |
| `/gurps/campanhas` | Campanhas (mestre/admin). |
| `/gurps/combate` | Arena: iniciar / status / avançar turno / finalizar (lista de IDs separada do combate D&D 3.5). |

Todas as rotas usam `dependencies=[Depends(requer_game_gurps)]` — com `MULTI_GAME_STRICT_MODE=true`, o JWT deve trazer `game_slug=gurps`.

## Persistência

Migration: `b1a2c3d4e5f6_add_gurps_core_tables.py` — tabelas `gurps_campanhas`, `gurps_personagens`, filhos de lista (`gurps_personagem_*`) e `gurps_combates`.

## Frontend

Páginas em `frontend/games/gurps/pages/` (`dashboard.html`, `ficha-personagem.html`), servidas em `/games/gurps/...`.

## Catálogo

`gurps` está **disponível** no seed em `app/shared/startup/game_catalog.py`. Membership é criado automaticamente com os slugs em `AUTO_ENROLL_MEMBERSHIP_GAME_SLUGS` (`app/shared/constants.py`).
