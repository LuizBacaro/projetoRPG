# `backend/app/shared/`

Pacote do **Auth Hub** e utilitários **realmente transversais** à plataforma
(constantes, convenções). A reorganização multi-jogo está descrita em
`docs/arquitetura-multi-jogo.md`. **Roteiro** das próximas melhorias (rotas,
hub → `shared`, Postgres, produto): `docs/roteiro-melhorias-arquitetura.md`.

## Estado vigente (abr/2026)

- O **código do hub** está canônico em `app/shared/` (`core`, `models`,
  `schemas`, `repositories`, `services`, `api/v1`, `exceptions`).
- Os shims duplicados do hub em `app/schemas/*`, `app/api/v1/{auth,games,usuarios}.py`,
  `app/repositories/{game,usuario}_repository.py`, `app/services/{game,usuario}_service.py`,
  `app/models/{usuario,game}.py`, `app/models/mixins.py`, `app/seeds/pericias_seed.py`
  e `app/exceptions/custom_exceptions.py` foram **removidos**; o pacote vazio
  `app/exceptions/` foi retirado (confirmado com `rg` + testes).
- `app/api/v1/` contém apenas `__init__.py` (agregador legado); `app.main` importa
  o hub de `app.shared.api.v1` e regista modelos hub via `app.shared.models` quando
  necessário.
- **`app.shared.core.*`** é o import canónico para config, BD, deps de plataforma,
  segurança, cache de catálogo, rate limit e request size. Os re-exports finos
  `app.core.{config,database,catalog_cache,deps}` foram removidos; **`app.core`**
  mantém `dependencies.py`. O startup da API importa seeds em `main.py` a partir
  de `shared/startup/` e `games/dnd35/`.
  Segurança JWT, auditoria, rate limit e limite de payload estão só em
  `app.shared.core.{security,security_audit,rate_limit,request_size}`.
- **D&D 3.5** vive em `app/games/dnd35/`. Não há shims por domínio em
  `app.models.*` / `app.schemas.*` para o jogo; imports de domínio apontam para
  `app.games.dnd35.*`. `SoftDeleteMixin` importa-se de **`app.shared.core.mixins`**.

## Alvo (após consolidação do hub)

| Item / subpasta-alvo   | Conteúdo |
|------------------------|----------|
| `shared/constants.py` (já) | Constantes do hub (`GAME_SLUG_DND35`, …) — usado por `deps` e `game_service`. |
| `shared/core/`         | `config.py`, `database.py`, `deps.py`, `security.py`, `security_audit.py`, `rate_limit.py`, `request_size.py`, `catalog_cache.py`, `mixins.py`, logging |
| `shared/models/`       | `usuario.py`, `game.py` (canónicos) |
| `shared/schemas/`      | `usuario.py`, `game.py`, contratos de tokens |
| `shared/repositories/` | `usuario_repository.py`, `game_repository.py`, `base.py` |
| `shared/services/`     | `usuario_service.py`, `game_service.py` |
| `shared/api/v1/`       | `auth.py`, `usuarios.py`, `games.py` |
| `shared/startup/`      | `game_catalog.py`, `admin_default.py` (arranque de BD / admin; testes em `backend/tests/test_admin_default.py`) |
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
from app.shared.services.game_service import GameService
```

Dentro de `games/dnd35`, o hub costuma ser alcançado com imports relativos até
`app` e depois `shared` (ex.: `.....shared.core.deps` a partir de `api/v1/`).
Ver exemplos em `backend/app/games/dnd35/README.md`.

## Migração incremental do hub

Cada pasta movida para `app/shared/...` pode, durante a transição, manter um
re-export mínimo no path antigo (`app.core.*`, `app.models.*`, …) até não
restarem imports ao path legado (`rg` / testes). Isso **não** se aplica ao
padrão antigo de um shim **por domínio de jogo** em `app.models.*` — esse
padrão foi retirado para D&D 3.5 em favor de `app.games.dnd35.*`.

### Inventário rápido (próxima limpeza)

**Conteúdo atual de `backend/app/core/`** (abr/2026):

| Ficheiro | Papel |
|----------|--------|
| `dependencies.py` | Factories FastAPI (repositórios, services D&D 3.5 + hub) |

BBA, resistências de salvamento base e habilidades especiais por nível:
**`app.games.dnd35.bonus_base_ataque`**. Catálogos D&D 3.5 em
**`app.games.dnd35.catalogs`**. Normalização de texto (classes/magias):
**`app.games.dnd35.text_utils`**. **`SoftDeleteMixin`**: **`app.shared.core.mixins`**.

Na raiz do repo, com `rg` instalado:

```bash
rg 'from app\.core\.' backend -g '*.py'
rg 'app\.core\.(security|rate_limit|request_size|security_audit)' backend -g '*.py'
```

A segunda linha deve continuar vazia. Objetivo incremental: reduzir a primeira
sem mexer em `dependencies.py` até eventual refator maior.

### `app.core.dependencies` (porque ainda não mudou de pasta)

- É o **único agregador de factories** `Depends(...)` para FastAPI: repositórios e
  services do hub **e** de D&D 3.5 num único módulo importável por rotas.
- Mover para `app.shared` implica repartir ou duplicar factories “só de jogo” vs
  “só de hub”, revisar **dezenas** de routers e todos os
  `dependency_overrides` nos testes — PR de alto risco.
- **Convenção:** em rotas novas, importar de `app.core.dependencies` (caminho
  estável) até existir ADR para `app.shared.dependencies` ou pacote por jogo.
