# `backend/app/shared/`

Pacote do **Auth Hub** e utilitários **realmente transversais** à plataforma
(constantes, convenções). A reorganização multi-jogo está descrita em
`docs/arquitetura-multi-jogo.md`. **Roteiro** das próximas melhorias (rotas,
hub → `shared`, Postgres, produto): `docs/roteiro-melhorias-arquitetura.md`.

## Estado vigente (abr/2026)

- O **código do hub** (config, database, deps, security, `Usuario`, `Game`,
  rotas `auth` / `usuarios` / `games`, etc.) continua majoritariamente nos
  paths históricos: `app/core/`, `app/models/` (com `mixins.py` e `__init__.py`
  que também agrega modelos D&D 3.5 para metadata/Alembic),
  `app/schemas/`, `app/repositories/`, `app/services/`, `app/api/v1/`.
- `app/models/usuario.py` e `app/models/game.py` já são shims; os modelos
  canónicos vivem em `app/shared/models/usuario.py` e
  `app/shared/models/game.py`.
- `app/repositories/usuario_repository.py` e
  `app/repositories/game_repository.py` já são shims; os repositórios canónicos
  vivem em `app/shared/repositories/`.
- `app/services/usuario_service.py` e `app/services/game_service.py` já são
  shims; os services canónicos vivem em `app/shared/services/`.
- `app/api/v1/auth.py`, `app/api/v1/usuarios.py` e `app/api/v1/games.py` já
  são shims; os routers canónicos do hub vivem em `app/shared/api/v1/`.
- **`app/shared/`** já contém `constants.py`, `shared/exceptions/custom_exceptions.py`
  e módulos em `shared/core/` (`catalog_cache.py`, `request_size.py`,
  `rate_limit.py`, `security_audit.py`, `security.py`, `deps.py`) em uso
  pelo backend; os paths legados `app.exceptions.custom_exceptions`,
  `app.core.catalog_cache`, `app.core.request_size`, `app.core.rate_limit`,
  `app.core.security_audit`, `app.core.security` e `app.core.deps` foram
  mantidos como shims.
  O restante da árvore continua em migração incremental.
- **D&D 3.5** vive em `app/games/dnd35/` (`models`, `schemas`, `repositories`,
  `services`, `api/v1`, …). Não há ficheiros-shim por domínio em
  `app.models.combatente` ou `app.schemas.campanha`; imports de domínio
  apontam para `app.games.dnd35.*`. Re-exports finos que ainda fazem sentido:
  `app.models.mixins` → `app.core.mixins`, e alguns `app.api.v1.*` que
  expõem o mesmo `router` definido em `games/dnd35/api/v1`.

## Alvo (após consolidação do hub)

| Item / subpasta-alvo   | Conteúdo |
|------------------------|----------|
| `shared/constants.py` (já) | Constantes do hub (`GAME_SLUG_DND35`, …) — usado por `deps` e `game_service`. |
| `shared/core/`         | `config.py`, `database.py`, `deps.py`, `security.py`, `security_audit.py`, `rate_limit.py`, `request_size.py`, `catalog_cache.py`, logging |
| `shared/models/`       | `usuario.py`, `game.py` (canónicos) + futuro `mixins.py` |
| `shared/schemas/`      | `usuario.py`, `game.py`, contratos de tokens |
| `shared/repositories/` | `usuario_repository.py`, `game_repository.py`, `base.py` |
| `shared/services/`     | `usuario_service.py`, `game_service.py` |
| `shared/api/v1/`       | `auth.py`, `usuarios.py`, `games.py` |
| `shared/exceptions/`   | `custom_exceptions.py`, `http_errors.py` |

## O que NÃO pertence ao hub

- Regras de combate, magia, ficha, campanha, equipamento, etc. →
  `app/games/<slug>/` (hoje: `games/dnd35/`).
- Catálogos de sistema (PHB 3.5, tabelas de classe, …) → `games/dnd35/`
  (`catalogs/`, `seeds/`, …).

## Imports

**Hoje** (preferencial para o que já migrou):

```python
from app.shared.core.deps import get_usuario_atual
from app.shared.models.usuario import Usuario
from app.services.game_service import GameService
```

**Alvo** (quando o módulo tiver sido movido para `app/shared/...`):

```python
from app.shared.core.deps import get_usuario_atual
from app.shared.models.usuario import Usuario
from app.shared.services.game_service import GameService
```

Dentro de `games/dnd35`, o hub costuma ser alcançado com imports relativos
para `app` (ex.: `.....shared.core.deps` a partir de `api/v1/`). Ver exemplos em
`backend/app/games/dnd35/README.md`.

## Migração incremental do hub

Cada pasta movida para `app/shared/...` pode, durante a transição, manter um
re-export mínimo no path antigo (`app.core.*`, `app.models.*`, …) até não
restarem imports ao path legado (`rg` / testes). Isso **não** se aplica ao
padrão antigo de um shim **por domínio de jogo** em `app.models.*` — esse
padrão foi retirado para D&D 3.5 em favor de `app.games.dnd35.*`.
