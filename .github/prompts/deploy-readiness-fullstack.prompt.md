---
description: "Valida se uma feature ou conjunto de mudancas esta pronto para deploy, cobrindo contratos, riscos operacionais, migrations, frontend e backend."
name: "Deploy Readiness Fullstack"
argument-hint: "Descreva a feature, branch ou conjunto de alteracoes que deseja validar antes do deploy"
agent: "Fullstack Orchestrator"
model: ["GPT-5 (copilot)", "Claude Sonnet 4.5 (copilot)"]
---
Receba a solicitacao abaixo e trate como checklist tecnico pre-deploy deste projeto.

Objetivos do fluxo:
- Auditar se a mudanca esta coerente entre frontend, backend, persistencia e infraestrutura relevante.
- Procurar riscos de regressao, contratos quebrados, falhas de autenticacao, cache-busting ausente e migrations inseguras.
- Identificar lacunas de validacao, testes e passos operacionais necessarios.
- Responder com parecer claro: pronto, pronto com ressalvas, ou nao pronto.

Criticos deste projeto:
- Preservar autenticacao real e autorizacao por perfil.
- Verificar `getApiUrl()` no frontend e `Authorization: Bearer <token>` nos fluxos protegidos.
- Validar impacto em Render, Vercel, Neon e Cloudinary quando a mudanca tocar essas integracoes.
- Verificar cache-busting `?v=` em controllers/services carregados via HTML quando aplicavel.

Solicitacao do usuario:

{{input}}