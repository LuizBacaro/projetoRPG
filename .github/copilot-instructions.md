# Copilot Instructions

Este workspace usa instrucoes granulares por dominio em `.github/instructions`.

## Escopo Geral

- Projeto fullstack TTRPG com backend FastAPI/SQLAlchemy e frontend HTML/CSS/JavaScript vanilla.
- Priorize mudancas pequenas e de causa raiz; evite reformatacao ampla sem necessidade.
- Nao reverta mudancas existentes do usuario sem solicitacao explicita.

## Infra de Producao

- **Frontend:** Vercel (estatico, CDN global) — dominio `arena-de-combate-rpg.com.br` via Cloudflare
- **Backend:** Render.com (free tier) — `https://projetorpg-7ih3.onrender.com` — branch `feature/salva`
- **Banco:** Neon PostgreSQL `quiet-rain-00826948` — serverless, connection pooling
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

## Estado Atual do Banco (Neon producao)

- `pericias_classes`: populada com 175 associacoes (11 classes x pericias D&D 3.5)
- Custo de pericias: 1 pt (da classe) / 2 pts (fora da classe) — calculado via `obter_custos_pericias()`
- Seeds aplicados em producao: magias (~400+), pericias (54), pericias_classes (175), condicoes (25)

## Convencoes Transversais

- Preserve autenticacao real e autorizacao por perfil; nao introduza atalhos permissivos.
- Ao mexer em fluxos criticos (auth, cache, listagens, migrations), valide o impacto e informe risco residual quando nao houver teste automatizado.
- Para textos de interface, prefira portugues consistente com o restante do produto.
- `isClasseConjuradora()` de `combat-rules.js` e a fonte de verdade para quais classes tem magia — usar em vez de listas manuais.
- `getApiUrl()` de `api.config.js` e obrigatorio em todos os services/controllers do frontend; nunca hardcode localhost ou URL de producao.
