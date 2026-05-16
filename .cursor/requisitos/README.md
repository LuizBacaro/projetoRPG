# Requisitos de feature (Arena TTRPG)

Especificações funcionais por sistema de jogo (D&D 3.5, Tormenta 20, GURPS) para orientar implementação no código.

## Gate obrigatório antes de implementar

**Não comece a codar** a partir de qualquer ficheiro desta pasta sem cumprir, nesta ordem:

1. **[AGENTS.md](../../AGENTS.md)** — arquitetura deployada, **camadas/SOLID/multi-jogo**, protocolo de implementação, SDD leve.
2. **[docs/arquitetura-camadas-solid.md](../../docs/arquitetura-camadas-solid.md)** — profundidade sobre camadas, modularidade e evolução do código.
3. Instruções da área alterada em **[.github/instructions](../../.github/instructions)** (`backend`, `frontend` ou `migrations`).
4. Skill do jogo, quando existir:
   - Tormenta: [.cursor/skills/tormenta-20-arena-arquitetura-e-regras/SKILL.md](../skills/tormenta-20-arena-arquitetura-e-regras/SKILL.md)
   - D&D 3.5 em produção (`dnd35`, conjuração): [.cursor/skills/dnd-spellcasting-conventions/SKILL.md](../skills/dnd-spellcasting-conventions/SKILL.md)
   - D&D 5E (requisitos em `dnd5e/`): [.cursor/requisitos/dnd5e/README.md](dnd5e/README.md) e [5e-database](https://github.com/5e-bits/5e-database)
   - GURPS: [.cursor/skills/gurps-4e-requisitos-ficha-arena/SKILL.md](../skills/gurps-4e-requisitos-ficha-arena/SKILL.md)
5. Deploy/dados em produção: [.cursor/skills/arena-producao-dados-neon-render/SKILL.md](../skills/arena-producao-dados-neon-render/SKILL.md) e [PRE_DEPLOY_CHECKLIST.md](../../PRE_DEPLOY_CHECKLIST.md), se a tarefa tocar schema ou `DATABASE_URL`.

Os ficheiros aqui descrevem **o quê** implementar; `AGENTS.md` define **como** encaixar na plataforma existente.

## Estrutura

| Pasta | Conteúdo |
|-------|----------|
| `dnd5e/` | Ficha e mecânicas **D&D 5E** (ver [dnd5e/README.md](dnd5e/README.md); catálogo JSON: [5e-bits/5e-database](https://github.com/5e-bits/5e-database)) |
| `tormenta/` | Ficha e mecânicas Tormenta 20 (MB) |
| `gurps/` | Ficha e mecânicas GURPS 4E |

## Materiais de referência locais (não versionados)

PDFs, planilhas e scripts de extração ficam em `livros/` e `helpers/` na raiz do repositório (`.gitignore`). Use-os só na máquina local; não commitar.

## Ao concluir uma feature

- Alinhar contrato API + teste mínimo (ver SDD leve em `AGENTS.md`).
- Incrementar `?v=` nos HTML se alterar JS/CSS do frontend.
- Migrations: `server_default` boolean em Postgres = `true`/`false`, nunca `0`/`1`.
