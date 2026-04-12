---
name: rpg-requirements-analysis
description: "Levantamento de requisitos funcionais, regras de negocio e impactos tecnicos a partir de livros, PDFs, documentos e mecanicas de D&D 3.5/TTRPG. Use quando precisar transformar texto de regra em especificacao acionavel para a plataforma."
---

# Skill de Levantamento de Requisitos RPG

Use esta skill quando a tarefa for interpretar regras de livro, PDF ou documento e converter isso em especificacao clara para o produto.

## Objetivo

Transformar uma fonte textual em um pacote de analise que diferencie:
- regra original;
- interpretacao operacional para a plataforma;
- requisitos funcionais;
- regras de negocio;
- requisitos tecnicos;
- decisoes pendentes de produto.

## Fontes Aceitas

- PDF do livro do jogador ou suplemento.
- Documento funcional interno.
- Texto colado pelo usuario.
- Descricao de funcionalidade inspirada em regra de D&D 3.5.

## Principios

- Nao assumir que a plataforma precisa reproduzir a regra literal sem adaptacao.
- Rotular explicitamente o que e regra da fonte e o que e decisao de produto.
- Preservar compatibilidade com a arquitetura existente do projeto.
- Quando a fonte for protegida por direitos autorais, evitar reproduzir trechos longos; priorizar resumo, classificacao e referencia local da origem.

## Metodo de Analise

1. Delimitar escopo
- Identificar capitulo, paginas, tema ou mecanica.
- Definir o que entra e o que fica fora do levantamento.

2. Extrair conceitos nucleares
- Entidades envolvidas.
- Acoes permitidas.
- Estados e transicoes.
- Restricoes e pre-condicoes.
- Excecoes e casos especiais.

3. Separar camadas de entendimento
- Regra da fonte: o que o livro ou documento efetivamente define.
- Interpretacao operacional: como isso vira comportamento do sistema.
- Decisao de produto: simplificacoes, cortes, defaults e limites adotados pela plataforma.

4. Classificar os requisitos
- Requisitos funcionais.
- Regras de negocio.
- Requisitos tecnicos.
- Requisitos de dados e persistencia.
- Requisitos de validacao e autorizacao.
- Requisitos de observabilidade e testes quando aplicavel.

5. Mapear impacto tecnico
- Frontend: telas, estados, validacoes, UX e cache-busting se houver controllers/services alterados.
- Backend: rotas, schemas, services, repositories, dependencias e seguranca.
- Banco: models, migrations, seeds, constraints e backfill.
- Testes: unidade, integracao, regressao e casos de borda.

6. Identificar ambiguidades
- Pontos em que a fonte e ambigua.
- Pontos em que o produto precisa decidir UX ou simplificacao.
- Pontos que exigem validacao com implementacao existente.

## Template de Saida

### 1. Contexto
- Fonte analisada.
- Escopo do levantamento.

### 2. Resumo interpretativo
- Sintese curta da mecanica ou necessidade.

### 3. Requisitos funcionais
- Lista objetiva do que o sistema precisa fazer.

### 4. Regras de negocio
- Formulas, restricoes, permissao, limites, gatilhos e excecoes.

### 5. Requisitos tecnicos
- API, persistencia, processamento, integracoes, performance e seguranca.

### 6. Ambiguidades e decisoes pendentes
- O que precisa de confirmacao antes de implementar.

### 7. Criterios de aceite
- Cenarios verificaveis em linguagem de negocio.

### 8. Backlog inicial
- Fatias pequenas, independentes e implementaveis.

## Checklist de Qualidade

- A resposta separa claramente regra, interpretacao e decisao de produto.
- Os requisitos podem virar task tecnica sem releitura extensa da fonte.
- As excecoes relevantes foram capturadas.
- O impacto por camada foi mapeado.
- Existe criterio de aceite suficiente para validar implementacao.

## Quando Escalar

Escalar para especialista quando a analise exigir confirmacao concreta no codigo:
- `Backend FastAPI Specialist` para contratos, autorizacao e services.
- `Frontend Arena Specialist` para impacto em UI, controllers e integracao.
- `Database and Migrations Specialist` para schema, migration e persistencia.
- `Fullstack API Contract Orchestrator` quando a funcionalidade atravessar varias camadas com payloads sensiveis.
