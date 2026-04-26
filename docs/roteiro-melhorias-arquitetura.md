# Roteiro: melhorias de arquitetura (pós-migração `games/dnd35`)

Este documento **ordena e detalha** os trabalhos opcionais mencionados em
`docs/arquitetura-multi-jogo.md` e em `backend/app/shared/README.md`, depois
de o domínio D&D 3.5 estar canónico em `app.games.dnd35.*` (sem shims por
ficheiro em `app.models.<domínio>` / `app.schemas.<domínio>`).

**Objetivo:** reduzir dívida estrutural, clarificar fronteiras hub ↔ jogo e
preparar evolução para Postgres com schemas e, no futuro, deploy multi-serviço.

**Princípios**

- PRs **pequenos** e reversíveis; evitar misturar **migração destrutiva de BD**
  com refactors enormes de imports na mesma entrega.
- **Regressão:** `pytest tests/ --ignore=tests/e2e` verde antes de merge;
  onde existir job com Postgres, mantê-lo verde após Fase C.
- **Contratos HTTP** (`/api/v1/...`) e **JWT** inalterados salvo decisão
  explícita de versão de API.

---

## Ordem recomendada (dependências)

```text
Fase A (rotas / api.v1)  →  Fase B (hub → app.shared)  →  Fase C (Postgres schemas)
                                                                    ↓
                                                          Fase D (produto / deploy) — paralelo ou depois
```

- **A antes de B:** menos ficheiros a mover quando o hub mudar de pasta;
  `main.py` e testes já refletem a origem canónica dos routers de jogo.
- **B antes de C:** modelos e imports estáveis facilitam aplicar
  `__table_args__ = {"schema": "..."}` e rever ForeignKeys com cabeça fria.
- **D** é majoritariamente independente (frontend, novos jogos, serviços
  separados), mas convém não acoplar a A/B/C na mesma branch.

---

## Fase A — Registo de rotas e `app.api.v1`

**Inventário (A.0):** [fase-a-inventario-routers.md](./fase-a-inventario-routers.md)
— tabela *router → origem hoje → alvo*, comandos `grep`/`rg` e impacto em
`backend/tests/`.

**Problema:** vários módulos em `app/api/v1/` re-exportam o `router` (e por
vezes helpers de DI) definidos em `app/games/dnd35/api/v1/`, o que duplica
superfície e confunde “quem é dono” do router.

**Meta:** `main.py` (e eventualmente `app/api/v1/__init__`) importa routers
de jogo **a partir do pacote canónico**; ficheiros em `app/api/v1/` ficam
só com o que for estritamente hub **ou** um re-export **mínimo** e
documentado para compatibilidade (ex.: overrides de testes).

**Tarefas sugeridas**

1. Inventariar: `rg "from app\.games\.dnd35\.api"` e `rg "games\.dnd35\.api"`
   em `app/api/v1/` e `app/main.py`.
2. Por router D&D 3.5: decidir **registar direto** em `main.py` a partir de
   `app.games.dnd35.api.v1.<módulo>` **vs.** manter um ficheiro fino em
   `app/api/v1/<módulo>.py` que só faz `from app.games... import router`.
3. Rever **testes** que fazem `dependency_overrides` ou patch em símbolos
   importados de `app.api.v1.*` — alinhar ao módulo que a app realmente usa.
4. Correr suíte + smoke OpenAPI (`tests/test_openapi_docs.py` ou equivalente).

**Critérios de saída**

- Nenhum path HTTP removido ou renomeado sem ADR/changelog.
- `pytest tests/ --ignore=tests/e2e` verde.
- Documentação: uma linha em `arquitetura-multi-jogo.md` ou neste roteiro
  a marcar A como “feita” com data/PR.

**Riscos:** patches frágeis em testes; imports circulares se `main` passar a
importar demasiado de `games` antes do hub estar explícito.

---

## Fase B — Consolidação do Auth Hub em `app/shared/`

**Problema:** o hub continua disperso em `app/core`, `app/models`, `app/schemas`,
`app/repositories`, `app/services`, `app/api/v1`; `app/shared/` é ainda
andaime (`constants.py` + README).

**Meta:** tabela em `backend/app/shared/README.md` cumprida — código de
identidade, sessão, jogos e infra partilhada vive sob `app/shared/...`,
com imports de aplicação a apontar para o novo path.

**Tarefas sugeridas (incremental)**

1. Definir **ordem de movimento** (baixo risco → alto):
   - `exceptions/` → `shared/exceptions/`
   - trechos de `core/` pouco acoplados (ex.: `catalog_cache`) se fizer sentido
   - `database`, `config`, `security`, `deps` (núcleo — PR dedicado)
   - `models/usuario`, `models/game`, `schemas`, `repositories`, `services`
   - `api/v1/auth`, `usuarios`, `games`
2. Por cada módulo movido: **re-export** no path antigo
   (`from app.shared.X import Y as Y` ou re-export explícito) até `rg` no
   monorepo zerar referências antigas; só então apagar o ficheiro legado.
3. **Decisão documentada — `app.models.__init__.py`:** hoje agrega modelos
   D&D 3.5 para `Base.metadata` / Alembic. Opções:
   - **Manter:** barrel em `app.models` importa de `games.dnd35.models` (estado
     atual; simples).
   - **Explicitar em `main.py` / `init_db`:** importar side-effect só os
     modelos necessários ao metadata, e afunilar `app.models` ao hub.
   Escolher uma estratégia **antes** da Fase C e registar em ADR curto ou
   neste doc.

**Critérios de saída**

- `rg "from app\.core\.|from app\.models\.usuario"` (ajustar queries) tende
  a zero **para código novo**; legado pode coexistir até último PR da fase.
- Testes e arranque local (`uvicorn`) OK.
- `backend/app/shared/README.md` atualizado com estado “hub migrado” e
  exemplos de import finais.

**Riscos:** import circular (`deps` ↔ `models`); tempo de branch longa —
mitigar com um módulo por PR.

---

## Fase C — Schemas Postgres (`auth`, `dnd35`)

**Problema:** todas as tabelas no `public` (ou schema default); separação
lógica auth vs jogo exige disciplina em código e complica futuro multi-DB.

**Meta:** em **Postgres** (dev/staging/prod), tabelas do hub em `auth` (ou
nome acordado) e tabelas D&D 3.5 em `dnd35`; ForeignKeys e migrations
coerentes.

**Tarefas sugeridas**

1. **ADR / desenho:** nomes de schema, lista de tabelas por bucket, FKs
   cruzadas (`dnd35.combatentes.usuario_id` → `auth.usuarios.id`).
2. **Migration Alembic** (janela planeada): `CREATE SCHEMA`; `ALTER TABLE ...
   SET SCHEMA ...`; dados preservados.
3. **SQLAlchemy:** `__table_args__ = {"schema": "dnd35"}` (e `auth`) nos
   modelos afetados; revisão de **todos** os `ForeignKey("tabela.col")` para
   forma qualificada se necessário.
4. **SQLite (testes locais):** hoje o doc de arquitetura alerta que schemas
   Postgres não espelham SQLite sem cuidado — escolher **uma** estratégia:
   - testes de integração só em CI com Postgres; SQLite para unitários sem
     schema; ou
   - `MetaData` / `__table_args__` condicional ao URL; ou
   - attached databases — documentar a opção escolhida no README do backend.

**Critérios de saída**

- Migration aplicável em staging com checklist (backup, rollback).
- Documentação: secção em `arquitetura-multi-jogo.md` ou runbook com env vars.
- Critério de aceitação de prod: zero erros de FK/schema nos logs após deploy.

**Riscos:** maior da lista — downtime, bugs de FK, divergência SQLite/Postgres.
**Mitigação:** Fase C só depois de A/B estáveis; feature flag ou deploy em
janela; dry-run em cópia da BD.

---

## Fase D — Produto, frontend por jogo e deploy multi-app (opcional)

Referência principal: secção **“Fase 5”** e **“Pontos de extensão”** em
`docs/arquitetura-multi-jogo.md`.

**Exemplos de entregas** (cada uma pode ser épico próprio):

- Casca e rotas dedicadas por jogo no frontend (`frontend/games/<slug>/`).
- Novo `game_slug` no catálogo + pacote `app/games/<slug>/`.
- Repositórios separados por serviço / domínio canónico em subdomínio.
- Observabilidade e secrets por serviço.

**Critério:** alinhado a roadmap de produto, não a “dívida” do monólito atual.

---

## Checklist rápido (por fase)

| Fase | Antes do merge | Após deploy (se aplicável) |
|------|----------------|----------------------------|
| A    | pytest; grep por routers órfãos | Smoke rotas críticas (login, combatentes, campanhas) |
| B    | pytest; grep imports; arranque local | Logs sem `ModuleNotFoundError` |
| C    | pytest + migração em staging | Monitor FK/schema; plano de rollback |
| D    | critério por épico | métricas / UX por jogo |

---

## Ligações

- Visão global: [arquitetura-multi-jogo.md](./arquitetura-multi-jogo.md)
- Andaime do hub: [../backend/app/shared/README.md](../backend/app/shared/README.md)
- D&D 3.5 no repo: [../backend/app/games/dnd35/README.md](../backend/app/games/dnd35/README.md)

---

## Manutenção deste roteiro

Ao concluir uma fase, atualizar este ficheiro (data, PR de referência) ou
arquivar a secção correspondente para não gerar duplicidade com
`arquitetura-multi-jogo.md`.
