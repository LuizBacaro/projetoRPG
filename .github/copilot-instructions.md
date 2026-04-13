# Copilot Instructions

Este workspace usa instrucoes granulares por dominio em `.github/instructions`.

## Idioma

- **Sempre responder em Portugues (Brasil)** em todas as mensagens, explicacoes e comentarios de codigo.

## Escopo Geral

- Projeto fullstack TTRPG com backend FastAPI/SQLAlchemy e frontend HTML/CSS/JavaScript vanilla.
- Priorize mudancas pequenas e de causa raiz; evite reformatacao ampla sem necessidade.
- Nao reverta mudancas existentes do usuario sem solicitacao explicita.

## Protocolo Obrigatorio de Implementacao

- Antes de qualquer refatoracao estetica/estrutural, priorizar validacao e preservacao dos requisitos funcionais do fluxo afetado.
- Antes de implementar qualquer melhoria/correcao/feature, revisar o contexto em `README.md` e as instrucoes em `.github/instructions/*.md` aplicaveis ao dominio alterado.
- Quando a mudanca tocar arquitetura, infraestrutura, deploy, dados, fluxo critico ou decisoes historicas, consultar tambem `HISTORICO_EVOLUCAO.md` antes da implementacao.
- Em tarefas com uso de skills, agentes ou instrucoes especializadas, manter o mesmo protocolo de leitura de contexto documental antes de codar.
- Sempre priorizar reuso e modularidade: evitar duplicacao de regras, centralizar fonte de verdade e preservar contratos existentes.
- Aplicar SOLID e Clean Code em toda alteracao:
	- funcoes/metodos curtos com responsabilidade unica (SRP);
	- baixo acoplamento e alta coesao;
	- nomes claros e semanticos;
	- evitar logica duplicada e efeitos colaterais ocultos;
	- minimizar breaking changes e manter compatibilidade quando possivel.
- Ao concluir mudancas em fluxos sensiveis, validar impacto e registrar risco residual quando nao houver cobertura automatizada suficiente.

## Infra de Producao

- **Frontend:** Vercel (estatico, CDN global) — dominio `arena-de-combate-rpg.com.br` via Cloudflare
- **Backend:** Render.com (free tier) — `https://projetorpg-7ih3.onrender.com` — branch `feature/salva`
- **Banco:** Neon PostgreSQL `ep-bold-night-ak4zfe7p` (us-west-2 Oregon) — serverless, connection pooling — co-localizado com o Render backend
- **Imagens:** Cloudinary — `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET` como env vars no Render
- **Anti-sleep:** cron-job.org `*/10 * * * *` → `GET /health` (evita cold start do Render free tier)
- **Deploy:** merge `feature/responsivo` → `feature/salva` aciona deploy automatico no Render

## Convencoes de Versionamento Frontend

- Scripts com cache-busting explicito: `?v=<numero>` nos imports de HTML
- Versao atual dos controllers principais: `v=21` (FichaPersonagemController)
- Ao modificar qualquer controller/service, incrementar o `?v=` correspondente no HTML

## Onde Estao as Regras Especificas

- Backend Python: `.github/instructions/backend.instructions.md`
- Frontend Web: `.github/instructions/frontend.instructions.md`
- Migrations Alembic: `.github/instructions/migrations.instructions.md`
- Historico de evolucao: `HISTORICO_EVOLUCAO.md` (infra + features ao longo do tempo)

## Orquestracao de Agentes

- Agente coordenador recomendado: `Fullstack Orchestrator` em `.github/agents/fullstack-orchestrator.agent.md`.
- Agente complementar para features com contrato entre camadas: `Fullstack API Contract Orchestrator` em `.github/agents/fullstack-api-contract-orchestrator.agent.md`.
- Agente especializado em levantamento de requisitos a partir de livros/PDFs/regras: `RPG Requirements Analyst` em `.github/agents/rpg-requirements-analyst.agent.md`.
- Especialistas recomendados:
	- `Backend FastAPI Specialist`
	- `Frontend Arena Specialist`
	- `Database and Migrations Specialist`
	- `PostgreSQL Database Administrator` para estado real do banco em execucao
- Fluxo esperado para demandas multi-area:
	1. Classificar a solicitacao por dominio.
	2. Delegar para especialistas em paralelo apenas quando nao houver dependencia direta.
	3. Tratar schema e persistencia antes de consolidar impactos em backend/frontend quando necessario.
	4. Consolidar contratos, validacao e risco residual em uma resposta unica.

## Prompts Reutilizaveis

- Prompt recomendado para novas funcionalidades: `.github/prompts/nova-feature-fullstack.prompt.md`.
- Use esse prompt quando quiser iniciar uma feature com triagem automatica por dominio e consolidacao final pelo orquestrador.
- Prompt para investigacao e correcao de bugs: `.github/prompts/correcao-bug-fullstack.prompt.md`.
- Prompt para refatoracao incremental e segura: `.github/prompts/refatoracao-segura-por-dominio.prompt.md`.
- Prompt para revisao tecnica antes de merge: `.github/prompts/auditoria-pre-merge-fullstack.prompt.md`.
- Prompt para mudancas de schema com seguranca de rollout: `.github/prompts/migration-segura.prompt.md`.
- Prompt para validar prontidao de deploy: `.github/prompts/deploy-readiness-fullstack.prompt.md`.
- Prompt para investigar gargalos de performance: `.github/prompts/investigacao-performance-fullstack.prompt.md`.
- Prompt para levantamento de requisitos a partir de livros, PDFs ou regras de negocio: `.github/prompts/levantamento-requisitos-rpg.prompt.md`.

## Hooks

- Hooks de workspace ficam em `.github/hooks`.
- Hook atual: `operational-safety.json`.
- Objetivo atual do hook: pedir atencao extra antes de comandos potencialmente destrutivos em terminal ou modificacoes SQL sensiveis.
- Hooks devem permanecer pequenos, auditaveis e focados em enforcement real; nao usar hooks para duplicar instrucoes textuais.

## Estado Atual do Banco (Neon producao)

- `pericias_classes`: populada com 175 associacoes (11 classes x pericias D&D 3.5)
- Custo de pericias: 1 pt (da classe) / 2 pts (fora da classe) — calculado via `obter_custos_pericias()`
- Seeds aplicados em producao: magias (~400+), pericias (54), pericias_classes (175), condicoes (25)

## Armazenamento de Imagens

- `FileService` roteia automaticamente: Cloudinary quando `CLOUDINARY_*` configurado (producao), filesystem local senao (dev).
- `foto_url` no banco armazena URL HTTPS absoluta do Cloudinary em producao (ex: `https://res.cloudinary.com/...`).
- Em dev local, `foto_url` armazena URL relativa `/uploads/<uuid>.ext` — normal, nao confundir com bug.
- Nunca armazene imagens apenas no filesystem do Render — e efemero e perdido em cada deploy/restart.
- Ao deletar combatente com foto, `FileService.deletar_arquivo()` lida com ambos os casos automaticamente.

## Convencoes Transversais

- Preserve autenticacao real e autorizacao por perfil; nao introduza atalhos permissivos.
- Ao mexer em fluxos criticos (auth, cache, listagens, migrations), valide o impacto e informe risco residual quando nao houver teste automatizado.
- Para textos de interface, prefira portugues consistente com o restante do produto.
- `isClasseConjuradora()` de `combat-rules.js` e a fonte de verdade para quais classes tem magia — usar em vez de listas manuais.
- `getApiUrl()` de `api.config.js` e obrigatorio em todos os services/controllers do frontend; nunca hardcode localhost ou URL de producao.
