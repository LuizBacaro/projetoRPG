# Skills do Arena TTRPG — índice para agentes e humanos

Skills são **playbooks curtos** que o agente carrega **só quando a tarefa pede**. Eles entram na **janela de contexto** (o texto que o modelo “vê” de uma vez) e **não substituem**:

- [AGENTS.md](../../AGENTS.md) — governança, camadas, multi-jogo, protocolo
- [.cursor/requisitos/](../requisitos/) — **o quê** implementar (RF por jogo)
- [.cursor/rules/](../rules/) — regras automáticas por área (backend, CI, requisitos)

## Janela de contexto em 30 segundos

| Ideia | Prática neste repo |
|--------|-------------------|
| Espaço limitado | Conversa longa + muitos ficheiros + vários skills = diluição |
| Carregar sob demanda | 1–2 skills relevantes por tarefa |
| Prioridade | Pedido atual + RF + código tocado > skills genéricos |
| Multi-jogo | **Nunca** misturar skills/RF de `dnd35` com `dnd5e`, Tormenta ou GURPS na mesma implementação |

## Onde estão os skills

| Local | Conteúdo |
|-------|----------|
| **`.cursor/skills/`** (esta pasta) | Domínio Arena: deploy, D&D 3.5, Tormenta, GURPS, produção |
| **`.github/skills/`** | Análise de requisitos, PDF, auditoria JS, design — ver [índice GitHub](../.github/skills/README.md) |

Skills globais do Cursor (`~/.cursor/skills-cursor/`: create-skill, babysit, PR split) são do editor, não deste repositório.

---

## Atalho: qual skill usar?

| Tu queres… | Skill / documento |
|------------|-------------------|
| Livro/PDF → especificação RF | [rpg-requirements-analysis](../.github/skills/rpg-requirements-analysis/SKILL.md) |
| Implementar RF já escrito | RF em [requisitos/](../requisitos/) + [requisitos-implementacao](../rules/requisitos-implementacao.mdc) |
| Ficha D&D 3.5 — progressão de classe | [class-progression-conventions](class-progression-conventions/SKILL.md) |
| Ficha D&D 3.5 — conjuração / grimório | [dnd-spellcasting-conventions](dnd-spellcasting-conventions/SKILL.md) |
| Companheiro animal / familiar | RF [09](../requisitos/dnd35/09-companheiro-animal-dnd35.md) · [10](../requisitos/dnd35/10-familiar-dnd35.md) |
| Tormenta 20 | [tormenta-20-arena-arquitetura-e-regras](tormenta-20-arena-arquitetura-e-regras/SKILL.md) |
| GURPS 4E | [gurps-4e-requisitos-ficha-arena](gurps-4e-requisitos-ficha-arena/SKILL.md) |
| CORS, 404 API, Vercel, `getApiUrl` | [arena-ttrpg-architecture](arena-ttrpg-architecture/SKILL.md) |
| Neon, Render, migrations, dados em prod | [arena-producao-dados-neon-render](arena-producao-dados-neon-render/SKILL.md) |
| Extrair texto de PDF | [pdf](../.github/skills/pdf/SKILL.md) |

---

## Skills em `.cursor/skills/` (detalhe)

### Plataforma — deploy e dados

| Skill | Pasta | Carregar quando… |
|-------|--------|------------------|
| **arena-ttrpg-architecture** | [arena-ttrpg-architecture/](arena-ttrpg-architecture/SKILL.md) | Deploy Vercel + API Render, CORS, `vercel.json`, rotas `/arena` `/dashboard`, erros 404 na API em produção, `getApiUrl` |
| **arena-producao-dados-neon-render** | [arena-producao-dados-neon-render/](arena-producao-dados-neon-render/SKILL.md) | `DATABASE_URL`, branch Neon, PITR/backups, `alembic upgrade`, incidentes “dados sumidos”, health `/health/live` |

**Ordem típica em incidente de prod:** architecture (app responde?) → produção-dados (schema/URL corretos?).

### D&D 3.5 (`dnd35`) — regras e ficha

| Skill | Pasta | Carregar quando… |
|-------|--------|------------------|
| **class-progression-conventions** | [class-progression-conventions/](class-progression-conventions/SKILL.md) | BBA, resistências, defesas, iniciativa, tabelas de classe, progressão por nível |
| **dnd-spellcasting-conventions** | [dnd-spellcasting-conventions/](dnd-spellcasting-conventions/SKILL.md) | Slots, grimório, atributo de conjuração, magias preparadas, seeds de magia |

Código: `backend/app/games/dnd35/`, `frontend/games/dnd35/`. Requisitos: [requisitos/dnd35/](../requisitos/dnd35/).

### Outros jogos (não misturar com dnd35)

| Skill | Pasta | Carregar quando… |
|-------|--------|------------------|
| **tormenta-20-arena-arquitetura-e-regras** | [tormenta-20-arena-arquitetura-e-regras/](tormenta-20-arena-arquitetura-e-regras/SKILL.md) | Ficha Tormenta, MB, rotas `/tormenta/`, catálogos JSON |
| **gurps-4e-requisitos-ficha-arena** | [gurps-4e-requisitos-ficha-arena/](gurps-4e-requisitos-ficha-arena/SKILL.md) | Ficha e arena GURPS |

---

## Skills em `.github/skills/`

| Skill | Uso |
|-------|-----|
| [rpg-requirements-analysis](../.github/skills/rpg-requirements-analysis/SKILL.md) | Análise de regra → RF acionável (camadas: fonte / produto / técnico) |
| [pdf](../.github/skills/pdf/SKILL.md) | Operações com PDF (extrair, mesclar, OCR) |
| [javascript-audit](../.github/skills/javascript-audit/SKILL.md) | Auditoria ampla de JS — não para bug pontual |
| [frontend-design-teste](../.github/skills/frontend-design-teste/SKILL.md) | UI nova com foco em design — não para correção de API |
| [postgresql](../.github/skills/postgresql/SKILL.md) | Migração Oracle→Postgres **.NET** — **não** é o Neon do Arena |

Índice completo: [.github/skills/README.md](../.github/skills/README.md).

---

## Receitas por tipo de tarefa

### A) Nova mecânica / novo RF (ex.: montaria, prestígio)

1. [AGENTS.md](../../AGENTS.md)
2. [rpg-requirements-analysis](../.github/skills/rpg-requirements-analysis/SKILL.md) + [pdf](../.github/skills/pdf/SKILL.md) se houver livro
3. Escrever ou atualizar ficheiro em [requisitos/dnd35/](../requisitos/dnd35/) (ou jogo correto)
4. Na implementação: RF + [arquitetura-camadas](../rules/arquitetura-camadas.mdc) — **sem** skills de deploy

### B) Bug ou feature na ficha D&D 3.5

1. RF específico (ex. `09`, `10`, `05-magia`)
2. Skill de domínio se aplicável (`dnd-spellcasting`, `class-progression`) ou nenhum se for CRUD simples
3. Código em `games/dnd35/`

### C) Erro só em produção (500, CORS, API)

1. [arena-ttrpg-architecture](arena-ttrpg-architecture/SKILL.md)
2. [arena-producao-dados-neon-render](arena-producao-dados-neon-render/SKILL.md) se envolver BD/migrations
3. **Não** carregar rpg-requirements-analysis nem skills de outro jogo

### D) Arena de combate (turnos, iniciativa, vínculos na mesa)

1. [requisitos/dnd35/04-combate-dnd35.md](../requisitos/dnd35/04-combate-dnd35.md)
2. [arena-ttrpg-architecture](arena-ttrpg-architecture/SKILL.md) se front/API em prod
3. Vínculos (companheiro/familiar na mesa): RF 09/10 § arena + `VinculoArenaService`

---

## O que evitar na mesma conversa

- Três ou mais skills longos ao mesmo tempo
- RF de **dnd35** + código **dnd5e** (ou Tormenta/GURPS)
- Skill **postgresql** (github) para problemas do **Neon** do Arena
- **frontend-design-teste** para bugs de backend ou migrations

---

## Relação com regras Cursor (`.cursor/rules/`)

| Regra | Quando entra sozinha |
|-------|---------------------|
| [requisitos-implementacao.mdc](../rules/requisitos-implementacao.mdc) | Trabalho em requisitos ou implementação a partir de RF |
| [arquitetura-camadas.mdc](../rules/arquitetura-camadas.mdc) | Backend / refactor estrutural |
| [backend-qualidade-ci.mdc](../rules/backend-qualidade-ci.mdc) | Python: `make format-backend`, `make ci-backend-lint` |

Skills **complementam** estas regras; não as duplicam.

---

## Manutenção deste índice

Ao criar skill nova em `.cursor/skills/<nome>/SKILL.md`:

1. Frontmatter `description` com gatilhos claros (“Usar quando…”).
2. Entrada na tabela **Atalho** e na secção **detalhe** deste README.
3. Se for skill de jogo, link no [requisitos/README.md](../requisitos/README.md) gate (passo 4).
