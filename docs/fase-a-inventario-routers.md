# Fase A.0 — Inventário: routers `api/v1` (hub vs D&D 3.5)

**Data:** abril de 2026  
**Objetivo:** mapear o que `app.main` monta hoje, de onde vem cada `router` e
qual o **alvo** da Fase A ([roteiro-melhorias-arquitetura.md](./roteiro-melhorias-arquitetura.md)):
registo canónico a partir de `app.games.dnd35.api.v1` (e hub em `app.api.v1`),
reduzindo shims finos sem alterar URLs sob `settings.API_V1_PREFIX` (tipicamente
`/api/v1`).

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
| `grimorio` | `/grimorio` | Re-export `games…grimorio` | Idem |
| `equipamentos` | `/equipamentos` | Re-export `games…equipamentos` | Idem |
| `armaduras_protecao` | `/armaduras_protecao` | Re-export `games…armaduras_protecao` | Idem |
| `talentos` | `/talentos` | Re-export `games…talentos` | Idem |
| `tabelas_classes` | `/tabelas-classes` | Re-export `games…tabelas_classes` | Idem |
| `racas` | `/racas` | Re-export `games…racas` | Idem |
| `habilidades_especiais` | `/habilidades-especiais` | Re-export `games…habilidades_especiais` | Idem |

**Resumo:** 3 módulos são **hub** (`auth`, `games`, `usuarios`). Os outros **16**
são shims de **router** D&D 3.5 (15 com `from app.games.dnd35.api.v1…import router`;
`divindades_custom` usa import relativo equivalente).

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
| `test_grimorio_api.py` | `grimorio` |
| `test_armaduras_protecao_api.py` | `armaduras_protecao` |
| `test_catalog_cache_api.py` | `equipamentos`, `magias`, `pericias` |
| `test_habilidades_especiais_catalog.py` | `habilidades_especiais` |
| `test_racas_api.py` | `racas` |
| `test_tabelas_classes_api.py` | `tabelas_classes` |
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

## Próximo PR após este inventário (Fase A.1)

1. Escolher **um** router D&D 3.5 de baixo risco (ex.: `tabelas_classes` ou
   `racas`) e alterar **só** `main.py` + imports diretos; `pytest` verde.
2. Tratar **`combate`** num PR separado (overrides + `__all__` do shim).
3. Atualizar este doc com data/PR e marcar linhas da tabela como concluídas.
