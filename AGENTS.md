# Governanca Operacional de Agentes

Este arquivo e a **fonte normativa principal** de instrucoes do projeto para humanos e agentes (Cursor, GitHub Copilot, etc.).

- **Regras por dominio (codigo, migrations, frontend):** [.github/instructions](.github/instructions) — sempre aplicar o ficheiro correspondente a area alterada.
- **Entrada para o GitHub Copilot:** [.github/copilot-instructions.md](.github/copilot-instructions.md) e apenas um **indicador** que aponta para este `AGENTS.md`; nao duplicar aqui normas longas.

## Idioma

- **Sempre responder em Portugues (Brasil)** em todas as mensagens, explicacoes e comentarios de codigo.

## Escopo geral

- Projeto fullstack TTRPG com backend FastAPI/SQLAlchemy e frontend HTML/CSS/JavaScript vanilla.
- Priorizar mudancas pequenas, de causa raiz e com baixo risco de regressao.
- Nao reverter mudancas existentes do usuario sem solicitacao explicita.
- Antes de implementar, ler contexto em [README.md](README.md) e instrucoes aplicaveis em [.github/instructions](.github/instructions).
- Em tarefas que toquem arquitetura, deploy, dados, schema ou decisoes historicas, consultar [HISTORICO_EVOLUCAO.md](HISTORICO_EVOLUCAO.md).

## Protocolo obrigatorio de implementacao

- Antes de qualquer refatoracao estetica/estrutural, priorizar validacao e preservacao dos requisitos funcionais do fluxo afetado.
- Em tarefas com uso de skills, agentes ou instrucoes especializadas, manter o mesmo protocolo de leitura de contexto documental antes de codar.
- Sempre priorizar reuso e modularidade: evitar duplicacao de regras, centralizar fonte de verdade e preservar contratos existentes.
- Aplicar SOLID e Clean Code em toda alteracao:
	- funcoes/metodos curtos com responsabilidade unica (SRP);
	- baixo acoplamento e alta coesao;
	- nomes claros e semanticos;
	- evitar logica duplicada e efeitos colaterais ocultos;
	- minimizar breaking changes e manter compatibilidade quando possivel.
- Ao concluir mudancas em fluxos sensiveis, validar impacto e registrar risco residual quando nao houver cobertura automatizada suficiente.

## Infra de producao

- **Frontend:** Vercel (estatico, CDN global) — dominio `arena-de-combate-rpg.com.br` via Cloudflare
- **Backend:** Render.com (free tier) — `https://projetorpg-7ih3.onrender.com` — branch `feature/salva`
- **Banco:** Neon PostgreSQL `ep-bold-night-ak4zfe7p` (us-west-2 Oregon) — serverless, connection pooling — co-localizado com o Render backend
- **Imagens:** Cloudinary — `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET` como env vars no Render
- **Anti-sleep:** cron-job.org `*/10 * * * *` → `GET /health` (evita cold start do Render free tier)
- **Deploy:** merge `feature/responsivo` → `feature/salva` aciona deploy automatico no Render
- **Dados em producao (critico):** antes de alterar `DATABASE_URL`, rodar migrations destrutivas ou mudar schemas em prod, consultar [PRE_DEPLOY_CHECKLIST.md](PRE_DEPLOY_CHECKLIST.md) (secao Protecao de dados em producao), a skill [.cursor/skills/arena-producao-dados-neon-render/SKILL.md](.cursor/skills/arena-producao-dados-neon-render/SKILL.md) e o bullet correspondente abaixo. No Render, health de startup: `GET /health/live`; monitoramento continuo: `GET /health`.

## Convencoes de versionamento frontend

- Scripts com cache-busting explicito: `?v=<numero>` nos imports de HTML.
- Ao modificar qualquer controller/service, incrementar o `?v=` correspondente no HTML (ver comentarios nos ficheiros ou historico recente para o valor atual).

## Onde estao as regras especificas

- Backend Python: [.github/instructions/backend.instructions.md](.github/instructions/backend.instructions.md)
- Frontend Web: [.github/instructions/frontend.instructions.md](.github/instructions/frontend.instructions.md)
- Migrations Alembic: [.github/instructions/migrations.instructions.md](.github/instructions/migrations.instructions.md)
- Historico de evolucao: [HISTORICO_EVOLUCAO.md](HISTORICO_EVOLUCAO.md)

## Referencias por tema (leitura antes de codar)

- Para evolucoes da ficha por classe/nivel (BBA, resistencias, defesas CA/Toque/Surpresa, iniciativa e habilidades especiais), consultar [docs/progressao-classes-bba-resistencias-habilidades.md](docs/progressao-classes-bba-resistencias-habilidades.md).
- Para pre-definicoes por raca e catalogo racial normalizado, consultar [docs/predefinicoes-raciais-contrato.md](docs/predefinicoes-raciais-contrato.md) e `docs/dados/racas_caracteristicas_catalogo.json`.
- Arquitetura de deploy (Vercel + Render, CORS, `getApiUrl`, rewrites): skill [.cursor/skills/arena-ttrpg-architecture/SKILL.md](.cursor/skills/arena-ttrpg-architecture/SKILL.md).
- Protecao de dados em producao (Neon branch, `DATABASE_URL`, PITR/snapshots, staging antes de prod, health `/health/live`): [PRE_DEPLOY_CHECKLIST.md](PRE_DEPLOY_CHECKLIST.md) (secao **Protecao de dados**) e skill [.cursor/skills/arena-producao-dados-neon-render/SKILL.md](.cursor/skills/arena-producao-dados-neon-render/SKILL.md).
- Conjuracao D&D 3.5 (atributo por classe, Tabela 1-1, clerigo, troca Bardo/Feiticeiro): [docs/regras-conjuracao-dnd-arena.md](docs/regras-conjuracao-dnd-arena.md) e skill [.cursor/skills/dnd-spellcasting-conventions/SKILL.md](.cursor/skills/dnd-spellcasting-conventions/SKILL.md).
- Arquitetura multi-jogo (Auth Hub global + jogos isolados, `games_catalog`, `game_slug` no token, seletor de jogo pos-login, guard `AuthService.exigirJogo`): [docs/arquitetura-multi-jogo.md](docs/arquitetura-multi-jogo.md).
- Contratos de repositorio para servicos (`typing.Protocol`, pacotes `ports` no backend): [docs/ports-repositorios-servicos.md](docs/ports-repositorios-servicos.md).
- GURPS 4E (ficha + arena, Lite primeiro): skill [.cursor/skills/gurps-4e-requisitos-ficha-arena/SKILL.md](.cursor/skills/gurps-4e-requisitos-ficha-arena/SKILL.md) e checklist em [melhoria-arquitetura](melhoria-arquitetura) (secao 7).
- Admin em dev: `ADMIN_EMAIL` + `ADMIN_PASSWORD` em `backend/.env` (exemplo em `backend/.env.example`); `criar_admin_padrao` no startup so cria se ambos estiverem definidos — ver secao de credenciais no [README.md](README.md).

## Orquestracao de agentes (definicoes)

- Agente coordenador recomendado: `Fullstack Orchestrator` em [.github/agents/fullstack-orchestrator.agent.md](.github/agents/fullstack-orchestrator.agent.md).
- Agente complementar para features com contrato entre camadas: `Fullstack API Contract Orchestrator` em [.github/agents/fullstack-api-contract-orchestrator.agent.md](.github/agents/fullstack-api-contract-orchestrator.agent.md).
- Agente especializado em levantamento de requisitos a partir de livros/PDFs/regras: `RPG Requirements Analyst` em [.github/agents/rpg-requirements-analyst.agent.md](.github/agents/rpg-requirements-analyst.agent.md).
- Especialistas recomendados: ver secao **Agentes** abaixo; ficheiros em [.github/agents](.github/agents).

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

- `RPG Requirements Analyst`
Usar quando for preciso transformar regras de livro, PDFs, documentos e mecanicas de D&D 3.5/TTRPG em requisitos funcionais, regras de negocio, criterios de aceite e impacto tecnico para a plataforma.

- `PDF Explore Specialist`
Usar quando for preciso extrair texto, tabelas e informacoes de PDFs com suporte a terminal e fallback OCR em PDFs escaneados.

## Regras de Orquestracao

- O orquestrador deve classificar primeiro a demanda por dominio.
- Delegar em paralelo apenas quando as frentes forem independentes.
- Se houver mudanca de schema, tratar persistencia antes da consolidacao completa de backend e frontend.
- Consolidar conflitos de contrato entre camadas antes de responder.
- Preservar autenticacao real, autorizacao por perfil, `getApiUrl()` no frontend e contratos existentes quando possivel.
- Quando o `RPG Requirements Analyst` receber pedido de execucao, deve preparar handoff estruturado e delegar ao `Fullstack Orchestrator`.
- Fluxo esperado para demandas multi-area:
	1. Classificar a solicitacao por dominio.
	2. Delegar para especialistas em paralelo apenas quando nao houver dependencia direta.
	3. Tratar schema e persistencia antes de consolidar impactos em backend/frontend quando necessario.
	4. Consolidar contratos, validacao e risco residual em uma resposta unica.

## Prompts Reutilizaveis

- Nova feature: [.github/prompts/nova-feature-fullstack.prompt.md](.github/prompts/nova-feature-fullstack.prompt.md)
- Correcao de bug: [.github/prompts/correcao-bug-fullstack.prompt.md](.github/prompts/correcao-bug-fullstack.prompt.md)
- Refatoracao segura: [.github/prompts/refatoracao-segura-por-dominio.prompt.md](.github/prompts/refatoracao-segura-por-dominio.prompt.md)
- Auditoria pre-merge: [.github/prompts/auditoria-pre-merge-fullstack.prompt.md](.github/prompts/auditoria-pre-merge-fullstack.prompt.md)
- Migration segura: [.github/prompts/migration-segura.prompt.md](.github/prompts/migration-segura.prompt.md)
- Deploy readiness: [.github/prompts/deploy-readiness-fullstack.prompt.md](.github/prompts/deploy-readiness-fullstack.prompt.md)
- Investigacao de performance: [.github/prompts/investigacao-performance-fullstack.prompt.md](.github/prompts/investigacao-performance-fullstack.prompt.md)
- Levantamento de requisitos RPG: [.github/prompts/levantamento-requisitos-rpg.prompt.md](.github/prompts/levantamento-requisitos-rpg.prompt.md)

## Skills Especializadas

- `rpg-requirements-analysis`
Workflow para transformar texto de regra, PDF ou documento em especificacao acionavel, separando regra da fonte, interpretacao operacional e decisao de produto.

- `dnd-spellcasting-conventions` ([.cursor/skills/dnd-spellcasting-conventions/SKILL.md](.cursor/skills/dnd-spellcasting-conventions/SKILL.md))
Atributo de conjuracao por classe, Tabela 1-1, planilhas Excel, clerigo (dominio), troca de magias Bardo/Feiticeiro e pontos de codigo.

- `class-progression-conventions` ([.cursor/skills/class-progression-conventions/SKILL.md](.cursor/skills/class-progression-conventions/SKILL.md))
Convencoes de progressao por classe na ficha (BBA, resistencias, defesas, iniciativa e habilidades especiais), incluindo regra de `bonus_ca` de Armadura/Item de Protecao, com contrato entre backend/frontend/banco e compatibilidade legada.

## Hooks

- Configuracao de hooks do workspace: [.github/hooks](.github/hooks)
- Hook atual: [.github/hooks/operational-safety.json](.github/hooks/operational-safety.json)
- Script do hook: [.github/hooks/scripts/pre_tool_use_guard.py](.github/hooks/scripts/pre_tool_use_guard.py)
- Papel atual: aumentar seguranca operacional antes de comandos destrutivos de terminal e modificacoes SQL sensiveis.
- Hooks devem permanecer pequenos, auditaveis e focados em enforcement real; nao usar hooks para duplicar instrucoes textuais.

## Estado de referencia do banco (producao)

*Snapshot indicativo; validar no ambiente real quando for critico.*

- `pericias_classes`: populada com 175 associacoes (11 classes x pericias D&D 3.5)
- Custo de pericias: 1 pt (da classe) / 2 pts (fora da classe) — calculado via `obter_custos_pericias()`
- Seeds aplicados em producao: magias (~400+), pericias (54), pericias_classes (175), condicoes (25)

## Armazenamento de imagens

- `FileService` roteia automaticamente: Cloudinary quando `CLOUDINARY_*` configurado (producao), filesystem local senao (dev).
- `foto_url` no banco armazena URL HTTPS absoluta do Cloudinary em producao (ex: `https://res.cloudinary.com/...`).
- Em dev local, `foto_url` armazena URL relativa `/uploads/<uuid>.ext` — normal, nao confundir com bug.
- Nunca armazene imagens apenas no filesystem do Render — e efemero e perdido em cada deploy/restart.
- Ao deletar combatente com foto, `FileService.deletar_arquivo()` lida com ambos os casos automaticamente.

## Repositorios e protocols (backend)

- Novos ou alterados servicos que injetam repositorio devem alinhar-se aos `Protocol` em `backend/app/shared/ports/` (hub) e `backend/app/games/<jogo>/ports/` (por jogo), conforme [docs/ports-repositorios-servicos.md](docs/ports-repositorios-servicos.md).
- O repositorio concreto nao precisa herdar o `Protocol`; o construtor do servico e que deve ser anotado com o contrato.

## Convencoes transversais

- Preserve autenticacao real e autorizacao por perfil; nao introduza atalhos permissivos.
- Ao mexer em fluxos criticos (auth, cache, listagens, migrations), valide o impacto e informe risco residual quando nao houver teste automatizado.
- Para textos de interface, prefira portugues consistente com o restante do produto.
- `isClasseConjuradora()` de `combat-rules.js` e a fonte de verdade para quais classes tem magia — usar em vez de listas manuais.
- `getApiUrl()` de `api.config.js` e obrigatorio em todos os services/controllers do frontend; nunca hardcode localhost ou URL de producao.

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

### Levantamento de requisitos a partir de livro ou PDF

Use o prompt `Levantamento Requisitos RPG` ou o agente `RPG Requirements Analyst`.

Exemplo de pedido:

```text
/Levantamento Requisitos RPG
Analisar as regras de familiars no Livro do Jogador de D&D 3.5 e transformar isso em requisitos funcionais, regras de negocio, impacto tecnico e criterios de aceite para a plataforma.
```

## Manutencao desta governanca

- Alterar normas, listas e protocolos **neste** `AGENTS.md` (e em `.github/instructions/` por dominio).
- Manter `.github/copilot-instructions.md` como entrada minima; nao voltar a duplicar paragrafos longos la.
