# `backend/app/games/dnd5e/` — EM BREVE

Backend do sistema **Dungeons & Dragons 5e**. Reservado.

Status atual: **andaime visual**. Não há código de regras D&D 5e ainda;
a pasta existe para deixar evidente, no repositório, que D&D 5e é um
próximo sistema planejado e onde ele vai morar.

## Quando começar a implementar

1. Marcar `dnd5e` como `disponivel` em `GAME_CATALOG_SEED`
   (`backend/app/core/init_db.py`).
2. Adicionar destino em `destinoPorSlug()` no
   `frontend/pages/selecionar-jogo.html`.
3. Criar guard `requer_game_dnd5e` em `backend/app/core/deps.py`
   (espelho de `requer_game_dnd35`).
4. Replicar a estrutura de `backend/app/games/dnd35/`:
   - `api/v1/` — routers
   - `core/` — deps específicos, parsers
   - `models/`, `repositories/`, `schemas/`, `services/`, `seeds/`
5. Aplicar `dependencies=[Depends(requer_game_dnd5e)]` em todos os
   routers do pacote.
6. Registrar os routers em `app/main.py`.
7. Substituir a casca do frontend (`frontend/games/dnd5e/em-breve.html`)
   pelas páginas reais do jogo.

> Enquanto este pacote estiver vazio, o frontend mostra apenas a página
> "D&D 5e — em breve" para qualquer usuário que selecione esse jogo.
