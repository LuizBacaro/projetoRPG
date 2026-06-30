# FEATURE: Raças Tormenta 20 (Edição Jogo do Ano v1.3)

> **Fonte:** `Tormenta20-Edicao-Jogo-do-Ano-v1.3.pdf` — Raças p.18–31; **Tabela 1-2** p.18; Tamanho p.106 / Tabela 1-21.

## Descrição

**17 raças jogáveis** com modificadores de atributo (v1.3: tipicamente **+2/+1/−1**, não +4/+2 do MB), habilidades de raça e tamanho/deslocamento. Ajustes raciais aplicam-se **após** gerar atributos (passo 2 da construção).

## Regras gerais (p.18)

| Regra | Detalhe |
|-------|---------|
| Modificadores | Somados aos atributos; podem levar valor **acima de +4** ou **abaixo de −2** |
| Habilidades de raça | Funcionam como habilidades (Cap. 5); muitas gastam **PM** |
| Raças comuns | Humano, anão, dahllan, elfo, goblin, lefou, minotauro, qareen |
| Raças raras | Golem, hynne, kliren, medusa, osteon, sereia/tritão, sílfide, suraggel, trog — mecânicas mais avançadas (indicadas a veteranos) |

## Tabela 1-2 — Modificadores de atributo (p.18)

| Raça | Modificadores |
|------|----------------|
| Humano | **+1 em três atributos diferentes** |
| Anão | Con +2, Sab +1, Des −1 |
| Dahllan | Sab +2, Des +1, Int −1 |
| Elfo | Int +2, Des +1, Con −1 |
| Goblin | Des +2, Int +1, Car −1 |
| Lefou | **+1 em três atributos diferentes (exceto Car)**, Car −1 |
| Minotauro | For +2, Con +1, Sab −1 |
| Qareen | Car +2, Int +1, Sab −1 |
| Golem | For +2, Con +1, Car −1 |
| Hynne | Des +2, Car +1, For −1 |
| Kliren | Int +2, Car +1, For −1 |
| Medusa | Des +2, Car +1 |
| Osteon | **+1 em três atributos diferentes (exceto Con)**, Con −1 |
| Sereia/Tritão | **+1 em três atributos diferentes** |
| Sílfide | Car +2, Des +1, For −2 |
| Suraggel | Sab +2, Car +1 (**aggelus**) **ou** Des +2, Int +1 (**sulfure**) — escolha |
| Trog | Con +2, For +1, Int −1 |

> **MB antigo (backend):** ajustes +4/+2 e humano «+2 em dois» — **incompatível** com Tabela 1-2.

## Destaques mecânicos por raça (resumo — sem texto longo)

| Raça | Tamanho / desloc. (típico) | Notas Arena |
|------|----------------------------|-------------|
| Humano | Médio, 9 m | **Versátil** (abaixo) |
| Anão | Médio, **6 m** (pernas curtas; armadura/carga não reduzem) | Visão no escuro, resistências |
| Goblin | **Pequeno**, **9 m** | Tabela 1-21: +2 Furtividade / −2 manobras |
| Hynne | **Pequeno**, 6 m | Substitui halfling MB; sorte, etc. |
| Sílfide | Minúsculo/Pequeno, **voo 12 m** (PM) | |
| Suraggel | Médio | Subtipo aggelus ou sulfure na criação |
| Lefou | Médio | Deformidade / Tormenta (escolhas UI) |
| Qareen | Médio | Desejos / domínio (escolhas UI) |

Demais raças: extrair tamanho/deslocamento e habilidades do bloco p.19–31 ao implementar catálogo.

### Humano — Versátil (p.19)

| Opção | Benefício |
|-------|-----------|
| A (padrão) | Treinado em **duas perícias** à escolha (não precisam ser da classe) |
| B | Treinado em **uma perícia** + **um poder geral** à escolha |

Persistir escolha em `ficha_json` (ex.: `humano_versatil: "duas_pericias" | "pericia_poder"`).

## Catálogo — slugs alvo (17)

`humano`, `anao`, `dahllan`, `elfo`, `goblin`, `lefou`, `minotauro`, `qareen`, `golem`, `hynne`, `kliren`, `medusa`, `osteon`, `sereia_tritao`, `silfide`, `suraggel`, `trog`

## Requisitos funcionais

| ID | Requisito | Prioridade |
|----|-----------|------------|
| RF-T02a | API `GET /tormenta/regras/racas` com **17** entradas v1.3 | P0 |
| RF-T02b | Ajustes conforme Tabela 1-2 (+1×3 humano, não +2×2 MB) | P0 |
| RF-T02c | Humano **Versátil**: 2 perícias OU 1 perícia + 1 poder geral | P0 |
| RF-T02d | Lefou / Osteon / Sereia: regras de +1×3 com exceção | P0 |
| RF-T02e | Suraggel: escolha aggelus vs sulfure | P1 |
| RF-T02f | Preview traços + motor `tracos_raciais_t20.py` | P0 |
| RF-T02g | Tamanho/deslocamento automático (Tabela 1-21 + exceções) | P1 |
| RF-T02h | Escolhas estruturadas (lefou, qareen, dahllan magias, etc.) | P2 |

## Estado de implementação

| Item | Estado | Notas |
|------|--------|-------|
| `racas_v13.json` (17 raças) | **Feito** | Tabela 1-2; API dual |
| `tracos_mecanicos_v13.json` | **Feito** | Motor dual; escala v1.3 |
| Humano +1×3 + Versátil | **Feito** | UI + `humano_versatil` no JSON |
| Lefou / Osteon / Sereia +1×3 | **Feito** | Exclusões de atributo na UI |
| Suraggel aggelus/sulfure | **Feito** | UI + persistência |
| Tamanho/deslocamento automático | **Parcial** | Preview API aplica desloc/tamanho |
| Escolhas P2 (lefou deformidade, qareen…) | **Pendente** | P2 |
| `racas_mb.json` legado | **Mantido** | Fichas MB antigas |

## Gap código (MB → v1.3)

```text
Remover core:     gnomo, meio_elfo, meio_orc, halfling
Adicionar:        dahllan, golem, hynne, kliren, medusa, osteon,
                  sereia_tritao, silfide, suraggel, trog
Reescrever ajustes: todos conforme Tabela 1-2 (±1/±2)
Migrar:           racas_mb.json → racas_t20.json (ou _meta v1.3)
Compat legado:      slugs MB em personagens antigos
```

## Critérios de aceite

- Humano novo: +1 em **três** atributos distintos + Versátil registrado.
- Anão com DES 2 após raça: Defesa base inclui **+2** (valor DES), não modificador MB.
- Goblin/Hynne: tamanho Pequeno refletido na ficha (Furtividade +2).
- Nenhum texto longo de traço racial no repo.

## Referência

- Livro: p.18–31 (Tabela 1-2); p.106 / Tabela 1-21 (tamanho).
- Dados: `racas_mb.json`, `tracos_mecanicos_mb.json`.
