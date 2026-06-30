# FEATURE: Poderes Tormenta 20 (Edição Jogo do Ano v1.3)

> **Fonte:** `Tormenta20-Edicao-Jogo-do-Ano-v1.3.pdf` — Cap. 2 **Poderes p.124–136**; habilidades de classe p.32; PM universal (Introdução item 16).  
> **Nota:** v1.3 renomeou «talentos» → **poderes** (Introdução item 8).

## Descrição

Sistema de **poderes** escolhidos na construção e na progressão (classe, origem, raça, devoção, humano Versátil). Poderes funcionam como **habilidades** (Cap. 5); muitos gastam **PM** ao ativar.

## Fontes de poderes

| Fonte | Exemplo |
|-------|---------|
| Classe | «Poder de [Classe]» a cada nível (listas por classe) |
| Origem | 1 dos 2 benefícios escolhidos (p.85) |
| Raça | Humano Versátil: 1 poder geral (p.19) |
| Devoção | 1 poder concedido ao tornar-se devoto (p.96) |
| Multiclasse / Mesa | Negociação ou troca conforme livro |

## Regras gerais (p.32, p.124+)

| Regra | Detalhe |
|-------|---------|
| Pré-requisitos | Atributo mínimo, perícia treinada, outro poder, nível, proficiência — validar antes de escolher |
| Escolha no nível | Pode escolher poder quando **atinge** todos os pré-requisitos |
| Repetição | Salvo indicação, **não** escolher o mesmo poder duas vezes |
| **Substituição** | Poder de classe pode ser trocado por **poder geral** (qualquer lista de gerais/combate/destino/magia) |
| PM | Custo indicado no poder; PM vêm do pool universal do personagem |
| Aprimoramento | Poderes que aumentam custo PM de magia = categoria **Poderes de Aprimoramento** (p.131) |

## Categorias (livro)

| Categoria | p. | Escopo Arena |
|-----------|-----|--------------|
| **Poderes Gerais** | 124 | Utilidade, perícias, carga, parceiros — ex.: Sortudo, Treinamento em Perícia, Inventário Organizado, Parceiro, Surto Heroico |
| **Poderes de Combate** | 124–128 | Estilos, manobras, proficiências — ver tabela resumo abaixo |
| **Poderes de Destino** | 129 | Ex.: Acrobático, Ao Sabor do Destino (tabela por nível 6–19), Vitalidade, Lobo Solitário |
| **Poderes de Magia** | 131 | Pré-req.: lançar magias — Celebrar Ritual, Escrever Pergaminho, **Poderes de Aprimoramento** |
| **Poderes Concedidos** | 132 | Um por devoto; lista por divindade (Tabela 1-20 + blocos p.96+) |
| **Poderes da Tormenta** | 136 | Corrupção/lefeu; origem Assistente de Laboratório pode escolher 1 |

### Poderes de Combate — lista para catálogo (p.125)

Metadados: `slug`, `categoria: combate`, `pre_requisitos[]`, `custo_pm`, `pagina`.

Acuidade com Arma, Ataque Poderoso, Quebrar Aprimorado, Trespassar, Combate Defensivo, Derrubar Aprimorado, Desarmar Aprimorado, Empunhadura Poderosa, Encouraçado, Fanático, Inexpugnável, Esquiva, Estilo Desarmado, Estilo de Arma e Escudo, Ataque com Escudo, Bloqueio com Escudo, Estilo de Arma Longa, Piqueiro, Estilo de Uma Arma, Ataque Preciso, Estilo de Duas Armas, Arma Secundária Grande, Estilo de Duas Mãos, Ataque Pesado, Estilo de Arremesso, Arremesso Múltiplo, Arremesso Potente, Estilo de Disparo, Disparo Preciso, Mira Apurada, Disparo Rápido, Finta Aprimorada, Foco em Arma, Ginete, Carga de Cavalaria, Presença Aterradora, Proficiência, Reflexos de Combate, Saque Rápido, Vitalidade.

Demais categorias: indexar por nome + página; efeitos completos permanecem no PDF (sem texto longo no repo).

### Poderes Concedidos (Tabela 1-20 — índice)

Cada deus oferece **4** poderes concedidos; devoto escolhe **1** ao aderir. Cross-ref `09-origens-divindades-tormenta.md`. Suplemento `T20-Deuses-de-Arton` expande listas (P1 backlog).

## UX e nomenclatura

| Legado (MB/código) | v1.3 |
|--------------------|------|
| Talento | **Poder** |
| `talentos_mb_catalogo.json` | Manter path; `_meta.conceito = "poderes"` até migração |
| API `/tormenta/regras/talentos` | Alias futuro `/poderes` |
| SQL `tormenta_talentos_personagem` | Coluna/conceito «poder» na UI |

## Requisitos funcionais

| ID | Requisito | Prioridade |
|----|-----------|------------|
| RF-T08a | Catálogo poderes v1.3 com **6 categorias** + `pagina` | P0 |
| RF-T08b | API `GET /tormenta/regras/talentos` (alias `/poderes` futuro) | P0 |
| RF-T08c | Vínculo SQL `tormenta_talentos_personagem` | P0 |
| RF-T08d | UI: rótulo **Poderes**, filtros por categoria | P1 — **Feito** |
| RF-T08e | Poderes concedidos filtrados por `divindade.slug` | P1 — **Feito** (RF-T09-v13) |
| RF-T08f | Regra substituição: poder de classe → poder geral | P2 |
| RF-T08g | Validação de pré-requisitos (nível, atributo, perícia, poderes) | **Feito** |
| RF-T08h | Debitar PM ao ativar poder com custo | P1 — **Feito** |
| RF-T08i | Poderes de origem e humano Versátil na criação | P1 — **Feito** |
| RF-T08j | Poderes da Tormenta (flag `tormenta: true`) | P3 |

## Estado de implementação

| Item | Estado |
|------|--------|
| Catálogo talentos MB + API | **Feito** (nomenclatura legada) |
| Vínculo personagem-poder | **Feito** |
| Categorias v1.3 completas | **Feito** (`categoria_v13` + filtro UI) |
| PM ao ativar | **Feito** (`POST /poderes/ativar`, catálogo `custo_pm`) |
| Poderes concedidos por deus | **Feito** (`tendencias_divindades_mb.json` + UI filtrada) |
| Substituição classe → geral | **Não feito** |
| Pré-requisitos automáticos | **Feito** | `poderes_pre_requisitos_v13_t20.py`, overlay JSON, API `POST /poderes/validar-pre-requisitos`, bloqueio ao vincular v1.3 |

## Gap código

- Frontend ainda pode exibir «Talento» — trocar para «Poder».
- Expandir `talentos_mb_catalogo.json` com slugs estáveis e categorias p.124–136.
- Poderes concedidos: sincronizar nomes com Tabela 1-20 (ex.: Aharadak → Afinidade com a Tormenta, Êxtase da Loucura, Percepção Temporal, Rejeição Divina).
- Integrar novos concedidos do suplemento Deuses de Arton (p.42+).

## Critérios de aceite

- Ficha exibe «Poderes», não «Talentos», para personagem v1.3.
- Poder concedido só selecionável com devoção compatível (RF-T09).
- Catálogo lista categoria + slug + pré-requisitos estruturados (sem parágrafos do livro).
- Ativação com custo PM reduz pool e respeita limite «não gastar mais PM que possui».

## Referência

- Livro: Cap. 2 p.124–136.
- Dados: `talentos_mb_catalogo.json`, `tormenta_talentos*`, `tendencias_divindades_mb.json`
- Cross-ref: `09-origens-divindades-tormenta.md`, `02-races-tormenta.md` (Versátil)
