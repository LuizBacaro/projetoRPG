# FEATURE: Classes Tormenta 20 (Edição Jogo do Ano v1.3)

> **Fonte:** `Tormenta20-Edicao-Jogo-do-Ano-v1.3.pdf` — **Tabela 1-3** p.32; blocos por classe p.36–81; subir de nível p.34.

## Descrição

**14 classes** com PV/PM iniciais, ganho por nível, perícias treinadas de classe, proficiências e habilidade **Poder de [Classe]** (escolha de poderes — Cap. 2). Conjuradores seguem RF 06 (Arcanista com 3 caminhos).

## Tabela 1-3 — Resumo (p.32)

¹ PV inicial + **Constituição**; por nível: ganho da classe + **Constituição** (mín. 1 PV ao subir — p.34).  
² Perícias «fixas» treinadas + N à escolha; **+INT** perícias extras se INT positiva (não precisam ser da classe).

| Classe | Atributo principal | PV¹ | PM/nív | Perícias de classe² |
|--------|-------------------|-----|--------|---------------------|
| Arcanista | INT ou CAR | 8 | 6 | Misticismo, Vontade + **2** |
| Bárbaro | FOR | 24 | 3 | Fortitude, Luta + **4** |
| Bardo | CAR | 12 | 4 | Atuação, Reflexos + **6** |
| Bucaneiro | DES | 16 | 3 | Luta ou Pontaria, Reflexos + **4** |
| Caçador | FOR ou DES | 16 | 4* | Luta ou Pontaria, Sobrevivência + **6**† |
| Cavaleiro | FOR | 20 | 3 | Fortitude, Luta + **2** |
| Clérigo | SAB | 16 | 5 | Religião, Vontade + **2** |
| Druida | SAB | 16 | 4 | Sobrevivência, Vontade + **4** |
| Guerreiro | FOR ou DES | 20 | 3 | Luta ou Pontaria, Fortitude + **2** |
| Inventor | INT | 12 | 4 | Ofício, Vontade + **4** |
| Ladino | DES ou INT | 12 | 4 | Ladinagem, Reflexos + **8** |
| Lutador | FOR | 20 | 3 | Fortitude, Luta + **4** |
| Nobre | CAR | 16 | 4 | Diplomacia ou Intimidação, Vontade + **4** |
| Paladino | FOR e CAR | 20 | 3 | Luta, Vontade + **2** |

\* Tabela 1-3 resume PM **6** para Caçador; bloco da classe (p.49) indica **4 PM/nível** — **usar bloco da classe** como fonte de implementação.  
† Bloco p.49 confirma «mais **6**» perícias à escolha.

## PV por nível (blocos de classe — fórmula)

| Classe | Início ( + CON ) | Por nível ( + CON ) |
|--------|------------------|---------------------|
| Arcanista | 8 | **2** |
| Bárbaro | 24 | **6** |
| Bardo | 12 | **3** |
| Bucaneiro | 16 | **4** |
| Caçador | 16 | **4** |
| Cavaleiro | 20 | **5** |
| Clérigo | 16 | **4** |
| Druida | 16 | **4** |
| Guerreiro | 20 | **5** |
| Inventor | 12 | **3** |
| Ladino | 12 | **3** |
| Lutador | 20 | **5** |
| Nobre | 16 | **4** |
| Paladino | 20 | **5** |

**PM total** = soma dos PM/nível de **cada** classe (multiclasse, p.34).

## Arcanista (p.36–39) — ver também RF 06

| Caminho | Conjuração | Atributo-chave |
|---------|------------|----------------|
| **Bruxo** | Via **foco** (ou Misticismo CD 20 + custo PM) | INT |
| **Mago** | **Grimório**; memoriza metade das conhecidas | INT |
| **Feiticeiro** | Espontâneo; magia nova a cada **nível ímpar**; **linhagem** p.39 | CAR |

Escolha de caminho **irreversível** na criação (`ficha_json.caminho_arcanista`).

## Poderes de classe (p.32+)

- Toda classe tem habilidade **Poder de [Classe]** — escolhe poder da lista (pré-requisitos por nível).
- Pode **substituir** poder de classe por **poder geral** (Cap. 2).
- Poderes que aumentam custo PM de magia = **aprimoramentos** (RF 06).

## Multiclasse (p.34)

| Regra | Detalhe |
|-------|---------|
| 1º nível nova classe | PV = ganho de **nível subsequente**, não PV de 1º nível |
| PM | **Soma** PM de todas as classes |
| Perícias/proficiências | **Não** ganha treinos/proficiências da nova classe no 1º nível nela |
| Nível de personagem | Soma dos níveis de classe |

## Regras de combate / progressão

- **Ataque:** teste de **Luta** ou **Pontaria** vs **Defesa** (não BBA d20 separado como eixo principal — revisar se `bba_tipo` permanece como atalho UI).
- **Bônus em perícias por nível:** ⌊nível/2⌋ (a cada nível par +1) — ver RF 04.
- **Devoção:** Clérigo, Paladino, Druida e outras — p.96+ (RF 09).

## Requisitos funcionais

| ID | Requisito | Prioridade |
|----|-----------|------------|
| RF-T03a | API `GET /tormenta/regras/classes` — **14** classes v1.3 | P0 |
| RF-T03b | PV/PM iniciais + ganho/nível conforme tabelas acima | P0 |
| RF-T03c | Arcanista + caminho Bruxo/Mago/Feiticeiro | P0 |
| RF-T03d | Perícias de classe (fixas + N escolhas + INT) | P0 |
| RF-T03e | Modal benefícios / Poder de [Classe] por nível (1–20) | P0 |
| RF-T03f | Multiclasse: PV/PM/perícias conforme p.34 | P1 |
| RF-T03g | Orçamento perícias na criação | P1 | **Feito** — wizard v1.3 + validação API + hint na ficha |
| RF-T03h | Habilidades ativas (fúria, etc.) na arena | P2 |

## Estado de implementação

| Item | Estado |
|------|--------|
| `classes_v13.json` (14 classes) | **Feito** |
| API `GET /regras/classes?regra_versao=v13` | **Feito** |
| PV automático por fórmula v1.3 | **Feito** | `progressao_pv_t20.py`, cálculo automático na ficha, wizard |
| PM/nível por classe (todas as classes) | **Feito** | `conjuracao_classe_v13.json` + preview |
| Arcanista 3 caminhos | **Feito** | Wizard + ficha + validação salvar |
| Bucaneiro, Caçador, Cavaleiro, Inventor, Lutador, Nobre | **Feito** | `classes_v13.json` |
| mago, feiticeiro, monge, samurai, swashbuckler, ranger | **Legado — ocultar no core v1.3** | **Feito** (lista v13 não inclui) |
| PM multiclasse na UI | **Feito** | `multiclasse_v13` + `t20-multiclasse-v13.js`; API `/pm-preview-multiclasse` |
| Subir nível multiclasse | **Feito** | Modal escolhe classe; `multiclasse_v13` + PV/PM p.34 |
| Modal 20 níveis | **Feito** (texto v1.3 quando `regra_versao=v13`) |
| Orçamento perícias wizard/ficha v1.3 | **Feito** | `t20-dashboard-pericias-v13.js`, `t20-pericias-orcamento.js`, API validar-criacao |

## Gap código (MB → v1.3)

```text
Mapeamento:
  mago + feiticeiro  → arcanista (+ caminho_arcanista)
  ranger             → cacador
  swashbuckler       → bucaneiro
  monge, samurai     → (fora do core; lutador ou suplemento Heróis)

Novos JSON/campos:
  pv_inicial, pv_por_nivel, pm_por_nivel  — por slug v1.3
  pericias_fixas[], pericias_escolha_qtd
  caminho_arcanista: bruxo | mago | feiticeiro

Arquivos:
  classes_mb.json, beneficios_nivel_mb.json, conjuracao_classe_mb.json
```

## Critérios de aceite

- Bárbaro 1º nível, CON 2: PV = **26** (24 + 2); PM = **3**.
- Arcanista 1º nível: PV = **8 + CON**; PM = **6**; caminho obrigatório na criação.
- Multiclasse arcanista 3 / paladino 1: PM máx = 3×6 + 1×3 = **21** (exemplo livro p.34).
- Personagem novo não lista mago, feiticeiro, ranger, swashbuckler, monge, samurai.

## Referência

- Livro: Tabela 1-3 p.32; classes p.36–81; multiclasse p.34.
- Dados: `classes_mb.json`, `beneficios_nivel_mb.json`.
- Magia: [06-magia-tormenta.md](06-magia-tormenta.md).
