---
description: "Planeja e executa uma nova feature fullstack com coordenacao entre frontend, backend e banco quando necessario."
name: "Nova Feature Fullstack"
argument-hint: "Descreva a feature, os requisitos funcionais, regras de negocio e restricoes"
agent: "Fullstack Orchestrator"
model: ["GPT-5 (copilot)", "Claude Sonnet 4.5 (copilot)"]
---
Receba a solicitacao abaixo e trate como uma feature real deste projeto.

Objetivos do fluxo:
- Classificar a demanda por dominio: frontend, backend, banco ou multiplos.
- Ler README, historico e instrucoes aplicaveis antes de propor ou editar.
- Delegar para especialistas quando a tarefa envolver mais de uma area.
- Executar em paralelo apenas o que nao tiver dependencia direta.
- Consolidar contratos, validacoes, testes e risco residual em uma resposta unica.

Criticos deste projeto:
- Preservar autenticacao real e autorizacao por perfil.
- Nao hardcode URL de API no frontend.
- Em alteracoes com schema, tratar migration incremental e compatibilidade SQLite/PostgreSQL.
- Em alteracoes de frontend com controllers/services servidos por HTML, verificar cache-busting `?v=` quando aplicavel.
- Seguir especificacao minima (SDD leve): [docs/fluxo-spec-driven-leve.md](../../docs/fluxo-spec-driven-leve.md) — criterios de aceite no PR/issue; nova rota com schemas + teste; regras de jogo com levantamento RPG ou doc/skill canonica; ADR curto apenas para decisoes dificeis de reverter.

Solicitacao do usuario:

{{input}}