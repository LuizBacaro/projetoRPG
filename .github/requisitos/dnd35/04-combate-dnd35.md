# FEATURE: Sistema de Combate D&D 3.5

## Descrição Breve
Implementar combate com Iniciativa (1d20 + DEX mod), BAB (Bônus de Ataque Base), Ataques (1d20 + BAB + STR/DEX vs. AC), e Dano com críticos.

## Regra Principal
Combate em rodadas de 6 segundos. Ordem por Iniciativa (1d20 + DEX mod). Cada turno: ação padrão + ação movimento + ação livre. Ataque = 1d20 + BAB + STR/DEX mod vs. AC. Crítico = 20 natural (confirma com novo ataque, dano ×2).

## Dados/Campos Necessários

### Combatente
- combatanteId: string
- nome: string
- hp: number (atual)
- maxHp: number (máximo)
- ac: number (classe de armadura, base 10)
- bab: number (bônus de ataque base)
- dexMod: number
- strMod: number (para corpo-a-corpo)
- conMod: number (PV)
- armas: Arma[]
- condicoes: string[] (atordoado, cego, etc.)

### Rodada
- rodadaAtual: number
- ordemIniciativa: Combatente[] (ordenado)
- turnoAtual: Combatente

## 1. INICIATIVA

**Fórmula**: 1d20 + DEX mod

Maior resultado vai primeiro. Em empate: DEX mod mais alto. Se ainda empatado: role novamente.

### Exemplo
- Guerreiro: 1d20 (14) + 2 (DEX mod) = 16
- Mago: 1d20 (12) + 3 (DEX mod) = 15
- Resultado: Guerreiro vai primeiro

## 2. BÔNUS DE ATAQUE BASE (BAB)

Progressão por classe:

| Nível | BAB Rápido (d10/d12) | BAB Médio (d8) | BAB Lento (d6) |
|-------|-----|-----|-----|
| 1 | +1 | +0 | +0 |
| 2 | +2 | +1 | +1 |
| 3 | +3 | +2 | +1 |
| 4 | +4 | +3 | +2 |
| 5 | +5 | +3 | +2 |
| 6 | +6 | +4 | +3 |
| 7 | +7 | +5 | +3 |
| 8 | +8 | +6 | +4 |
| 9 | +9 | +6 | +4 |
| 10 | +10 | +7 | +5 |

### Classes por Progressão
- **Rápido**: Bárbaro, Guerreiro, Paladino, Ranger
- **Médio**: Bardo, Clérigo, Druida, Ladino, Monge
- **Lento**: Feiticeiro, Mago

## 3. ATAQUES

### Ataque Corpo-a-Corpo
**Fórmula**: 1d20 + BAB + STR mod + modificadores vs. AC alvo

1. Role 1d20
2. Adicione BAB + STR mod
3. Adicione/subtraia modificadores
4. Compare com AC alvo

**Se resultado >= AC alvo**: ACERTO → dano

### Ataque à Distância
**Fórmula**: 1d20 + BAB + DEX mod + modificadores vs. AC alvo

Mesmo que corpo-a-corpo, mas usa DEX mod.

### Modificadores Simples

| Situação | Modificador |
|----------|------------|
| Alvo desprevenido | +4 (flanqueado) |
| Alvo acuado | +2 |
| Atacante em elevação | +1 |
| Penalidade pelo alcance | -2, -4, -6... |
| Defesa (esquiva) | -4 ataque, +2 AC |
| Cansado | -2 |

### Exemplo Ataque
- Guerreiro: BAB +5, STR +3
- Ataque: 1d20 (16) + 5 + 3 = 24
- AC alvo: 18
- 24 >= 18 → **ACERTO**

## 4. DANO

### Dano Corpo-a-Corpo
**Fórmula**: 1d[X] + STR mod

- X = dado de arma (1d6, 1d8, 1d10, 2d6)
- Adicione STR mod (pode ser negativo)
- Mínimo 1 ponto

### Dano à Distância
**Fórmula**: 1d[X] (sem mod, normalmente)

Exceto arco (pode ser DEX mod se especializado).

### Crítico
**Ameaça**: rolar 20 natural no d20

1. Confirme crítico: role ataque novamente
2. Se confirmar (resultado >= AC): dano ×2
3. Multiplicador por arma: maioria ×2, alguns ×3 (espada larga)

**Exemplo Crítico**:
- Normal: 1d8 (7) + 3 = 10 dano
- Crítico: 2d8 (8 + 6) + 3 = 17 dano

## 5. AÇÕES POR TURNO

### Ação Padrão (1 por turno)
- Atacar (1 ataque, múltiplos com Ataque Extra)
- Conjurar feitiço
- Usar habilidade de classe
- Usar objeto complexo

### Ação Movimento (1 por turno)
- Deslocar até velocidade base
- Sacar/guardar arma
- Montar/desmontar

### Ação Livre (múltiplas, bom senso)
- Falar
- Soltar objeto
- Olhar ao redor

## 6. CONDIÇÕES

| Condição | Efeito |
|----------|--------|
| Atordoado | -4 em ataques/AC |
| Cego | -4 em ataques, +2 contra ataques |
| Agarrado | -4 em ataques, movimento 0 |
| Incapacitado | Não age |
| Envenenado | -2 testes/ataques |

## Validações

- Iniciativa = 1d20 + DEX
- Ataque = 1d20 + BAB + STR/DEX vs. AC
- Dano = 1d[X] + mod (mínimo 1)
- Crítico = 20 natural (confirma em novo teste)
- AC nunca < 10 (sem armadura)
- HP: morte em 0

## Referência do Livro
Capítulo 8: Combate | Iniciativa, BAB, Ataques, Críticos
