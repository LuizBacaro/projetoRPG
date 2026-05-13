# Tormenta 20 — levantamento de requisitos (Arena TTRPG)

Documentação para **implementação confiável** da ficha e regras do jogo Tormenta 20 no módulo `backend/app/games/tormenta` e `frontend/games/tormenta/`.

## Ordem de leitura

| Ficheiro | Conteúdo |
|----------|----------|
| [00-visao-e-fontes-legais.md](00-visao-e-fontes-legais.md) | Escopo, direitos autorais, como usar o livro sem copiar tabelas |
| [01-indice-livro-planilhas-e-rastreabilidade.md](01-indice-livro-planilhas-e-rastreabilidade.md) | Índice do livro ↔ planilhas no repo ↔ artefactos de código |
| [02-inventario-tabelas-regras-por-secao.md](02-inventario-tabelas-regras-por-secao.md) | Inventário de tabelas/regras (páginas a confirmar; tipo de implementação) |
| [03-requisitos-funcionais-backlog.md](03-requisitos-funcionais-backlog.md) | RFs priorizados e critérios de aceite |
| [04-catalogos-dinamicos-roadmap.md](04-catalogos-dinamicos-roadmap.md) | Talentos, magias, equipamento, habilidades — catálogos dinâmicos |
| [05-contrato-dados-ficha-json-e-api.md](05-contrato-dados-ficha-json-e-api.md) | `ficha_json`, colunas SQL, `foto_url`, evolução da API |
| [06-trilha-levantamento-por-capitulo.md](06-trilha-levantamento-por-capitulo.md) | Checklist ao folhear o livro capítulo a capítulo |
| [tabelas/README.md](tabelas/README.md) | JSONs de dados (estrutura; valores a partir do livro) |

## Ferramentas de requisitos (genérico RPG)

- Prompt: [.github/prompts/levantamento-requisitos-rpg.prompt.md](../../.github/prompts/levantamento-requisitos-rpg.prompt.md)
- Skill: [.github/skills/rpg-requirements-analysis/SKILL.md](../../.github/skills/rpg-requirements-analysis/SKILL.md)

## Estado atual no código

- CRUD de personagens: ver [backend/app/games/tormenta/README.md](../../backend/app/games/tormenta/README.md).
- Planilhas de referência visual na raiz do repo: `planilha-tormenta.png`, `planilha-tormenta2.png`, `planilha-tormenta3.png`.

## Fluxo de trabalho recomendado

1. Confirmar **número de página** de cada tabela no **teu** exemplar físico ou PDF licenciado.
2. Preencher valores em `docs/tormenta/tabelas/*.json` (formato em [tabelas/README.md](tabelas/README.md)) — não commitar conteúdo protegido se a política do repositório não permitir; em caso de dúvida, manter só estrutura vazia e carregar dados em ambiente privado.
3. Implementar motor de regras ou seeds a partir dos JSONs, com testes unitários.
