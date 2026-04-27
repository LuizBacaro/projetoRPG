# Fase C: Janela de execução (template preenchível)

Use este documento como checklist executável no dia da mudança.

## Metadados da janela

- Data: `<YYYY-MM-DD>`
- Horário início (UTC-3): `<HH:MM>`
- Horário fim previsto (UTC-3): `<HH:MM>`
- Ambiente: `staging`
- Executor técnico: `<nome>`
- Revisor técnico: `<nome>`
- Aprovador go/no-go: `<nome>`
- Ticket/issue: `<link>`

## Variáveis de execução

```bash
export STAGING_DB_URL="<postgresql://...>"
export BACKUP_FILE="staging_pre_fase_c_<YYYYMMDD_HHMM>.dump"
```

## Pré-check (T-60 a T-15)

- [ ] Branch/tag confirmada: `<tag>`
- [ ] Deploy concorrente bloqueado
- [ ] Backup executado
- [ ] Restore testado
- [ ] Suíte backend sem e2e verde
- [ ] Comunicação de janela enviada

## Execução (T0)

### 1) Backup

```bash
pg_dump "$STAGING_DB_URL" --format=custom --file "$BACKUP_FILE"
```

Evidência: `<colar saída/resumo>`

### 2) Head atual (antes)

```bash
cd backend
python3 -m alembic -c alembic.ini current
python3 -m alembic -c alembic.ini heads
```

Evidência: `<colar saída>`

### 3) Aplicar migration

```bash
cd backend
python3 -m alembic -c alembic.ini upgrade head
```

Evidência: `<colar saída>`

### 4) Verificar schemas

```sql
SELECT schema_name FROM information_schema.schemata
WHERE schema_name IN ('auth', 'dnd35');

SELECT table_schema, table_name
FROM information_schema.tables
WHERE table_schema IN ('auth', 'dnd35')
ORDER BY table_schema, table_name;
```

Evidência: `<colar saída>`

## Smoke pós-migration (T+0 a T+15)

- [ ] `/api/v1/auth/login` OK
- [ ] `/api/v1/auth/refresh` OK
- [ ] `/api/v1/games` autenticado OK
- [ ] `/api/v1/games/selecionar` OK
- [ ] `/api/v1/combatentes` OK
- [ ] `/api/v1/campanhas` OK

Evidência: `<links/logs>`

## Queries de integridade

```sql
SELECT COUNT(*) FROM auth.usuarios;
SELECT COUNT(*) FROM auth.games_catalog;
SELECT COUNT(*) FROM auth.user_game_memberships;
SELECT COUNT(*) FROM dnd35.combatentes;
SELECT COUNT(*) FROM dnd35.campanhas;
SELECT COUNT(*) FROM dnd35.magias;
```

Evidência: `<colar saída>`

## Decisão Go / No-Go

- Decisão: `<GO|NO-GO>`
- Horário: `<HH:MM>`
- Responsável: `<nome>`
- Observações: `<texto>`

## Rollback (se NO-GO)

### Opção A: downgrade Alembic

```bash
cd backend
python3 -m alembic -c alembic.ini downgrade a7b9d3e1c2f4
```

### Opção B: restore backup

```bash
pg_restore --clean --if-exists --no-owner --dbname "$STAGING_DB_URL" "$BACKUP_FILE"
```

Pós-rollback:

- [ ] Reexecutar smoke crítico
- [ ] Registrar causa raiz e próximos passos

## Encerramento

- [ ] Log final publicado
- [ ] Documento anexado ao ticket
- [ ] Próxima ação definida (promover para produção ou abrir correções)

