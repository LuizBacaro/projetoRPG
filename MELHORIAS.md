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

- [ ] **#6 — Padrões de Export Inconsistentes no Frontend**
  - Mix de ES6 modules, globals (`window.X`) e CommonJS
  - `NotificationService.js` causa SyntaxError no console

- [ ] **#7 — Rotas sem Autenticação**
  - `GET /combatentes`, `GET /magias` etc expostos sem login
  - Adicionar `Depends(get_usuario_atual)` nas rotas necessárias

- [ ] **#8 — Sem Rate Limiting**
  - Nenhum middleware de proteção contra DoS/brute-force
  - Implementar slowapi ou similar

- [ ] **#9 — JWT sem Refresh Endpoint**
  - Token de 24h expira e exige re-login manual
  - Implementar `/auth/refresh` com rotation de tokens

- [ ] **#10 — Sem Verificação de Propriedade (RBAC)**
  - Qualquer usuário autenticado pode manipular combatentes de outros
  - Adicionar checks de ownership nas rotas

- [ ] **#11 — URL da API Hardcoded no Frontend**
  - `frontend/js/config.js` — Domínio fixo, sem config por ambiente
  - Usar detecção automática de origem ou variável de build

- [ ] **#12 — Sem Rollback de Transações**
  - `db.commit()` direto nos repositories, sem transaction boundary
  - Operações em massa (resetar HP) podem falhar parcialmente

- [ ] **#13 — Constraints de Banco Faltando**
  - `hp_atual` sem limites, `tipo` como string livre
  - Duplicatas permitidas em MagiaPreparada (sem unique constraint)

- [ ] **#14 — Potencial N+1 Queries**
  - Padrões de fetch sem batch em repositórios
  - `lazy="selectin"` ajuda, mas nem todos os patterns cobertos

- [ ] **#15 — Sem Paginação nas Listas**
  - `/magias` pode retornar 400+ registros de uma vez
  - `get_all()` tem params mas sem defaults razoáveis

- [ ] **#16 — Sem Logging de Segurança**
  - Login falho, acessos negados não logados
  - Sem audit trail para ações de admin

- [ ] **#17 — CSS Duplicado (pericias_backup.css)**
  - `pericias_backup.css` ao lado de `pericias.css` — conflito potencial
  - Remover arquivo morto

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
