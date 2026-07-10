# Runbook — alinhar Alembic no Neon produção

Projeto: **projetoRPG_Oreon** (Neon, `us-west-2`)  
API: `https://projetorpg-7ih3.onrender.com`  
Head atual do repositório: `p1q2r3s4t5u6`

## Por que não usar `alembic upgrade head` agora?

| Situação | Detalhe |
|----------|---------|
| `alembic_version` | `a7b9d3e1c2f4` (desatualizado) |
| Schema real | Tabelas Tormenta, OAuth, handouts, convite etc. **já existem** em `public` |
| Migration `fase_c_schemas_auth_dnd35` | Moveria tabelas D&D/auth para schemas `dnd35` / `auth` — a app usa `public` |
| Migrations antigas | Várias fazem `CREATE TABLE` sem checar existência → erro "already exists" |

O schema foi evoluído por **guards no `main.py`**, deploys parciais e hotfix SQL. O histórico Alembic não reflete isso.

**Procedimento seguro:** `alembic stamp head` após pre-check (registra o head sem reexecutar SQL).

## Antes de começar

1. [ ] Confirmar no [Neon Console](https://console.neon.tech) → projeto **projetoRPG_Oreon** → branch **production**
2. [ ] **Backup:** Backup & Restore (PITR) ou criar branch de backup no Neon
3. [ ] Copiar `DATABASE_URL` do **Render** (Environment do serviço de produção) — não usar `.env` local
4. [ ] Janela de manutenção curta (opcional; stamp é rápido e não altera dados)

## Passo a passo

### 1. Exportar URL (só no seu terminal — nunca commitar)

```bash
export DATABASE_URL='postgresql://USER:PASS@ep-xxx-pooler.c-3.us-west-2.aws.neon.tech/neondb?sslmode=require'
```

### 2. Pre-check

```bash
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f scripts/neon-producao-alembic-precheck.sql
```

Se o bloco `DO $$` levantar exceção, **pare** e investigue antes de continuar.

### 3. Alinhar (script automatizado)

```bash
chmod +x scripts/neon-producao-alinhar-alembic.sh
./scripts/neon-producao-alinhar-alembic.sh
```

Ou manualmente:

```bash
cd backend
alembic current
alembic stamp head
alembic current   # deve mostrar p1q2r3s4t5u6 (head)
```

### 4. Validar produção

```bash
curl -sS https://projetorpg-7ih3.onrender.com/health
```

Smoke manual:

- Login no dashboard
- Abrir ficha Tormenta com campanha
- Listar campanhas / personagens

### 5. Próximo deploy

O `Procfile` executa `alembic upgrade head` antes do uvicorn. Com `alembic_version` no head, isso vira **no-op** — sem tentar recriar tabelas nem mover schemas.

## Depois do stamp

| Cenário | Ação |
|---------|------|
| Nova migration no repo | `alembic upgrade head` no deploy (normal) |
| Hotfix SQL manual no Neon | Criar migration idempotente no código + upgrade, ou repetir stamp se schema já estiver aplicado |
| Branch staging | Pode testar `upgrade head` em branch Neon separada antes de prod |

## Rollback

`stamp` só altera `alembic_version`. Para reverter o registro:

```bash
cd backend
alembic stamp a7b9d3e1c2f4
```

Isso **não** desfaz colunas/tabelas. Para rollback de schema, use PITR/snapshot do Neon.

## Referências

- [PRE_DEPLOY_CHECKLIST.md](../PRE_DEPLOY_CHECKLIST.md) — proteção de dados
- Skill `.cursor/skills/arena-producao-dados-neon-render/SKILL.md`
- `scripts/reconcile_alembic_neon.sql` — reconciliação antiga (multi-hash); **não** usar neste caso
