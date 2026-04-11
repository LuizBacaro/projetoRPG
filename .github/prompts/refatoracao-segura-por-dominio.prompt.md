---
description: "Planeja e executa uma refatoracao segura focada em um dominio especifico, com baixo risco de regressao e preservacao de contratos."
name: "Refatoracao Segura por Dominio"
argument-hint: "Descreva o dominio, o problema de manutencao e a refatoracao desejada"
agent: "Fullstack Orchestrator"
model: ["GPT-5 (copilot)", "Claude Sonnet 4.5 (copilot)"]
---
Receba a solicitacao abaixo e trate como refatoracao controlada neste projeto.

Objetivos do fluxo:
- Delimitar o dominio principal da refatoracao: backend, frontend, banco, JS global/modular ou combinacao.
- Revisar o codigo existente antes de propor mudancas estruturais.
- Priorizar refatoracao incremental, com alteracoes pequenas e justificadas.
- Evitar breaking changes e preservar contratos publicos quando possivel.
- Destacar claramente ganhos esperados, riscos e validacoes necessarias.

Criticos deste projeto:
- Preservar autenticacao, autorizacao e fluxos sensiveis.
- Manter a arquitetura em camadas no backend.
- Respeitar o modo de carregamento atual no frontend: modulo vs global.
- Nao introduzir duplicacao de regras nem listas manuais onde ja existe fonte de verdade.
- Em alteracoes de frontend com controllers/services servidos por HTML, verificar cache-busting `?v=` quando aplicavel.

Solicitacao do usuario:

{{input}}