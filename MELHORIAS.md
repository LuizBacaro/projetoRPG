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
  - Implementado middleware custom em `app/core/rate_limit.py` (sliding window por IP)
  - Limite geral na API: `API_RATE_LIMIT_PER_MINUTE` (default 180/min)
  - Limite específico para `POST /api/v1/auth/login`: `LOGIN_RATE_LIMIT_PER_MINUTE` (default 10/min)
  - Retorna `429` com `Retry-After`, `X-RateLimit-Limit`, `X-RateLimit-Remaining`
  - Configurável via `app/core/config.py` (`RATE_LIMIT_ENABLED`, limites por minuto)

- [x] **#9 — JWT sem Refresh Endpoint**
  - Implementado `POST /auth/refresh` em `auth.py`
  - `login` agora retorna `access_token` + `refresh_token`
  - Refresh valida `type=refresh` e emite novo par de tokens (rotation)
  - Expiração configurável via `REFRESH_TOKEN_EXPIRE_DAYS` em `config.py`

- [x] **#10 — Sem Verificação de Propriedade (RBAC)**
  - Adicionado ownership em `combatentes` com coluna `dono_id` + migration Alembic
  - Criadas dependências `requer_dono_ou_admin_combatente` e `requer_dono_ou_admin_slot_magia` em `core/deps.py`
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
  - Criado helper central `core/security_audit.py` para logs estruturados de segurança com IP, ator, alvo e motivo
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
| 🔴 Crítico | 5 | — |
| 🟡 Importante | 15 | — |
| 🟢 Bom ter | 20 | — |
| **Total** | **40** | — |
