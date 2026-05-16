# FEATURE: Sistema de Combate D&D 5E

## Descrição Breve
Implementar combate com Iniciativa (1d20 + DEX), Ataques (1d20 + bônus vs. AC), Ações variadas, e Dano com críticos.

## Regra Principal
Combate em rodadas de 6 segundos. Ordem por Iniciativa (1d20 + DEX mod). Cada turno: 1 ação + 1 movimento + reações. Ataque = 1d20 + bônus vs. AC. Acerto = dano do d. de arma + mod.

## Dados/Campos Necessários

### Combatente
- combatanteId: string
- nome: string
- hp: number (atual)
- maxHp: number (máximo)
- ac: number (classe de armadura)
- dexMod: number
- strMod: number (para corpo-a-corpo)
- proficienciaBonus: number
- armas: Arma[]
- condicoes: string[] (incapacitado, atordoado, cego, etc.)

### Rodada
- rodadaAtual: number
- ordemIniciativa: Combatente[] (ordenado)
- turnoAtual: Combatente

## 1. INICIATIVA

**Fórmula**: 1d20 + DEX mod

Maior resultado vai primeiro. Sem rerolls em empate — usar DEX mod como tiebreaker.

### Exemplo
- Guerreiro: 1d20 (14) + DEX +1 = 15
- Mago: 1d20 (12) + DEX +3 = 15
- Resultado: Mago vai primeiro (DEX +3 > +1)

## 2. AÇÕES POR TURNO

### Ação Padrão (1 por turno)
- Atacar (1 ataque ou múltiplos com Ataque Extra)
- Conjurar feitiço (tempo padrão)
- Usar habilidade de classe
- Usar objeto
- Ajuda/interferência

### Movimento (até velocidade)
- Deslocar até velocidade base (9m típico)
- Sacar/guardar arma
- Montar/desmontar
- Abrir porta simples

### Reação (1 por rodada)
- Ataque de oportunidade (sair do alcance)
- Escudo de feitiço
- Outras que especificam "reação"

### Ação Bônus (variável)
- Depende de classe/habilidade/feitiço
- Não automática

## 3. ATAQUES

### Ataque Corpo-a-Corpo
**Fórmula**: 1d20 + STR mod + bônus proficiência (se proficiente)

1. Role 1d20
2. Adicione STR mod + proficiência bônus (se tem proficiência)
3. Compare com AC alvo

**Se resultado >= AC**: ACERTO → dano

### Ataque à Distância
**Fórmula**: 1d20 + DEX mod + bônus proficiência (se proficiente)

Mesma base, mas usa DEX mod.

### Modificadores de Ataque

| Situação | Bônus |
|----------|-------|
| Vantagem | role 2d20, use maior |
| Desvantagem | role 2d20, use menor |
| Alvo incapacitado | automático acerto, crítico em 10+ |
| Alvo a mais de 1.5m | sem bônus |
| Alvo acuado | +2 (aliado próximo) |
| Cego/cego atacante | desvantagem |

### Exemplo Ataque
- Guerreiro STR +3, Proficiência +2
- Ataque: 1d20 (16) + 3 + 2 = 21
- AC alvo: 16
- 21 >= 16 → **ACERTO**

## 4. DANO

### Dano Corpo-a-Corpo
**Fórmula**: 1d[X] + STR mod

- X = dado de arma (1d6, 1d8, 1d10, 2d6, etc.)
- Adicione STR mod
- Mínimo 1 ponto

### Dano à Distância
**Fórmula**: 1d[X] + DEX mod (arco)

Ou 1d[X] sem mod (arma arremessada), dependendo da arma.

### Dano de Feitiço
Varia por feitiço (1d6, 2d6, 3d6, etc.)

### Dano Crítico
**Crítico**: rolar 20 natural no d20

- Multiplique os dados de dano (roll 2× o d[X])
- Adicione mod normalmente

**Exemplo Crítico**:
- Normal: 1d8 + 3 = 6 de dano
- Crítico: 2d8 + 3 = (8 + 5) = 13 de dano

## 5. CONDIÇÕES EM COMBATE

| Condição | Efeito |
|----------|--------|
| Incapacitado | não se move, não age, fala mal |
| Atordoado | desvantagem em ataques, reação descartada |
| Cego | desvantagem em ataques, atacantes +2 |
| Agarrado | velocidade = 0 |
| Envenenado | desvantagem em ataques/testes força |
| Assustado | desvantagem em testes/ataques enquanto vê origem |
| Prostrado | desvantagem em ataque, atacantes +2 corpo-a-corpo |

## 6. PONTOS DE VIDA

### Morte
- HP = 0: inconsciente, morrendo
- 3 falhas em testes de morte (1d20) → morte
- 3 sucessos → estabilizado
- Dano crítico (>= dano máximo em um ataque) = insta-morte

### Cura
- Poção: restaura valores (1d4+1, 2d4+2, etc.)
- Feitiço: 1d8+INT/WIS conforme classe
- Repouso longo: recupera 1d8 + CON mod (mínimo 1)

## 7. ESTRUTURA DE RODADA

1. **Iniciativa**: 1d20 + DEX mod para cada combatente
2. **Turnos**: em ordem de iniciativa
   - Ação padrão
   - Movimento
   - Ação bônus (se aplicável)
3. **Reações**: podem acontecer entre turnos
4. **Próxima rodada**: repete com mesma ordem

**Duração rodada**: 6 segundos

## Validações

- Iniciativa = 1d20 + DEX
- Ataque = 1d20 + STR/DEX + proficiência vs. AC
- Dano = 1d[X] + mod (mínimo 1)
- Crítico = 20 natural (roll 2× dados dano)
- HP nunca < 0 (morte em 3 falhas)
- Ações: 1 padrão + movimento + reação/ação bônus

## Cálculos

### Iniciativa
iniciativa = 1d20 + DEX_mod
ordem = sort(combatentes by iniciativa DESC)

### Ataqueresultado = 1d20 + mod_atributo + proficiencia_bonus
sucesso = resultado >= ac_alvo

### Danodano = 1d[arma] + mod_atributo
dano_critico = 2d[arma] + mod_atributo
dano_final = max(1, dano)



## Exemplo: Combate Guerreiro vs. Goblin

### Setup
**Guerreiro**:
- HP 30, AC 16, STR +3, DEX +1, Prof +2
- Espada Longa (1d8)

**Goblin**:
- HP 8, AC 15, STR +0, DEX +2, Prof +2
- Meia-lança (1d6)

### Rodada 1: Iniciativa
- Guerreiro: 1d20 (12) + 1 = 13
- Goblin: 1d20 (8) + 2 = 10
- **Ordem**: Guerreiro vai primeiro

### Turno Guerreiro
- **Ataque**: 1d20 (16) + 3 + 2 = 21 vs. AC 15 → **ACERTO**
- **Dano**: 1d8 (6) + 3 = **9 de dano**
- Goblin HP: 8 - 9 = -1 (inconsciente, morrendo)

### Resultado
- Goblin faz teste de morte (3 falhas = morte)
- Se sobrevive: estabilizado em 0 HP

## Referência do Livro
Capítulo 9: Combate | Iniciativa, Ações, Ataques, Dano


## Exemplo: Combate Guerreiro vs. Goblin

### Setup
**Guerreiro**:
- HP 30, AC 16, STR +3, DEX +1, Prof +2
- Espada Longa (1d8)

**Goblin**:
- HP 8, AC 15, STR +0, DEX +2, Prof +2
- Meia-lança (1d6)

### Rodada 1: Iniciativa
- Guerreiro: 1d20 (12) + 1 = 13
- Goblin: 1d20 (8) + 2 = 10
- **Ordem**: Guerreiro vai primeiro

### Turno Guerreiro
- **Ataque**: 1d20 (16) + 3 + 2 = 21 vs. AC 15 → **ACERTO**
- **Dano**: 1d8 (6) + 3 = **9 de dano**
- Goblin HP: 8 - 9 = -1 (inconsciente, morrendo)

### Resultado
- Goblin faz teste de morte (3 falhas = morte)
- Se sobrevive: estabilizado em 0 HP

## Referência do Livro
Capítulo 9: Combate | Iniciativa, Ações, Ataques, Dano
