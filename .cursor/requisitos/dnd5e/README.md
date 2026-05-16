# Requisitos D&D 5E (Arena TTRPG)

Especificações em `*.md` desta pasta descrevem mecânicas **D&D 5ª edição** (bônus de proficiência, níveis 1–20, etc.).

**Antes de implementar:** seguir o gate em [.cursor/requisitos/README.md](../README.md) e [AGENTS.md](../../../AGENTS.md).

## Código de produção vs. esta pasta

| Área | Sistema | Nota |
|------|---------|------|
| `backend/app/games/dnd35/` | D&D **3.5** | Ficha, grimório e arena atuais no deploy |
| `.cursor/requisitos/dnd5e/` | D&D **5E** | Roadmap / novas features 5e; não confundir regras 3.5 com 5e |

Ao implementar um RF desta pasta, criar ou estender módulos **5e** de forma isolada (novo `game_slug` / pacote), salvo decisão explícita de convergir com `dnd35`.

## Fonte recomendada: 5e-database

Repositório: **[5e-bits/5e-database](https://github.com/5e-bits/5e-database)** — JSON estruturado usado pela API pública [dnd5eapi.co](https://www.dnd5eapi.co/).

**Uso válido nos requisitos e na implementação:**

- Catálogos: raças, classes, magias, talentos (feats), equipamento, antecedentes, etc.
- Metadados para seeds, slugs, nomes, níveis de magia, escolas, tipos — **sem** colar texto longo do SRD no repositório Arena.
- Prototipagem de API e contratos Pydantic a partir dos schemas JSON em `src/` do projeto upstream.

**Licença (resumo):** código do repositório sob **MIT**; conteúdo de jogo sob **OGL 1.0a** (ver [LICENSE.md](https://github.com/5e-bits/5e-database/blob/main/LICENSE.md) no upstream). Manter atribuição onde aplicável; não redistribuir PDFs proprietários da Wizards.

**Limitações — ler antes de importar em massa:**

1. **Não é D&D 3.5** — valores, progressão, conjuração e combate diferem do `dnd35` já em produção; não mapear 5e → 3.5 automaticamente sem tabela de equivalência aprovada.
2. **Idioma** — dados upstream em inglês; UI do Arena em PT-BR exige camada de tradução ou campos `nome_pt` no seed.
3. **Escopo SRD/OGL** — nem todo conteúdo de livros comerciais está no dataset; validar contra o RF concreto (`05-magia-dnd5e.md`, etc.).
4. **Versionamento** — fixar tag/release ao gerar seeds (ex.: `v5.7.0`) para reprodutibilidade.

## Outras fontes (complementares)

| Fonte | Uso |
|-------|-----|
| `livros/` (local, `.gitignore`) | PDF Livro do Jogador 3.5 ou 5e para regras narrativas e edge cases |
| `helpers/` (local) | Planilhas e scripts de extração já usados no projeto |
| [docs/regras-conjuracao-dnd-arena.md](../../../docs/regras-conjuracao-dnd-arena.md) | **Somente** conjuração **3.5** em `dnd35` |

## Mapa RF → dados 5e-database (orientativo)

| Ficheiro de requisito | Pastas JSON típicas no upstream (`src/`) |
|-----------------------|------------------------------------------|
| `01-habilidades-dnd5e.md` | Regras base (ability scores); pouco JSON — lógica no código |
| `02-raças-dnd5e.md` | `races` |
| `03-classes-dnd5e.md` | `classes`, `subclasses`, `features` |
| `04-combate-dnd5e.md` | `conditions`, `damage-types` |
| `05-magia-dnd5e.md` | `spells` |
| `06-talentos-feitos-dnd5e.md` | `feats` |
| `07-equipamento-dnd5e.md` | `equipment`, `magic-items` |
| `08-antecedentes-dnd5e.md` | `backgrounds` |

Consultar a árvore atual em [github.com/5e-bits/5e-database/tree/main/src](https://github.com/5e-bits/5e-database/tree/main/src).

## Fluxo sugerido para implementação

1. Ler o RF (`NN-*.md`) e o gate em `AGENTS.md`.
2. Baixar ou clonar [5e-database](https://github.com/5e-bits/5e-database) **fora** do commit principal (ou submodule opcional) e gerar seed JSON enxuto em `backend/app/games/.../data/`.
3. Adaptar campos ao contrato Arena (API + teste mínimo); traduzir rótulos na UI.
4. Se o RF tocar arena/combate 3.5 existente, documentar divergência e não alterar `dnd35` sem issue dedicada.
