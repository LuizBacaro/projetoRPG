# Arquitetura Multi-Jogo com Conta Global

Este documento descreve a arquitetura-alvo da plataforma para suportar múltiplos
sistemas de RPG (D&D 3.5, D&D 5e, GURPS, etc.) com **isolamento total por jogo**
(backend e banco próprios por jogo, futuramente também frontend dedicado) e
**conta global única** (login único, escolha de jogo após autenticar).

As Fases 1–4 já estão implementadas in-place no repositório atual (Auth Hub
embutido + D&D 3.5 atrás de guard + UI admin de memberships). A Fase 5
descreve a operação e a separação física futura em apps independentes.

> **Estado atual (abr/2026):** o backend é um único processo FastAPI que
> hospeda Auth Hub e D&D 3.5 lado a lado, distinguidos pelo claim
> `game_slug` no JWT. O frontend é um único bundle estático com guards
> por página. A separação física em `apps/frontend-shell`,
> `apps/frontend-dnd35` e `apps/game-dnd35/backend` continua planejada,
> mas é independente da entrega funcional multi-jogo.
>
> **Reorganização de pastas (abr/2026):** o D&D 3.5 está sob
> `backend/app/games/dnd35/` e o frontend por jogo em `frontend/games/`
> (ver "Convenção de pastas multi-jogo"). A migração foi feita por ondas;
> **não** existem mais ficheiros-shim por domínio em `app.models.<x>` /
> `app.schemas.<x>` para esse jogo — imports de domínio apontam para
> `app.games.dnd35.models|schemas|...`. O pacote `app.models` agrega
> modelos D&D 3.5 no `__init__.py` (metadata/migrations). O **Auth Hub**
> (usuario, game, auth, routers `/auth`, `/games`, `/usuarios`) vive em
> `app.shared.*` (canónico). Os shims finos em `app/schemas`, `app/api/v1`
> (auth/games/usuarios), `app/repositories/*`, `app/services/*` (hub),
> `app/models/{usuario,game}.py`, `app/seeds/pericias_seed.py`,
> `app/exceptions/custom_exceptions.py` e `app/models/mixins.py` foram
> removidos após `rg`/testes; `app/api/v1/` ficou só com o agregador
> `__init__.py` (router vazio legado). Rotas D&D 3.5 registam-se a partir de
> `app.games.dnd35.api.v1` em `app.main`.

## Visão geral

```mermaid
flowchart LR
    user[Usuário] --> shell[Frontend Shell\n(login + seletor)]
    shell --> authHub[Auth Hub API\n(/api/v1/auth + /api/v1/games)]
    authHub --> authDb[(Auth DB\nusuarios + games_catalog\n+ user_game_memberships)]
    shell --> dnd35fe[Frontend D&D 3.5]
    shell --> dnd5fe[Frontend D&D 5e (futuro)]
    shell --> gurpsfe[Frontend GURPS (futuro)]
    dnd35fe --> dnd35api[Backend D&D 3.5]
    dnd35api --> dnd35db[(DB D&D 3.5)]
    dnd5fe --> dnd5api[Backend D&D 5e (futuro)]
    dnd5api --> dnd5db[(DB D&D 5e)]
    gurpsfe --> gurpsapi[Backend GURPS (futuro)]
    gurpsapi --> gurpsdb[(DB GURPS)]
```

## Componentes da Fase 1 (já no repo)

### Backend

- Tabelas novas:
  - `games_catalog` — catálogo de jogos (`slug`, `nome`, `status`, `icone`, `ordem`).
  - `user_game_memberships` — vínculo usuário ↔ jogo + `perfil_no_jogo`.
- Migration: `a7b9d3e1c2f4_add_games_catalog_and_memberships.py`.
- Modelos: `app/models/game.py` (`Game`, `UserGameMembership`).
- Schemas: `app/schemas/game.py`.
- Repositório: `app/repositories/game_repository.py`.
- Service: `app/services/game_service.py`.
- Rotas: `GET /api/v1/games`, `POST /api/v1/games/selecionar`.
- Seed automático no startup:
  - `inicializar_catalogo_jogos` (`app/shared/startup/game_catalog.py`) —
    popula `dnd35` (disponível) + `dnd5e`/`gurps` (em breve).
  - `garantir_membership_dnd35_para_usuarios_legados`
    (`app/games/dnd35/legacy_membership.py`) — vincula usuários existentes ao
    D&D 3.5 sem precisar reentrar.
- JWT: `POST /games/selecionar` reemite o `access_token` com claim
  `game_slug` e `perfil_no_jogo`. O `decodificar_token` aceita tokens com ou
  sem o claim, mantendo compatibilidade com sessões antigas.
- Dependency `requer_game_dnd35` (modo permissivo) em `core/deps.py` —
  pronto para virar bloqueio rígido na Fase 2.

### Frontend

- Página nova: `pages/selecionar-jogo.html` + `css/selecionar-jogo.css`.
- `pages/login.html` redireciona para `/pages/selecionar-jogo.html` ao logar.
- `js/services/AuthService.js` ganhou:
  - `getGameSlugAtivo()`
  - `exigirJogo(slug)` — guard usado por `dashboard.html`, `arena.html`,
    `ficha-personagem.html`, `usuarios.html`, `magias.html`, `pericias.html`,
    `pericias-ficha.html`.
  - `trocarJogo()` — limpa o `game_slug_ativo` e volta ao seletor preservando
    a sessão.
  - Botão `#btnTrocarJogo` no header do dashboard (auto-instalado por
    `configurarHeaderUsuario`).
- LocalStorage:
  - `token`, `refresh_token`, `usuario` (existentes)
  - `game_slug_ativo` (novo)

### Comportamento atual

1. Usuário faz login → recebe access/refresh tokens **sem** `game_slug`.
2. Frontend redireciona para `/pages/selecionar-jogo.html`.
3. Frontend busca `GET /api/v1/games` (catálogo + memberships do usuário).
4. Usuário escolhe `D&D 3.5` (único disponível na Fase 1).
5. Frontend chama `POST /api/v1/games/selecionar { game_slug: "dnd35" }` →
   recebe novos tokens com `game_slug=dnd35` e salva `game_slug_ativo`.
6. Usuário entra no `/dashboard`. Páginas D&D 3.5 fazem
   `AuthService.exigirJogo('dnd35')` no carregamento.

## Próximas fases

### Fase 2 — Guard bloqueante para D&D 3.5 ✅

- Nova flag `settings.MULTI_GAME_STRICT_MODE` em `app/core/config.py`
  (env: `MULTI_GAME_STRICT_MODE=true`).
- `requer_game_dnd35` em `app/core/deps.py` agora bloqueia em modo estrito:
  - `409 X-Game-Slug-Required: dnd35` quando o token não carrega `game_slug`.
  - `403 X-Game-Slug-Required: dnd35` quando carrega outro jogo.
  - Em modo permissivo (default histórico) só registra warning para tokens
    legados — preserva sessões pré-multi-jogo durante o rollout.
- Guard aplicado nos routers sensíveis ao D&D 3.5 via
  `dependencies=[Depends(requer_game_dnd35)]`:
  `combatentes`, `campanhas`, `combate`, `grimorio`, `magias_preparadas`,
  `ataques`, `armaduras_protecao`, `divindades_custom`.
- Eventos de auditoria emitidos via `log_security_event`:
  `game_slug_required` (token sem claim) e `game_slug_mismatch` (jogo errado).

### Fase 3 — Badge do jogo ativo + interceptor 409/403 ✅

- Badge `#badgeJogoAtivo` (dashboard) e `#badgeJogoAtivoArena` (arena),
  estilizado em `frontend/css/layout.css` (`.badge-jogo`).
- Botão `Trocar jogo` no header — limpa `game_slug_ativo`/`game_nome_ativo`
  e devolve à tela de seletor preservando os tokens de auth.
- `localStorage` ganha `game_nome_ativo` (label visual) e `game_icon_ativo`,
  além do `game_slug_ativo` já existente.
- Monkey-patch global de `window.fetch` em `AuthService.js`:
  qualquer resposta com header `X-Game-Slug-Required` (ou `409` com `detail`
  apontando jogo ausente) chama `AuthService.lidarComJogoAusenteOuTrocado`,
  que limpa o estado de jogo e redireciona ao seletor com toast informativo.

### Fase 4 — Permissões divergentes + UI admin ✅

- `perfil_no_jogo` pode divergir do `perfil_global` do usuário.
  Útil quando o admin global é apenas jogador num jogo específico, ou
  quando o admin do jogo não precisa ser admin global.
- Endpoints admin (apenas `requer_admin` global) em
  `app/api/v1/games.py`:
  - `GET    /api/v1/games/{game_slug}/memberships` — lista todos os acessos.
  - `POST   /api/v1/games/{game_slug}/memberships` — concede acesso
    (`{ usuario_id, perfil_no_jogo?, ativo }`; quando `perfil_no_jogo` é
    nulo, espelha o global).
  - `PATCH  /api/v1/games/{game_slug}/memberships/{id}` — altera
    `perfil_no_jogo` e/ou `ativo`.
  - `DELETE /api/v1/games/{game_slug}/memberships/{id}` — revoga acesso.
- UI admin: seção "Acessos por jogo" em `pages/usuarios.html` com select
  por `game_slug`, tabela com toggle de status e revogação, e modal
  "Conceder acesso" reutilizando o select de usuários globais.
- Auto-enroll em D&D 3.5 continua acontecendo on-demand:
  `GameService.garantir_membership_padrao` é chamado em `GET /api/v1/games`
  e em `POST /api/v1/games/selecionar`, então qualquer conta nova ou legada
  fica vinculada na primeira interação com o catálogo. Não há job batch:
  é idempotente e barato.

### Fase 5 — Operação e deploy

#### 5.A — Operação no monorepo atual (estado vigente)

- **Variáveis de ambiente** (backend / Render):
  - `MULTI_GAME_STRICT_MODE` — `false` durante o rollout, `true` após
    confirmar nos logs que sessões legadas foram drenadas
    (procurar warnings "Acesso a endpoint D&D 3.5 com game_slug=...").
  - `SECRET_KEY` — **mesma** chave para Auth Hub e D&D 3.5. Não rotacionar
    sem invalidar tokens de todos os jogos simultaneamente.
  - `DATABASE_URL` — único Postgres com tabelas `usuarios`,
    `games_catalog`, `user_game_memberships` ao lado das tabelas D&D 3.5
    (`combatentes`, `magias`, etc.). A separação de banco vira a Fase 5.B.
- **Frontend (Vercel)**: nada mudou no `vercel.json`. As rotas
  `/dashboard`, `/arena`, `/pages/*` permanecem servidas pelo bundle
  estático único; o seletor de jogo é apenas mais uma página estática
  (`/pages/selecionar-jogo.html`).
- **Rollout do strict mode** (recomendado em duas janelas):
  1. Deploy do backend com guard aplicado em modo permissivo
     (`MULTI_GAME_STRICT_MODE=false`). Frontend já redireciona ao seletor
     em qualquer 409, então usuários reais que ainda não escolheram jogo
     são corrigidos automaticamente.
  2. Após 24-48h sem warnings de `game_slug` ausente nos logs, virar
     `MULTI_GAME_STRICT_MODE=true`. Tokens antigos passam a ser
     bloqueados explicitamente — frontend continua se recuperando via
     interceptor.
- **Cache busting**: páginas que carregam `AuthService.js` usam
  `?v=YYYYMMDD` (ex.: `?v=20260426b`). Bumpar a query string sempre que
  alterar fluxo de auth ou jogo ativo, para evitar service workers/cache
  de browser segurando versões antigas.
- **Segurança**: as rotas admin (`/games/{slug}/memberships*`) exigem
  `requer_admin` global. Auditadas via `log_security_event`. Em produção,
  manter no mínimo dois admins globais para evitar lockout.

#### 5.B — Observabilidade

- Logs estruturados (já emitidos):
  - `game_slug_required` — token sem claim em endpoint D&D 3.5.
  - `game_slug_mismatch` — token vinculado a outro jogo.
  - Auto-enroll: `GameService.garantir_membership_padrao` registra
    info quando cria membership default.
- Métricas a observar quando virar strict mode:
  - Taxa de `409` em `/api/v1/combatentes`, `/api/v1/campanhas` etc.
    Espera-se zero em regime; spike indica clientes com token cacheado.
  - Taxa de `403` no mesmo conjunto — indica usuário tentando atingir
    endpoint de outro jogo (importante quando D&D 5e entrar).
- Dashboards sugeridos (Datadog ou equivalente):
  - "Multi-jogo: tokens sem game_slug" — `count` de
    `game_slug_required` por hora.
  - "Multi-jogo: tokens cruzados" — `count` de `game_slug_mismatch`.
- **Logs brutos (Render):** filtrar por `game_slug_required`, `game_slug_mismatch` ou texto `X-Game-Slug-Required`; após subir `MULTI_GAME_STRICT_MODE=true`, monitorar picos de **409** nos paths `/api/v1/combatentes`, `/api/v1/campanhas`, `/api/v1/grimorio`, etc.

#### 5.C — Separação física futura (não-bloqueante)

- Cada app deploya independente:
  - Auth Hub: API (`/api/v1/auth`, `/api/v1/usuarios`, `/api/v1/games`)
    + shell estático em domínio canônico.
  - Cada game-service: API + frontend em sub-rota/subdomínio
    (ex.: `arena.../dnd35/*`, `arena.../dnd5e/*`).
- Observabilidade isolada por jogo (services Datadog distintos).
- Estratégia de rollout canário por jogo (D&D 5e libera primeiro para
  cohort fechado sem afetar D&D 3.5).
- Pré-requisito de banco: extrair `usuarios`, `games_catalog`,
  `user_game_memberships` para um schema/banco `auth_db`. Pode ser feito
  com `CREATE SCHEMA auth; ALTER TABLE ... SET SCHEMA auth;` em janela
  curta — os modelos SQLAlchemy passam a apontar para o schema novo via
  `__table_args__ = {"schema": "auth"}`.

## Decisões técnicas-chave

- **Token global compartilhado**: HS256 com mesma `SECRET_KEY` entre Auth Hub
  e cada game-service. Claims: `sub`, `game_slug`, `perfil_no_jogo`, `exp`,
  `type`, `jti`. Após `POST /games/selecionar`, o payload inclui também
  **`profile`**, espelho de `perfil_no_jogo` (vocabulário alinhado a planos
  multi-repo / game-services futuros; o backend continua a usar
  `perfil_no_jogo` como campo canónico em API e BD).
- **Auto-enroll em D&D 3.5**: enquanto for o único jogo disponível, qualquer
  conta nova ou legada é vinculada automaticamente, evitando UX de "sem acesso
  a nenhum jogo" durante a Fase 1.
- **Sem migração destrutiva**: a Fase 1 é aditiva. Não há rename de tabelas
  nem mudança de contrato de auth existente; tokens antigos sem `game_slug`
  continuam aceitos pelo backend e o frontend simplesmente redireciona ao
  seletor para enriquecê-los.
- **Isolamento por jogo**: regra de negócio de cada sistema fica fechada no
  seu service. O Auth Hub só conhece identidade global e mapeamento usuário ↔
  jogo. Tudo que é `Combatente`, `Campanha`, `Magia`, `Ficha`, etc. permanece
  100% no D&D 3.5 e não é compartilhado entre jogos.

## Visão multi-repo (evolução física)

O monólito atual já cumpre as **Fases 1–4** in-place (ver secções acima). A
separação em pastas `apps/auth-hub`, `apps/game-dnd35`, etc. é o **próximo
salto** de deploy (Fase 5), descrito de forma acionável em:

- [apps/README.md](../apps/README.md) — mapa “plano → código hoje” no repositório.
- [packages/README.md](../packages/README.md) — pacotes partilhados opcionais
  (`common-ui`, `common-infra`) reservados para quando existir mais de um
  frontend ou cliente HTTP partilhado.

## Convenção de pastas multi-jogo

A reorganização deixa explícito qual código pertence a cada sistema de RPG.
O domínio D&D 3.5 vive em `games/dnd35/`. O **Auth Hub** e a infra partilhada
(JWT, BD, deps, rate limit, `SoftDeleteMixin`, etc.) estão em **`app/shared/`**;
`app/core/` concentra só DI (`dependencies.py`); o startup importa os passos
canónicos em `main.py` (`shared/startup/`, `games/dnd35/`). Regras e utilitários
D&D 3.5 (BBA, catálogos, `text_utils`, …) estão em **`app/games/dnd35/`**.
Ver `backend/app/shared/README.md`.

### Backend (layout vigente)

```
backend/app/
    main.py                       (monta app; regista routers hub + games/*)
    core/                         dependencies
    models/                       __init__.py agrega modelos D&D 3.5 (metadata/Alembic)
    repositories/                 base.py (+ legado mínimo)
    services/                     file_service e legado mínimo
    api/v1/                       __init__.py (agregador legado; sem routers hub)
    shared/                       Auth Hub: core/, models/, schemas/, api/v1/, …
    games/
        dnd35/                    D&D 3.5 em produção
            models/
            schemas/
            repositories/
            services/
            api/v1/
            catalogs/               (divindades oficiais, raças, talentos, …)
            text_utils.py           (normalização classe/magia D&D 3.5)
            bonus_base_ataque.py    (BBA, resistências base, habilidades especiais)
            sync_progressao_combatentes.py  (backfill BBA/TRs/CA em combatentes)
            seeds/
        dnd5e/                    reservado (em breve)
        gurps/                    reservado (em breve)
```

Alvo de médio prazo (não bloqueante): concentrar Auth Hub sob `app/shared/`
(`core`, `models`, `schemas`, …) como na versão anterior deste doc — hoje
só existe `app/shared/` mínimo; o restante do hub permanece nos paths
históricos acima.

> Hoje, **onze** blocos estão fisicamente migrados em `games/dnd35/`:
>
> 1. **`divindade_custom*`** — 1ª onda (POC).
> 2. **`equipamento*`** (`Equipamento`, `EquipamentoJogador` e o router
>    `/equipamentos`) — 2ª onda.
> 3. **`campanha*`** (`Campanha`, `SessaoCampanha`, repositórios,
>    services e o router `/campanhas`) — 3ª onda.
> 4. **`habilidade_especial*`** (catálogo + schemas + router
>    `/habilidades-especiais`) — 4ª onda. Introduziu a subpasta
>    `games/dnd35/catalogs/`, destinada a loaders de catálogos
>    canônicos do PHB.
> 5. **`raca*`** (catálogo + schemas + router `/racas`) — 5ª onda.
> 6. **`talento*`** (models, schemas, repositórios, service, router
>    `/talentos` e `talentos_catalog_seed`) — 6ª onda.
> 7. **`pericia*`** (models, schemas, repositórios, service, router
>    `/pericias` e seed `app.games.dnd35.seeds.pericias_seed`) — 7ª onda.
> 8. **`tabelas_classes*`** (catálogo `classes_tables_catalog`, schemas,
>    service e router `/tabelas-classes`) — 8ª onda.
> 9. **`magia*`** (models `Magia`/`MagiaClasse`/`MagiaHistorico`, grimório,
>    schemas, repositórios, `MagiaService`/`MagiaImportService`/`GrimorioService`,
>    routers `/magias`, `/grimorio`, `/magias-preparadas`) — 9ª onda.
> 10. **`combate*`** (`Ataque`, `MagiaSlot`, `MagiaPreparada`, `Combate`,
>     `CombateHistorico`, `Condicao`, `CombatenteCondicao`,
>     `ArmaduraProtecao`, repositórios, services, routers `/combate`,
>     `/condicoes`, ataques/slots e `/armaduras_protecao`) — 10ª onda.
> 11. **`combatente*`** (model, schemas, repositório, `CombatenteService` e
>     router `/combatentes`) — 11ª onda (**ficha**, nó central de FKs).
>     `SoftDeleteMixin` está em `app/shared/core/mixins.py`; modelos D&D 3.5
>     importam-no a partir daí (sem shim em `app.models.mixins`).
>
> Próximos passos estruturais sugeridos: **schemas Postgres** (`auth.*`,
> `dnd35.*`), consolidação do hub em `app/shared/`, e eventual redução de
> re-exports em `app.api.v1` quando o registo em `main.py` apontar só para
> `games/dnd35/api/v1`.
>
> **Roteiro detalhado (fases, critérios de saída, riscos):**
> [roteiro-melhorias-arquitetura.md](./roteiro-melhorias-arquitetura.md).

### Frontend

```
frontend/
    pages/                        (legacy: páginas globais + D&D 3.5 misturadas)
    css/                          (legacy: tudo junto)
    js/                           (legacy: services/controllers misturados)
    games/                        Bundle visual por jogo (alvo)
        dnd35/                    Bundle D&D 3.5 (HTML/CSS/JS migrados)
        dnd5e/em-breve.html       Casca visual "em breve"
        gurps/em-breve.html       Casca visual "em breve"
```

> O `selecionar-jogo.html` mapeia cada `slug` para seu destino
> (`destinoPorSlug` para jogos disponíveis e `destinoEmBrevePorSlug`
> para jogos em construção). Cliques em "Em breve" abrem a casca local
> do jogo, dando feedback visual ao usuário e mantendo a pasta de cada
> sistema futuro visível para o desenvolvedor.

### Shims e re-exports ainda relevantes

- **`app.models.__init__.py`** — agrega imports dos modelos D&D 3.5 a partir de
  `app.games.dnd35.models.*` para que `Base.metadata` e o Alembic vejam todas
  as tabelas; **não** substitui ficheiros `app.models.combatente` etc. (esses
  shims por módulo foram removidos).
- **`app.core.*`** — `dependencies.py` (factories FastAPI). Arranque de BD em
  `main.py` (`shared/startup/`, `games/dnd35/`). Configuração, BD, deps de
  plataforma e cache de catálogo preferem **`app.shared.core.*`** em código novo;
  ver `backend/app/shared/README.md`.

### Plano de limpeza / próximos incrementos

1. **Feito (D&D 3.5):** retirar ficheiros-shim `app.models.<domínio>` e
  `app.schemas.<domínio>`; apontar código e testes para `app.games.dnd35.*`.
2. **Feito (hub):** shims de `app/schemas`, `app/api/v1` (hub), repositórios e
   services do hub, `app/models/{usuario,game}.py`, `app/models/mixins.py`,
   `app/seeds/pericias_seed`, `app/exceptions/custom_exceptions` removidos;
   `main` importa modelos hub via `app.shared.models`.
3. **Testes:** `get_db` canónico em `app.shared.core.database.get_db`
   (re-exportado em `app.shared.core.deps`). Os shims finos
   `app.core.{database,config,catalog_cache,deps}` foram removidos; usar só
   `app.shared.core.*` para esse núcleo. Preferir `dependency_overrides` no
   mesmo símbolo que a rota injeta.
4. **Front shell:** páginas globais (`login`, seletor) alinhadas a
   `frontend/js/shared/` (ex.: `render-api-origin-boot.js` e
   `render-api-origin.js` para origem da API em Render).

## Próximas ondas da reorganização (planejadas)

1. **Schemas Postgres (`auth.*`, `dnd35.*`)** — PR isolado, com janela
   de manutenção em prod e backup confirmado. Não foi feito junto com
   a reorganização de pastas porque schemas Postgres não funcionam em
   SQLite local sem ginástica adicional, e misturar os dois mascara
   bugs. Plano técnico (detalhado em
   [`fase-c-adr-schemas-postgres.md`](./fase-c-adr-schemas-postgres.md)):
   - Migration Alembic que faz `CREATE SCHEMA auth; CREATE SCHEMA dnd35;`
     e `ALTER TABLE ... SET SCHEMA ...` para cada tabela.
   - `__table_args__ = {"schema": "..."}` nos models, com switch
     condicional para SQLite (testes/dev) usando `MetaData(schema=None)`
     ou attached database.
   - Atualizar todas as ForeignKeys que cruzam schema
     (`auth.usuarios.id` referenciado por `dnd35.combatentes.usuario_id`).
2. **Onda backend "equipamento"** — ✅ concluída
   (`Equipamento`, `EquipamentoJogador`, router `/equipamentos`).
3. **Onda backend "campanha"** — ✅ concluída
   (`Campanha`, `SessaoCampanha`, repositórios, services e router
   `/campanhas` com guard `requer_game_dnd35` mantido).
4. **Onda backend "habilidades especiais"** — ✅ concluída
   (catálogo + schemas + router `/habilidades-especiais`; criou a
   subpasta `games/dnd35/catalogs/` para loaders de catálogos do PHB).
5. **Onda backend "raça"** — ✅ concluída
   (catálogo + schemas + router `/racas`).
6. **Onda backend "talento"** — ✅ concluída
   (models `Talento`/`TalentoJogador`, schemas, repositórios, service,
   router `/talentos` e `talentos_catalog_seed` em `catalogs/`).
7. **Onda backend "perícia"** — ✅ concluída
   (models `Pericia`/`PericiaClasse`/`PericiaJogador`, schemas,
   repositórios, service, router `/pericias` e
   `app.games.dnd35.seeds.pericias_seed`).
8. **Onda backend "tabelas de classe"** — ✅ concluída
   (`catalogs/classes_tables_catalog`, schemas, `TabelasClassesService`,
   router `/tabelas-classes`; loaders legados em `app.core` podem ainda
   delegar para o catálogo em `games/dnd35` — ver código).
9. **Onda backend "magia"** — ✅ concluída
   (`Magia`/`MagiaClasse`/`MagiaHistorico`, grimório, schemas, repositórios,
   services, routers `/magias`, `/grimorio`, `/magias-preparadas`;
   `MagiaSlot`/`MagiaPreparada` estão em `games/dnd35/models/ataque.py`
   (onda combate), importados de `app.games.dnd35.models.ataque`).
10. **Onda backend "combate"** — ✅ concluída (`combate`,
    `combatente_condicao`, `condicao`, `ataque` incluindo
    `MagiaSlot`/`MagiaPreparada`, `armadura_protecao`; routers
    `/combate`, `/condicoes`, ataques/slots, `/armaduras_protecao`).
11. **Onda backend "ficha"** — ✅ concluída (`Combatente`, repositório,
    service, router `/combatentes`; `SoftDeleteMixin` em
    `app/shared/core/mixins.py`; `app.core.dependencies` expõe
    `get_combate_service`, `get_condicao_service` e `get_usuario_atual`
    para overrides em testes).
12. **Onda frontend D&D 3.5** — ✅ concluída
   (`frontend/games/dnd35/` com `pages/`, `css/`, `js/`, `arena.html`;
   shell global em `frontend/pages/` — login + seletor + stubs de redirect;
   `vercel.json` com rewrites para `/dashboard`, `/arena`, `/pericias`;
   backend monta `/games/dnd35` em `main.py`).

Cada onda nova deve seguir o padrão estabelecido após a POC
`divindades_custom`:
- Implementar domínio em `games/<slug>/...` (models, schemas, services,
  `api/v1`).
- Atualizar `main.py`, `dependencies` e testes para importar só paths
  canónicos do jogo (sem criar ficheiro-shim `app.models.<domínio>`).
- Rodar a suíte de testes do domínio e regressão geral.
- PR pequeno e revisável de forma isolada.

## Pontos de extensão para novos jogos

Para adicionar um novo jogo (ex.: D&D 5e):

1. **Catálogo backend:** inserir entrada em `GAME_CATALOG_SEED`
   (`backend/app/shared/startup/game_catalog.py`) com `status="em_breve"`
   enquanto a stack ainda não estiver pronta.
2. **Casca visual:** criar `frontend/games/<slug>/em-breve.html` +
   `frontend/games/<slug>/css/em-breve.css` com identidade visual
   própria (paleta de cor distinta para o usuário não confundir jogos).
   Adicionar mapeamento no `destinoEmBrevePorSlug()` em
   `frontend/pages/selecionar-jogo.html`.
3. **Pacote backend reservado:** criar `backend/app/games/<slug>/`
   com `__init__.py` e `README.md` (mesmo padrão de
   `backend/app/games/gurps/`) — pasta vazia visualmente sinaliza que
   o jogo é planejado.
4. **Quando a stack estiver pronta:**
   - Replicar a estrutura completa de `backend/app/games/dnd35/`
     (api/v1, core, models, repositories, schemas, services, seeds).
   - Criar guard `requer_game_<slug>` em `backend/app/core/deps.py`
     (espelho de `requer_game_dnd35`).
   - Aplicar `dependencies=[Depends(requer_game_<slug>)]` em todos os
     routers do pacote.
   - Registrar os routers em `backend/app/main.py`.
   - Trocar `status` para `"disponivel"` no catálogo.
   - Substituir a casca em `frontend/games/<slug>/em-breve.html`
     pelas páginas reais e adicionar entrada em `destinoPorSlug()`.

## Resumo

As Fases 1–4 entregam a fundação multi-jogo sem reescrever o repositório:
Auth Hub embutido, seletor de jogo dedicado, D&D 3.5 atrás do guard
`game_slug=dnd35` (modo bloqueante opcional via `MULTI_GAME_STRICT_MODE`),
permissões divergentes por jogo e UI admin para gerenciar memberships.
A Fase 5 cobre operação (rollout, env vars, observabilidade) no monorepo
atual e deixa documentada a separação física futura em apps independentes,
sem mudar o contrato de tokens — garantindo migração incremental e segura.
