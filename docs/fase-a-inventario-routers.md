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
| `campanhas` | `/campanhas` | Re-export: `app.games.dnd35.api.v1.campanhas.router` | `main` importa `app.games.dnd35.api.v1.campanhas` (ou mantém shim fino documentado) |
| `combatentes` | `/combatentes` | Re-export: `app.games.dnd35.api.v1.combatentes.router` | Idem |
| `combate` | `/combate` | Re-export **+** `get_combate_service`, `get_condicao_service`, `get_usuario_atual` de `app.core.*` ([combate.py](../backend/app/api/v1/combate.py)) | Caso especial: testes fazem `from app.api.v1.combate import get_*`; alinhar overrides a `app.core.dependencies` / `app.core.deps` **ou** manter shim documentado até migrar testes |
| `condicoes` | `/condicoes` | Re-export `games…condicoes` | Idem campanhas |
| `ataques` | `""` (rotas com path completo, ex. `/combatentes/{id}/ataques`) | Re-export `games…ataques` | Idem |
| `pericias` | `/pericias` | Re-export `games…pericias` | Idem |
| `magias` | `/magias` | Re-export `games…magias` | Idem |
| `divindades_custom` | `/divindades` (router canónico; rotas em `/custom`) | Re-export relativo `from ...games.dnd35.api.v1.divindades_custom import router` | Idem; alinhar estilo de import ao resto (`from app.games…`) se se remover o shim |
| `magias_preparadas` | `/magias-preparadas` | Re-export `games…magias_preparadas` | Idem |
| `grimorio` | `/grimorio` | ~~Shim~~ → **`app.main` / `games.dnd35.api.v1.grimorio`** (A.2) | Manter (feito) |
| `equipamentos` | `/equipamentos` | ~~Shim~~ → **`app.main` / `games.dnd35.api.v1.equipamentos`** (A.2) | Manter (feito) |
| `armaduras_protecao` | `/armaduras_protecao` | Re-export `games…armaduras_protecao` | Idem |
| `talentos` | `/talentos` | ~~Shim~~ → **`app.main` / `games.dnd35.api.v1.talentos`** (A.2) | Manter (feito) |
| `tabelas_classes` | `/tabelas-classes` | ~~Shim `app.api.v1`~~ → **`app.main` importa `games.dnd35.api.v1.tabelas_classes`** (A.1) | Manter (feito) |
| `racas` | `/racas` | ~~Shim `app.api.v1`~~ → **`app.main` importa `games.dnd35.api.v1.racas`** (A.1) | Manter (feito) |
| `habilidades_especiais` | `/habilidades-especiais` | ~~Shim~~ → **`app.main` / `games.dnd35.api.v1.habilidades_especiais`** (A.2) | Manter (feito) |

**Resumo:** 3 módulos são **hub** (`auth`, `games`, `usuarios`). Restam **10**
módulos `app.api.v1.*` para D&D 3.5: **9** re-exportam só o `router` canónico
(`divindades_custom` usa import relativo equivalente); **`combate`**
re-exporta também `get_combate_service`, `get_condicao_service` e
`get_usuario_atual` para testes. **A.1 + A.2:** oito routers passaram a ser
registados só a partir de `app.games.dnd35.api.v1` em `app.main` (sem shim
correspondente em `app.api.v1`).

---

## Impacto em testes (`backend/tests`)

Ficheiros que importam `app.api.v1.*` (abril/2026):

| Ficheiro de teste | Importa |
|-------------------|---------|
| `test_auth_api.py` | `app.api.v1.auth` |
| `test_games_multi_api.py` | `auth`, `games` |
| `test_usuarios_api.py` | `usuarios` |
| `test_combatentes_api.py` | `combatentes` |
| `test_combate_api_history.py` | `combate` (+ `get_combate_service`, `get_usuario_atual`) |
| `test_combate_api_avancar_turno.py` | `combate` (+ `get_combate_service`, `get_condicao_service`, `get_usuario_atual`) |
| `test_condicoes_api.py` | `condicoes` |
| `test_magias_api.py`, `test_magias_import_api.py`, `test_magias_historico_api.py`, `test_divindades_custom_api.py` | `magias` |
| `test_magias_preparadas_api.py` | `magias_preparadas` |
| `test_grimorio_api.py` | `app.games.dnd35.api.v1.grimorio` (desde A.2) |
| `test_armaduras_protecao_api.py` | `armaduras_protecao` |
| `test_catalog_cache_api.py` | `app.games.dnd35.api.v1.equipamentos` (A.2), `magias`, `pericias` |
| `test_habilidades_especiais_catalog.py` | `app.games.dnd35.api.v1.habilidades_especiais` (desde A.2) |
| `test_racas_api.py` | `app.games.dnd35.api.v1.racas` (desde A.1) |
| `test_tabelas_classes_api.py` | `app.games.dnd35.api.v1.tabelas_classes` (desde A.1) |
| `test_divindades_custom_api.py` | `divindades_custom` |

**Nota:** migrar `main.py` para importar só `app.games.dnd35.api.v1` **não**
obriga a mudar estes testes **se** os routers forem semanticamente os mesmos
objetos; obriga se os testes passarem a montar a app a partir de módulos
diferentes ou se os overrides apontarem para símbolos só expostos no shim
(caso **`combate`**).

---

## Agregador legado `app/api/v1/__init__.py`

[`backend/app/api/v1/__init__.py`](../backend/app/api/v1/__init__.py) define
`api_router` e inclui apenas `combatentes` e `combate` — **não** é o caminho
usado por `app.main` (que importa cada módulo diretamente). Alvo futuro:
alinhá-lo ao padrão de `main` ou documentá-lo como legado / a remover.

---

## Próximo passo (Fase A.3 em diante)

1. Repetir o padrão para os **nove** restantes só com re-export de `router`:
   `campanhas`, `combatentes`, `condicoes`, `ataques`, `pericias`, `magias`,
   `divindades_custom`, `magias_preparadas`, `armaduras_protecao` (e migrar
   `magias`/`pericias` em `test_catalog_cache_api.py` no mesmo PR que os
   respetivos shims).
2. Tratar **`combate`** num PR **separado** (overrides em testes + `__all__`
   do shim que re-exporta `get_*`).
3. Ir atualizando a tabela acima e o bloco “Impacto em testes” conforme os
   imports migram.
