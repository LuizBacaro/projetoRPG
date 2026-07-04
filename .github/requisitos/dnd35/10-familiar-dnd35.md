# Familiar — Regras D&D 3.5 (Mago e Feiticeiro)

## Sumário

0. [Escopo e relação com Companheiro Animal](#escopo)
1. [Quem pode ter Familiar](#quem-pode)
2. [Convocação e custo](#convocacao)
3. [Escolha da espécie](#especies)
4. [Estatísticas básicas](#estatisticas)
5. [Tabela de progressão do mestre](#tabela-progressao)
6. [Habilidades do familiar](#habilidades-familiar)
7. [Habilidades especiais concedidas ao mestre](#bonus-mestre)
8. [Magias e vínculo](#magias)
9. [Morte, dispensa e substituição](#morte)
10. [Restrições e multiclasse](#restricoes)
11. [Contrato Arena (implementação futura)](#arena)
12. [Referência PHB](#referencia)

**Fonte:** Livro do Jogador D&D 3.5 — capítulo de classes (Mago e Feiticeiro); texto de *Familiar* no PHB (edição em `livros/D&D3_5_livro_jogador.pdf`, por volta da p. 40 na edição do repositório, junto às habilidades de classe).

**Documento irmão:** [09-companheiro-animal-dnd35.md](09-companheiro-animal-dnd35.md) (Druida / Ranger apenas).

---

## 0. Escopo e relação com Companheiro Animal {#escopo}

| | **Familiar** (este RF) | **Companheiro animal** (RF 09) |
|---|------------------------|--------------------------------|
| Classes | **Mago**, **Feiticeiro** | **Druida**, **Ranger** (4º+) |
| Tipo de criatura | Besta mágica (animal comum melhorado) | Animal típico da espécie com HD bônus |
| Convocação | 24 h + 100 PO | Vínculo natural (24 h após morte do anterior) |
| Nível para tabela | Soma dos níveis de classe com *Familiar* | Nível efetivo (Druida = nível; Ranger = nível − 3) |

**PHB:** *«Assim, um druida/feiticeiro não poderia usar seu companheiro animal como familiar.»* — o mesmo animal **não** pode cumprir os dois papéis.

**Arena hoje:** ficha e API dedicadas (`/api/v1/familiares`); na arena, ao iniciar combate com **«Incluir companheiro animal / familiar»** marcado, o familiar entra na ordem de iniciativa como NPC espelhado (`arena_combatente_id`).

---

## 1. Quem pode ter Familiar {#quem-pode}

**Classes beneficiárias:**

- **Mago** (*Wizard*): obtém a característica **Familiar** como habilidade de classe (PHB, classe Mago).
- **Feiticeiro** (*Sorcerer*): idem (PHB, classe Feiticeiro).

**Nível:** a partir do momento em que a classe concede a habilidade (normalmente **1º nível** de Mago ou Feiticeiro, conforme tabela da classe no PHB).

**Multiclasse Mago + Feiticeiro:**

- Os níveis das classes que possuem *Familiar* **acumulam** para determinar a linha da [tabela de progressão](#tabela-progressao) e as habilidades do familiar.
- Exemplo: Mago 3 / Feiticeiro 2 → tratar como mestre de familiar de **5º nível** na tabela.

**Não elegíveis:** Druida e Ranger usam [companheiro animal](09-companheiro-animal-dnd35.md), não familiar.

---

## 2. Convocação e custo {#convocacao}

Para obter um familiar:

1. **Tempo:** processo de **24 horas** ininterruptas (ritual).
2. **Custo:** materiais mágicos no valor de **100 PO**.
3. **Resultado:** a criatura escolhida torna-se **besta mágica** — companheira e serva do conjurador, mais resistente e inteligente que um animal comum.

O conjurador **escolhe o tipo de animal** entre a [lista permitida](#especies). O poder do familiar **aumenta** conforme o mestre ganha níveis de classe com *Familiar*.

---

## 3. Escolha da espécie {#especies}

Somente um **animal comum** pode tornar-se familiar (não mutação mágica prévia). Tipos PHB e bônus especiais ao mestre:

| Familiar | Bônus especial ao mestre |
|----------|---------------------------|
| Cobra (víbora pequena) ♦ | +3 em testes de Blefar |
| Gato | +3 em testes de Furtividade |
| Lagarto | +3 em testes de Escalar |
| Rato | +3 em testes de resistência de Fortitude |
| Texugo | +3 em testes de resistência de Reflexos |
| Coruja | +3 em testes de Observar na penumbra |
| Corvo* | +3 em testes de Avaliação |
| Falcão | +3 em testes de Observar em locais iluminados |
| Morcego | +3 em testes de Ouvir |
| Sapo | +3 pontos de vida |

\* Corvo: fala um idioma à escolha do mestre (habilidade sobrenatural).

♦ Víbora pequena.

> **Nota Arena:** catálogo separado do companheiro animal (lobo, cavalo, etc.). Não reutilizar `companheiros_especies.py` sem mapear espécie → `tipo_vinculo: familiar`.

---

## 4. Estatísticas básicas {#estatisticas}

Usar estatísticas da espécie no **Livro dos Monstros**, com as alterações abaixo.

### Dados de Vida (DV)

- Para efeitos que dependem de DV: usar o **nível de personagem do mestre** ou o **DV total da espécie**, o que for **maior**.

### Pontos de Vida

- PV do familiar = **metade dos PV totais do mestre** (sem PV temporários), **arredondado para baixo**.
- Exemplo PHB: mestre 2º nível com 9 PV → familiar com **4 PV**.

### Ataques

- Bônus de ataque base do **mestre** (todas as classes).
- Modificador de **Destreza ou Força** do familiar (o maior) no ataque natural.
- Dano: igual ao da criatura normal da espécie.

### Testes de resistência

- Usar os bônus base do **mestre** (todas as classes) ou os do familiar (Fort +2, Ref +2, Von +0), o que for **maior**.
- Modificadores de atributo do **familiar** nos testes; **não** partilha bônus de itens/talentos do mestre.

### Perícias

- Graduações do animal da espécie **ou** do mestre, o que for maior; modificadores do familiar.
- Perícias como Ofício ou Profissão podem estar além da capacidade do animal.

### Tipo

- Considerado **besta mágica** para efeitos que dependem do tipo de criatura.

### Alcance das habilidades

- Bônus especiais ao mestre e habilidades do familiar aplicam-se quando a criatura está a **1,5 m** do mestre (salvo indicação em contrário, ex.: vínculo empático 1,5 km).

---

## 5. Tabela de progressão do mestre {#tabela-progressao}

*Nível de classe do mestre* = soma dos níveis de Mago + Feiticeiro (e outras classes que concedam *Familiar*, se houver).

| Nível do mestre | Armadura natural | Int | Especial |
|-----------------|------------------|-----|----------|
| 1–2 | +1 | 6 | Prontidão, evasão aprimorada, partilhar magias, vínculo empático |
| 3–4 | +2 | 7 | Transmitir magias de toque |
| 5–6 | +3 | 8 | Falar com mestre |
| 7–8 | +4 | 9 | Falar com animais da espécie |
| 9–10 | +5 | 10 | — |
| 11–12 | +6 | 11 | Resistência à magia |
| 13–14 | +7 | 12 | Vidência no familiar |
| 15–16 | +8 | 13 | — |
| 17–18 | +9 | 14 | — |
| 19–20 | +10 | 15 | — |

- **Armadura natural:** bônus **adicional** à AN natural da espécie.
- **Int:** Inteligência do familiar (como humano comum; não necessariamente perspectiva humana na comunicação).

As habilidades da tabela **acumulam**.

---

## 6. Habilidades do familiar {#habilidades-familiar}

### Prontidão (Ext)

- Com o familiar ao alcance da mão, o mestre ganha o talento **Prontidão**.

### Evasão aprimorada (Ext)

- Se o familiar passar em Reflexos contra efeito que causa metade do dano em sucesso, **não sofre dano** em sucesso.

### Partilhar magias (Ext)

- Magias de alcance **pessoal** no mestre podem ser conjuradas com o familiar como alvo se este estiver a **≤ 1,5 m** no momento da conjuração.
- Se duração ≠ instantânea, deixa de afetar o familiar se ele sair da área (> 1,5 m) até voltar.
- Magias com alvo **«Você»** podem ser conjuradas no familiar (ex.: toque à distância).
- Mestre e familiar podem partilhar magias mesmo quando o efeito normalmente não afeta bestas mágicas.

### Vínculo empático (Ext)

- Alcance **1,5 km**; comunicação telepática limitada a **emoções** (medo, fome, curiosidade, etc.).
- Inteligência baixa e diferença de perspectiva podem causar mal-entendidos.
- Mestre pode **teletransportar-se** para local que o familiar investigou (como se tivesse visto o local).

### Transmitir magias de toque (Sob)

- A partir do **3º nível** do mestre: magias de toque podem ser «portadas» pelo familiar em contato durante a conjuração; familiar entrega o toque como o mestre.
- Outra magia conjurada antes do toque ser entregue **dissipa** o toque pendente.

### Falar com o mestre (Ext)

- A partir do **5º nível**: comunicação verbal em idioma comum (só entre mestre e familiar).

### Falar com animais da espécie (Ext)

- A partir do **7º nível**: comunica com animais comuns da mesma família (morcegos com morcegos, felinos com felinos, etc.), limitado pela Inteligência das criaturas.

### Resistência à magia (Ext)

- A partir do **11º nível**: RM = **nível do mestre + 5**; conjuradores precisam superar em teste de conjurador.

### Vidência no familiar (SM)

- A partir do **13º nível**: uma vez por dia, observar local remoto pelos sentidos do familiar (como magia *vidência*).

---

## 7. Habilidades especiais concedidas ao mestre {#bonus-mestre}

Ver [tabela de espécies](#especies) (+3 Blefar, Furtividade, etc.). Aplicam-se com familiar a **1,5 m** (salvo vínculo empático).

---

## 8. Magias e vínculo {#magias}

Resumo já coberto em [Partilhar magias](#habilidades-familiar) e [Transmitir toque](#habilidades-familiar). Implementação Arena deve validar:

- Alcance e alvo no momento da conjuração.
- Distância 1,5 m para manutenção de efeitos não instantâneos.
- Fila de toque transmitido pelo familiar.

---

## 9. Morte, dispensa e substituição {#morte}

### Morte do familiar ou dispensa voluntária

1. Teste de resistência de **Fortitude CD 15**.
2. **Falha:** perde **200 XP × nível na classe** (Mago/Feiticeiro relevante).
3. **Sucesso:** metade da perda de XP.
4. XP do feiticeiro/mago **nunca fica abaixo de 0** por morte do familiar (ex.: Hennet 3º, 3 230 XP, coruja morta — regra PHB).

### Substituição

- **Não** pode obter novo familiar durante **1 ano e 1 dia**.
- Familiar morto pode ser **ressuscitado** como personagem (sem perder nível/Constituição por ressurreição do familiar).
- Novo familiar após o período: novo ritual 24 h + 100 PO.

### Apenas um familiar

- Mesmo com várias classes que concedem *Familiar*, só **um** familiar **simultâneo**.

---

## 10. Restrições e multiclasse {#restricoes}

- ❌ Companheiro animal (Druida/Ranger) **e** familiar no mesmo personagem.
- ❌ Dois familiares simultâneos.
- ❌ Animal não comum como familiar base.
- ✅ Mago + Feiticeiro: níveis somam na tabela.

---

## 11. Contrato Arena (implementado) {#arena}

### Estado atual

| Camada | Situação |
|--------|----------|
| UI ficha | Modal dual **Companheiro animal / Familiar** (`CompanheiroAnimalFichaController.js`) |
| API | `/api/v1/familiares/*` — espécies, elegibilidade, calcular, CRUD |
| Regras | `rules/familiar.py`, `catalogs/familiares_especies.py` |
| Persistência | Tabela `familiares` (1:1 com `combatentes`); exclusão mútua com RF 09 |
| Arena | `VinculoArenaService` — NPC espelhado em `combatentes` (`tipo=npc`, `arena_combatente_id`); `POST /combate/iniciar` com `incluir_vinculos: true` (padrão) |

### Fluxo na arena

1. Jogador cadastra familiar na ficha (Mago/Feiticeiro).
2. Ao salvar, o backend sincroniza um NPC (`classe=Familiar`, PV/CA/INT da ficha).
3. Na configuração da arena, ao marcar **«Incluir companheiro animal / familiar»** e iniciar combate, o ID do NPC é acrescentado à ordem de iniciativa.
4. Dano/cura na arena usam o mesmo fluxo dos demais combatentes (`/combate/aplicar-dano`).

### Fora de escopo (arena MVP)

- Transmitir magias de toque, vínculo empático em tempo real, distância 1,5 m.
- Sincronização automática de PV do NPC → ficha após cada golpe (atualizar manualmente na ficha ou re-salvar).

### Critérios de aceite (MVP familiar)

- [x] Mago 1º e Feiticeiro 1º elegíveis; Druida usa só RF 09.
- [x] Convocação registra espécie, nome, PV derivados, Int e AN da tabela.
- [x] Multiclasse Mago+Feiticeiro soma nível na tabela.
- [x] Bloqueio se já existir companheiro animal no mesmo combatente.
- [x] Exibir bônus especial da espécie ao mestre na ficha.
- [x] Familiar entra na arena quando `incluir_vinculos` está ativo.

---

## 12. Referência PHB {#referencia}

- **Mago / Feiticeiro — Familiar:** convocação 24 h, 100 PO, besta mágica, tabela de progressão, morte (Fort CD 15, XP), 1 ano e 1 dia para substituir.
- **Exclusão:** companheiro animal ≠ familiar.
- **PDF do projeto:** `livros/D&D3_5_livro_jogador.pdf` (capítulo 3 — classes; localizar entrada *Familiar* na edição impressa/digital usada).

---

**Documento criado em:** maio/2026  
**Sistema:** D&D 3.5 — Livro do Jogador  
**Tradução:** Português brasileiro (texto alinhado ao PHB citado pelo projeto)
