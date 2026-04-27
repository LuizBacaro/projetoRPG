# Fase C Runbook: execução em staging (`auth` / `dnd35`)

Status: pronto para uso (abr/2026)  
Escopo: checklist operacional para janela de migração Postgres schemas

Template preenchível para uso no dia da mudança:  
`docs/fase-c-janela-execucao-template.md`

Rascunho inicial já preenchido (data/base):  
`docs/fase-c-janela-execucao-staging-rascunho.md`

## Objetivo

Executar a migration de schemas da Fase C em staging com segurança,
observabilidade e rollback validado.

## Pré-requisitos

- ADR lido: `docs/fase-c-adr-schemas-postgres.md`
- Inventário técnico validado: `docs/fase-c-inventario-tecnico-schemas.md`
- Migration presente:  
  `backend/alembic_migrations/versions/fase_c_schemas_auth_dnd35_skeleton.py`
- Janela de manutenção definida e aprovada.
- Acesso ao banco staging com permissões de DDL.

## Responsáveis (preencher antes da janela)

- Executor técnico:
- Revisor técnico:
- Owner do produto:
- Aprovador go/no-go:

## Checklist pré-janela (T-60 a T-15)

- [ ] Confirmar branch/tag da release.
- [ ] Confirmar `DATABASE_URL` aponta para **staging**.
- [ ] Confirmar que não há deploy concorrente em andamento.
- [ ] Executar backup lógico do banco staging.
- [ ] Validar restauração do backup em ambiente de teste.
- [ ] Rodar suíte backend sem e2e com o código da release.
- [ ] Confirmar endpoints críticos para smoke:
  - `/api/v1/auth/*`
  - `/api/v1/games/*`
  - `/api/v1/combatentes/*`
  - `/api/v1/campanhas/*`

## Comandos base (staging)

> Ajustar variáveis e paths conforme o ambiente real.

### 1) Backup antes da migration

```bash
export STAGING_DB_URL="postgresql://..."
pg_dump "$STAGING_DB_URL" --format=custom --file "staging_pre_fase_c.dump"
```

### 2) Verificar head atual

```bash
cd backend
python3 -m alembic -c alembic.ini current
python3 -m alembic -c alembic.ini heads
```

### 3) Aplicar migration

```bash
cd backend
python3 -m alembic -c alembic.ini upgrade head
```

### 4) Verificação rápida de schemas

```sql
SELECT schema_name FROM information_schema.schemata
WHERE schema_name IN ('auth', 'dnd35');

SELECT table_schema, table_name
FROM information_schema.tables
WHERE table_schema IN ('auth', 'dnd35')
ORDER BY table_schema, table_name;
```

## Smoke funcional pós-migration (T+0 a T+15)

- [ ] Login (`/api/v1/auth/login`) retorna 200 para usuário válido.
- [ ] Refresh token (`/api/v1/auth/refresh`) retorna 200.
- [ ] Catálogo de jogos (`/api/v1/games`) responde corretamente autenticado.
- [ ] Seleção de jogo (`/api/v1/games/selecionar`) emite token com `game_slug`.
- [ ] Listagem de combatentes (`/api/v1/combatentes`) sem erro de schema/FK.
- [ ] Rotas de campanhas (`/api/v1/campanhas`) sem erro de schema/FK.

## Consultas de validação de integridade

```sql
-- Tabelas hub no schema auth
SELECT COUNT(*) FROM auth.usuarios;
SELECT COUNT(*) FROM auth.games_catalog;
SELECT COUNT(*) FROM auth.user_game_memberships;

-- Tabelas D&D no schema dnd35
SELECT COUNT(*) FROM dnd35.combatentes;
SELECT COUNT(*) FROM dnd35.campanhas;
SELECT COUNT(*) FROM dnd35.magias;
```

## Critérios de Go / No-Go

### Go

- Migration aplica sem erro.
- Smoke funcional crítico verde.
- Sem erros recorrentes de `relation does not exist` / FK nos logs.

### No-Go

- Erro de migration sem correção imediata.
- Falha em login/troca de jogo/combatentes/campanhas.
- Erros de schema/FK persistentes após retry controlado.

## Rollback

### Opção A: Downgrade Alembic (preferida se íntegro)

```bash
cd backend
python3 -m alembic -c alembic.ini downgrade a7b9d3e1c2f4
```

### Opção B: Restore do backup (se downgrade não for suficiente)

```bash
pg_restore --clean --if-exists --no-owner --dbname "$STAGING_DB_URL" "staging_pre_fase_c.dump"
```

Após rollback:

- [ ] Reexecutar smoke de auth/games/combatentes/campanhas.
- [ ] Registrar causa raiz e ações corretivas antes de nova janela.

## Evidências a anexar

- Output do `alembic current` antes/depois.
- Log de execução da migration.
- Resultado das queries de verificação.
- Resultado dos smokes.
- Decisão final (Go/No-Go) com horário.

