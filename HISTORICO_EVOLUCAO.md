# Histórico de Evolução — Arena de Combate TTRPG

Registro cronológico de decisões de infraestrutura, stack e features relevantes.
Objetivo: entender por que cada mudança foi feita, se trouxe ganho real e para onde voltar se necessário.

---

## Formato de cada entrada

```
### [Data aproximada] Título da mudança
**O que era antes:** ...
**O que mudou:** ...
**Motivo:** ...
**Resultado / Avaliação:** ...
**Como reverter (se necessário):** ...
```

---

## Infraestrutura

---

### [2024 — início] Stack inicial
**O que era:**
- Backend: FastAPI local (SQLite)
- Frontend: HTML/CSS/JS estático servido localmente
- Sem deploy, sem banco de produção

**Avaliação:** Ponto de partida. Funcional para desenvolvimento, sem infra de produção.

---

### [2024] Primeiro deploy — Railway (backend) + SQLite remoto
**O que mudou:** Backend deployado no Railway com SQLite persistido em disco.

**Motivo:** Railway oferecia free tier simples para FastAPI.

**Resultado:** Instável — SQLite em disco no Railway perdia dados em re-deployments. Conexões simultâneas problemáticas.

**Decisão seguinte:** Migrar banco para PostgreSQL gerenciado.

---

### [2024] Migração de banco: Railway SQLite → Neon PostgreSQL
**O que era:** `DATABASE_URL=sqlite:///./rpg_arena.db` em produção no Railway.

**O que mudou:** `DATABASE_URL=postgresql://...@ep-xxx.neon.tech/neondb?sslmode=require`

**Motivo:** SQLite não é adequado para produção multi-usuário. Neon oferece PostgreSQL serverless gratuito com connection pooling.

**Resultado:** ✅ Estável. Dados persistem entre deploys. Queries mais confiáveis.

**Configuração no engine:**
```python
"pool_pre_ping": True,
"pool_recycle": 300,
"pool_size": 5,
"max_overflow": 10,
```

**Como voltar ao SQLite (só dev):** `DATABASE_URL=sqlite:///./rpg_arena.db` no `.env` local.

---

### [2024/2025] Migração de hosting: Railway → Render.com
**O que era:** Backend no Railway free tier.

**O que mudou:** Backend migrado para Render.com Web Service free tier.

**Motivo:** Railway encerrou free tier permanente. Render mantém free tier com limitação de 750h/mês e sleep após 15min.

**Resultado:** ✅ Funcional. Cold start de 30–60s após inatividade é o principal trade-off.

**Branch de produção:** `feature/salva` — qualquer merge nessa branch aciona deploy automático no Render.

**Configuração Render:**
- Root Directory: `backend`
- Build: `pip install -r requirements.txt`
- Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Python: 3.11

**Como reverter para Railway:** Reconectar o repo no Railway, usar as mesmas env vars. O código não precisa mudar.

---

### [2024/2025] Frontend: local → Vercel
**O que mudou:** Frontend (HTML/CSS/JS estático) deployado no Vercel.

**Motivo:** Vercel é CDN global, deploy automático via git push, gratuito para projetos estáticos.

**Resultado:** ✅ Excelente. Zero latência de frontend. Deploy em ~30s.

**DNS:** Cloudflare → CNAME `arena-de-combate-rpg.com.br` → `cname.vercel-dns.com`

---

### [2025] Correção de config.js — API URL hardcoded → same-origin
**O que era:**
```javascript
// config.js
return 'https://arena-de-combate-rpg-api.onrender.com'; // URL errada
```

**O que mudou:**
```javascript
return ''; // same-origin — /api/v1/... resolvido pelo Vercel proxy ou diretamente
```

**Motivo:** URL hardcoded apontava para serviço inexistente. Todas as chamadas de API falhavam em produção.

**Resultado:** ✅ Todas as chamadas passaram a funcionar.

---

### [2025] Anti-sleep: sem cron → UptimeRobot → cron-job.org
**Fase 1 — sem anti-sleep:**
Cold start frequente (30–60s). Usuários relatavam plataforma "lenta".

**Fase 2 — UptimeRobot:**
Tentativa com UptimeRobot (monitoramento gratuito a cada 5min). Funcionou parcialmente.

**Fase 3 — cron-job.org (atual, abril/2026):**
```
URL: https://projetorpg-7ih3.onrender.com/health
Schedule: */10 * * * *
Console: https://console.cron-job.org/jobs
```

**Resultado:** ✅ Render mantido acordado 24h. Cold start eliminado.

**Avaliação de custo:** Render free tier tem 750h/mês. 24h × 31 dias = 744h — dentro do limite.

**Como reverter:** Desativar o cron job. Cold start volta, mas nenhum custo.

---

## Python / Runtime

---

### [2024] Python 3.10 → 3.11
**Motivo:** Render passou a suportar 3.11. Melhor performance (10–15% parsing, startup) e suporte a `tomllib` nativo.

**Arquivo:** `runtime.txt` → `python-3.11.9`

**Resultado:** ✅ Sem breaking changes. Build mais rápido.

---

### [2024/2025] Pydantic v1 → v2 (com pin)
**O que era:** Pydantic sem versão fixada — instalava v2 com breaking changes na serialização.

**O que mudou:** `requirements.txt` com pin explícito. Services usam `model_dump()` (v2) com fallback para `.dict()` (v1).

**Resultado:** ✅ Compatível com SQLite em testes e PostgreSQL em produção.

---

## Banco de Dados — Schema

---

### [2024] DATETIME → TIMESTAMP (PostgreSQL compat)
**O que era:** Campos de data como `DATETIME` no modelo SQLAlchemy.

**O que mudou:** `TIMESTAMP(timezone=True)` com `server_default=func.now()`.

**Motivo:** `DATETIME` não é suportado pelo PostgreSQL via SQLAlchemy sem mapeamento explícito.

**Resultado:** ✅ Migrations funcionando no Neon sem erros de tipo.

---

### [2025] Seed: pericias_classes populada em produção
**O que era:** Tabela `pericias_classes` vazia no Neon. Custo de todas as perícias retornava 2 pts (fallback padrão).

**O que mudou:** 175 associações inseridas via `mcp_neon_run_sql` diretamente no Neon:
- 11 classes × perícias de classe (D&D 3.5 PHB)
- Custo 1 pt = perícia da classe, 2 pts = fora da classe

**Motivo:** Seeds locais não eram aplicados automaticamente em produção.

**Como re-aplicar se necessário:**
```bash
# Via script local (conectar ao Neon)
cd backend
python -m scripts.seed_simple
```
Ou re-inserir o SQL do `seed_pericias.py` via MCP Neon.

---

## Features Frontend

---

### [2025] TalentoService.js — URL hardcoded → getApiUrl()
**O que era:**
```javascript
this.baseUrl = 'http://localhost:8000/api/v1/talentos'; // hardcoded
```

**O que mudou:**
```javascript
import { getApiUrl } from '../config/api.config.js';
this.baseUrl = getApiUrl('/talentos');
```

**Resultado:** ✅ Talentos funcionando em produção.

---

### [2025] ArenaController — window.getApiUrl → getApiUrl importado
**O que era:** `_decrementarDuracaoCondicoes` testava `window.getApiUrl` (undefined em módulo ES) e fazia fallback para `localhost:8000`.

**O que mudou:** Usa diretamente `getApiUrl` já importado no topo do arquivo.

**Resultado:** ✅ Decremento de condições funcionando em produção.

---

### [2025] GrimorioController — Clérigo/Druida sem magias
**Problema:** Clérigo e Druida apareciam com grimório vazio (não têm lista de magias conhecidas — preparam do catálogo completo).

**Solução:** `_classeExibeCatalogoCompleto()` retorna `true` para `clerigo` e `druida`, auto-populando o catálogo completo.

**Resultado:** ✅ Clérigo e Druida veem todas as magias disponíveis para preparação.

---

### [2025] Grimório — Filtro "Preparadas"
**Adicionado:** Botão "🕯️ Preparadas" que filtra apenas magias já preparadas.

**Visível para:** Clérigo, Mago, Druida, Ranger, Paladino (classes que preparam magias).
**Oculto para:** Bardo, Feiticeiro (magias espontâneas — sem preparação diária).

---

### [2025 → 2026] Ficha do Personagem — Editor de Ataques inline
**O que era:** Ataques exibidos apenas como leitura na ficha.

**O que mudou:** Botão "✏️ Editar" abre editor collapsible com inputs para nome/bônus/dano. Salva via `PUT /combatentes/{id}/ataques`.

**Resultado:** ✅ Mestre/jogador pode editar ataques diretamente na ficha sem ir ao dashboard.

---

### [2026] secaoMagias — visível para não-conjuradores
**Problema:** Seção de slots de magia aparecia para Guerreiro, Bárbaro, Ladino etc.

**Solução:**
```javascript
const temMagia = this.combatente.tipo === 'jogador' && isClasseConjuradora(this.combatente.classe);
secao.style.display = temMagia ? 'flex' : 'none';
```

**Fonte de verdade:** `isClasseConjuradora()` de `combat-rules.js` — cobre Clérigo, Druida, Ranger, Mago, Feiticeiro, Bardo, Paladino.

**Resultado:** ✅ Seção de magias oculta para classes sem magia.

---

## Performance / Qualidade

---

### [2024/2025] N+1 em perícias — corrigido com batch query
**Problema:** `calcular_custo_pericia()` fazia 1 query por perícia ao listar (N+1).

**Solução:** `obter_custos_pericias()` faz 1 query com `IN (ids)` para todas as perícias de uma vez.

**Resultado:** ✅ Lista de 54 perícias = 2 queries (pericias + pericias_classes) em vez de 55.

---

### [2025] GZip Middleware ativado
**Adicionado:** `GZipMiddleware` no FastAPI com `minimum_size` configurável via env.

**Resultado:** Respostas grandes (lista de magias ~400 itens) comprimidas. Ganho em payload mobile.

---

### [2025] Cache em memória para catálogos
**Adicionado:** `CatalogCache` com TTL para endpoints de leitura pesada (`/magias`, `/pericias`, `/condicoes`).

**Resultado:** Segunda requisição ao catálogo retorna do cache em-memória, sem query ao Neon.

**Trade-off:** Cache é por instância — em caso de múltiplos workers, cada um tem seu próprio cache. Aceitável no free tier (1 worker).

---

## Decisões Arquiteturais

---

### Frontend: React/Vue vs Vanilla JS
**Decisão:** Vanilla JS com ES Modules.

**Motivo:** Sem build step. Deploy no Vercel é direto (arquivos estáticos). Curva de aprendizado menor. Para o volume de dados do projeto, não há necessidade de reatividade complexa.

**Trade-off:** Sem reatividade declarativa. Atualizações de DOM são manuais (`innerHTML`, `querySelector`).

**Revisitar se:** A complexidade da ficha de personagem crescer significativamente (ex: modo colaborativo em tempo real).

---

### Backend: FastAPI vs Django/Flask
**Decisão:** FastAPI.

**Motivo:** Async nativo, validação automática via Pydantic, Swagger gerado automaticamente, Python 3.11 type hints nativos.

**Resultado:** ✅ Correto para o caso de uso. Swagger `/docs` é usado ativamente para debug.

---

### Banco em produção: Neon vs PlanetScale vs Supabase
**Decisão:** Neon PostgreSQL.

**Motivo:** Free tier generoso (0.5GB storage, connection pooling). Serverless — branch computa-zero reduz custos. SQLAlchemy suporta nativamente.

**Trade-off:** "Branch scaling to zero" — primeira query após inatividade pode levar 1–3s extras para despertar o compute. Mitigado pelo cron-job que mantém o Render (e indiretamente o Neon) ativo.

**Alternativas se Neon mudar pricing:**
- Supabase (PostgreSQL + auth + storage)
- Fly.io Postgres (mais controle, mas mais configuração)
- PlanetScale (MySQL — requer mudança de queries)
