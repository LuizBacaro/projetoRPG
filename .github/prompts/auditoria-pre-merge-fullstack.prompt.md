---
description: "Executa uma auditoria tecnica pre-merge para identificar riscos, regressao comportamental, lacunas de teste e inconsistencias entre camadas."
name: "Auditoria Pre-Merge Fullstack"
argument-hint: "Descreva a feature, branch, PR ou conjunto de mudancas que deseja auditar"
agent: "Fullstack Orchestrator"
model: ["GPT-5 (copilot)", "Claude Sonnet 4.5 (copilot)"]
---
Receba a solicitacao abaixo e trate como uma revisao tecnica pre-merge deste projeto.

Objetivos do fluxo:
- Priorizar achados por severidade: bugs, regressao comportamental, risco de integracao, contrato quebrado e falta de testes.
- Identificar quais dominios precisam ser auditados: frontend, backend, banco ou multiplos.
- Delegar para especialistas quando a revisao exigir leitura aprofundada por dominio.
- Responder em formato de review, com foco principal em findings.
- Destacar risco residual quando nao houver validacao automatizada suficiente.

Criticos deste projeto:
- Preservar autenticacao real e autorizacao por perfil.
- Verificar integracao frontend/backend em payloads, erros e estados vazios.
- Verificar impacto em migrations, schema e compatibilidade SQLite/PostgreSQL quando houver persistencia.
- Verificar cache-busting de frontend quando controllers/services servidos por HTML forem alterados.

Solicitacao do usuario:

{{input}}