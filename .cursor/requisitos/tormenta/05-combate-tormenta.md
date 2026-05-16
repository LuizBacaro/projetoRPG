# FEATURE: Sistema de Combate Tormenta RPG

## Descrição Breve
Implementar o sistema completo de combate com Iniciativa, cálculo de Ataques, tipos de Ações (padrão, movimento, livre) e resolução de Dano.

## Regra Principal
Combate ocorre em rodadas de 6 segundos. Ordem determinada por Iniciativa (1d20 + DEX mod). Cada personagem executa uma ação por turno + movimento. Ataque = 1d20 + BAB + STR/DEX mod vs. AC do alvo. Acerto = aplica dano.

## Dados/Campos Necessários

### Combatente
- combatanteId: string
- nome: string
- hp: number (pontos de vida atuais)
- maxHp: number (pontos de vida máximos)
- ac: number (classe de armadura)
- bab: number (bônus de ataque base)
- strMod: number (modificador de força)
- dexMod: number (modificador de destreza)
- conMod: number (modificador de constituição)
- reflexos: number (bônus de testes de reflexo)
- fortitude: number (bônus de testes de fortitude)
- vontade: number (bônus de testes de vontade)
- deslocamento: number (velocidade em metros por rodada)
- armas: Weapon[] (lista de armas equipadas)
- armadura: Armor (armadura equipada)
- condicoes: string[] (estados especiais: atordoado, cego, etc.)

### Rodada de Combate
- rodadaAtual: number
- ordemIniciativa: Combatente[] (ordenado de maior para menor iniciativa)
- combatanteAtual: Combatente
- rodadaFinalizada: boolean

## 1. INICIATIVA

### Cálculo de Iniciativa
**Fórmula**: 1d20 + DEX mod

- Role 1d20 (dado de 20 faces)
- Adicione o modificador de Destreza do personagem
- Ordem de combate: maior resultado começa

**Exemplo**:
- Guerreiro: 1d20 (rolou 12) + 1 (DEX mod) = 13
- Ladino: 1d20 (rolou 8) + 3 (DEX mod) = 11
- Resultado: Guerreiro vai primeiro (13 > 11)

### Tied Iniciatives (Empates)
Se dois combatentes tiverem o mesmo resultado de iniciativa:
- O que tiver DEX mod maior vai primeiro
- Se DEX mod forem iguais, o que tiver DEX maior vai primeiro
- Se ainda forem iguais, role novamente

### Status de Surpresa
Se uma parte não sabe que está em combate:
- Personagem surpreso NÃO age na primeira rodada
- Inimigos preparados agem normalmente

## 2. RODADA DE COMBATE

### Estrutura
1. **Iniciativa**: calcular ordem (vide acima)
2. **Turnos**: cada combatente agora com HP até fim da rodada
3. **Resolução**: testes, ataques, efeitos especiais
4. **Próxima Rodada**: reinicia com mesma ordem de iniciativa

### Duração
- Uma rodada = 6 segundos de tempo de jogo
- Turno individual ≈ 6 segundos

## 3. AÇÕES DO TURNO

Cada personagem por turno pode fazer:

### Ação Padrão (1 por turno)
- **Atacar** com arma (ataque corpo-a-corpo ou à distância)
- **Conjurar Feitiço** (tempo de execução 1 ação padrão)
- **Usar Habilidade de Classe** (atacar furtivo, invocar aliado, etc.)
- **Usar Objeto** complexo (abrir porta trancada, operar máquina)
- **Beber Poção**
- **Lançar Granada/Arremesso**

### Ação de Movimento (1 por turno)
- **Deslocar-se** até seu deslocamento em metros (ex: 9m)
- **Sacar Arma**
- **Montar/Desmontar Criatura**
- **Apanhar Objeto** do chão
- **Abrir Porta** simples

### Ações Livres (múltiplas, bom senso)
- **Falar** (frases curtas)
- **Soltar Objeto**
- **Virar-se** para outro combatente
- **Defender-se** (+2 AC, penalidade -4 em ataques, requer ação padrão)

### Ação Preparada (antes de combate)
- Preparar ação para evento específico
- Não executa até o evento acontecer
- Pode ser usada fora do turno normal

### Ação Reação (resposta rápida)
- Ataque de Oportunidade (quando inimigo se move para fora do alcance)
- Escudo de Feitiço
- Não consome ação padrão

## 4. ATAQUES

### Cálculo de Ataque Corpo-a-Corpo
**Fórmula**: 1d20 + BAB + STR mod + modificadores de arma

1. Role 1d20
2. Adicione BAB (Bônus de Ataque Base) da classe/nível
3. Adicione modificador de STR (força)
4. Adicione bônus de arma (se houver)
5. Subtraia penalidades (defesa, cegueira, etc.)
6. Compare com AC do alvo

**Se resultado >= AC do alvo**: ACERTO → aplica dano

### Cálculo de Ataque à Distância
**Fórmula**: 1d20 + BAB + DEX mod + bônus de arma + penalidades de distância

- Mesma base que corpo-a-corpo, MAS:
- Use DEX mod ao invés de STR mod
- Penalidades por distância:
  - -2 até 10m (curta distância)
  - -5 de 10m até 30m
  - -10 acima de 30m

**Exemplo Ataque à Distância**:
- Arqueiro: 1d20 (rolou 15) + 3 (BAB) + 2 (DEX) + 1 (arco) - 0 (distância curta) = 21
- AC do alvo: 16
- Resultado: 21 >= 16 → **ACERTO**

### Modificadores de Ataque

| Situação | Modificador |
|----------|------------|
| Alvo desprevenido | +4 (ataque furtivo) |
| Alvo acuado | +2 |
| Atacante em elevação | +1 |
| Atacante montado | +1 |
| Penalidade de arma pesada | -2 |
| Defesa (+2 AC) | -4 ataque |
| Cego | -4 ataque |
| Atordoado | -4 ataque |
| Ação preparada (tira tempo) | sem penalidade |

### Acerto e Falha
- **Acerto**: 1d20 + modificadores >= AC do alvo
- **Falha**: 1d20 + modificadores < AC do alvo → nenhum dano

## 5. DANO

### Cálculo de Dano Corpo-a-Corpo
**Fórmula**: 1d[X] + STR mod + bônus de arma

- X = dado de dano da arma (ex: 1d8 para espada longa, 1d6 para adaga)
- Adicione STR mod (pode ser negativo)
- Adicione bônus especial da arma (raro, +1 a +5)

**Exemplo Ataque Guerreiro com Espada Longa**:
- Arma: Espada Longa (1d8)
- STR mod: +3
- Dano: 1d8 + 3
- Rolou: 5 no dado → 5 + 3 = **8 de dano**

### Cálculo de Dano à Distância
**Fórmula**: 1d[X] + bônus de arma (SEM DEX mod, normalmente)

- X = dado de dano da arma (ex: 1d6 para arco curto, 1d8 para arco longo)
- Adicione bônus de arma APENAS (não adiciona DEX)
- EXCEÇÃO: Balestra mágica pode usar DEX

**Exemplo Ataque de Arqueiro com Arco Longo**:
- Arma: Arco Longo (1d8)
- Dano: 1d8
- Rolou: 6 → **6 de dano**

### Dano de Feitiços
Varia por feitiço (1d6, 2d6, 1d8, etc.)
- Testes de Resistência podem reduzir à metade
- Salvação bem-sucedida = dano reduzido

### Dano Crítico
**Ameaça Crítica**: (20 natural) ou (arma com range crítico melhorado)
- **Confirmação**: role novamente o ataque
- **Se confirmar**: multiplique o dano por 2 (geralmente)

**Exemplo Crítico**:
- Ataque: 1d20 + modificadores (rolou 20) → ameaça crítica
- Confirmação: 1d20 + modificadores (resultado >= AC) → crítico confirmado
- Dano: (1d8 + STR) × 2

### Dano Mínimo
Dano mínimo por ataque = 1 ponto (mesmo com modificador negativo)
- Exceção: efeitos mágicos podem fazer dano > 1

### Redução de Dano
Algumas resistências/armaduras reduzem dano:
- Redução 5/magia: tira 5 pontos de dano (exceto magia)
- Armadura oferece proteção (já inclusa no AC)
- Feitos especiais: escudo magico, defesa +2

## 6. PONTOS DE VIDA

### PV Atual vs. Máximo
- **PV Máximo**: definido por classe/nível + CON mod
- **PV Atual**: decresce com dano, aumenta com cura

### Ferimentos
- PV = 0 → Inconsciente, morrendo
- PV < 0 → Morte em 10 turnos (cada turno, -1 PV)
- PV <= -10 → Morte imediata

### Cura
- **Poção de Cura**: restaura 1d8 + 1 (cura menor) ou superior
- **Feitiço Curar Ferimentos**: 1d8 + nível do conjurador
- **Descanso Noturno**: 1 PV por hora de repouso
- **Canalizar Energia (Clérigo)**: 1d6 + nível/4

## 7. CONDIÇÕES ESPECIAIS EM COMBATE

### Estados Especiais
- **Atordoado**: -4 em ataques/defesa, perturbo durante rodada
- **Cego**: -4 em ataques, +4 AC contra ataques corpo-a-corpo
- **Envenenado**: dano contínuo ou penalidades
- **Encantado**: afeta testes de resistência
- **Agarrado**: -4 em ataques, movimento 0
- **Aterrorizado**: -2 em testes de ataque

### Movimento Provocado
Sair do alcance de um oponente em combate = **Ataque de Oportunidade**
- Inimigo rol 1d20 + BAB + STR vs. AC você
- Se acertar: 1 ataque com dano normal

### Morte
- PV <= 0 e não recupera em 10 turnos → morte permanente

## Validações
- Iniciativa: resultado = 1d20 + DEX mod
- Ataque: resultado >= AC do alvo
- Dano: mínimo 1 ponto (exceto efeitos especiais)
- PV: nunca vai abaixo de morte (-10 ou menos)
- Ações por turno: máximo 1 padrão + 1 movimento + ilimitadas livres

## Cálculos

### Ordem de Combate
1. Calcular iniciativa para cada combatente
2. Ordenar do maior para menor
3. Executar turnos nessa ordem

### Resolução de Ataque
1. Role 1d20 + modificadores
2. Compare com AC do alvo
3. Se >= AC: acertou
4. Role dano: 1d[X] + modificadores
5. Reduza PV do alvo

### Estrutura de Loop (Pseudocódigo)

## Exemplo Completo de Rodada

### Setup: Guerreiro vs. Goblin

**Guerreiro (Aliado)**
- DEX mod: +1
- BAB: +3
- STR mod: +3
- AC: 16 (armadura + escudo)
- HP: 30/30
- Arma: Espada Longa (1d8)

**Goblin (Inimigo)**
- DEX mod: +2
- BAB: +1
- STR mod: 0
- AC: 13 (armadura leve)
- HP: 8/8
- Arma: Arco Curto (1d6)

### Rodada 1: Iniciativa
- Guerreiro: 1d20 + 1 = 15
- Goblin: 1d20 + 2 = 14
- **Ordem**: Guerreiro vai primeiro

### Turno do Guerreiro
- **Ação Padrão**: Atacar com Espada Longa
  - 1d20 (rolou 12) + 3 (BAB) + 3 (STR) = 18
  - AC do Goblin: 13
  - 18 >= 13 → **ACERTO**
  - Dano: 1d8 (rolou 6) + 3 (STR) = **9 de dano**
  - Goblin HP: 8 - 9 = -1 (morto)
- **Ação de Movimento**: Aproxima-se 6m
- **Ação Livre**: Fala com o aliado

### Goblin está morto
- Combate termina

## Referência do Livro
Capítulo 9: Combate | Iniciativa, Ações, Ataques, Dano, PV
Páginas 100-130 (aproximadamente)
