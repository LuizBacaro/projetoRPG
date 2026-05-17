# Passo a passo: CI/CD com GitHub Actions (Arena / projetoRPG)

Este guia explica como o repositório [LuizBacaro/projetoRPG](https://github.com/LuizBacaro/projetoRPG) usa o workflow [`.github/workflows/ci.yml`](.github/workflows/ci.yml), o que configurar no GitHub (secrets, **Environments**, proteções) e como alinhar com **Render** (API) e **Vercel** (frontend estático), sem deploy duplicado nem surpresas no banco.

---

## 1. O que a esteira faz hoje

| Gatilho | O que roda |
|--------|------------|
| **Push** em `feature/**`, `develop`, `feature/salva`, `main`, `master` | `backend` (lint + pytest + coverage), `migrations` (Postgres + Alembic), `frontend` (ESLint + teste JS). |

**Normas de lint/format do backend (evitar falha no deploy):** [docs/normas-qualidade-backend-ci.md](docs/normas-qualidade-backend-ci.md) — rodar `make ci-backend-lint` antes do push.
| **Pull request** com base nessas branches | O mesmo acima. |
| **Push** em `develop` | Após jobs verdes: job **`deploy-staging`** (hooks opcionais). |
| **Push** em `feature/salva` | Roda também **E2E** (Playwright); depois **`deploy-prod`** (hook opcional + smoke em `/health/live` + smoke GURPS opcional). |
| **`workflow_dispatch`** | Permite acionar E2E manualmente (`run_e2e = true`). |

Fluxo de branches alvo do produto:

- **`feature/*`** — integração contínua: validar código em toda branch de feature, **sem** deploy automático de produção.
- **`develop`** — ambiente de **desenvolvimento/staging** após merge ou push direto (conforme sua política de equipe).
- **`feature/salva`** — ramo acordado para **produção** (alinhado ao `AGENTS.md` e ao deploy no Render).

---

## 2. Pré-requisitos no GitHub

1. Acesse [Actions](https://github.com/LuizBacaro/projetoRPG/actions) e confirme que **GitHub Actions está habilitado** para o repositório.  
   **Settings** → **Actions** → **General** → *Allow all actions and reusable workflows* (ou a política que sua organização exigir).

2. O ficheiro do workflow deve estar na branch default (normalmente `main` ou `master`) **ou** na branch que dispara o evento; o GitHub usa o workflow do commit que recebeu o push/PR.

---

## 3. Environments (ambientes) — o que criar e por quê

Os jobs `deploy-staging` e `deploy-prod` usam:

```yaml
environment: staging
# ...
environment: production
```

Isso ativa o painel **Settings** → **Environments** do GitHub: secrets específicos por ambiente, revisores obrigatórios, branches permitidas, etc.

### 3.1. Criar o environment `staging`

1. Repositório → **Settings** → **Environments** → **New environment**.  
2. Nome: **`staging`** (exatamente esse nome, igual ao `ci.yml`).  
3. Opcional mas recomendado:  
   - **Deployment branches** → *Selected branches* → adicionar `develop` (e `main` se quiser).  
   - **Required reviewers** → 0 ou 1 revisor (staging costuma ser mais leve).

### 3.2. Criar o environment `production`

1. **New environment** → nome: **`production`**.  
2. Recomendado para produção:  
   - **Required reviewers** → pelo menos **1** aprovador antes de cada deploy.  
   - **Deployment branches** → apenas **`feature/salva`** (ou a branch que você fixar como produção).  
   - **Wait timer** → opcional (ex.: 5 minutos para cancelar deploy acidental).

Sem esses environments, o workflow pode falhar ao referenciar `environment: staging` / `production` **se** o repositório exigir que o environment exista previamente (comportamento padrão: o primeiro deploy cria o environment automaticamente em muitos casos; criar manualmente evita surpresas).

### 3.3. Onde colocar cada secret

| Secret | Onde colocar (recomendado) | Uso |
|--------|----------------------------|-----|
| `RENDER_DEPLOY_HOOK_STAGING` | Environment **`staging`** ou *Repository secrets* | `curl -X POST` dispara rebuild no Render (staging). |
| `RENDER_DEPLOY_HOOK_PROD` | Environment **`production`** ou *Repository secrets* | Deploy API produção. |
| `VERCEL_TOKEN` | `staging` (e/ou *Repository*) | `vercel --prod` no job de staging. |
| `SMOKE_TOKEN_GURPS` | **`production`** | JWT válido com jogo GURPS para smoke do catálogo Lite (opcional). |
| `ADMIN_EMAIL`, `ADMIN_PASSWORD` | *Repository secrets* (opcional) | E2E usa fallback local se vazios. |
| `SLACK_WEBHOOK` | *Repository secrets* (opcional) | Notificação em falha. |

**Dica de segurança:** secrets de **produção** (`RENDER_DEPLOY_HOOK_PROD`, `SMOKE_TOKEN_GURPS`) ficam mais seguros só no environment **`production`**, não como secret global do repositório.

**Como adicionar:**  
**Settings** → **Secrets and variables** → **Actions** → **Environments** → escolha `staging` / `production` → **Add secret**.

---

## 4. Secrets detalhados

### 4.1. `RENDER_DEPLOY_HOOK_STAGING` e `RENDER_DEPLOY_HOOK_PROD`

**São obrigatórios?** Não. Ambos são **opcionais**: se o secret não existir, o passo correspondente apenas registra `::warning::` e o workflow segue. Use isso para configurar staging/produção em momentos diferentes.

**Quando faz sentido criar cada um:**

| Secret | Quando criar | Quando deixar de fora |
|---|---|---|
| `RENDER_DEPLOY_HOOK_PROD` | Quer que o GitHub Actions seja o **único** gatilho do deploy de produção (modelo B da seção 5). Você desliga o auto-deploy do Render para `feature/salva` e deixa o Actions disparar via hook. | Prefere que o **Render** continue fazendo auto-deploy ao push em `feature/salva` (modelo A); use o Actions só para CI. |
| `RENDER_DEPLOY_HOOK_STAGING` | Você criou um **segundo Web Service no Render** apontando para a branch `develop` (com Neon branch separado). | Não tem ambiente de staging ainda; pode esperar até criar um serviço dedicado. |

**Qual valor colocar:** uma URL inteira gerada pelo próprio Render (não é um token nem um caminho). Formato:

```text
https://api.render.com/deploy/srv-XXXXXXXXXXXXXXXXXX?key=YYYYYYYYYYYYYYYY
```

**Como obter no Render:**

1. Render Dashboard → abra o **Web Service** desejado (produção, ou um segundo serviço para staging).  
2. **Settings** → **Build & Deploy** → seção **Deploy Hook** → clique em **Create Hook** (ou copie a URL existente).  
3. Copie a URL completa, sem aspas, sem espaços extras.

**Como salvar no GitHub:**

1. Repositório → **Settings** → **Environments** → escolha o environment correspondente:  
   - `RENDER_DEPLOY_HOOK_STAGING` → environment **`staging`**.  
   - `RENDER_DEPLOY_HOOK_PROD` → environment **`production`**.  
2. **Add secret** → **Name**: o nome exato (`RENDER_DEPLOY_HOOK_STAGING` ou `RENDER_DEPLOY_HOOK_PROD`) → **Value**: a URL completa do Render.  
3. Salvar.

> Manter os secrets dentro do environment (em vez de *Repository secrets*) limita o acesso ao job correto e permite usar **required reviewers** para o environment de produção.

**Como testar com segurança:**

- Faça um push em `develop` (staging) ou `feature/salva` (produção).  
- O job de deploy correspondente vai chamar `curl -fsS -X POST <URL>`. Se a URL estiver correta, o Render inicia um build e responde `200`.  
- Se a URL estiver errada, o step falha e o erro aparece no Actions, sem afetar o serviço em execução (o Render só inicia build com URL válida).

### 4.2. `VERCEL_TOKEN`

**Onde fica:** **no GitHub**, não no Render. O Render hospeda só a API (backend); o **Vercel** publica o frontend, e quem precisa autenticar é o job `deploy-staging` rodando no GitHub Actions, que chama `vercel --prod` a partir da pasta `frontend/`.

**Secrets ou Variables?** Sempre **Environment secrets**.

| | Environment **secrets** | Environment **variables** |
|---|---|---|
| Conteúdo é mascarado nos logs | Sim (`***`) | Não (texto puro) |
| Acessado por | `${{ secrets.VERCEL_TOKEN }}` | `${{ vars.NOME }}` |
| Adequado para credenciais | Sim | Não |

`VERCEL_TOKEN` é uma credencial pessoal de deploy: tem que ir em **Environment secrets** para o GitHub mascarar o valor nos logs.

**Passo a passo:**

1. [Vercel Account Settings → Tokens](https://vercel.com/account/tokens) → **Create Token**. Escolha o time/conta correto e copie o valor (só aparece uma vez).  
2. No GitHub, repositório → **Settings** → **Environments** → **`staging`** → **Add secret** (na seção **Environment secrets**).  
3. **Name**: `VERCEL_TOKEN`. **Value**: cole o token. Salvar.

**Por que no environment `staging`** (e não em *Repository secrets*): o job tem `environment: staging`, então o GitHub injeta o secret só naquele contexto e respeita as proteções do environment (branches permitidas, revisores).

**`VERCEL_ORG_ID` / `VERCEL_PROJECT_ID` (opcional):** se o `vercel --prod` perguntar “Which scope?” / “Link to existing project?”, adicione também:

- `VERCEL_ORG_ID` em **Environment variables** (não é sensível).  
- `VERCEL_PROJECT_ID` em **Environment variables**.

Para o setup atual, só **`VERCEL_TOKEN`** já basta.

### 4.3. `SMOKE_TOKEN_GURPS` (opcional)

Token JWT de um usuário de teste com acesso ao jogo **GURPS**, usado só no job `deploy-prod` para chamar:

`GET /api/v1/gurps/personagens/catalogo/lite-ficha`

Se não configurar, o passo de smoke GURPS é omitido. O smoke de **`/health/live`** só roda quando **`RENDER_DEPLOY_HOOK_PROD`** está definido (pressupõe que um deploy acabou de ser disparado pelo hook).

**Não** commite tokens; renove se vazar.

### 4.4. `ADMIN_EMAIL` / `ADMIN_PASSWORD` (E2E)

Opcionais. Se os secrets não existirem no GitHub, o valor chega vazio e o step **Start API server** usa `export ADMIN_EMAIL="${ADMIN_EMAIL:-admin@arena.local}"` (e o mesmo para a senha), ou seja, fallback local no runner.

### 4.5. `SLACK_WEBHOOK` (opcional)

URL de **Incoming Webhook** do Slack. O job `notify-failure` envia um JSON com `curl` e `jq` (disponível no `ubuntu-latest`). Se o secret estiver ausente, o passo só emite aviso e termina com sucesso.

### 4.6. Secrets e condicionais no YAML

O workflow **não** depende de `if: ${{ secrets.ALGO != '' }}` nos steps (há limitações e comportamentos inconsistentes no motor do GitHub). Em vez disso, os valores vão para `env:` do job e o step em **bash** verifica `[ -z "${NOME:-}" ]` antes de chamar `curl` ou `vercel`.

---

## 5. Render: evitar deploy duplicado

Hoje o [`Procfile`](Procfile) na raiz já faz:

```text
cd backend && alembic upgrade head && … && uvicorn …
```

Ou seja, **cada deploy no Render já aplica Alembic antes do uvicorn**.

Se no GitHub Actions você **também** dispara o mesmo serviço via Deploy Hook em **todo** push para `feature/salva`, pode haver **dois deploys** (auto-deploy do Render no merge **e** o hook do Actions).

**Escolha um modelo:**

| Modelo | O que fazer |
|--------|-------------|
| **A — Só Render (auto deploy)** | Não defina `RENDER_DEPLOY_HOOK_PROD` no GitHub. Use Actions só para **CI** (testes + Alembic em Postgres). Configure o Render para fazer deploy ao push na branch `feature/salva`. |
| **B — Só GitHub (hook)** | No Render, **desative** auto-deploy por branch ou limite a branches que não sejam `feature/salva`. Defina `RENDER_DEPLOY_HOOK_PROD` e deixe o Actions ser o único gatilho. |

O mesmo raciocínio vale para **staging** (`develop`).

---

## 6. Variáveis obrigatórias no Render (produção)

O backend valida em **`production`** e **`staging`**:

- `DATABASE_URL` deve ser **PostgreSQL** (`postgresql://` após normalização; `postgres://` da Neon é aceito e convertido).  
- **Não** pode ser SQLite (evita o erro `table gurps_campanhas already exists` causado por `create_all` + Alembic em banco efêmero).

Além disso:

- `ENVIRONMENT=production` (ou `staging` no ambiente de homologação).  
- `SECRET_KEY`, `ADMIN_EMAIL`, `ADMIN_PASSWORD` em produção (já exigidos pela app).

Comportamento do startup (resumo):

- Com **`STARTUP_RUN_ALEMBIC=1`**: só **Alembic** no passo crítico (sem `create_all` antes).  
- Com **`STARTUP_RUN_ALEMBIC=0`** (padrão em produção se a variável não estiver definida): espera Alembic no **Procfile**; a app usa **`create_all`** para compatibilidade com bases antigas.

Detalhes no código: `backend/app/main.py` (`_inicializar_banco_critico`, `_executar_alembic_migrations`) e `backend/app/shared/core/config.py`.

---

## 7. Fluxo de trabalho recomendado para a equipa

1. Criar branch **`feature/nome-da-tarefa`** a partir de `develop`.  
2. Abrir **Pull Request** para `develop`.  
   - Actions roda: backend + migrations + frontend + E2E.  
3. Revisar e fazer merge em **`develop`**.  
   - Push em `develop` dispara **deploy-staging** (se os secrets existirem).  
4. Quando estiver estável, abrir PR **`develop` → `feature/salva`** (ou merge direto, conforme governança).  
5. Após merge/push em **`feature/salva`**:  
   - E2E + **deploy-prod** (se `RENDER_DEPLOY_HOOK_PROD` configurado) + smoke.

---

## 8. Como acompanhar e depurar

1. [Actions](https://github.com/LuizBacaro/projetoRPG/actions) → clique no workflow **CI/CD Pipeline** → abra a execução falha.  
2. Verifique qual job falhou: `backend`, `migrations`, `frontend`, `e2e`, `deploy-*`.
3. Se o job `backend` falhou em **Lint and format code**, aplicar [docs/normas-qualidade-backend-ci.md](docs/normas-qualidade-backend-ci.md) (`make format-backend` + `make ci-backend-lint`).  
4. **Migrations**: erros de Alembic (head múltiplo, SQL, ordem de revisões) aparecem primeiro neste job.  
5. **E2E**: confira se `/health/live` subiu (timeout indica crash no startup, muitas vezes migração ou `DATABASE_URL`).

---

## 9. Checklist rápido antes do primeiro deploy via Actions

- [ ] Criados environments **`staging`** e **`production`** no GitHub.  
- [ ] Definido `RENDER_DEPLOY_HOOK_STAGING` (se quiser deploy automático de staging).  
- [ ] Definido `RENDER_DEPLOY_HOOK_PROD` **ou** desligado auto-deploy duplicado no Render.  
- [ ] `DATABASE_URL` no Render aponta para **Neon** (branch correto).  
- [ ] `ENVIRONMENT=production` no serviço de produção.  
- [ ] (Opcional) `SMOKE_TOKEN_GURPS` para validar catálogo GURPS pós-deploy.  
- [ ] (Opcional) `SLACK_WEBHOOK` para alertas de falha.

---

## 10. Referências no repositório

| Ficheiro | Conteúdo |
|----------|----------|
| [`.github/workflows/ci.yml`](.github/workflows/ci.yml) | Pipeline completa. |
| [`Procfile`](Procfile) | Alembic + uvicorn no Render. |
| [`PRE_DEPLOY_CHECKLIST.md`](PRE_DEPLOY_CHECKLIST.md) | Dados e migrações em produção. |
| [`.cursor/skills/arena-producao-dados-neon-render/SKILL.md`](.cursor/skills/arena-producao-dados-neon-render/SKILL.md) | Neon + Render. |
| [`.cursor/skills/arena-ttrpg-architecture/SKILL.md`](.cursor/skills/arena-ttrpg-architecture/SKILL.md) | CORS, front, API. |

---

## 11. Ajustes futuros (opcional)

- **Path filters** (`dorny/paths-filter`): não rodar backend quando só mudou documentação.  
- **Matriz** Python 3.11 / 3.12.  
- **Cache** npm com `package-lock.json` se passar a usar lockfile no frontend.  
- **Deploy de produção só por tag** `v*` em vez de push em branch.

Se algo neste passo a passo divergir do que aparece na UI do GitHub (nomes de menus mudam com o tempo), use a busca nas **Settings** do repositório por *Environments*, *Secrets*, *Actions*.
