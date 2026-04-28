# 🛡️ Plano de Melhorias — Arena de Combate RPG

> Arquivo gerado em 29/03/2026 após análise completa do projeto.  
> Itens organizados por severidade. Marcar com `[x]` conforme forem resolvidos.

---

## 🔴 CRÍTICO (Segurança)

- [x] **#1 — Credenciais de Admin e SECRET_KEY Hardcoded**
  - `backend/app/core/config.py` — Defaults removidos, validação por ambiente
  - SECRET_KEY gerada automaticamente em dev, obrigatória em prod
  - `.env.example` atualizado com todos os campos documentados

- [x] **#2 — Inconsistência de Token (sessionStorage vs localStorage)**
  - Unificado para `localStorage` com chave `token` em todo o projeto
  - AuthService, login.html, pericias-auth.js e todos os services alinhados

- [x] **#3 — CORS com Wildcard + allow_credentials**
  - `backend/app/main.py` — Origens agora vêm do `.env` (ALLOWED_ORIGINS)
  - `allow_credentials` desabilitado automaticamente se wildcard detectado

- [x] **#4 — XSS via innerHTML sem sanitização**
  - Criado `escapeHtml()` em `formatters.js` (export + window global)
  - Aplicado em: FichaPersonagemController, GrimorioController, ArenaController, ArenaView, OrdemIniciativa, ModalDanoCura, DashboardController
  - Backend: `_strip_html()` validator nos schemas Pydantic de Combatente

- [x] **#5 — Upload de Arquivos sem Validação de MIME Type**
  - `backend/app/services/file_service.py` — Validação por magic bytes adicionada
  - Verificação de tamanho máximo implementada
  - Path traversal bloqueado no `deletar_arquivo()` com validação de diretório

---

## 🟡 IMPORTANTE (Arquitetura / Backend)

- [x] **#6 — Padrões de Export Inconsistentes no Frontend**
  - `NotificationService.js` — Corrigido: adicionado `window.NotificationService` bridge + carregado como `type="module"` em ficha-personagem.html
  - `CombateService.js` — Removido (duplicata morta de CondicaoService, nunca importado)
  - `api.config.module.js` — URL hardcoded corrigida para `window.location.origin`
  - Padrão híbrido (export + window global) documentado como bridge aceito

- [x] **#7 — Rotas sem Autenticação**
  - Corrigido bug em `auth.py` `/me` — usava `Depends(get_db)` em vez de `Depends(get_usuario_atual)`
  - Removido dummy `get_current_user` (try/except fallback) de `pericias.py` e `equipamentos.py`
  - Adicionado `Depends(get_usuario_atual)` em: `combatentes.py` (11), `combate.py` (6), `condicoes.py` (6), `ataques.py` (5), `magias_preparadas.py` (5), `talentos.py` (5), `pericias.py` (11), `equipamentos.py` (7)
  - Rotas sensíveis de domínio protegidas; públicas intencionais: autenticação e catálogo de magias (read-only)

- [x] **#8 — Sem Rate Limiting**
  - Implementado middleware custom em `app/shared/core/rate_limit.py` (sliding window por IP)
  - Limite geral na API: `API_RATE_LIMIT_PER_MINUTE` (default 180/min)
  - Limite específico para `POST /api/v1/auth/login`: `LOGIN_RATE_LIMIT_PER_MINUTE` (default 10/min)
  - Retorna `429` com `Retry-After`, `X-RateLimit-Limit`, `X-RateLimit-Remaining`
  - Configurável via `app/shared/core/config.py` (`RATE_LIMIT_ENABLED`, limites por minuto)

- [x] **#9 — JWT sem Refresh Endpoint**
  - Implementado `POST /auth/refresh` em `auth.py`
  - `login` agora retorna `access_token` + `refresh_token`
  - Refresh valida `type=refresh` e emite novo par de tokens (rotation)
  - Expiração configurável via `REFRESH_TOKEN_EXPIRE_DAYS` em `config.py`

- [x] **#10 — Sem Verificação de Propriedade (RBAC)**
  - Adicionado ownership em `combatentes` com coluna `dono_id` + migration Alembic
  - Criadas dependências `requer_dono_ou_admin_combatente` e `requer_dono_ou_admin_slot_magia` em `app/shared/core/deps.py`
  - Rotas por `combatente_id` agora validam dono/admin (combatentes, ataques, condições, perícias do jogador, equipamentos do jogador, talentos do jogador, magias preparadas)
  - `listar_combatentes` agora respeita escopo do usuário (admin vê todos; demais veem apenas os próprios)
  - `combate/iniciar` e `combate/aplicar-dano` validam propriedade para listas/IDs de combatente

- [x] **#11 — URL da API Hardcoded no Frontend**
  - `api.config.js` — `BASE_URL` alterado para `window.location.origin`
  - `api.config.module.js` — Idem
  - `dashboard.html` — `getApiUrl` inline corrigido
  - Todas as referências `127.0.0.1:8000` / `localhost:8000` eliminadas

- [x] **#12 — Sem Rollback de Transações**
  - Criado helper transacional `commit_with_rollback()` em `repositories/base.py`
  - Aplicado em repositories e services que faziam `commit()` direto
  - `AtaqueRepository.substituir_todos` e `substituir_magias` agora são atômicos (delete+insert em uma única transação)
  - `CombatenteService` e `PericiaService` migrados para fluxo com rollback automático em caso de falha

- [x] **#13 — Constraints de Banco Faltando**
  - `Combatente` agora possui check constraints de integridade (`hp_atual >= 0`, `hp_maximo > 0`, `hp_atual <= hp_maximo`, `tipo` em `jogador|monstro|npc`)
  - `MagiaPreparada` agora possui unique constraint para (`combatente_id`, `magia_id`)
  - Startup guard em `main.py` normaliza dados legados e remove duplicatas antes de criar índice único
  - Migration Alembic adicionada para formalizar as constraints (`c1b7e4d2a9f0_add_data_constraints.py`)

- [x] **#14 — Potencial N+1 Queries**
  - `PericiaService.obter_custos_pericias()` criado para buscar custo por classe em lote e evitar consulta por item nos endpoints de listagem
  - `listar_pericias_combatente()` agora usa eager loading de `PericiaJogador.pericia`, evitando N+1 na serialização de perícias do jogador
  - `api/v1/pericias.py` deixou de recalcular custo com query individual em loops de listagem

- [x] **#15 — Sem Paginação nas Listas**
  - `/magias`, `/combatentes` e `/usuarios` agora aceitam `skip/limit`, com teto de página e metadados de paginação
  - `/magias` e `/combatentes` expõem `X-Total-Count`, `X-Skip` e `X-Limit` nos headers sem quebrar o formato atual de resposta
  - `/usuarios` passou a retornar `total`, `skip` e `limit` corretos no envelope de resposta, sem depender do tamanho da página atual
  - Frontend de grimório/magias atualizado para usar `limit=500` também no fallback de listagem completa

- [x] **#16 — Sem Logging de Segurança**
  - Criado helper central `app/shared/core/security_audit.py` para logs estruturados de segurança com IP, ator, alvo e motivo
  - Fluxos de `login`, `refresh`, token ausente/inválido e negações RBAC agora emitem eventos auditáveis
  - Ações administrativas em `/usuarios` (criar, atualizar, inativar) agora deixam trilha de auditoria em log

- [x] **#17 — CSS Duplicado (pericias_backup.css)**
  - `pericias_backup.css` removido — não era referenciado em nenhum HTML

- [x] **#18 — Dependency Injection Inconsistente**
  - `core/dependencies.py` deixou de usar `db=None` e `next(get_db())`; factories agora usam `Depends(get_db)` de forma consistente
  - Rotas de combate, combatentes e condições passaram a receber services por injeção em vez de instanciá-los manualmente

- [x] **#19 — Sem Limite de Tamanho no Input**
  - Criado `RequestSizeLimitMiddleware` com limites distintos para request total e corpo JSON
  - Schemas e formulários mais expostos (`usuario`, `magia`, `pericia`, `equipamento`, `talento`, `auth`, `combatente`) agora têm `max_length`/limites explícitos

- [x] **#20 — Startup sem Error Handling**
  - Startup agora executa etapas com `_executar_passo_startup()` e falha explicitamente com contexto da etapa que quebrou
  - `seed_condicoes` deixou de engolir exceções e passa a abortar a inicialização quando falha

---

## 🟢 BOM TER (Qualidade / UX)

- [x] **#21 — Sem Soft Delete / Audit Trail**
  - `deleted_at` adicionado para combatentes, perícias, equipamentos e talentos; exclusões principais agora são soft delete

- [x] **#22 — `.env.example` Faltando**
  - `backend/.env.example` atualizado com todas as variáveis de configuração ativas (projeto, segurança, banco, CORS, upload e rate limit)

- [x] **#23 — Cobertura de Testes ~15%**
  - Cobertura ampliada com testes de autenticação (`login`, `refresh`, `me`) e upload (`FileService`) em cenários de sucesso e falha
  - Suíte de backend agora inclui testes de paginação, segurança, soft delete, DI, auth e upload

- [x] **#24 — Swagger sem Customização**
  - OpenAPI agora documenta `JWTBearer` e exige Bearer token nas rotas protegidas
  - Endpoints de autenticação ganharam exemplos explícitos de request/response e respostas de erro no Swagger

- [x] **#25 — Sem Retry/Circuit Breaker no Frontend**
  - `fetch` global agora passa por camada de resiliência com retry exponencial (requisições idempotentes) e circuit breaker para falhas repetidas de rede/5xx
  - Eventos `api:circuit-open` e `api:circuit-close` expostos para UI reagir a indisponibilidade da API

- [x] **#26 — Lógica de Tipo Repetida**
  - Regras de tipo/classe centralizadas em `frontend/js/utils/combat-rules.js` e `combat-rules.global.js`
  - `ArenaController`, `GrimorioController` e `DashboardController` passaram a reutilizar helpers compartilhados em vez de checks duplicados

- [x] **#27 — Sem Compressão gzip**
  - `GZipMiddleware` habilitado no backend com `minimum_size` configurável via settings
  - `.env.example` atualizado com `GZIP_ENABLED` e `GZIP_MINIMUM_SIZE`

- [x] **#28 — Variáveis Globais Extensivas no Frontend**
  - Ações inline de Dashboard e Arena migradas para namespaces únicos (`window.dashboardActions` e `window.arenaActions`) em vez de múltiplas funções soltas no `window`
  - Estado de edição no dashboard deixou de usar `window.combatenteEmEdicao`, mantendo estado encapsulado no controller

- [x] **#29 — Sem Controle de Concorrência no Combate**
  - Controle otimista por versão no backend de combate (`versao` no status + validação por cabeçalho `If-Match` em mutações)
  - API agora retorna `409` para versão desatualizada e `428` quando precondição de versão não é enviada
  - Frontend legado (`frontend/script.js`) passou a enviar `If-Match` e sincronizar estado automaticamente em caso de conflito

- [x] **#30 — Admin Recriado a Cada Startup**
  - `criar_admin_padrao()` agora normaliza email e faz criação idempotente (rechecagem + fallback em `IntegrityError`)
  - Em cenário de corrida, se outro processo criar o admin entre o check e o insert, startup continua sem duplicar usuário

- [x] **#31 — Sem Histórico de Combate**
  - Novo histórico persistido em `combates_historico` com estatísticas consolidadas (rodadas, turnos, vivos/mortos, snapshot final)
  - Encerramento manual, reset e término por eliminação total agora registram resultado automaticamente
  - Endpoint `GET /api/v1/combate/historico` adicionado com paginação (`skip/limit`)

- [x] **#32 — Preparação de Magias sem Validação de Classe**
  - Endpoint de preparar magia agora valida compatibilidade entre classe do combatente e classe da magia
  - Normalização de acentos/aliases aplicada (ex.: `Clérigo`/`CLERIGO`, `Feiticeiro` usando lista de `MAGO`)

- [x] **#33 — URL de Imagem Não Configurável**
  - `FileService` agora gera `foto_url` usando `UPLOADS_BASE_URL` (compatível com CDN) em vez de path fixo
  - Mantido fallback padrão (`/uploads`) para não quebrar ambiente local existente

- [x] **#34 — Sem Caching**
  - Cache em memória com TTL para catálogos de magias, perícias e equipamentos
  - Invalidação por namespace em escritas de catálogo (perícias/equipamentos)
  - Chaves de cache consideram filtros/paginação para evitar resposta incorreta

- [x] **#35 — Migrations sem Backfill**
  - Migration `a35b1f4c9d10_backfill_legacy_nulls` adicionada para preencher nulos legados em colunas novas
  - Backfill idempotente com checagem de existência de tabela/coluna antes de executar updates

- [x] **#36 — Uploads Possivelmente no Git**
  - Regras explícitas adicionadas em `.gitignore` para `backend/uploads/` e conteúdo interno
  - Verificação do índice Git confirma ausência de arquivos de upload rastreados

- [x] **#37 — Toasts sem Contexto**
  - Services de slots/preparação agora propagam `HTTP status` + `detail` do backend com contexto (combatente/slot/magia)
  - Toasts de Arena/Grimório passaram a exibir mensagens acionáveis com nível/magia quando há falha

- [x] **#38 — Sem Graceful Degradation**
  - Helpers de bootstrap resiliente adicionados para capturar falhas e manter UI em modo degradado
  - Inicialização protegida em Arena, Dashboard, Ficha, Grimório, Usuários e Perícias com fallback visual/toast

- [x] **#39 — Estado de Combate em Memória**
  - Fluxo da arena passou a usar endpoints de combate para iniciar/avançar/finalizar/resetar com versão (`If-Match`)
  - Recuperação automática de combate ativo em carregamento da arena via `GET /combate/status`

- [x] **#40 — Nomes de Colunas Genéricos**
  - Joins críticos migrados para aliases e labels explícitos em repositórios (equipamentos, talentos e condições)
  - Serviços de listagem passaram a consumir projeções nomeadas, reduzindo ambiguidade sem quebrar schema atual

---

## 📊 Resumo

| Severidade | Qtde | Status |
|------------|------|--------|
| 🔴 Crítico | 5 | 5/5 concluídos |
| 🟡 Importante | 15 | 15/15 concluídos |
| 🟢 Bom ter | 20 | 20/20 concluídos |
| **Total** | **40** | **40/40 concluídos** |

---

## ✅ Fechamento do Ciclo 1

- [x] Checklist original concluído integralmente
- [x] Endurecimento de segurança aplicado no backend e frontend
- [x] Correções estruturais de auth, cache, uploads, RBAC e paginação estabilizadas
- [x] Melhorias de UX e resiliência validadas nas telas críticas

> O checklist acima passa a servir como histórico consolidado da rodada principal de hardening + arquitetura.

---

## 🧭 Checklist 5 — Consolidação Técnica (Abril/2026)

> Análise realizada em 07/04/2026 após varredura completa do codebase pós-Ciclo 1.
> Foco em: débitos técnicos de Python/SQLAlchemy, duplicações de código, deploy seguro e micro-otimizações.

### 🔴 Crítico

- [x] **C4 — `alembic upgrade head` ausente no deploy**
  - `Procfile` só sobe o uvicorn; migrations Alembic nunca são aplicadas em produção
  - Fix: `web: alembic upgrade head && uvicorn backend.app.main:app ...`

- [x] **C2 — Swagger/OpenAPI exposto em produção**
  - `docs_url="/api/docs"` e `redoc_url="/api/redoc"` ativos em todos os ambientes
  - Fix: condicionar a `settings.ENVIRONMENT != "production"` (setar `None` em prod)

- [x] **C1 — `datetime.utcnow()` deprecado em 20+ lugares**
  - Afeta models, repositories, services e security.py
  - Fix: substituir por `datetime.now(timezone.utc)` + importar `timezone` de `datetime`

- [x] **C3 — `@app.on_event("startup")` deprecado no FastAPI 0.93+**
  - Fix aplicado: `lifespan` com `@asynccontextmanager` em `backend/app/main.py` +
    `FastAPI(..., lifespan=lifespan)`.

### 🟡 Importante

- [x] **I11 — Arquivos mortos no repositório**
  - `backend/app/models/magia-bkp.py` — backup manual com código ativo duplicado
  - `backend/alembic_migrations/env copy.py` — cópia obsoleta do env.py
  - Fix: remover os dois arquivos

- [x] **I4 — `/health` não verifica conexão com banco**
  - Retorna `{"status": "ok"}` sem consultar o banco
  - Fix: adicionar `db.execute(text("SELECT 1"))` no health check

- [x] **I1 — `_normalizar_classe` duplicada em 3 arquivos**
  - `api/v1/magias_preparadas.py`, `repositories/magia_repository.py`, `services/magia_service.py`
  - Fix: centralizar em `app/games/dnd35/text_utils.py` e importar nos 3 lugares

- [ ] **I2 — Lógica de negócio no router `magias_preparadas.py`**
  - Funções `_normalizar_classe`, `_classes_magia`, `_normalizar_quantidade`, `_enriquecer` no arquivo de rota
  - Fix: extrair para `services/magia_preparada_service.py`

- [x] **P5 — Sincronização automática em todo GET de notificações**
  - `listar_notificacoes()` roda `_sincronizar_magias_automaticas + _reconciliar` em cada request
  - Fix: sincronizar apenas se `force_sync=True` ou 1× por sessão com flag de TTL

- [x] **P6 — Duplo `listar_paginado(limit=500)` no mesmo request de notificações**
  - `_sincronizar_magias_automaticas()` e `_garantir_notificacoes_sistema()` buscam catálogo separadamente
  - Fix: extrair uma busca só e passar como parâmetro para ambas

### 🟢 Bom ter

- [x] **P3 — Cache singleton de `MagiaService` no frontend**
  - Instância destruída a cada abertura do grimório; cache `Map` interno perdido
  - Fix: mover para `window._magiaServiceSingleton` ou `sessionStorage`

- [x] **B5 — `finalizar_todos` itera combates em Python**
  - Loop Python para marcar cada combate como inativo
  - Fix: `UPDATE combates SET ativo = false WHERE ativo = true` (SQL único)

- [x] **B3 — Índices compostos ausentes em `grimorio_notificacoes`**
  - Queries por `(combatente_id, classe, lida)` e `(combatente_id, tipo)` sem índice composto
  - Fix: migration Alembic com `Index('ix_...', col1, col2, col3)`

- [ ] **B1 — `declarative_base()` de import deprecado**
  - `from sqlalchemy.ext.declarative import declarative_base` → legado desde SQLAlchemy 1.4
  - Fix: `from sqlalchemy.orm import DeclarativeBase`

- [ ] **P2 — Paralelizar `_carregarCatalogoClasse` no Grimório** *(Bloqueado)*
  - `_carregarItensGrimorio` depende de `catalogoIndex` → refatoração maior necessária
  - Fix futuro: separar o merge do fetch para permitir paralelização no `Promise.all`

---

## 🧭 Checklist 2 — Consolidação Pós-Implementação

> Novo checklist para revisão do projeto após a grande rodada de melhorias.  
> Objetivo: consolidar UX, consistência entre telas, governança de frontend e validação operacional.

### 2.1 Concluído nesta rodada

- [x] **Arena — corrigir 401 em dano/cura/condições por falta de Authorization**
  - `CondicaoService` e `DanoCuraService` passaram a enviar token JWT corretamente

- [x] **Arena — mitigar carregamento de script antigo por cache do navegador**
  - `index.html` ajustado com cache-busting controlado para assets críticos

- [x] **Arena — restaurar ação de Encerrar Combate**
  - Rebind da ação global e migração para listeners explícitos

- [x] **Arena/Dashboard — reduzir dependência de handlers inline**
  - Dashboard e trechos relevantes da Arena migrados para `addEventListener`

- [x] **Navegação — parar de abrir múltiplas abas entre Dashboard, Ficha e Perícias**
  - Fluxo padronizado para mesma aba com `return_to` explícito quando necessário

- [x] **Backend — eliminar ruído de `favicon.ico` 404**
  - Adicionada rota segura para favicon com fallback sem erro visual

- [x] **Usuários — redesign visual e operacional da tela administrativa**
  - Hero, métricas, filtros, tabela, governança visual e modal revisados

- [x] **Usuários — tornar modal de Novo Usuário responsivo em telas menores**
  - Modal com `max-height`, scroll interno e ações sempre acessíveis

- [x] **Usuários — substituir alertas crus por feedback no padrão visual do sistema**
  - Validação e falha de salvamento agora usam `ModalConfirm`/feedback padronizado

- [x] **Usuários — bloquear envio duplo no modal de criação/edição**
  - Botão `Salvar` entra em estado `Salvando...` e ignora cliques repetidos

- [x] **Acessibilidade visual — refinar foco em botões críticos da tela de usuários**
  - Estados `:focus-visible` reforçados em hero, modal e ações de tabela

- [x] **Governança de workspace — criar instruções granulares do Copilot por domínio**
  - Estrutura em `.github/instructions` separada para backend, frontend e migrations

- [x] **Consolidação frontend (parcial) — limpar handlers inline e feedbacks crus no frontend moderno**
  - Ficha do personagem, perícias da ficha, modal de usuários, modais auxiliares e Arena moderna migrados para listeners explícitos
  - Restante relevante agora está concentrado majoritariamente no legado de `frontend/script.js`

### 2.2 Checklist de revisão para a próxima etapa

- [x] **Fazer uma varredura final de handlers inline restantes fora de Dashboard/Usuários**
  - Prioridade para páginas antigas com HTML legado e acoplamento em `window.*`
  - Estado atual: frontend moderno da Arena/Ficha consolidado; varredura final agora foca só em remanescentes de baixo impacto
  - Auditoria atual: ocorrências funcionais de `onclick/onchange/oninput` removidas das telas ativas; matches restantes são comentários/documentação

- [x] **Validar e aposentar legado órfão do frontend antigo (fase 1)**
  - `frontend/pages/arena-combate.html` foi aposentada com redirecionamento explícito para `/arena` (compatibilidade preservada)
  - README atualizado para sinalizar `arena-combate.html` como legado

- [x] **Validar e aposentar legado órfão do frontend antigo (fase 2)**
  - `frontend/script.js` removido após validação de ausência de referência ativa em HTML/rotas
  - Superfície de manutenção reduzida e risco de regressão em código morto eliminado

- [x] **Padronizar feedback visual de erro/aviso em todas as telas administrativas**
  - Eliminar `alert()` restante e alinhar para `Toast`/`ModalConfirm`
  - Auditoria atual: `alert()`/`confirm()` funcionais não detectados no frontend ativo

- [ ] **Executar smoke test manual orientado por fluxo principal**
  - Login → Dashboard → Arena → Ficha → Perícias → Usuários
  - Pré-validação técnica concluída: suíte backend crítica executada com sucesso (`test_auth_api`, `test_combate_api_history`, `test_security_audit` = 9/9 pass).
  - Smoke técnico HTTP (ambiente local em `127.0.0.1:8000`) executado:
    - `200`: `/pages/login.html`, `/pages/dashboard.html`, `/arena`, `/pages/ficha-personagem.html?id=1`, `/pages/pericias.html?id=1`, `/pages/usuarios.html`, `/health`.
    - `204`: `/favicon.ico` (sem erro visual de 404).
    - Autenticação validada no ambiente local com `POST /api/v1/auth/login` e `GET /api/v1/auth/me` (`200`).
    - Script reutilizável criado para repetir essa validação: `backend/scripts/smoke_http.sh`.
  - Status: smoke técnico concluído; falta apenas validação manual visual/funcional no navegador para fechar este item.
  - Roteiro rápido sugerido:
    1. Login com perfil admin e confirmar header/perfil corretos.
    2. Dashboard: listar, filtrar e abrir ficha sem abrir nova aba.
    3. Arena: iniciar combate, avançar turno e encerrar combate sem erro visual.
    4. Ficha: abrir/fechar grimório, abrir perícias e voltar mantendo navegação limpa.
    5. Usuários: abrir modal novo usuário em tela menor, validar botões visíveis e estado "Salvando...".
    6. Usuários: tentar salvar sem campos obrigatórios e confirmar feedback no padrão visual.

- [x] **Adicionar checklist de regressão visual para responsividade**
  - Cenários definidos:
    1. Laptop pequeno (~1366x768): sem corte de header, botões primários visíveis, tabelas com scroll controlado.
    2. Tablet vertical (~768x1024): modais com ações acessíveis sem overflow fora da viewport.
    3. Mobile estreito (~360x800): CTA principal por tela acionável sem zoom e sem sobreposição de blocos.
  - Critérios rápidos por tela crítica:
    - Arena: painel e ordem de iniciativa utilizáveis sem quebra visual.
    - Ficha/Perícias: navegação e botões de salvar/voltar sempre alcançáveis.
    - Usuários: filtros, tabela e modal operáveis com scroll interno.

- [x] **Revisar consistência de navegação entre páginas com botão Voltar**
  - Auditoria atual: nenhuma ocorrência funcional de `history.back()` detectada no frontend ativo.
  - Fluxo consolidado com origem controlada por `return_to` nas rotas de Ficha/Perícias.

- [x] **Inventariar pontos ainda sensíveis a cache de script**
  - Mapa atual:
    - `index.html` já usa cache-busting em assets críticos da Arena (`?v=20260329*`).
    - Páginas antigas ainda usam versões heterogêneas (`?v=1`, `?v=5`, `?v=8.0`, etc.).
    - `sw.js` mantém cache próprio de perícias e exige controle explícito de versão de cache.
  - Estratégia única definida para próxima rodada:
    1. Adotar `ASSET_VERSION` único por release e aplicar em todos os assets críticos.
    2. Versionar também `CACHE_NAME` do service worker com o mesmo identificador da release.
    3. Documentar checklist de bump de versão no release process (frontend + SW).

- [x] **Definir bateria mínima de testes automatizados para frontend crítico**
  - Escopo inicial (E2E smoke):
    1. Login válido/inválido + persistência de sessão.
    2. Dashboard: listagem e abertura da ficha em mesma aba.
    3. Arena: iniciar, avançar turno e encerrar combate.
    4. Usuários: abrir modal, validar campos obrigatórios e estado `Salvando...`.
  - Estratégia recomendada: suite Playwright enxuta (4-6 cenários), executada por PR de release.
  - Critério de adoção: bloquear release apenas para falhas em cenários smoke críticos.

- [x] **Padronizar comportamento de loading/disabled em ações assíncronas importantes**
  - Criado utilitário global `AsyncButtonState` (`frontend/js/utils/async-button.global.js`) com estado unificado (`disabled` + `aria-busy` + texto de loading).
  - Aplicado em fluxos críticos:
    1. Dashboard: formulários de cadastro e edição de combatente.
    2. Perícias: ação de salvar perícias.
  - Mantido fallback defensivo para operação manual caso o utilitário não esteja disponível em runtime.

- [x] **Revisar modais do projeto para altura máxima, scroll interno e foco acessível**
  - Hardening aplicado em modais legados e administrativos:
    1. `frontend/css/modais.css`: overlay com `padding` + `overflow-y` e foco visível em fechar/ações.
    2. `frontend/css/modal-condicao.css`: overlay com scroll seguro e foco visível em fechar/aplicar/cancelar.
    3. `frontend/css/login.css`: `modal-box` com `max-height` + scroll interno e close com `:focus-visible`.
    4. `frontend/css/dashboard.css`: foco visível para close e botões dentro do modal.

- [x] **Montar backlog da versão seguinte com foco em polimento e confiabilidade operacional**
  - Backlog VNext proposto:
    - `bugfix`: fechar regressões encontradas no smoke manual (navegação, estados de modal e feedback).
    - `DX`: unificar estratégia de versionamento de assets e script de bump por release.
    - `UX`: padronizar loading/disabled em ações assíncronas de Arena, Ficha e Perícias.
    - `testes`: subir suite mínima E2E smoke e incorporar no fluxo de validação pré-release.

---

## 🧭 Checklist 3 — Regras Divinas do Grimório + Confiabilidade

> Entregue em 03–04/04/2026. Foco em restrições canônicas de magia por alinhamento/domínio,
> diagnóstico de grimório e correção de modal de perfil divino na ficha.

### 3.1 Regras Divinas — Backend

- [x] **Restrição de magia por alinhamento para classes divinas**
  - `grimorio_service.py`: função `_magia_bloqueada_por_alinhamento` com lookup no CSV canônico + fallback semântico por nome/descrição
  - Classes divinas afetadas: `CLERIGO`, `DRUIDA`, `PALADINO` (Ranger excluído após análise de regras)
  - Cobertura: adição manual, auto-adição por nível e remoção automática retroativa após mudança de alinhamento

- [x] **Restrição de magia por domínio oposto para clérigo**
  - `grimorio_service.py`: função `_magia_bloqueada_por_dominios_opostos` ampliada para bloquear qualquer magia com tag/semântica de domínio oposto, não apenas magias com flag de domínio
  - Domínios opostos canônicos: BEM↔MAL, ORDEM↔CAOS

- [x] **Validar comportamento contra matriz canônica de alinhamento**
  - Matriz 9 alinhamentos × 4 tendências (BEM/MAL/ORDEM/CAOS) implementada como fixtures parametrizadas
  - Assets canônicos versionados: `restricoes_clerigo_completo.{csv,xlsx}`
  - Script de seed: `backend/scripts/seed_magias_clerigo_regras.py`

- [x] **Endpoint de diagnóstico de grimório**
  - `GET /api/v1/grimorio/{combatente_id}/diagnostico?classe=...`
  - Retorna lista de magias com motivo de bloqueio/permissão por magia
  - Schemas adicionados: `GrimorioDiagnosticoMagiaResponse`, `GrimorioDiagnosticoResponse`
  - Método de serviço: `diagnosticar_regras_divinas()`

- [x] **Cobertura de testes backend: 44 → 129 testes passando**
  - Casos novos: druida/paladino bloqueado por domínio oposto, clérigo bloqueado por semântica de nome, fallback de alinhamento para spells sem tag, full matriz 9 linhas, endpoint diagnóstico

### 3.2 Feedback Visual — Frontend Grimório

- [x] **Notice contextual de regras ativas no grimório do clérigo**
  - `GrimorioController.js`: aviso exibido quando classe é Clérigo com domínios configurados
  - `grimorio.css`: estilos para variantes de alerta (info, warn, bloqueio)

- [x] **Feedback de falha ao adicionar magia com motivo de bloqueio**
  - `GrimorioController.js`: mapeamento de mensagem de erro da API para texto legível
  - Card de preview identifica visualmente magias bloqueadas antes da tentativa

### 3.3 Modal Perfil Divino — Frontend Ficha

- [x] **Corrigir prefill de "Divindade" ao abrir modal**
  - `Combatente.js`: campo `divindade` adicionado explicitamente com fallback legado `data.deidade`
  - Root cause: campo não estava mapeado no construtor do modelo frontend

- [x] **Centralizar leitura do perfil divino**
  - `FichaPersonagemController.js`: helper `_lerPerfilDivino()` extrai alinhamento, divindade, domínio1, domínio2 de forma segura
  - `abrirModalPerfilMagico()` refatorado para usar o helper, eliminando leitura direta duplicada

- [x] **Testes unitários do perfil divino (frontend)**
  - `frontend/test-ficha-perfil-simples.js`: 19 asserções, casos: mapeamento básico, fallback legado, helper com domínios, campos vazios, persistência após update, round-trip modal

### 3.4 CI/CD

- [x] **GitHub Actions: pipeline backend + frontend**
  - `.github/workflows/ci.yml`: jobs `backend` (pytest, Python 3.9) e `frontend` (Node 18)
  - Triggers: push e PR em `main`, `master`, `develop`

- [x] **Makefile: `make test` unificado**
  - `make test`: roda `pytest` + teste JS sequencialmente
  - `make test-backend` e `make test-frontend` disponíveis individualmente
  - `make lint`: flake8 opcional se instalado

---

## 🧭 Checklist 4 — Performance em Produção

> Diagnóstico realizado em 04/2026. Foco em latência percebida pelo usuário no Brasil acessando
> backend no Render (Virginia) + Neon PostgreSQL (EUA). Cada request serial acumula ~250–500ms
> de round-trip intercontinental.

### 4.1 Contexto do Diagnóstico

- Latência base por request API: **250–500ms** (Brasil → Virginia EUA)
- Cold start do Render free tier: **+5–10s** após 15 min de inatividade (mitigado pelo cron `/health` a cada 10 min)
- Cache em memória (`CatalogCache`, TTL=30s) **perdido em cada restart** do Render
- Pool de conexões configurado: `pool_size=5`, `max_overflow=10`, `pool_pre_ping=True` ✅
- GZip ativo com `minimum_size=1000` ✅

### 4.2 Waterfall ao Abrir o Grimório (~1,6–2,5s total)

Sequência atual (5 requests):
1. `_carregarCatalogoClasse()` → `GET /magias/?classe=MAGO&limit=500` — **SERIAL, bloqueia o resto** (~400ms)
2. `_carregarItensGrimorio()` → `GET /grimorio/{id}` (~300ms) — em `Promise.all`
3. `_carregarNotificacoes()` → `GET /grimorio/{id}/notificacoes` (~400ms+) — em `Promise.all`
4. `_carregarMagiasPreparadas()` → `GET /magias-preparadas/{id}` (~300ms) — em `Promise.all`
5. `_carregarHistoricoTrocas()` → `GET /grimorio/{id}/historico` (~250ms) — **SERIAL, após o `Promise.all`**

### 4.3 Operações Extras em `listar_notificacoes` (request mais pesado)

A cada chamada ao endpoint de notificações são disparadas internamente:
- `_sincronizar_magias_automaticas()` → `listar_paginado(limit=500)` + `grimorio.listar()`
- `_reconciliar_magias_invalidas()` → `grimorio.listar()` novamente
- `_garantir_notificacoes_sistema()` → `listar_paginado(limit=500)` **de novo**
- = **2× `listar_paginado(limit=500)` no mesmo request** + 2× `grimorio.listar()`

### 4.4 Checklist de Melhorias

#### 🔴 Alta Prioridade

- [x] **P1 — Paralelizar carregamento inicial da Ficha do Personagem**
  - Arquivo: `frontend/js/controllers/FichaPersonagemController.js`
  - Problema: `inicializar()` chama 4 métodos em sequência com `await` serial
    ```js
    await this.carregarRenderizarPericias(id);          // ~350ms
    await this.carregarRenderizarEquipamentos(id);      // ~300ms
    await this.carregarRenderizarArmadurasProtecao(id); // ~300ms
    await this.carregarRenderizarTalentos(id);          // ~300ms
    ```
  - Fix: substituir por `Promise.all([...])` — reduz de ~1,25s para ~350ms
  - Risco: baixo (requests independentes, sem dependência entre si)

- [ ] **P2 — Mover `_carregarCatalogoClasse` para dentro do `Promise.all` no Grimório**
  - ⚠️ **Bloqueado:** `_carregarItensGrimorio` usa `this.catalogoIndex` e `this.catalogoClasse` internamente (`_mapearItemGrimorio` + `_mesclarCatalogoDisponivelNoGrimorio`). Para paralelizar, seria necessário separar o merge do fetch — refatoração maior.
  - Arquivo: `frontend/js/controllers/GrimorioController.js`, método `_recarregarDados()`
  - Problema: `await this._carregarCatalogoClasse()` executa antes do `Promise.all`, adicionando ~400ms seriais
  - Fix: incluir `this._carregarCatalogoClasse()` dentro do `Promise.all` junto com os demais
  - Risco: baixo (catálogo não é dependência dos outros requests no `Promise.all`)

- [x] **P3 — Cache de catálogo de magias entre aberturas do Grimório**
  - Arquivo: `frontend/js/services/MagiaService.js`
  - Problema: `MagiaService` é reinstanciado a cada abertura do grimório → cache `Map` interno destruído
  - Fix: mover instância para `window._magiaService` (singleton de sessão) ou usar `sessionStorage` para o catálogo por classe
  - Impacto: elimina 1 request de ~400ms em todas as reaberturas do grimório

- [x] **P4 — Aumentar TTL do cache de catálogos de 30s para 300s**
  - Arquivo: `backend/app/core/config.py`, variável `CACHE_CATALOG_TTL_SECONDS`
  - Problema: TTL=30s é muito curto para dados que raramente mudam (magias, perícias)
  - Fix: `CACHE_CATALOG_TTL_SECONDS: int = 300` (5 minutos)
  - Env var: adicionar `CACHE_CATALOG_TTL_SECONDS=300` no Render e `.env.example`
  - Risco: dados de catálogo levam até 5 min para refletir edições manuais no banco (aceitável)

#### 🟡 Média Prioridade

- [x] **P5 — Separar sincronização automática do endpoint de notificações**
  - Arquivo: `backend/app/services/grimorio_service.py`, método `listar_notificacoes()`
  - Problema: sincronização (_sincronizar_magias_automaticas + _reconciliar_magias_invalidas) roda em todo GET de notificações
  - Fix opção A: executar sincronização apenas se `force_sync=True` (query param)
  - Fix opção B: sincronizar apenas 1× por sessão com flag no backend (ex: `_ultima_sync` por combatente com TTL)
  - Fix opção C: mover sincronização para evento de abertura do grimório (`POST /grimorio/{id}/sync`)
  - Impacto estimado: reduz endpoint de notificações de ~400ms para ~150ms

- [x] **P6 — Eliminar duplo `listar_paginado(limit=500)` no mesmo request de notificações**
  - Arquivo: `backend/app/services/grimorio_service.py`
  - Problema: `_sincronizar_magias_automaticas()` e `_garantir_notificacoes_sistema()` ambas chamam `listar_paginado(limit=500)` no mesmo request
  - Fix: extrair `magias_catalogo = await listar_paginado(limit=500)` uma vez e passar como parâmetro para ambas
  - Impacto: elimina 1 query extra de catálogo por request de notificações

- [x] **P7 — Mover `_carregarHistoricoTrocas` para dentro do `Promise.all` no Grimório**
  - Arquivo: `frontend/js/controllers/GrimorioController.js`, método `_recarregarDados()`
  - Problema: histórico é carregado após o `Promise.all` em sequência serial
  - Fix: incluir no `Promise.all` (histórico não depende dos outros dados)
  - Risco: baixo

#### 🟢 Baixa Prioridade

- [x] **P8 — Skeleton loader visual durante carregamento do Grimório e Ficha**
  - `frontend/css/skeleton.css` criado com animação shimmer e variantes para ficha (azul) e grimório (dourado)
  - `FichaPersonagemController._mostrarSkeletonFicha()`: injeta `.sk-item` com círculo + linhas nos containers `fichaTalentos`, `fichaEquipamentos`, `fichaArmadurasProtecao` e `fichaPericiasLista` antes do `Promise.all`
  - `GrimorioController._mostrarLoading(true)`: injeta 6 `.sk-card-grimorio` no `grimorioLista` ao abrir; substituídos pelo `filtrar()` após os dados chegarem
  - `FichaPersonagemController.js?v=24`, `GrimorioController.js?v=22`

- [ ] **P9 — Avaliar migração de infraestrutura para região mais próxima do Brasil**
  - Ver seção **5. Análise Railway vs Render** abaixo
  - Candidatos: Railway São Paulo (AWS sa-east-1) + Supabase São Paulo
  - Impacto potencial: reduzir latência de ~350ms para ~80ms por request

### 4.5 Resumo de Ganhos Estimados

| # | Melhoria | Redução estimada | Esforço |
|---|----------|-----------------|---------|
| P1 | Ficha: 4 requests seriais → `Promise.all` | ~900ms → ~350ms | Baixo |
| P2 | Grimório: catálogo serial → paralelo | +400ms eliminados | Baixo |
| P3 | Cache singleton MagiaService | +400ms na reabertura | Baixo |
| P4 | TTL cache 30s → 300s | reduz cold cache | Muito Baixo |
| P5 | Sync lazy em notificações | ~250ms por request | Médio |
| P6 | Eliminar 2ª query catálogo | ~150ms por sync | Baixo |
| P7 | Histórico: serial → paralelo | ~250ms eliminados | Baixo |

---

## 🛤️ Análise: Railway vs Render (Para Futuro)

### Gargalo Principal

O custo dominante de latência hoje é **distância Brasil → Virginia EUA (~300–500ms por request)**,
não a capacidade computacional do servidor. Isso afeta Render, Railway EUA e qualquer opção
em US-East igualmente.

### Opções de Infraestrutura

| Plano | Região disponível BR | Cold start | Custo/mês | Latência Brasil |
|-------|---------------------|-----------|-----------|----------------|
| Render free tier | ❌ (só US/EU) | ~5–10s | $0 | ~350ms base |
| Render starter | ❌ (só US/EU) | sem sleep 24h | $7 | ~350ms base |
| Railway Starter | ✅ **São Paulo (sa-east-1)** | sem sleep | $5 uso | **~80ms base** |
| Fly.io | ✅ São Paulo (GRU) | ~2s (scale to 0) | $0–$3 | **~80ms base** |
| Koyeb | ✅ São Paulo | sem sleep | ~$0–$3 | **~80ms base** |

### Benefício do Railway (São Paulo)

- Latência de ~300–500ms → ~60–100ms por request (4–5× menor)
- Sem cold start no plano Starter ($5/mês por uso — paga pelo que usar)
- Deploy por push de branch (igual ao Render)
- Suporta variáveis de ambiente, Dockerfile ou buildpack automático
- **Limitação:** Neon PostgreSQL ainda fica em US-East-2 → cada query ao banco adiciona ~200ms
  mesmo com backend em São Paulo

### Solução Completa (Backend + DB em BR)

Para eliminar totalmente a latência, seria necessário migrar o banco também:
- **Supabase** — PostgreSQL serverless com região São Paulo (`sa-east-1`) no plano gratuito
- **Neon** — ainda sem região São Paulo (apenas US-East, EU-Central, AWS AP-Southeast)
- Migração: exportar dump do Neon → importar no Supabase + ajustar `DATABASE_URL`
- Alembic funciona da mesma forma com Supabase (PostgreSQL padrão)

### Recomendação

> Se a latência for prioridade real: **Railway São Paulo + Supabase São Paulo** = solução completa.
> Se quiser testar com custo mínimo: mover só o backend para **Railway São Paulo** já reduz
> tempo de resposta em ~2× para requests sem query pesada (health, token, cache hit).
> Render continua sendo a opção zero-custo se performance não for crítica agora.
