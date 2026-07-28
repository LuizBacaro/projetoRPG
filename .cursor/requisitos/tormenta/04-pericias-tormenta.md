# FEATURE: Perícias Tormenta 20 (Edição Jogo do Ano v1.3)

> **Fonte:** `Tormenta20-Edicao-Jogo-do-Ano-v1.3.pdf` — Cap. 2 p.114–123; Tabela 2-1 p.115; subir de nível p.34 (bônus em perícias).  
> **Fontes de bônus externos (itens/poderes/raça):** ver [14-bonus-penalidades-pericias-fontes.md](14-bonus-penalidades-pericias-fontes.md) (RF-T14) e `bonus_pericias_fontes_v13.json`.

## Descrição

**28 perícias** com atributo-chave, flags de treinamento obrigatório e penalidade de armadura. Teste = **1d20 + valor de perícia** vs CD (Cap. 5).

## Fórmula principal (p.114)

```
Valor de Perícia = ⌊nível / 2⌋ + atributo-chave + bônus de treinamento (se treinado)
```

| Patamar de nível | Bônus de treinamento |
|------------------|----------------------|
| 1º–6º | **+2** |
| 7º–14º | **+4** |
| 15º+ | **+6** |

**Exemplo (livro):** 3º nível, FOR **4**, treinado em Luta → ⌊3/2⌋ + 4 + 2 = **+7**.

**Não treinado:** usa ⌊nível/2⌋ + atributo **sem** bônus de treino; perícias marcadas «Treinada» no livro **não podem** ser usadas sem treinamento.

### Perícias de resistência (p.114+)

**Fortitude**, **Reflexos** e **Vontade** resistem a efeitos negativos; efeitos que bonificam «testes de resistência» aplicam-se às três.

## Catálogo v1.3 — Tabela 2-1 (p.115)

Legenda: **T** = somente treinada; **A** = penalidade de armadura.

| Perícia | Atrib. | T | A | Perícia | Atrib. | T | A |
|---------|--------|---|---|---------|--------|---|---|
| Acrobacia | DES | | A | Luta | FOR | | |
| Adestramento | CAR | T | | Misticismo | INT | T | |
| Atletismo | FOR | | | Nobreza | INT | T | |
| Atuação | CAR | T | | Ofício | INT | T | |
| Cavalgar | DES | | | Percepção | SAB | | |
| Conhecimento | INT | T | | Pilotagem | DES | T | |
| Cura | SAB | | | Pontaria | DES | | |
| Diplomacia | CAR | | | Reflexos | DES | | |
| Enganação | CAR | | | Religião | SAB | T | |
| Fortitude | CON | | | Sobrevivência | SAB | | |
| Furtividade | DES | | A | Vontade | SAB | | |
| Guerra | INT | T | | | | | |
| Iniciativa | DES | | | | | | |
| Intimidação | CAR | | | | | | |
| Intuição | SAB | | | | | | |
| Investigação | INT | | | | | | |
| Jogatina | CAR | T | | | | | |
| Ladinagem | DES | T | A | | | | |

**Exceção (texto p.116):** em **Atletismo**, penalidade de armadura aplica-se apenas a **natação**, não a todos os usos.

## Perícias removidas vs MB antigo

| MB (remover) | v1.3 |
|--------------|------|
| Identificar Magia | **Misticismo** |
| Obter Informação | (incorporada em Diplomacia / Investigação) |
| Adestrar Animais | **Adestramento** |

## Requisitos funcionais

| ID | Requisito | Prioridade |
|----|-----------|------------|
| RF-T04a | API com **28** perícias + metadados Tabela 2-1 | P0 |
| RF-T04b | `calcular-bonus`: ⌊nível/2⌋ + **valor atributo** + treino +2/+4/+6 | P0 |
| RF-T04c | Bloquear usos «somente treinada» sem treino | P0 |
| RF-T04d | Penalidade armadura só onde Tabela 2-1 / exceção Atletismo | P0 |
| RF-T04e | UI tabela + rolagem `POST …/pericias/rolar` | P0 |
| RF-T04f | Percepção passiva (derivada de Percepção) | P1 |
| RF-T04g | Ofício: especialidades múltiplas (mesma perícia) | **Feito** |
| RF-T04h | DCs padrão (`pericias_dc_*.json`) | P1 |
| RF-T04i | Seletor de **uso** na rolagem (mesma perícia; não linha separada) | **Feito** (Cap. 2 + Atuação + `bonus_uso`) |

### RF-T04i — Usos vs especialidades (decisão de produto)

Em T20 **não** se desmembra Atletismo/Enganação em linhas com treino próprio. Isso vale só para **Ofício**. **Atuação** (p.116) é a **mesma** perícia com usos Apresentação / Impressionar — seletor no modal.

O que vale a pena é um **seletor de uso no momento da rolagem** (rótulo + `bonus_uso`), mantendo um único Tr/Atrib/Out/Σ.

Usos canônicos (Cap. 2 v1.3 p.114–123) em `t20-pericias-usos.js`:

| Perícia | Usos (ids) |
|---------|------------|
| Acrobacia | amortecer_queda · equilibrio · escapar · levantar_se · espaco_apertado · passar_inimigo |
| Adestramento | acalmar_animal · manejar_animal |
| Atletismo | corrida · escalar · **natacao** · saltar |
| Atuação | apresentacao · impressionar |
| Cavalgar | conduzir · galopar · montar_rapidamente |
| Conhecimento | idiomas · informacao |
| Cura | cuidados_prolongados · necropsia · primeiros_socorros · tratamento |
| Diplomacia | barganha · mudar_atitude · persuasao |
| Enganação | disfarce · falsificacao · fintar · insinuacao · intriga · mentir |
| Furtividade | esconder_se · seguir |
| Guerra | analisar_terreno · plano_de_acao |
| Intimidação | assustar · coagir |
| Intuição | perceber_mentira · pressentimento |
| Investigação | interrogar · procurar |
| Jogatina | apostar |
| Ladinagem | abrir_fechadura · ocultar · punga · sabotar |
| Misticismo | detectar_magia · identificar_criatura · identificar_item · identificar_magia · informacao · lancar_magia_armadura |
| Nobreza | etiqueta · informacao |
| Percepção | observar · ouvir |
| Religião | identificar_criatura · identificar_item · informacao · rito |
| Sobrevivência | acampamento · identificar_criatura · orientar_se · rastrear |

**Não entram no seletor:** Fortitude, Reflexos, Vontade, Iniciativa, Luta, Pontaria, Pilotagem (sem usos nomeados). **Ofício** = linhas por especialidade.

**Modelo Ofício (linha própria), não seletor:**

| Perícia | Tratamento |
|---------|------------|
| Ofício | **Feito** — linha por especialidade. |
| Atuação | **Feito** — seletor (Apresentação / Impressionar); não Ofício. |

**Critério de aceite (RF-T04i):**

1. Rolagem de perícia com usos listados pergunta o uso (ou usa default) **sem** criar linha extra nem consumir vaga de treinada.
2. Atletismo + uso `natacao` (legado `nadar`) → pen. armadura; demais usos sem pen. de natação.
3. Resultado / toast / log contextual mostra `Enganação (Mentir)`, não só `Enganação`.
4. Bônus «Outros» da linha separado de **`bonus_uso`** na API (`POST …/calcular-bonus`); mapa `ficha_json.pericias_usos_bonus`; badge na linha quando houver usos com bônus; migração de ids legados em `aplicarBonusMap`.

**Fora de escopo deste RF:** desmembrar Enganação/Atletismo em várias perícias treinadas.

## Estado de implementação

| Item | Estado | Notas |
|------|--------|-------|
| Catálogo v1.3 (`pericias_atributo_chave_v13.json`, 29 perícias) | **Feito** | Tabela 2-1; MB legado filtra placeholders |
| Fórmula v1.3 (⌊nível/2⌋ + atributo + treino +2/+4/+6) | **Feito** | `calcular-bonus`, rolagem, testes |
| Flags Atuação/Ofício treinada | **Feito** | v13: `somente_treinado: true` |
| Orçamento criação v1.3 | **Feito** | Sem graduações; INT valor direto |
| UI ficha (tabela, orçamento, rolagem) | **Feito** | Coluna graduação oculta em v1.3; restore por nome |
| Motor rolagem | **Feito** | Bloqueio «somente treinada» sem treino |
| Misticismo | **Feito** | Substitui Identificar Magia |
| Percepção passiva (UI) | **Feito** | Cartão «Pass.» na coluna esquerda; atualiza com perícias/equipamento |
| Ofício especialidades múltiplas | **Feito** | `oficio_especialidades[]` na ficha v1.3 |
| Ofício: linha por especialidade | **Feito** | Cada especialidade é uma linha com Tr/Atrib/Out/Σ e rolagem próprios; salva em `pericias[]` como `Ofício (x)`. Linha «Ofício» vira cabeçalho do grupo (sem treino/valores) e cada especialidade treinada consome uma vaga de treinada. Linhas filhas repetem `data-per-idx` do pai e usam `data-per-nome-canon="Ofício"` para bônus racial e lookup do backend. |
| Atletismo penalidade só natação | **Feito** | Seletor `natacao` + `uso_atletismo_natacao` na API |
| Seletor de uso na rolagem (RF-T04i) | **Feito** | Catálogo Cap. 2 completo; Atuação incluída; `bonus_uso` explícito na API; badge `N usos` |
| Catálogo fontes bônus/penalidade (RF-T14) | **Feito (dados+MVP)** | Catálogo JSON; melhorias TS em ataques → `itens_com_melhorias` no calcular-bonus |

## Gap código

```text
Alvo catálogo (28): acrobacia, adestramento, atletismo, atuacao, cavalgar, conhecimento,
  cura, diplomacia, enganacao, fortitude, furtividade, guerra, iniciativa, intimidacao,
  intuicao, investigacao, jogatina, ladinagem, luta, misticismo, nobreza, oficio,
  percepcao, pilotagem, pontaria, reflexos, religiao, sobrevivencia, vontade

Remover: identificar_magia, obter_informacao, placeholders, oficio_2
```

- `calcular-bonus`: trocar `modificador_atributo_t20(atributo)` por **valor do atributo** persistido.
- Treino: patamar por **nível do personagem**, não booleano fixo +2.

## Critérios de aceite

- Nível 7, DES 3, treinado Acrobacia → ⌊7/2⌋ + 3 + **4** = **+10** (não +2 de treino).
- Conhecimento sem treino → API/UI impede uso (exceto casos «informação» livre do livro).
- Acrobacia com armadura pesada aplica penalidade; Diplomacia não.
- Atletismo escalada: sem penalidade armadura; Atletismo natação: com penalidade.

## Referência

- Livro: Cap. 2 p.114–123; Tabela 2-1 p.115.
- Dados: `pericias_atributo_chave.json`, `pericias_dc_mb.json` (renomear).
