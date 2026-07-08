# FEATURE: Atributos Tormenta 20 (Edição Jogo do Ano v1.3)

> **Fonte:** `Tormenta20-Edicao-Jogo-do-Ano-v1.3.pdf` — Termos p.11; «Definindo seus atributos» + Tabela 1-1 p.17; «Toques Finais» p.106.  
> **Não usar** regras d20 3.5 (`(valor−10)/2`, compra 15 pts) **nem** escala MB 8–18 / 20 pts.

## Descrição

Seis atributos (FOR, DES, CON, INT, SAB, CAR) na escala v1.3: **0 = média humana**, valores negativos e positivos possíveis. O **valor numérico do atributo** entra **diretamente** nas fórmulas (Defesa, perícias, CD de magia) — **não** há conversão `(valor−10)/2` nem tabela de «modificador por faixas» estilo MB/d20.

## Regras de negócio (v1.3)

### Escala e uso mecânico

| Conceito | Regra (livro) |
|----------|----------------|
| Média humana | Atributo **0** |
| Defesa (p.106) | **10 + Destreza + bônus de armadura e escudo** |
| CD de magia (p.170) | **10 + metade do nível + atributo-chave** |
| Valor de perícia (p.114) | **⌊nível/2⌋ + atributo-chave + bônus de treino** (ver RF 04) |
| INT positiva (p.17) | Perícias treinadas extras = **valor de INT** (não precisam ser de classe) |

> **Legado Arena:** `modificador_atributo_t20()` e escala 8–18 são **MB antigo** — migrar para valor direto v1.3.

### Geração («Definindo seus atributos», p.17)

| Método | Regra |
|--------|--------|
| **Pontos** | Todos os atributos começam em **0**; **10 pontos** para aumentar (Tabela 1-1). Reduzir um atributo para **−1** concede **+1 ponto** adicional. |
| **Rolagens** | **6×** (4d6, descarta menor, soma os três). Converte cada total na Tabela 1-1 e distribui entre os seis atributos. Se **soma dos seis < 6**, rerrola o **menor** até **≥ 6**. |

**Tabela 1-1 (resumo operacional — confirmar no exemplar p.17):**

| Atributo | Custo (pontos) | Rolagem 4d6 |
|----------|----------------|-------------|
| −2 | — | ≤ 7 |
| −1 | −1 pt (reduzir de 0) | 8–9 |
| 0 | 0 | 10–11 |
| +1 | 1 pt | 12–13 |
| +2 | 2 pts | 14–15 |
| +3 | 4 pts | 16–17 |
| +4 | 7 pts | 18 |

Registrar `metodo_geracao_atributos`: `compra_pontos` | `4d6`.

### Atributos mínimos (p.17)

Valor **< −5**: FOR/DES → paralisado; CON → morte; INT/SAB → inconsciente; CAR → vira NPC (ignora imunidades).

### PV e PM (p.11, p.106)

| Recurso | Regra |
|---------|--------|
| **PV** | ≥ 1 PV → age normalmente; **≤ 0** → inconsciente e **sangrando** (detalhe combate p.236) |
| **PM** | Gasto para **magias, poderes e habilidades** de **todas** as classes (Introdução item 16) |
| Recuperação (noite 8h, p.106) | Ruim = ⌊nível/2⌋ PV/PM; Normal = nível; Confortável = 2× nível; Luxuosa = 3× nível |

### Características derivadas (p.106)

| Campo | Regra |
|-------|--------|
| Deslocamento | **9 m** padrão (Médio); raça pode alterar |
| Tamanho | Médio padrão; tabela 1-21 (Pequeno +2 Furtividade / −2 manobras, etc.) |
| Ajustes raciais | Somados **após** geração de atributos (passo raça) |

## Requisitos funcionais

| ID | Requisito | Prioridade |
|----|-----------|------------|
| RF-T01a | Persistir 6 atributos na escala v1.3 (−2…+4 na criação típica) | P0 |
| RF-T01b | Compra: **10 pts**, base **0**, −1 → +1 pt; validar Tabela 1-1 | P0 |
| RF-T01c | 4d6: conversão Tabela 1-1 + reroll menor se soma < 6 | P0 |
| RF-T01d | Fórmulas usam **valor do atributo**, não `modificador_atributo_t20` | P0 |
| RF-T01e | Defesa = 10 + DES + armadura/escudo na ficha | P0 |
| RF-T01f | `metodo_geracao_atributos` em `ficha_json` | P1 |
| RF-T01g | PM máx/atual por classe (Tabela 1-3) + recuperação por descanso | P1 |
| RF-T01h | INT > 0 → N perícias treinadas extras (= INT) | P2 |

## Backlog UI — escala v1.3 na mesa (RF-T01-ui-*)

> **Contexto (v1.3 vs MB):** na mesa e na ficha pronta fala-se **For 5, Des 2, Int 0** — nunca **14 ou 15**. Escala 6–18 / Tabela 1-1 **só** na geração (4d6 ou compra no wizard). Backend e JSON v1.3 já persistem nativo; gap principal é **UI + contrato frontend**.

### Matriz de exibição

| Contexto | Exibir |
|----------|--------|
| Wizard passo atributos (4d6) | Rolagem bruta (opcional) → **resultado nativo** |
| Wizard passo atributos (compra) | **−2…+4** + contador 10 pts |
| Ficha jogador (pós-criação) | **Só nativo** |
| Ficha monstro/NPC | **Só nativo** (ex. For 5) |
| Perícias / defesa / CD | Valor do atributo, não score 10–18 |
| Legado MB (`regra_versao !== v13`) | Manter 8–18; não misturar |

### Requisitos

| ID | Requisito | Prioridade | Estado | Artefatos principais |
|----|-----------|------------|--------|----------------------|
| RF-T01-ui-a | Ficha v1.3: círculos de atributo exibem **valor nativo** (−2…+4 típico; monstros sem teto rígido) — **nunca** score 10–18 (ex. 14, 16) | P0 | **Feito** | `t20-atributos-resumo.js`, `ficha-personagem.html` |
| RF-T01-ui-b | Ficha v1.3: edição e resumo usam inputs/labels em nativo; remover duplicata confusa «valor / mod.» | P0 | **Feito** | `ficha-personagem.html`, `t20-atributos-ui.js` |
| RF-T01-ui-c | Ficha v1.3: hints e tooltips pós-criação **sem** escala 10–18 («10 = 0», «12–13 = +1») | P0 | **Feito** | `t20-atributos-ui.js` |
| RF-T01-ui-d | Raça v1.3: UI mostra **base + ajuste racial = final** todos em escala nativa (ex. 0 + 2 = 2) | P0 | **Feito** | badges raciais dashboard + ficha resumo |
| RF-T01-ui-e | Wizard compra v1.3: inputs **−2…+4**, base 0, **10 pts** (Tabela 1-1); sem campos 8–18 | P0 | **Feito** | `t20-atributos-geracao.js`, `dashboard.html` |
| RF-T01-ui-f | Wizard 4d6 v1.3: rolagem bruta (3–18) **opcional** na UI; ao salvar persiste **só nativo**; reroll se soma < 6 | P0 | **Feito** | `t20-atributos-geracao.js` (4d6 já converte; UI nativa) |
| RF-T01-ui-g | Cadastro monstro/NPC: atributos em escala nativa (ex. Bugbear For 5, Des 3, Int −1) — sem `min=6 max=18` | P1 | **Feito** | `dashboard.html` (−99…99) |
| RF-T01-ui-h | `contribuicaoAtributo(val, rv)`: v1.3 trata `val` como **nativo** (sem `(val−10)/2`); documentar contrato | P0 | **Feito** | `t20-regra-versao.js`, `docs/tormenta/05-contrato-dados-ficha-json-e-api.md` |
| RF-T01-ui-i | Arena/combate v1.3: rolagens e previews usam nativo da API (corrigir passagem score↔nativo) | P0 | **Feito** | `t20-combate-rolagens.js` + `contribuicaoAtributo` |
| RF-T01-ui-j | Dashboard preview PV/CON v1.3: ler **CON nativa** persistida, não score cru | P0 | **Feito** | `t20-dashboard-step2-v13.js` (inputs nativos) |
| RF-T01-ui-k | Backend conjuração v1.3: trocar `modificador_atributo_t20` por `contribuicao_atributo_t20(..., regra_versao)` | P1 | **Feito** | `conjuracao_combate_t20.py`, `magias_*_t20.py` |
| RF-T01-ui-l | Subir nível: atributos **não mudam**; UI não sugere aumento; se exibir atributos, usar nativo | P1 | **Feito** | `t20-subir-nivel.js` |
| RF-T01-ui-m | Contrato: `for_valor`…`car_valor` = atributo de jogo v1.3; escala 6–18 só em `atributos_compra` / wizard | P1 | **Feito** | `docs/tormenta/05-contrato-dados-ficha-json-e-api.md` |
| RF-T01-ui-n | Migração opcional: detectar fichas v1.3 com score 10–18 e converter → nativo | P2 | **Feito** | `scripts/migrar_atributos_v13_score.py`, `atributos_migracao_v13_t20.py` |

**Executar migração (RF-T01-ui-n):**

```bash
# Dry-run (lista candidatos, não grava)
python3 backend/scripts/migrar_atributos_v13_score.py

# Aplicar em staging/prod (após revisar dry-run)
python3 backend/scripts/migrar_atributos_v13_score.py --aplicar

# Uma ficha só
python3 backend/scripts/migrar_atributos_v13_score.py --id 42 --aplicar
```

Heurística: só `regra_versao=v13`; converte atributo se `>= 12`, ou 6/8/10 se outro atributo da ficha for `>= 12`. **For 5** (Bugbear) não é alterado. Auditoria em `ficha_json._migracao_atributos_v13_score`.
| RF-T01-ui-o | Testes: resumo ficha v1.3 exibe nativo; Bugbear For 5; perícia nv 3 FOR 4 treinada = +7 | P1 | **Parcial** | `t20-atributos-resumo.test.js`; E2E manual pendente |

### Critérios de aceite (RF-T01-ui)

1. Ficha pronta: círculos mostram **0, 1, 2, 3, 4, −1…** — nunca 10–18.
2. Monstro Bugbear: **For 5, Des 3, Con 2, Int −1, Sab 0, Car −2** na ficha e no cadastro.
3. Criação 4d6: conversão visível (opcional); resultado final só em nativo após salvar.
4. Compra: 10 pts, base 0, custos 1/2/4/7 — sem sensação «a cada 2 pontos de atributo» estilo MB.
5. Humano FOR 0 + raça +2 → UI exibe **2**, não 12 nem 14.
6. Perícia nv 3, FOR 4, treinada → **+7** na ficha (⌊3/2⌋ + 4 + 2).
7. Subir nível: atributos inalterados e exibidos em nativo.
8. Legado MB (`regra_versao=mb`) continua com 8–18 sem regressão.

### Dependências sugeridas

```
RF-T01-ui-m (contrato) ──┐
RF-T01-ui-h (contribuição) ─┬─► RF-T01-ui-a,b,c ─► RF-T01-ui-d
RF-T01-ui-e,f (wizard) ────┘         │
                                     ├─► RF-T01-ui-i,j,k
                                     └─► RF-T01-ui-g,l,o
RF-T01-ui-n (migração) — após ui-a…g em staging
```

### Perguntas abertas (mesa)

| # | Pergunta |
|---|----------|
| Q1 | Na criação 4d6, exibir rolagem bruta (ex. «15 → +2») ou só resultado final? |
| Q2 | Edição de atributo pós-criação: permitida na ficha ou só na criação? |
| Q3 | Monstros com For > 4: confirmar UI sem converter para escala 10. |
| Q4 | Fichas já salvas com valores 12–18: migrar automaticamente ou manual? |

## Estado de implementação

| Item | Estado | Notas |
|------|--------|-------|
| 6 atributos na ficha | **Feito** | UI v1.3 exibe valor nativo (RF-T01-ui-a…c) |
| `modificador_atributo_t20` (faixas d20) | **Feito (legado MB)** | v1.3: RF-T01-ui-h, RF-T01-ui-k |
| Compra 20 pts / 8–18 | **Feito (v1.3)** | Wizard −2…+4 / 10 pts (RF-T01-ui-e) |
| 4d6 + reroll | **Feito** | Converte para nativo; UI nativa (RF-T01-ui-f) |
| Defesa 10 + DES (valor) + armadura/escudo | **Feito** | `defesa_t20.py`, `t20-regra-versao.js`, ficha v1.3 |
| Monstro/NPC atributos | **Feito** | RF-T01-ui-g |
| PM universal | **Parcial** | |
| Recuperação PV/PM por descanso | **Não feito** | RF-T01g |

## Gap código

| Ficheiro / módulo | Problema | Alvo v1.3 |
|-------------------|----------|-----------|
| `atributos_compra_pontos.json` | `pontos_iniciais: 20`, custos 8–18 | 10 pts, Tabela 1-1 p.17 |
| `atributos_t20.py` | `modificador_atributo_t20`, validação 4d6 MB | Valor direto; conversão 4d6 v1.3 |
| Ficha / combate | Defesa, CD magia, perícias | Valor de atributo, não modificador MB |
| Personagens legados | Escala 8–18 | Estratégia de migração ou flag `edicao: mb` |

## Critérios de aceite

- Personagem nível 3, FOR **4**, treinado em Luta → valor de perícia **+5** (+1 ⌊3/2⌋ + 4 FOR), conforme exemplo p.114.
- Defesa com DES **2** e sem armadura → **12** (10 + 2).
- Compra: exatamente **10 pts** gastos (líquido após reduções a −1).
- Rolagem: soma final dos seis atributos **≥ 6**.
- Nenhuma fórmula v1.3 usa `(valor−10)/2`.

## Referência

- Livro: p.11 (termos); p.17 (Tabela 1-1); p.106 (PV, PM, Defesa, tamanho, deslocamento).
- Contrato: `docs/tormenta/05-contrato-dados-ficha-json-e-api.md`.
