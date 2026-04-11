---
description: "Investiga e corrige bug fullstack com triagem entre frontend, backend e banco quando necessario."
name: "Correcao Bug Fullstack"
argument-hint: "Descreva o bug, sintomas, passos para reproduzir, comportamento esperado e logs/erros se houver"
agent: "Fullstack Orchestrator"
model: ["GPT-5 (copilot)", "Claude Sonnet 4.5 (copilot)"]
---
Receba a solicitacao abaixo e trate como um bug real deste projeto.

Objetivos do fluxo:
- Identificar o dominio principal afetado: frontend, backend, banco ou integracao entre camadas.
- Ler contexto relevante antes de editar: README, historico e instrucoes aplicaveis.
- Isolar causa raiz antes de propor correcao.
- Delegar para especialistas quando o bug atravessar mais de uma area.
- Validar regressao, impacto colateral e risco residual.

Criticos deste projeto:
- Nao quebrar autenticacao real e autorizacao por perfil.
- Nao hardcode URL de API no frontend.
- Preservar contratos existentes sempre que possivel.
- Em alteracoes de schema, tratar migration incremental e compatibilidade SQLite/PostgreSQL.
- Em alteracoes de frontend com controllers/services servidos por HTML, verificar cache-busting `?v=` quando aplicavel.

Solicitacao do usuario:

{{input}}