---
description: "Planeja e implementa uma migration segura com avaliacao de impacto em schema, dados legados e compatibilidade SQLite/PostgreSQL."
name: "Migration Segura"
argument-hint: "Descreva a alteracao de schema desejada, dados afetados e impacto funcional esperado"
agent: "Fullstack API Contract Orchestrator"
model: ["GPT-5 (copilot)", "Claude Sonnet 4.5 (copilot)"]
---
Receba a solicitacao abaixo e trate como uma alteracao real de schema deste projeto.

Objetivos do fluxo:
- Revisar models, migrations existentes, README, historico e instrucoes aplicaveis antes de editar.
- Definir impacto em schema, dados legados, backend e frontend.
- Garantir migration incremental, reversivel quando possivel e segura para deploy.
- Considerar defaults, backfill, colunas nulas, compatibilidade SQLite local e PostgreSQL em producao.
- Consolidar riscos de rollout e validacoes necessarias.

Criticos deste projeto:
- Nao reescrever historico Alembic ja aplicado.
- Em alteracoes criticas, tratar transicao de dados e compatibilidade de endpoints dependentes.
- Se o estado real do banco em execucao for necessario, considerar apoio do `PostgreSQL Database Administrator`.

Solicitacao do usuario:

{{input}}