# Governanca Operacional de Agentes

Este arquivo resume como o time deve usar os agentes e prompts deste workspace.

Fonte normativa principal de instrucoes do projeto: [.github/copilot-instructions.md](.github/copilot-instructions.md).
Instrucoes detalhadas por dominio: [.github/instructions](.github/instructions).
Este `AGENTS.md` existe como resumo operacional e guia de uso para o time.

## Escopo

- Projeto fullstack TTRPG com backend FastAPI/SQLAlchemy e frontend HTML/CSS/JavaScript vanilla.
- Priorizar mudancas pequenas, de causa raiz e com baixo risco de regressao.
- Antes de implementar, ler contexto em [README.md](README.md) e instrucoes aplicaveis em [.github/instructions](.github/instructions).
- Em tarefas que toquem arquitetura, deploy, dados, schema ou decisoes historicas, consultar [HISTORICO_EVOLUCAO.md](HISTORICO_EVOLUCAO.md).

## Agentes

- `Fullstack Orchestrator`
Responsavel por triagem da demanda, decomposicao por dominio, delegacao para especialistas e consolidacao final.

- `Fullstack API Contract Orchestrator`
Responsavel por features com contrato entre frontend, backend e persistencia, com foco em payload, validacoes, responses e compatibilidade entre camadas.

- `Backend FastAPI Specialist`
Responsavel por API, services, repositories, models, autenticacao e testes backend.

- `Frontend Arena Specialist`
Responsavel por HTML, CSS, JavaScript vanilla, integracao com API, eventos, cache-busting e responsividade.

- `Database and Migrations Specialist`
Responsavel por models, Alembic, seeds, compatibilidade SQLite/PostgreSQL e seguranca de rollout de schema.

- `PostgreSQL Database Administrator`
Usar quando for preciso verificar ou operar no estado real do PostgreSQL em execucao.

- `JavaScript Project Auditor`
Usar para auditoria ampla do codigo JavaScript, hotspots, riscos e roadmap tecnico.

## Regras de Orquestracao

- O orquestrador deve classificar primeiro a demanda por dominio.
- Delegar em paralelo apenas quando as frentes forem independentes.
- Se houver mudanca de schema, tratar persistencia antes da consolidacao completa de backend e frontend.
- Consolidar conflitos de contrato entre camadas antes de responder.
- Preservar autenticacao real, autorizacao por perfil, `getApiUrl()` no frontend e contratos existentes quando possivel.

## Prompts Reutilizaveis

- Nova feature: [.github/prompts/nova-feature-fullstack.prompt.md](.github/prompts/nova-feature-fullstack.prompt.md)
- Correcao de bug: [.github/prompts/correcao-bug-fullstack.prompt.md](.github/prompts/correcao-bug-fullstack.prompt.md)
- Refatoracao segura: [.github/prompts/refatoracao-segura-por-dominio.prompt.md](.github/prompts/refatoracao-segura-por-dominio.prompt.md)
- Auditoria pre-merge: [.github/prompts/auditoria-pre-merge-fullstack.prompt.md](.github/prompts/auditoria-pre-merge-fullstack.prompt.md)
- Migration segura: [.github/prompts/migration-segura.prompt.md](.github/prompts/migration-segura.prompt.md)
- Deploy readiness: [.github/prompts/deploy-readiness-fullstack.prompt.md](.github/prompts/deploy-readiness-fullstack.prompt.md)
- Investigacao de performance: [.github/prompts/investigacao-performance-fullstack.prompt.md](.github/prompts/investigacao-performance-fullstack.prompt.md)

## Hooks

- Configuracao de hooks do workspace: [.github/hooks](.github/hooks)
- Hook atual: [.github/hooks/operational-safety.json](.github/hooks/operational-safety.json)
- Script do hook: [.github/hooks/scripts/pre_tool_use_guard.py](.github/hooks/scripts/pre_tool_use_guard.py)
- Papel atual: aumentar seguranca operacional antes de comandos destrutivos de terminal e modificacoes SQL sensiveis.

## Fluxo Recomendado

1. Receber a demanda e identificar se e feature, bug, refatoracao, review, migration, deploy ou performance.
2. Escolher o prompt ou agente adequado.
3. Ler documentacao minima obrigatoria antes de editar.
4. Delegar por dominio quando houver mais de uma camada envolvida.
5. Validar impacto, testes e risco residual antes de consolidar a resposta.

## Exemplos de Uso

### Feature nova fullstack

Use o prompt `Nova Feature Fullstack` ou o agente `Fullstack Orchestrator`.

Exemplo de pedido:

```text
/Nova Feature Fullstack
Adicionar sistema de familiar vinculado ao personagem, com persistencia no banco, CRUD no backend, exibicao na ficha e validacoes de permissao por usuario.
```

Comportamento esperado do orquestrador:

1. Classificar dominios: banco, backend e frontend.
2. Acionar `Database and Migrations Specialist` para modelagem, migration e impacto de dados.
3. Acionar `Backend FastAPI Specialist` para endpoints, services, schemas e autorizacao.
4. Acionar `Frontend Arena Specialist` para UI, integracao com API e cache-busting se houver controller/service alterado.
5. Consolidar contrato final, validacoes executadas e risco residual.

### Mudanca centrada em contrato entre camadas

Use o agente `Fullstack API Contract Orchestrator`.

Exemplo de pedido:

```text
Implementar preparacao de magias por circulo com novo payload entre ficha, API e persistencia, sem quebrar classes nao conjuradoras.
```

### Estado real do banco

Use `PostgreSQL Database Administrator` quando precisar confirmar schema real, dados existentes, indices, performance ou executar operacoes SQL auditaveis.

## Observacoes

- Este arquivo resume a governanca operacional; detalhes de implementacao e restricoes continuam centralizados em [.github/copilot-instructions.md](.github/copilot-instructions.md) e nos arquivos de [.github/instructions](.github/instructions).
- Se o time decidir migrar a governanca principal para `AGENTS.md`, o ideal e reduzir ou remover a duplicidade com o `copilot-instructions.md` em uma etapa dedicada.