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

## Estado de implementação

| Item | Estado | Notas |
|------|--------|-------|
| 6 atributos na ficha | **Feito** | Escala errada (MB) |
| `modificador_atributo_t20` (faixas d20) | **Feito (legado MB)** | **Incompatível v1.3** |
| Compra 20 pts / 8–18 | **Feito (MB errado)** | Alvo: 10 pts / base 0 |
| 4d6 + reroll | **Parcial** | Falta Tabela 1-1 e soma ≥ 6 |
| Defesa 10 + DES (valor) | **Parcial** | Confirmar se usa mod. ou valor |
| PM universal | **Parcial** | |
| Recuperação PV/PM por descanso | **Não feito** | |

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
