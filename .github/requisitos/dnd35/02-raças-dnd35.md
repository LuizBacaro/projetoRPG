# FEATURE: Sistema de Raças D&D 3.5

## Descrição Breve
Criar 7 raças jogáveis (Humano, Anão, Elfo, Gnomo, Meio-Elfo, Meio-Orc, Halfling) com ajustes de habilidades, tamanho e habilidades especiais.

## Regra Principal
Cada raça aplica bônus/penalidades a habilidades PRÉ-cálculo de modificador, define tamanho e velocidade, e fornece características especiais.

## Dados/Campos Necessários
- raca: enum — "Humano" | "Anao" | "Elfo" | "Gnomo" | "Meio_Elfo" | "Meio_Orc" | "Halfling"
- tamanho: enum — "Pequeno" | "Médio"
- velocidade: number (em pés: 30, 20, etc.)

## Modificadores Raciais

| Raça | STR | DEX | CON | INT | WIS | CHA |
|------|-----|-----|-----|-----|-----|-----|
| Humano | — | — | — | — | — | — |
| Anão | — | — | +2 | — | — | -2 |
| Elfo | — | +2 | -2 | — | — | — |
| Gnomo | — | — | +2 | — | — | +2 |
| Meio-Elfo | — | — | — | — | — | +2 |
| Meio-Orc | +2 | — | — | -2 | — | -2 |
| Halfling | — | +2 | — | — | — | — |

## Características Especiais

### Humano
- Talento extra no nível 1
- +1 perícia por nível

### Anão
- Visão no escuro 60 pés
- Resistência 25% contra magia
- Bônus +2 com machados/armas anãs
- Imunidade a veneno

### Elfo
- Visão noturna 60 pés
- Imunidade a sono mágico
- +1 em testes de Percepção

### Gnomo
- Visão no escuro 60 pés
- Tamanho Pequeno (bônus AC/ataques, penalidade força)
- Ligeireza: velocidade +3m

### Meio-Elfo
- Visão noturna 60 pés
- **+2 Carisma** (único bônus de habilidade racial; ver tabela acima)
- **+2 perícias** de sua escolha (não confundir com D&D 5E, que usa dois **+1** em atributos distintos — ver [02-raças-dnd5e.md](../dnd5e/02-raças-dnd5e.md))

### Meio-Orc
- Visão no escuro 60 pés
- Grande demanda de alimento

### Halfling
- Tamanho Pequeno
- Bônus +2 em Furtividade
- Sorte: reroll 1d20 uma vez por dia

## Tamanho e Velocidade

| Raça | Tamanho | Velocidade |
|------|---------|-----------|
| Humano | Médio | 30 pés |
| Anão | Médio | 20 pés |
| Elfo | Médio | 30 pés |
| Gnomo | Pequeno | 20 pés |
| Meio-Elfo | Médio | 30 pés |
| Meio-Orc | Médio | 30 pés |
| Halfling | Pequeno | 20 pés |

## Validações
- Raça em lista de 7
- Tamanho automático por raça
- Modificadores aplicados PRÉ-cálculo mod
- Velocidade correta por tamanho

## Referência do Livro
Capítulo 2: Raças | Características e ajustes raciais
