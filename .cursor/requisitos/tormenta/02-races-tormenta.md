# FEATURE: Sistema de Raças Tormenta RPG

## Descrição Breve
Criar 8 raças jogáveis (Anões, Elfos, Goblins, Halflings, Humanos, Lefou, Minotauros, Qareen) com modificadores de habilidades, tamanho, velocidade e habilidades raciais.

## Regra Principal
Cada raça aplica bônus/penalidades a habilidades, define tamanho e velocidade base, e fornece habilidades especiais únicas.

## Dados/Campos Necessários
- race: enum — "Anao" | "Elfo" | "Goblin" | "Halfling" | "Humano" | "Lefou" | "Minotauro" | "Qareen"
- raceName: string
- raceDescription: string

## Modificadores Raciais de Habilidades

| Raça | STR | DEX | CON | INT | WIS | CHA | TAM | VEL |
|------|-----|-----|-----|-----|-----|-----|-----|-----|
| Anão | — | -2 | +2 | — | — | -2 | P | 6m |
| Elfo | — | +2 | — | +2 | — | — | P | 9m |
| Goblin | — | +2 | — | — | -2 | — | P | 6m |
| Halfling | — | +2 | — | — | — | — | P | 6m |
| Humano | — | — | — | — | — | — | M | 9m |
| Lefou | -2 | — | — | — | +2 | — | P | 6m |
| Minotauro | +2 | — | — | -2 | — | — | M | 9m |
| Qareen | — | — | — | — | — | +2 | M | 9m |

*TAM: P=Pequeno, M=Médio | VEL: Velocidade de movimento*

## Características Especiais por Raça

### Anão
- Visão no escuro 18m
- Resistência contra magia: +2
- Bônus +1 com armas anãs (machadinha, machado grande)
- Ausência de ferro: falha automática em testes contra magia de ferro mágico

### Elfo
- Visão noturna 60m (preto e branco)
- Imunidade a sono mágico e encantamento
- Bônus +2 em Percepção (ouvida e visão)
- Arco longo adicional na tabela de favoritas

### Goblin
- Visão no escuro 18m
- Bônus +2 em Enganação e Furtividade
- Tamanho pequeno: passe em espaços de 30cm
- Fraqueza a fogo: -2 em testes de resistência contra

### Halfling
- Sorte (+1 em testes de ataque e resistência)
- Tamanho pequeno: passe em espaços de 30cm
- Bônus +2 em Furtividade
- Ligeireza: +3m em movimento

### Humano
- Sem penalidades ou bônus especiais
- Um talento extra no nível 1
- Progressão versátil: melhor para multiclasse

### Lefou
- Visão normal (apesar do tamanho pequeno)
- Tamanho pequeno: passe em espaços de 30cm
- Regeneração: recupera 1 PV por 10 minutos em repouso
- Bônus +2 em Sobrevivência

### Minotauro
- Chifres: ataque natural 1d6 (STR mod)
- Tamanho médio: mas fraqueza a espaços fechados
- Bônus +2 em Intimidação
- Bônus +3 ao derrubar inimigos (special feat)

### Qareen
- Resistência ao fogo: reduz dano em 5 pontos
- Ênfase em magia: +1 espaço de feitiço arcano
- Bônus +2 em Identificar Magia
- Herança divina: acesso a magias de domínio

## Aplicação dos Modificadores
Somar bônus raciais ao valor base ANTES de calcular modificador.

**Exemplo**: Elfo com Inteligência 15
- Base: 15
- Bônus racial: +2
- Final: 17
- Modificador: +3

## Validações
- Raça deve estar em enum de 8 raças
- Modificadores aplicados automaticamente
- Valores finais não podem exceder 25
- Tamanho reflete em resistência a combate (Pequeno = bônus defesa vs. grandes)

## Referência do Livro
Capítulo 2: Raças | Características raciais específicas
