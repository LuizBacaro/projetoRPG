---
description: "Regras para migrations Alembic e evolucao de schema: cadeia de revisoes, compatibilidade SQLite e seguranca de upgrade."
applyTo: "backend/alembic_migrations/**/*.py"
---

# Migrations Instructions

- Respeitar cadeia Alembic atual em `backend/alembic_migrations`.
- Nao reescrever historico de revisoes ja aplicado; criar nova revisao incremental.
- Em SQLite local, operacoes nao suportadas (ex.: `ALTER COLUMN`) devem ser tratadas como no-op seguro quando necessario.

## Compatibilidade e Deploy

- Garantir que upgrade local e em producao nao quebre startup.
- Evitar migrations destrutivas sem backfill/estrategia de transicao.
- Quando houver alteracao de coluna critica, considerar defaults e preenchimento de dados legados.

## Validacao

- Validar impacto em endpoints que dependem do schema alterado.
- Em mudancas sensiveis, documentar risco residual se nao houver teste automatizado cobrindo o caso.
