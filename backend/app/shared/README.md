# `backend/app/shared/`

Pacote do **Auth Hub** + utilitários globais da plataforma.

> Esta pasta existe como **andaime** (scaffold) da reorganização multi-jogo
> descrita em `docs/arquitetura-multi-jogo.md` (Fase 5). Os arquivos
> atualmente continuam em `backend/app/{core,models,schemas,repositories,
> services,api/v1,exceptions}/`. A migração é incremental.

## O que pertence aqui

| Item / subpasta-alvo     | Conteúdo                                                         |
|--------------------------|------------------------------------------------------------------|
| `constants.py` (já)    | Constantes do hub (`GAME_SLUG_DND35`, …) — usado por `deps` e `game_service`. |
| `shared/core/`           | `config.py`, `database.py`, `deps.py`, `security.py`, `security_audit.py`, `rate_limit.py`, `request_size.py`, `catalog_cache.py`, `logging` |
| `shared/models/`         | `usuario.py`, `game.py`, `mixins.py`                             |
| `shared/schemas/`        | `usuario.py`, `game.py`, tokens                                  |
| `shared/repositories/`   | `usuario_repository.py`, `game_repository.py`, `base.py`         |
| `shared/services/`       | `usuario_service.py`, `game_service.py`                          |
| `shared/api/v1/`         | `auth.py`, `usuarios.py`, `games.py`                             |
| `shared/exceptions/`     | `custom_exceptions.py`, `http_errors.py`                         |

## O que NÃO pertence aqui

- Regras de combate, magia, ficha, campanha, equipamento → `games/<slug>/`.
- Catálogos específicos de sistema (D&D 3.5: Tabela 3-7 de divindades,
  truques, etc.) → `games/dnd35/`.

## Convenção de imports (após migração completa)

```python
from ...shared.core.deps import get_usuario_atual
from ...shared.models.usuario import Usuario
from ...shared.services.game_service import GameService
```

Enquanto a migração acontece, ambos os caminhos coexistem. Quando um
módulo for movido, o caminho antigo passa a ser um **shim de
compatibilidade** que re-exporta do novo local, mantido até o último
import legado ser removido.
