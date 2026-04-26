# Runbook — deploy e smoke test (produção)

Guia curto em **português (Brasil)** para deploy seguro da Arena TTRPG (API no **Render**, banco no **Neon**, front no **Vercel** ou domínio próprio). Não substitui backup completo nem revisão de código; evita esquecimentos comuns.

**Referências:** `README.md` (URLs de produção), `FIX_MIGRATIONS_STARTUP.md` (Alembic no startup), `docs/arquitetura-multi-jogo.md` (multi-jogo), `backend/.env.example`.

---

## URLs e painéis (este repositório)

Valores **como estão hoje no código / README** — se mudares o serviço no Render ou o domínio, atualiza o runbook e os ficheiros indicados.

### Site (produção)

| Uso | URL |
|-----|-----|
| Aplicação (apex) | `https://arena-de-combate-rpg.com.br` |
| Aplicação (www) | `https://www.arena-de-combate-rpg.com.br` |

### API (Render)

| Uso | URL |
|-----|-----|
| Origem da API (usada pelo front fora de `localhost`) | `https://projetorpg-7ih3.onrender.com` |
| Swagger / OpenAPI | `https://projetorpg-7ih3.onrender.com/docs` |
| Health (se exposto) | `https://projetorpg-7ih3.onrender.com/health` |

**Código:** a origem fixa do Render está em `frontend/games/dnd35/js/config/api.config.js` (`RENDER_API_ORIGIN`). Se criares **outro** Web Service ou URL no Render, **altera esse valor** e faz deploy do front (Vercel) para o browser voltar a bater na API certa.

### Preview do Vercel (`*.vercel.app`)

1. No [Vercel Dashboard](https://vercel.com) → o teu projeto → **Deployments** → abre o último deploy e copia a URL (ex.: `https://projeto-rpg-xxxxx.vercel.app`).
2. No **Render** → variável `ALLOWED_ORIGINS` (JSON array), inclui **essa URL** entre aspas, além do domínio de produção, senão o browser bloqueia CORS nos testes de preview.  
   Exemplo (uma linha, adapta ao teu caso):  
   `["https://arena-de-combate-rpg.com.br","https://www.arena-de-combate-rpg.com.br","https://projeto-rpg-xxxxx.vercel.app"]`
3. Smoke no preview: mesmos caminhos relativos (`/pages/login.html`, `/arena`, etc.) em cima da URL do preview.

### Neon (Postgres)

- Painel: [console.neon.tech](https://console.neon.tech) → escolhe o **projeto** ligado ao `DATABASE_URL` do Render → **Branches** (backup) e **SQL Editor** (queries da secção 4).

### Render (hospedagem da API)

- Painel: [dashboard.render.com](https://dashboard.render.com) → Web Service da API (nome pode ser `projetorpg` ou outro) → **Logs**, **Shell**, **Environment**.

---

## 1. Antes do deploy

1. **Backup do Neon**  
   No painel Neon: **Branches** → criar branch de backup **ou** export (`pg_dump`) conforme a tua rotina. Sem backup, não há volta fácil se algo correr mal no schema.

2. **Revisar variáveis no Render** (API)  
   - `DATABASE_URL` — string de conexão do Neon (com `sslmode=require` se aplicável).  
   - `SECRET_KEY`, `ADMIN_EMAIL`, `ADMIN_PASSWORD` em produção (obrigatórios conforme `config.py`).  
   - `ALLOWED_ORIGINS` — JSON com o domínio do **Vercel** e o site (ex.: `https://arena-de-combate-rpg.com.br`, `https://www.…`).  
   - `MULTI_GAME_STRICT_MODE` — manter **`false`** até fazer smoke com login + seletor de jogo + token com `game_slug`. Só ativa `true` quando quiseres bloqueio rígido D&D 3.5.

3. **Catálogo de magias (grimório)**  
   Se a tabela `magias` estiver **vazia** no Postgres:  
   - **Uma vez:** no Render, shell ou job one-off, a partir da pasta `backend/`:  
     `python scripts/seed_magias.py`  
   - **Ou** definir `SEED_MAGIAS_ON_EMPTY=1` no `.env` **só no primeiro arranque** com BD vazio (o startup pode demorar ~20–40 s). Em SQLite local vazio, o próprio startup já tenta popular — ver `init_db.py`.

---

## 2. Deploy

1. Fazer merge na branch que o **Render** faz deploy (ex.: `main`).  
2. Aguardar o build terminar e o serviço ficar **Live**.  
3. Se o deploy falhar no **startup** (migrations, seed), ver logs no Render antes de repetir.

---

## 3. Depois do deploy — Alembic (opcional mas recomendado)

Na máquina local (com o mesmo código que foi para produção) ou no **shell do Render**, com `DATABASE_URL` apontando para o Neon:

```bash
cd backend
export DATABASE_URL='postgresql://...neon...'   # colar a string do Render/Neon
alembic current
```

- Confirma que a revisão atual é a esperada (ex.: inclui migrações multi-jogo / equipamentos, etc.).  
- Se precisares de contexto: `alembic history -r -5:head` (últimas revisões).

> Em muitos ambientes o `main.py` já executa `alembic upgrade head` no startup; mesmo assim `alembic current` ajuda a **confirmar** o estado.

---

## 4. Depois do deploy — SQL rápido (Neon → SQL Editor)

Executar no **SQL Editor** do Neon (ajustar nomes de tabela se o teu schema divergir):

```sql
SELECT COUNT(*) AS total_magias FROM magias;
SELECT slug, status FROM games_catalog ORDER BY ordem;
SELECT COUNT(*) AS memberships FROM user_game_memberships;
```

- `total_magias` = 0 → grimório vazio até correres `seed_magias.py` (secção 1).  
- `games_catalog` deve listar pelo menos `dnd35` como disponível (ou o estado que configurares).

---

## 5. Smoke test no browser (ordem sugerida)

Substitui `https://arena-de-combate-rpg.com.br` pelo teu domínio real se for diferente.

| Ordem | O quê | URL / ação |
|------|--------|------------|
| 1 | Login | `https://arena-de-combate-rpg.com.br/pages/login.html` |
| 2 | Seletor de jogo (pós-login) | `…/pages/selecionar-jogo.html` — escolher **D&D 3.5** |
| 3 | Dashboard | `…/games/dnd35/pages/dashboard.html` |
| 4 | Arena — configuração | `…/arena` ou `…/games/dnd35/arena.html` — lista de combatentes carrega |
| 5 | Ficha + grimório | Abrir uma ficha conjuradora — grimório com magias e filtros por escola |

**Swagger (API no Render):** `https://projetorpg-7ih3.onrender.com/docs` (não depende do domínio do site no Vercel).

**Teste rápido de API (opcional):** no browser ou `curl` (catálogo público, normalmente sem token):

```text
GET https://projetorpg-7ih3.onrender.com/api/v1/magias/?classe=MAGO&limit=5
```

Deve devolver um **JSON array** com itens se a tabela `magias` estiver populada (ver secção 1 e `seed_magias.py`).

---

## 6. Se algo falhar

| Sintoma | Onde olhar |
|---------|------------|
| CORS / preflight | `ALLOWED_ORIGINS` no Render; `main.py` — `CORSMiddleware` e `OPTIONS` no rate limit |
| 404 na API a partir do Vercel | `getApiUrl` no front não pode apontar só para o domínio estático; ver skill `arena-ttrpg-architecture` |
| Coluna em falta / 500 na API | Logs Render + migrações; `FIX_MIGRATIONS_STARTUP.md` |
| Login ok mas páginas D&D 3.5 redirecionam | Token sem `game_slug` — passar pelo seletor de jogo; `MULTI_GAME_STRICT_MODE` |
| Grimório vazio com personagem conjurador | `SELECT COUNT(*) FROM magias;` — correr `python scripts/seed_magias.py` no `backend/` |

---

## 7. Checklist de uma linha (copiar para o Notion / issue)

`[ ] Backup Neon` → `[ ] Deploy Render OK` → `[ ] alembic current` → `[ ] SQL magias + games_catalog` → `[ ] Login → seletor D&D 3.5 → dashboard → arena → grimório` → `[ ] MULTI_GAME_STRICT_MODE só se já testado`

---

*Última atualização: URLs alinhadas a `README.md`, `api.config.js` (Render) e fluxo Neon + Render + Vercel. Atualiza este ficheiro se mudares domínio, nome do serviço ou URL de preview.*
