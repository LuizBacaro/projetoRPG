# Guia de Orquestracao de Agentes

Este documento explica como a orquestracao de agentes foi estruturada neste workspace e qual e o papel de cada tipo de customizacao.

O objetivo e deixar claro:

- o que a pasta `.github` faz;
- o que o runtime do Copilot faz;
- como funcionam agentes e subagentes;
- quando usar instructions, skills, prompts e hooks;
- como iniciar uma demanda nova usando o orquestrador.

## Visao Geral

Neste projeto, a `.github` nao e o motor que executa agentes. Ela funciona como a camada de configuracao e governanca.

Em termos práticos:

- `.github` define papeis, regras, contexto e atalhos reutilizaveis;
- o runtime do Copilot no VS Code decide como carregar essas definicoes e executar a conversa;
- o orquestrador pode chamar subagentes quando o ambiente suportar essa delegacao.

Resumo curto:

- `.github` organiza a inteligencia operacional;
- o Copilot executa a orquestracao;
- hooks reforcam comportamentos deterministicos;
- prompts e agentes facilitam a entrada correta em cada fluxo.

## O Que a `.github` Faz Neste Projeto

Neste workspace, a pasta `.github` foi usada para centralizar:

- instrucoes gerais do projeto;
- instrucoes por dominio;
- agentes especializados;
- prompts reutilizaveis;
- hooks operacionais.

Estrutura principal:

- `.github/copilot-instructions.md`
- `.github/instructions/`
- `.github/agents/`
- `.github/prompts/`
- `.github/hooks/`

Isso permite que o projeto tenha uma governanca consistente para tarefas de frontend, backend, banco, migrations, revisoes e features completas.

## O Que o Runtime do Copilot Faz

O runtime do Copilot e a camada que realmente interpreta a solicitacao do usuario e decide o fluxo de execucao.

Quando voce pede algo como uma feature nova, o runtime pode:

- carregar as instrucoes gerais do projeto;
- considerar instructions especificas do dominio afetado;
- usar um prompt reutilizavel como ponto de entrada;
- acionar um agente customizado;
- permitir que esse agente invoque subagentes especializados.

Ou seja, a `.github` nao executa nada sozinha. Ela prepara o terreno para o runtime agir de forma mais organizada.

## Agentes

Agentes sao personas especializadas com escopo, ferramentas e comportamento definidos em arquivos `.agent.md`.

No projeto, eles ficam em `.github/agents/`.

Exemplos deste workspace:

- `Fullstack Orchestrator`
- `Fullstack API Contract Orchestrator`
- `Backend FastAPI Specialist`
- `Frontend Arena Specialist`
- `Database and Migrations Specialist`
- `PostgreSQL Database Administrator`
- `JavaScript Project Auditor`

Cada agente define, por exemplo:

- quando deve ser usado;
- quais ferramentas pode usar;
- se pode chamar outros agentes;
- como deve conduzir o trabalho;
- como deve formatar a resposta.

## Orquestrador

O orquestrador e um agente coordenador. Ele nao existe para saber mais sobre um dominio especifico, mas para decompor a demanda e chamar os especialistas corretos.

Neste projeto, esse papel e feito principalmente por:

- `Fullstack Orchestrator`

E, para demandas fortemente guiadas por contrato entre camadas:

- `Fullstack API Contract Orchestrator`

As responsabilidades do orquestrador sao:

- classificar a demanda por dominio;
- decidir a ordem de execucao;
- delegar para um ou mais especialistas;
- evitar conflito entre frontend, backend e banco;
- consolidar a resposta final.

## Subagentes

Subagentes sao agentes chamados por outro agente.

Na pratica, o fluxo funciona assim:

1. Voce faz um pedido ao orquestrador.
2. O orquestrador avalia a demanda.
3. Se a tarefa for simples, ele pode resolver sem delegar.
4. Se a tarefa for transversal, ele pode chamar um ou mais subagentes.
5. Depois ele consolida o resultado em uma resposta unica.

Exemplo:

Uma feature nova de familiar pode exigir:

- `Database and Migrations Specialist` para modelagem e migration;
- `Backend FastAPI Specialist` para API, services e autorizacao;
- `Frontend Arena Specialist` para interface e integracao.

Importante: a capacidade de um agente chamar subagentes depende do runtime suportar esse fluxo. A estrutura do projeto ja esta preparada para isso.

## O Orquestrador Chama os Agentes Sozinho?

Sim, essa e a intencao da configuracao atual.

Quando voce aciona o `Fullstack Orchestrator`, ele foi configurado para decidir se precisa chamar:

- nenhum agente;
- um especialista;
- varios especialistas.

O comportamento esperado e:

- demanda simples: pode resolver sozinho;
- demanda de um dominio: chama um especialista;
- demanda multi-area: chama dois ou mais especialistas;
- demanda com schema: trata persistencia antes de consolidar backend e frontend.

O que define isso nao e uma automacao externa fixa, mas a decisao do runtime do agente com base nas regras dos arquivos de customizacao.

## Instructions

Instructions sao regras textuais que orientam o comportamento do agente.

No projeto, existem dois niveis principais:

- `.github/copilot-instructions.md`: regras gerais do workspace;
- `.github/instructions/*.md`: regras por dominio.

Exemplos deste projeto:

- backend: arquitetura em camadas, seguranca e compatibilidade de API;
- frontend: modo modulo/global, auth, binds e cache-busting;
- migrations: cadeia Alembic, rollout seguro e compatibilidade SQLite/PostgreSQL.

Instructions nao executam nada de forma deterministica. Elas guiam o comportamento do agente.

## Skill

Skills sao pacotes reutilizaveis orientados a tarefas especificas. Normalmente aparecem como fluxos especializados que o agente pode carregar sob demanda.

No projeto, existem skills como:

- `canvas-design`
- `frontend-design-teste`
- `javascript-audit`
- `pdf`
- `postgresql`

Em geral, uma skill faz sentido quando:

- a tarefa e especifica e recorrente;
- existe um mini-workflow reutilizavel;
- vale a pena encapsular conhecimento, passos e eventualmente assets auxiliares.

Em comparacao:

- instruction = regra geral ou contextual;
- skill = fluxo especializado reutilizavel.

## Prompt

Prompts sao atalhos reutilizaveis para iniciar um tipo de trabalho com contexto e orientacao ja preparados.

No projeto, eles ficam em `.github/prompts/`.

Exemplos atuais:

- `Nova Feature Fullstack`
- `Correcao Bug Fullstack`
- `Refatoracao Segura por Dominio`
- `Auditoria Pre-Merge Fullstack`
- `Migration Segura`
- `Deploy Readiness Fullstack`
- `Investigacao Performance Fullstack`

Em vez de escrever tudo do zero no chat, voce pode usar um prompt como ponto de partida.

Exemplo:

```text
/Nova Feature Fullstack
Adicionar sistema de familiar vinculado ao personagem, com persistencia no banco, CRUD no backend, exibicao na ficha e validacoes de permissao por usuario.
```

## Hooks

Hooks sao automacoes deterministicamente executadas em eventos do ciclo do agente.

Eles sao diferentes de instructions:

- instruction orienta;
- hook fiscaliza ou reforca comportamento em tempo de execucao.

Neste projeto, existe atualmente:

- `.github/hooks/operational-safety.json`
- `.github/hooks/scripts/pre_tool_use_guard.py`

Esse hook foi criado para pedir atencao extra antes de:

- comandos potencialmente destrutivos em terminal;
- modificacoes SQL sensiveis.

Ele nao substitui as instrucoes. Ele atua como um guarda operacional.

## Quando Usar Cada Coisa

Use este mapa mental:

- instruction: quando a regra vale para uma classe ampla de tarefas;
- agent: quando voce precisa de uma persona especializada com escopo proprio;
- subagent: quando um agente precisa delegar parte do trabalho;
- skill: quando existe um workflow reutilizavel e especializado;
- prompt: quando voce quer iniciar uma tarefa recorrente com um atalho bem definido;
- hook: quando o comportamento precisa de enforcement deterministico.

## Arquitetura Atual de Governanca

Hoje, a governanca deste projeto esta distribuida assim:

- fonte normativa principal: `.github/copilot-instructions.md`;
- resumo operacional do time: `AGENTS.md`;
- regras por dominio: `.github/instructions/`;
- especialistas e coordenadores: `.github/agents/`;
- atalhos de entrada: `.github/prompts/`;
- enforcement operacional leve: `.github/hooks/`.

## Exemplo de Uso do Orquestrador

### Exemplo 1: feature nova completa

Pedido no chat:

```text
/Nova Feature Fullstack
Adicionar sistema de familiar vinculado ao personagem, com:
- persistencia no banco
- CRUD no backend
- exibicao na ficha do personagem
- permissao por usuario
- compatibilidade com personagens antigos sem familiar
```

Fluxo esperado:

1. O `Fullstack Orchestrator` classifica a demanda como banco + backend + frontend.
2. Ele aciona `Database and Migrations Specialist` para modelagem e migration.
3. Ele aciona `Backend FastAPI Specialist` para endpoints, services, schemas e autorizacao.
4. Ele aciona `Frontend Arena Specialist` para interface e integracao.
5. Ele consolida tudo em uma resposta unica.

### Exemplo 2: feature guiada por contrato

Pedido no chat:

```text
Use o Fullstack API Contract Orchestrator para implementar preparacao de magias por circulo com novo payload entre ficha, API e persistencia, sem quebrar classes nao conjuradoras.
```

Fluxo esperado:

1. O agente define o contrato alvo.
2. Coordena schema e backend.
3. Valida impacto no frontend.
4. Consolida naming, obrigatoriedade, estados de erro e compatibilidade.

## Limites Importantes

- A `.github` nao e um motor autonomo de execucao.
- O runtime do Copilot e quem decide e executa o fluxo.
- Nem toda tarefa obrigatoriamente precisara de subagentes.
- Hooks nao devem virar uma segunda camada de instrucoes longas.
- `AGENTS.md` neste projeto e um resumo operacional, nao a fonte normativa principal.

## Recomendacao de Uso Diario

Para o dia a dia do time:

- use prompts para iniciar tarefas recorrentes;
- use o orquestrador para demandas multi-area;
- use o agente de contrato quando a integracao entre camadas for a parte mais critica;
- use o DBA apenas quando precisar confirmar o estado real do banco em execucao;
- mantenha hooks pequenos, auditaveis e focados em seguranca operacional.

## Documentos Relacionados

- [README.md](README.md)
- [HISTORICO_EVOLUCAO.md](HISTORICO_EVOLUCAO.md)
- [AGENTS.md](AGENTS.md)
- [.github/copilot-instructions.md](.github/copilot-instructions.md)
- [.github/instructions](.github/instructions)
- [.github/agents](.github/agents)
- [.github/prompts](.github/prompts)
- [.github/hooks](.github/hooks)