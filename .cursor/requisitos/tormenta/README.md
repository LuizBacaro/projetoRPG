# Tormenta 20 — requisitos Arena (Edição Jogo do Ano v1.3)

> **Fonte normativa de regras:** livros licenciados locais em `livros/` (não versionados).  
> **Código:** `backend/app/games/tormenta/`, `frontend/games/tormenta/`.  
> **Skill:** [.cursor/skills/tormenta-20-arena-arquitetura-e-regras/SKILL.md](../../skills/tormenta-20-arena-arquitetura-e-regras/SKILL.md).

## Edições e PDFs de referência

| PDF | Uso neste backlog |
|-----|-------------------|
| `Tormenta20-Edicao-Jogo-do-Ano-v1.3.pdf` | **Regras core** — construção de personagem, perícias, poderes, equipamento, magia, combate |
| `T20-Deuses-de-Arton-v1-1.pdf` | Panteão expandido, devoção, poderes concedidos, distinções, classe Frade |
| `T20-Herois-de-Arton-v1-1.pdf` | **Opcional** — raças/classes variantes, distinções, arsenal, regras opcionais |
| `Atlas-de-Arton-v1.0-17-11-2023.pdf` | **Ambientação** — regiões, organizações; origens regionais (Apêndice p.470) |

**Páginas citadas nos RFs = numeração impressa do livro** (Sumário), não índice do ficheiro PDF.

## Legado MB vs v1.3

O código e JSONs ainda usam sufixo `_mb` (Módulo Básico / edição anterior). Os RFs abaixo descrevem **T20 v1.3**; onde o backend diverge, há secção **Gap código**.

Principais mudanças v1.3 (sem copiar texto do livro):

- **17 raças** (Cap. 1, p.18–31) — saem gnomo, meio-elfo, meio-orc do core; entram dahllan, golem, hynne, kliren, medusa, osteon, sereia/tritão, sílfide, suraggel, trog; halfling → **hynne**.
- **14 classes** (p.32–81) — mago+feiticeiro → **arcanista**; ranger → **caçador**; swashbuckler → **bucaneiro**; saem monge e samurai; entram **cavaleiro**, **lutador**, **inventor**, **nobre**.
- **28 perícias** (Cap. 2, p.114–123) — saem Identificar Magia, Obter Informação; entram **Misticismo**, **Reflexos** (como perícia).
- **Talentos → Poderes** (Cap. 2, p.124–136).
- **Origens** (p.85–105) — novo passo de construção.
- **PM universais** — habilidades especiais de todas as classes gastam PM (Introdução, item 16).
- **Alinhamento** — guia narrativo; sem restrição mecânica por classe (exceto paladino = bem e ordem); devoção a deus > alinhamento (item 17).

## Índice de requisitos

| Arquivo | Tema | Livro (v1.3) |
|---------|------|----------------|
| [01-habilidades-tormenta.md](01-habilidades-tormenta.md) | Atributos, PV, PM | Cap. 1 p.17; Termos p.11 |
| [02-races-tormenta.md](02-races-tormenta.md) | 17 raças | Cap. 1 p.18–31 |
| [03-classes-tormenta.md](03-classes-tormenta.md) | 14 classes | Cap. 1 p.32–81 |
| [04-pericias-tormenta.md](04-pericias-tormenta.md) | 28 perícias | Cap. 2 p.114–123 |
| [05-combate-tormenta.md](05-combate-tormenta.md) | Combate, condições | Cap. 5 p.230; Lista p.394 |
| [06-magia-tormenta.md](06-magia-tormenta.md) | PM, círculos, grimório | Cap. 4 p.168–178 |
| [07-equipamento-tormenta.md](07-equipamento-tormenta.md) | Armas, armaduras, itens | Cap. 3 p.138–164 |
| [08-poderes-tormenta.md](08-poderes-tormenta.md) | Poderes gerais e de classe | Cap. 2 p.124–136 |
| [09-origens-divindades-tormenta.md](09-origens-divindades-tormenta.md) | Origens, deuses, alinhamento | Cap. 1 p.85–109; suplemento Deuses |
| [10-suplementos-opcionais.md](10-suplementos-opcionais.md) | Heróis, Atlas, regras opcionais | Heróis + Atlas + Deuses |
| [11-herois-de-arton-plano-implementacao.md](11-herois-de-arton-plano-implementacao.md) | Plano Heróis de Arton | Suplemento HA |
| [12-inspiracao-roll20-ux-mesa.md](12-inspiracao-roll20-ux-mesa.md) | Benchmark Roll20 — UX ficha/mesa (sem VTT mapa) | Referência externa |
| [13-construcao-npc-monstro.md](13-construcao-npc-monstro.md) | Ameaça (NPC/monstro) — bloco estilo livro + CRUD | Bestiário / Reforma Monstrográfica |

## Direitos autorais

Não copiar texto longo nem tabelas completas do livro no repositório. RFs trazem estrutura, fórmulas genéricas, remissão de página e critérios de aceite — ver `docs/tormenta/00-visao-e-fontes-legais.md`.

## Backlog v1.3

Itens pendentes e prioridades transversais: **[docs/tormenta/03-requisitos-funcionais-backlog.md](../../docs/tormenta/03-requisitos-funcionais-backlog.md)** (secção **Backlog v1.3**).
