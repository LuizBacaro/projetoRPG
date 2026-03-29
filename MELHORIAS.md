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

- [ ] **#14 — Potencial N+1 Queries**
  - Padrões de fetch sem batch em repositórios
  - `lazy="selectin"` ajuda, mas nem todos os patterns cobertos

- [ ] **#15 — Sem Paginação nas Listas**
  - `/magias` pode retornar 400+ registros de uma vez
  - `get_all()` tem params mas sem defaults razoáveis

- [ ] **#16 — Sem Logging de Segurança**
  - Login falho, acessos negados não logados
  - Sem audit trail para ações de admin

- [x] **#17 — CSS Duplicado (pericias_backup.css)**
  - `pericias_backup.css` removido — não era referenciado em nenhum HTML

- [ ] **#18 — Dependency Injection Inconsistente**
  - `get_combatente_repository(db=None)` aceita None e tenta `next(get_db())`
  - Deveria usar sempre `Depends(get_db)` do FastAPI

- [ ] **#19 — Sem Limite de Tamanho no Input**
  - Campos de texto sem `max_length` em algumas rotas/schemas
  - Sem Content-Length limits no Uvicorn

- [ ] **#20 — Startup sem Error Handling**
  - Se criação de admin falhar, app inicia em estado quebrado silenciosamente

---

## 🟢 BOM TER (Qualidade / UX)

- [ ] **#21 — Sem Soft Delete / Audit Trail**
  - Dados apagados permanentemente, sem `deleted_at`

- [ ] **#22 — `.env.example` Faltando**
  - Novos devs não sabem quais variáveis configurar

- [ ] **#23 — Cobertura de Testes ~15%**
  - Apenas 2 arquivos de teste, sem testes de auth, upload, integração ou frontend

- [ ] **#24 — Swagger sem Customização**
  - JWT não documentado no OpenAPI, sem exemplos de request/response

- [ ] **#25 — Sem Retry/Circuit Breaker no Frontend**
  - Erro de rede = falha silenciosa

- [ ] **#26 — Lógica de Tipo Repetida**
  - `CLASSES_CONJURADORAS`, checks de tipo duplicados em vários controllers

- [ ] **#27 — Sem Compressão gzip**
  - Respostas JSON grandes enviadas sem compressão

- [ ] **#28 — Variáveis Globais Extensivas no Frontend**
  - `window.AuthService`, `window.Toast` etc poluem namespace global

- [ ] **#29 — Sem Controle de Concorrência no Combate**
  - Dois usuários podem editar o mesmo combate simultaneamente

- [ ] **#30 — Admin Recriado a Cada Startup**
  - Potencial duplicação se check de existência falhar

- [ ] **#31 — Sem Histórico de Combate**
  - Resultados não persistidos, sem relatórios ou estatísticas

- [ ] **#32 — Preparação de Magias sem Validação de Classe**
  - Pode preparar magias de Clérigo para Mago

- [ ] **#33 — URL de Imagem Não Configurável**
  - Path fixo `/uploads/`, incompatível com CDN

- [ ] **#34 — Sem Caching**
  - Magias, perícias, equipamentos consultados no banco a cada request

- [ ] **#35 — Migrations sem Backfill**
  - Colunas novas ficam NULL em registros existentes

- [ ] **#36 — Uploads Possivelmente no Git**
  - Verificar `.gitignore` para `backend/uploads/`

- [ ] **#37 — Toasts sem Contexto**
  - "Erro ao buscar slots" sem detalhe de qual magia ou motivo

- [ ] **#38 — Sem Graceful Degradation**
  - Se um controller falhar, a página inteira quebra

- [ ] **#39 — Estado de Combate em Memória**
  - Restart do servidor perde combates ativos

- [ ] **#40 — Nomes de Colunas Genéricos**
  - `nome`, `tipo`, `classe` em várias tabelas dificultam joins

---

## 📊 Resumo

| Severidade | Qtde | Status |
|------------|------|--------|
| 🔴 Crítico | 5 | — |
| 🟡 Importante | 15 | — |
| 🟢 Bom ter | 20 | — |
| **Total** | **40** | — |
