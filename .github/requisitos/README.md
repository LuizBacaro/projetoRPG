# Requisitos de feature (Arena TTRPG)

Especificações funcionais por sistema de jogo (D&D 3.5, D&D 5E, Tormenta 20, GURPS) para orientar implementação no código.

## Gate obrigatório antes de implementar

**Não comece a codar** a partir de qualquer ficheiro desta pasta sem cumprir, nesta ordem:

1. **[AGENTS.md](../../AGENTS.md)** — arquitetura deployada, **camadas/SOLID/multi-jogo**, protocolo de implementação, SDD leve.
2. **[docs/arquitetura-camadas-solid.md](../../docs/arquitetura-camadas-solid.md)** — profundidade sobre camadas, modularidade e evolução do código.
3. Instruções da área alterada em **[.github/instructions](../../.github/instructions)** (`backend`, `frontend` ou `migrations`).
4. Skill do jogo, quando existir (índice completo: [.cursor/skills/README.md](../skills/README.md)):
   - Tormenta: [.cursor/skills/tormenta-20-arena-arquitetura-e-regras/SKILL.md](../skills/tormenta-20-arena-arquitetura-e-regras/SKILL.md)
   - D&D 3.5 em produção (`dnd35`): requisitos em [dnd35/](dnd35/) e conjuração em [.cursor/skills/dnd-spellcasting-conventions/SKILL.md](../skills/dnd-spellcasting-conventions/SKILL.md)
   - D&D 5E (`dnd5e`): [.cursor/requisitos/dnd5e/README.md](dnd5e/README.md) e [5e-database](https://github.com/5e-bits/5e-database) — **não** misturar regras com `dnd35`
   - GURPS: [.cursor/skills/gurps-4e-requisitos-ficha-arena/SKILL.md](../skills/gurps-4e-requisitos-ficha-arena/SKILL.md)
5. Deploy/dados em produção: [.cursor/skills/arena-producao-dados-neon-render/SKILL.md](../skills/arena-producao-dados-neon-render/SKILL.md) e [PRE_DEPLOY_CHECKLIST.md](../../PRE_DEPLOY_CHECKLIST.md), se a tarefa tocar schema ou `DATABASE_URL`.

Os ficheiros aqui descrevem **o quê** implementar; `AGENTS.md` define **como** encaixar na plataforma existente.

## D&D 3.5 e D&D 5E — jogos distintos (nunca misturar)

No Arena, **`dnd35` e `dnd5e` são dois sistemas com `game_slug`, código e requisitos próprios.** Não são edições intercambiáveis.

- Alterou **3.5** → ler só [dnd35/](dnd35/) e editar só `backend/app/games/dnd35/`, `frontend/games/dnd35/`.
- Alterou **5E** → ler só [dnd5e/](dnd5e/) e editar só `backend/app/games/dnd5e/`, `frontend/games/dnd5e/`.
- **Proibido:** portar RF, catálogo, UI ou fórmula de um para o outro; util partilhado com regra de jogo embutida; “unificar” meio-elfo/humano/etc. entre edições.

Índices por jogo: [dnd35/README.md](dnd35/README.md) · [dnd5e/README.md](dnd5e/README.md)

## Estrutura

| Pasta | Conteúdo |
|-------|----------|
| `dnd35/` | Ficha e mecânicas **D&D 3.5** em produção (`backend/app/games/dnd35/`, `frontend/games/dnd35/`) |
| `dnd5e/` | Ficha e mecânicas **D&D 5E** (ver [dnd5e/README.md](dnd5e/README.md); catálogo JSON: [5e-bits/5e-database](https://github.com/5e-bits/5e-database)) |
| `tormenta/` | Ficha e mecânicas **Tormenta 20 — Edição Jogo do Ano v1.3** ([tormenta/README.md](tormenta/README.md)) |
| `gurps/` | Ficha e mecânicas GURPS 4E |

## Materiais de referência locais (não versionados)

PDFs, planilhas e scripts de extração ficam em `livros/` e `helpers/` na raiz do repositório (`.gitignore`). Use-os só na máquina local; não commitar.

## Matriz de cobertura (requisito × código)

```bash
python3 scripts/generate_requisitos_cobertura_matrix.py
```

Saída: [docs/requisitos-cobertura-matrix.md](../../docs/requisitos-cobertura-matrix.md) (heurística API/testes/FE — revisar manualmente).

## Ao concluir uma feature

- Alinhar contrato API + teste mínimo (ver SDD leve em `AGENTS.md`).
- Incrementar `?v=` nos HTML se alterar JS/CSS do frontend.
- Migrations: `server_default` boolean em Postgres = `true`/`false`, nunca `0`/`1`.
