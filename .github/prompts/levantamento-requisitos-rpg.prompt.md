---
description: "Levanta requisitos funcionais, regras de negocio e impactos tecnicos a partir de livro, PDF, documento ou mecanica de D&D 3.5/TTRPG."
name: "Levantamento Requisitos RPG"
argument-hint: "Descreva a fonte, o tema e o objetivo do levantamento"
agent: "RPG Requirements Analyst"
model: ["GPT-5 (copilot)", "Claude Sonnet 4.5 (copilot)"]
---
Receba a solicitacao abaixo e trate como um levantamento formal de requisitos para esta plataforma.

Objetivos do fluxo:
- Identificar a fonte analisada e delimitar o escopo do levantamento.
- Separar regra original, interpretacao operacional e decisao de produto.
- Extrair requisitos funcionais, regras de negocio, requisitos tecnicos e criterios de aceite.
- Mapear impacto em frontend, backend, banco, API, testes e riscos.
- Sinalizar ambiguidades e perguntas que precisam de decisao antes da implementacao.

Criticos deste projeto:
- Preservar autenticacao real e autorizacao por perfil.
- Manter contratos existentes quando possivel.
- Em alteracoes de frontend, considerar cache-busting `?v=` se houver controllers/services alterados.
- Em alteracoes de schema, tratar migration incremental e compatibilidade SQLite/PostgreSQL.
- Evitar reproducao extensa de texto protegido por direitos autorais; preferir sintese estruturada.

Solicitacao do usuario:

{{input}}
