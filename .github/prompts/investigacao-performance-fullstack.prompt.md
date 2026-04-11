---
description: "Investiga gargalos de performance em frontend, backend ou banco, priorizando causa raiz, metricas e correcoes de maior impacto."
name: "Investigacao Performance Fullstack"
argument-hint: "Descreva o sintoma de lentidao, onde ocorre, como reproduzir e qualquer evidencia observada"
agent: "Fullstack Orchestrator"
model: ["GPT-5 (copilot)", "Claude Sonnet 4.5 (copilot)"]
---
Receba a solicitacao abaixo e trate como investigacao de performance deste projeto.

Objetivos do fluxo:
- Identificar o dominio principal do problema: frontend, backend, banco ou integracao.
- Levantar hipoteses com base em codigo, fluxo e configuracao existente antes de otimizar.
- Delegar para especialistas quando a lentidao puder estar distribuida entre camadas.
- Priorizar causa raiz, impacto percebido pelo usuario e custo de correcao.
- Entregar findings, recomendacoes e validacao possivel com os recursos disponiveis.

Criticos deste projeto:
- Evitar micro-otimizacoes sem evidencia.
- Se o problema envolver banco em execucao, considerar uso do `PostgreSQL Database Administrator` para diagnostico real.
- Em frontend, considerar cache, carga de scripts, binds redundantes e chamadas de API repetidas.
- Em backend, considerar consultas, servicos, serializacao, autenticacao e startup.

Solicitacao do usuario:

{{input}}