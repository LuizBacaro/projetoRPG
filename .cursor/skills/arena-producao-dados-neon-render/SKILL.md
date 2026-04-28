---
name: arena-producao-dados-neon-render
description: >-
  Regras criticas para nao perder dados de producao: Neon (branch, PITR, snapshots),
  Render (DATABASE_URL, health /health/live), staging antes de prod, migrations e seeds.
  Usar em deploy, variaveis de ambiente, Alembic em Postgres, incidentes de banco ou
  quando o usuario pedir garantias sobre dados em producao.
---

# Arena TTRPG — producao: proteger dados (Neon + Render)

## Fonte normativa no repositorio

- Checklist detalhado e tabelas: [PRE_DEPLOY_CHECKLIST.md](../../../PRE_DEPLOY_CHECKLIST.md) (secao **Protecao de dados em producao**).
- Deploy e URLs: [.cursor/skills/arena-ttrpg-architecture/SKILL.md](../arena-ttrpg-architecture/SKILL.md).

## Regras que o agente deve lembrar

1. **`DATABASE_URL` no servico de producao do Render** tem de apontar **so** para o Postgres de producao no Neon (branch acordado, ex. `production`). Nunca assumir que um `.env` local ou string copiada e a mesma base.

2. **Staging separado**: idealmente outro branch Neon + outro `DATABASE_URL` / outro servico Render. Deploy e migrations testam primeiro fora de producao.

3. **Neon**: `Backup & Restore` — point-in-time restore tem **janela limitada** (ex.: horas no free). Fora disso: `pg_dump` periodico ou plano com retencao maior. Antes de mudanca grande: snapshot ou branch de backup quando o painel permitir.

4. **Render**: health check de deploy em **`/health/live`**; `/health` continua util para verificar BD depois.

5. **Migrations / seeds**: evitar `DROP`/`TRUNCATE`/reseed destrutivo em producao; preferir idempotencia (ver secao 7.1 do PRE_DEPLOY).

## O que NAO prometer ao usuario

- Nao garantir "nunca perder dados" de forma absoluta; sim **camadas** (URL correta, staging, backups, PITR, dump).

## Se o usuario relatar dados "sumidos"

1. Confirmar se o `DATABASE_URL` aponta para o projeto/branch certos.
2. Neon: `Backup & Restore` — restore no tempo dentro da janela.
3. Logs do Render no startup (migrations, erros).
