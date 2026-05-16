# FEATURE: Sistema de Raças D&D 5E

## Descrição Breve
Criar 9 raças jogáveis (Anão, Elfo, Halfling, Humano, Draconato, Gnomo, Meio-Elfo, Meio-Orc, Tiefling) com bônus de habilidades, velocidade e capacidades especiais.

## Regra Principal
Cada raça aplica bônus/penalidades a habilidades, define velocidade base (9m para maioria), e fornece características especiais (visão no escuro, resistências, etc.).

## Dados/Campos Necessários
- raca: enum — "Anao" | "Elfo" | "Halfling" | "Humano" | "Draconato" | "Gnomo" | "Meio_Elfo" | "Meio_Orc" | "Tiefling"
- tamanho: enum — "Pequeno" | "Médio"
- velocidade: number (em metros)

## Modificadores Raciais de Habilidades

| Raça | STR | DEX | CON | INT | WIS | CHA |
|------|-----|-----|-----|-----|-----|-----|
| Anão | — | — | +2 | — | — | — |
| Elfo | — | +2 | — | — | — | — |
| Halfling | — | +2 | — | — | — | — |
| Humano | +1 | +1 | +1 | +1 | +1 | +1 |
| Draconato | +2 | — | — | — | — | +1 |
| Gnomo | — | — | — | +2 | — | — |
| Meio-Elfo | — | — | — | — | — | +2 |
| Meio-Orc | +2 | — | +1 | -2 | — | — |
| Tiefling | — | — | — | — | — | +2 |

## Características Especiais

### Anão
- Visão no escuro 18m
- Resistência: +2 em salvados contra veneno
- Bônus +2 com machados

### Elfo
- Visão noturna 18m (P&B)
- Imunidade a sono mágico
- Vantagem em testes contra encantamento

### Halfling
- Sorte: reroll 1d20 uma vez/dia
- Agilidade: ignorar oportunidade ao sair de espaço
- Tamanho Pequeno (bônus em furtividade)

### Humano
- Feat extra no nível 1
- +1 proficiência em perícia à escolha

### Draconato
- Ancestralidade dracônica (8 tipos)
- Resistência 5 a dano do tipo ancestral
- Sopro inalado (dano 2d6)

### Gnomo
- Vantagem em INT, WIS, CHA salvados vs. magia
- Vantagem em testes de mágica

### Meio-Elfo
- Dois aumentos de habilidade extras
- Proficiência em perícia à escolha

### Meio-Orc
- Agressividade: ação bônus quando HP <= 1/2
- Vantagem em testes de Intimidação

### Tiefling
- Herança infernal (4 variantes)
- Resistência 5 a fogo
- Visão no escuro 18m

## Aplicação de Modificadores
Somar bônus raciais ao valor base ANTES de calcular modificador.

**Exemplo**: Elfo com DEX 15
- Base: 15 + DEX racial +2 = 17
- Modificador: +3

## Validações
- Raça deve estar na lista de 9
- Velocidade: 6m (Halfling), 9m (maioria), 10.5m (Draconato)
- Tamanho: automaticamente correto por raça
- Modificadores aplicados PRÉ-cálculo de mod

## Referência do Livro
Capítulo 2: Raças | Características e bônus raciais
