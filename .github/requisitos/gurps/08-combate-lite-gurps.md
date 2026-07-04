# FEATURE: Sistema de Combate Lite GURPS

## Descrição Breve
Implementar versão simplificada de combate com Iniciativa, Ataques rápidos, Defesa passiva, Dano simplificado e Condições básicas.

## Regra Principal
Combate em rodadas de 1 segundo. Iniciativa = 1d6 + WIS mod. Ataque = 1d20 + skill vs. Defesa Passiva (10 + DEX). Acerto = aplica dano. Sem reações complicadas ou ações múltiplas — apenas atacar ou defender.

## Dados/Campos Necessários

### Combatente Lite
- combatanteId: string
- nome: string
- hp: number
- defesa_passiva: number (10 + DEX mod)
- skill_combate: number (nível em combate)
- dano_arma: string (ex: "1d8+2")
- condicoes: string[] (atordoado, cego, preso)

## 1. INICIATIVA SIMPLIFICADA

**Fórmula**: 1d6 + WIS mod

Maior resultado vai primeiro. Sem rerolls em empates — quem tem WIS mod maior vai primeiro.

### Exemplo
- Guerreiro: 1d6 (rolou 4) + WIS +1 = 5
- Mago: 1d6 (rolou 3) + WIS +2 = 5
- Resultado: Mago vai primeiro (WIS +2 > +1)

## 2. ATAQUES RÁPIDOS

### Fórmula de Ataque

resultado = 1d20 + skill_combate + modificadores
sucesso = resultado >= defesa_passiva_alvo


### Modificadores Simples

| Situação | Bônus |
|----------|-------|
| Alvo desprevenido | +4 |
| Alvo acuado | +2 |
| Atacante em elevação | +2 |
| Atacante em desvantagem | -2 a -4 |
| Cansado | -2 |
| Ferido (metade HP) | -1 |

### Exemplo Ataque
- Guerreiro: skill 12, STR mod +2
- Ataque: 1d20 (rolou 14) + 12 = 26
- Defesa Passiva Goblin: 10 + DEX 1 = 11
- 26 >= 11 → **ACERTO**

## 3. DEFESA PASSIVA

**Fórmula**: 10 + DEX mod

Sem testes — use direto. Não pode mudar durante rodada.

### Modificadores de Defesa

| Situação | Ajuste |
|----------|--------|
| Escudo | +2 |
| Armadura Leve | -1 |
| Armadura Média | -2 |
| Armadura Pesada | -3 |
| Cego | +4 (atacantes têm penalidade) |

### Exemplo Defesa
- Mago com DEX 12 (mod +1): Defesa = 10 + 1 = 11
- Com Escudo: 11 + 2 = 13

## 4. DANO SIMPLIFICADO

**Fórmula**: 1d[X] + STR mod + bônus arma

### Dano por Arma (Resumido)

| Tipo | Dano | Exemplo |
|------|------|---------|
| Adaga | 1d4 | Ladrão |
| Espada Curta | 1d6 | Escudeiro |
| Espada Média | 1d8 | Guerreiro |
| Espada Grande | 1d10 | Guerreiro Pesado |
| Machado | 1d8 | Berserker |
| Arco | 1d8 | Arqueiro |
| Pistola | 2d6 | Atirador |

### Exemplo Dano
- Guerreiro com STR +3 ataca com Espada Longa (1d8)
- Dano: 1d8 (rolou 6) + 3 = **9 de dano**

## 5. CRÍTICOS RÁPIDOS

**Crítico**: rolar 20 natural no ataque
- Multiplique o dano por 2
- Sem testes adicionais

### Exemplo Crítico
- Ataque: 1d20 (rolou 20) + 12 = 32 → **CRÍTICO CONFIRMADO**
- Dano normal: 1d8 + 3 = 6
- Dano crítico: 6 × 2 = **12 de dano**

## 6. CONDIÇÕES ESPECIAIS

### Condições Simples

| Condição | Efeito | Duração |
|----------|--------|---------|
| Atordoado | -2 em ataque, defender passivamente | 1 rodada |
| Cego | Atacantes têm +4, defesa +2 | Até remover |
| Agarrado | -4 em ataque, movimento 0 | Até escapar (teste STR vs STR) |
| Incapacitado | Não age | Até recuperar (1 rodada repouso) |
| Envenenado | -1 DEX, dano 1 PV/rodada | 10 rodadas |

### Remover Condições
- **Atordoado**: recupera ao final da próxima rodada
- **Cego**: magia ou tempo
- **Agarrado**: teste STR (CD = STR do atacante)
- **Envenenado**: antídoto ou tempo (10 rodadas)

## 7. PV E MORTE RÁPIDA

### Faixas de Saúde

| HP | Estado |
|----|--------|
| 100% | Saudável |
| 50% | Ferido |
| 0 | Inconsciente |
| -10 | Morte |

### Morte Rápida
- PV <= 0: inconsciente
- PV < -10: morte imediata
- Se mantém acima de -10: sobrevive (teste se recupera)

## 8. ESTRUTURA DE RODADA

1. **Iniciativa**: calcular no início do combate
2. **Turnos**: cada um ataca ou se defende
3. **Dano**: resolver imediatamente
4. **Próxima Rodada**: repetir com mesma ordem

### Duração
- Rodada = 1 segundo de ação
- Combate típico: 3-10 rodadas

## 9. FUGA E MOVIMENTO

- Mover 1× distância = ação (sem ataque)
- Fugir: teste de corrida (DEX vs. STR do perseguidor)
- Alcance corpo-a-corpo: 2m de distância

## Validações

- Iniciativa = 1d6 + WIS, sem reroll em empate
- Defesa Passiva = 10 + DEX (constante)
- Ataque = 1d20 + skill vs. Defesa
- Dano = 1d[X] + STR (mínimo 1)
- PV >= -10 é morte, PV < -10 é morte automática
- Condições expira (atordoado = 1 rodada, outros = até remover)

## Cálculos

### Iniciativa
iniciativa = 1d6 + WIS_mod
ordem = sort(todos_combatentes by iniciativa DESC)

### Ataqueresultado = 1d20 + skill_combate + mod_situação
sucesso = resultado >= defesa_passiva

### Danodano = 1d[arma] + STR_mod
dano_final = max(1, dano)

## Exemplo Completo: Combate Rápido

### Setup: Guerreiro vs. 2 Goblins

**Guerreiro**:
- HP: 30, Defesa: 13 (10 + DEX +1 + Escudo +2)
- Skill Combate: 14, Dano: 1d8+2

**Goblin 1**:
- HP: 8, Defesa: 12 (10 + DEX +1)
- Skill Combate: 10, Dano: 1d6

**Goblin 2**:
- HP: 8, Defesa: 12
- Skill Combate: 10, Dano: 1d6

### Rodada 1: Iniciativa
- Guerreiro: 1d6 (4) + WIS +1 = 5
- Goblin 1: 1d6 (3) + WIS 0 = 3
- Goblin 2: 1d6 (2) + WIS 0 = 2
- **Ordem**: Guerreiro → Goblin 1 → Goblin 2

### Turno Guerreiro
- Ataque Goblin 1: 1d20 (16) + 14 = 30 vs. 12 → **ACERTO**
- Dano: 1d8 (6) + 2 = **8 de dano**
- Goblin 1 HP: 8 - 8 = 0 → Inconsciente

### Turno Goblin 1
- Inconsciente, pula

### Turno Goblin 2
- Ataque Guerreiro: 1d20 (8) + 10 = 18 vs. 13 → **ACERTO**
- Dano: 1d6 (3) = **3 de dano**
- Guerreiro HP: 30 - 3 = 27

### Rodada 2
- Guerreiro ataca Goblin 2...

## Referência do Livro
GURPS 4E: Módulo Básico - Combate Lite
Versão simplificada para jogo rápido

