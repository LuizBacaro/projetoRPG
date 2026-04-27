# Fase A.0 — Inventário: routers `api/v1` (hub vs D&D 3.5)

**Data:** abril de 2026  
**Objetivo:** mapear o que `app.main` monta hoje, de onde vem cada `router` e
qual o **alvo** da Fase A ([roteiro-melhorias-arquitetura.md](./roteiro-melhorias-arquitetura.md)):
registo canónico a partir de `app.games.dnd35.api.v1` (e hub em `app.api.v1`),
reduzindo shims finos sem alterar URLs sob `settings.API_V1_PREFIX` (tipicamente
`/api/v1`).

## Histórico de execução

| Marco | O que foi feito |
|-------|-----------------|
| **A.1** (abr/2026) | `racas` e `tabelas_classes`: `app.main` importa `app.games.dnd35.api.v1.*` diretamente; removidos `app/api/v1/racas.py` e `tabelas_classes.py`; testes apontam para o path canónico. |
| **A.2** (abr/2026) | `habilidades_especiais`, `talentos`, `equipamentos`, `grimorio`: mesmo padrão; removidos os quatro shims em `app/api/v1/`; testes atualizados. |
| **A.3** (abr/2026) | `campanhas`, `combatentes`, `condicoes`, `ataques`: `app.main` importa direto de `app.games.dnd35.api.v1.*`; removidos os quatro shims em `app/api/v1/`; testes de `combatentes` e `condicoes` migrados para path canônico. |
| **A.4** (abr/2026) | `pericias`, `magias`, `divindades_custom`, `magias_preparadas`, `armaduras_protecao`: `app.main` passa a registrar direto de `app.games.dnd35.api.v1.*`; removidos os cinco shims restantes em `app/api/v1/` (fora `combate`). |
| **A.5** (abr/2026) | `combate`: `app.main` registra `app.games.dnd35.api.v1.combate` diretamente; testes migrados para overrides em `app.core.*`; removido `app/api/v1/combate.py`. |

---

**Como reproduzir / atualizar este inventário** (a partir da raiz do repo):

```bash
# Re-exports D&D 3.5 em app/api/v1
grep -R "from app\.games\.dnd35\.api\.v1\|from \.\.\.games\.dnd35\.api" backend/app/api/v1 --include='*.py'

# Onde os testes ainda importam app.api.v1.* (impacto ao mudar main/tests)
grep -R "from app\.api\.v1\." backend/tests --include='*.py'

# Routers incluídos em main (lista de controlos)
grep "include_router" backend/app/main.py
```

Com `ripgrep` instalado:

```bash
rg "from app\.games\.dnd35\.api\.v1|from \.\.\.games\.dnd35\.api" backend/app/api/v1 -g '*.py'
rg "from app\.api\.v1\." backend/tests -g '*.py'
rg "include_router" backend/app/main.py
```

---

## Tabela: módulo em `main` → origem → alvo

Colunas:

- **Módulo:** pacote importado em `app/main.py` (`from .api.v1 import …`).
- **Prefixo HTTP:** `prefix=` do `APIRouter` canónico (D&D 3.5) ou nota; sempre montado com `settings.API_V1_PREFIX` no `include_router`.
- **Origem hoje:** onde está o `router` que `main` usa.
- **Alvo Fase A (sugerido):** onde o registo deveria passar a “pensar” primeiro; shims só se houver justificação (testes, compat).

| Módulo (`app.api.v1`) | Prefixo HTTP (router canónico) | Origem hoje | Alvo Fase A (sugerido) |
|----------------------|----------------------------------|-------------|-------------------------|
| `auth` | `/auth` (tags em `auth.py`) | `app.api.v1.auth` — router definido no hub | Manter `app.api.v1.auth` (hub; futuro `app.shared.api.v1.auth`) |
| `games` | `/games` (+ sub-rotas) | `app.api.v1.games` — hub | Manter `app.api.v1.games` |
| `usuarios` | `/usuarios` | `app.api.v1.usuarios` — hub | Manter `app.api.v1.usuarios` |
| `campanhas` | `/campanhas` | ~~Shim~~ → **`app.main` / `games.dnd35.api.v1.campanhas`** (A.3) | Manter (feito) |
| `combatentes` | `/combatentes` | ~~Shim~~ → **`app.main` / `games.dnd35.api.v1.combatentes`** (A.3) | Manter (feito) |
| `combate` | `/combate` | ~~Shim especial~~ → **`app.main` / `games.dnd35.api.v1.combate`** (A.5) | Manter (feito) |
| `condicoes` | `/condicoes` | ~~Shim~~ → **`app.main` / `games.dnd35.api.v1.condicoes`** (A.3) | Manter (feito) |
| `ataques` | `""` (rotas com path completo, ex. `/combatentes/{id}/ataques`) | ~~Shim~~ → **`app.main` / `games.dnd35.api.v1.ataques`** (A.3) | Manter (feito) |
| `pericias` | `/pericias` | ~~Shim~~ → **`app.main` / `games.dnd35.api.v1.pericias`** (A.4) | Manter (feito) |
| `magias` | `/magias` | ~~Shim~~ → **`app.main` / `games.dnd35.api.v1.magias`** (A.4) | Manter (feito) |
| `divindades_custom` | `/divindades` (router canónico; rotas em `/custom`) | ~~Shim~~ → **`app.main` / `games.dnd35.api.v1.divindades_custom`** (A.4) | Manter (feito) |
| `magias_preparadas` | `/magias-preparadas` | ~~Shim~~ → **`app.main` / `games.dnd35.api.v1.magias_preparadas`** (A.4) | Manter (feito) |
| `grimorio` | `/grimorio` | ~~Shim~~ → **`app.main` / `games.dnd35.api.v1.grimorio`** (A.2) | Manter (feito) |
| `equipamentos` | `/equipamentos` | ~~Shim~~ → **`app.main` / `games.dnd35.api.v1.equipamentos`** (A.2) | Manter (feito) |
| `armaduras_protecao` | `/armaduras_protecao` | ~~Shim~~ → **`app.main` / `games.dnd35.api.v1.armaduras_protecao`** (A.4) | Manter (feito) |
| `talentos` | `/talentos` | ~~Shim~~ → **`app.main` / `games.dnd35.api.v1.talentos`** (A.2) | Manter (feito) |
| `tabelas_classes` | `/tabelas-classes` | ~~Shim `app.api.v1`~~ → **`app.main` importa `games.dnd35.api.v1.tabelas_classes`** (A.1) | Manter (feito) |
| `racas` | `/racas` | ~~Shim `app.api.v1`~~ → **`app.main` importa `games.dnd35.api.v1.racas`** (A.1) | Manter (feito) |
| `habilidades_especiais` | `/habilidades-especiais` | ~~Shim~~ → **`app.main` / `games.dnd35.api.v1.habilidades_especiais`** (A.2) | Manter (feito) |

**Resumo:** a Fase A foi concluída. Em `app/api/v1` restam apenas módulos
do **hub** (`auth`, `games`, `usuarios`) e o agregador legado `__init__.py`.
Todos os routers D&D 3.5 são registados a partir de
`app.games.dnd35.api.v1` em `app.main`.

---

## Impacto em testes (`backend/tests`)

Ficheiros que importam `app.api.v1.*` (abril/2026):

| Ficheiro de teste | Importa |
|-------------------|---------|
| `test_auth_api.py` | `app.api.v1.auth` |
| `test_games_multi_api.py` | `auth`, `games` |
| `test_usuarios_api.py` | `usuarios` |
| `test_combatentes_api.py` | `app.games.dnd35.api.v1.combatentes` (desde A.3) |
| `test_combate_api_history.py` | `router` em `app.games.dnd35.api.v1.combate`; overrides em `app.core.*` (desde A.5) |
| `test_combate_api_avancar_turno.py` | `router` em `app.games.dnd35.api.v1.combate`; overrides em `app.core.*` (desde A.5) |
| `test_condicoes_api.py` | `app.games.dnd35.api.v1.condicoes` (desde A.3) |
| `test_magias_api.py`, `test_magias_import_api.py`, `test_magias_historico_api.py`, `test_divindades_custom_api.py` | `app.games.dnd35.api.v1.magias` (desde A.4) |
| `test_magias_preparadas_api.py` | `app.games.dnd35.api.v1.magias_preparadas` (desde A.4) |
| `test_grimorio_api.py` | `app.games.dnd35.api.v1.grimorio` (desde A.2) |
| `test_armaduras_protecao_api.py` | `app.games.dnd35.api.v1.armaduras_protecao` (desde A.4) |
| `test_catalog_cache_api.py` | `equipamentos` (A.2), `magias` e `pericias` em `app.games.dnd35.api.v1.*` (A.4) |
| `test_habilidades_especiais_catalog.py` | `app.games.dnd35.api.v1.habilidades_especiais` (desde A.2) |
| `test_racas_api.py` | `app.games.dnd35.api.v1.racas` (desde A.1) |
| `test_tabelas_classes_api.py` | `app.games.dnd35.api.v1.tabelas_classes` (desde A.1) |
| `test_divindades_custom_api.py` | `app.games.dnd35.api.v1.divindades_custom` (desde A.4) |

**Nota:** migrar `main.py` para importar só `app.games.dnd35.api.v1` **não**
obriga a mudar estes testes **se** os routers forem semanticamente os mesmos
objetos; obriga se os testes passarem a montar a app a partir de módulos
diferentes ou se os overrides apontarem para símbolos só expostos no shim
(caso **`combate`**).

---

## Agregador legado `app/api/v1/__init__.py`

[`backend/app/api/v1/__init__.py`](../backend/app/api/v1/__init__.py) define
`api_router` está vazio — **não** é o caminho usado por `app.main`
(que importa cada módulo diretamente). Pode ser removido quando o legado
`app.api.v1.__init__` deixar de ser necessário.

---

## Próximo passo (pós-Fase A)

1. Opcional: remover `app/api/v1/__init__.py` (agregador legado) quando não
   houver mais consumidores internos desse módulo.
2. Avançar para Fase B (`app/shared`) conforme `docs/roteiro-melhorias-arquitetura.md`.
