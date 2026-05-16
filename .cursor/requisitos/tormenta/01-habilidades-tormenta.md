# FEATURE: Sistema de Habilidades Tormenta RPG

## Descrição Breve
Implementar as 6 habilidades core do Tormenta (Força, Destreza, Constituição, Inteligência, Sabedoria, Carisma) com modificadores automáticos e suporte a 6 métodos de geração.

## Regra Principal
Cada habilidade tem valor 3-18 (ou 1-25 com bônus raciais). Modificador = (valor - 10) / 2, arredondado para baixo. Sistema suporta 6 métodos de geração: Padrão, Clássico, Heroico, Audacioso, Elite, Compra de Pontos.

## Dados/Campos Necessários
- strength: number (1-25) — Força
- dexterity: number (1-25) — Destreza
- constitution: number (1-25) — Constituição
- intelligence: number (1-25) — Inteligência
- wisdom: number (1-25) — Sabedoria
- charisma: number (1-25) — Carisma
- generationMethod: enum — "padrao" | "classico" | "heroico" | "audacioso" | "elite" | "compra_pontos"

## Campos Calculados (Automáticos)
- strengthMod: number
- dexterityMod: number
- constitutionMod: number
- intelligenceMod: number
- wisdomMod: number
- charismaMod: number

## Métodos de Geração de Habilidades

### Padrão (Standard)
- Role 4d6, descarte o menor, repita 6 vezes (valores 3-18)

### Clássico (Classic)
- Role 3d6 seis vezes (valores 3-18)

### Heroico (Heroic)
- Role 2d6+6 seis vezes (valores 8-18)

### Audacioso (Audacious)
- Role 4d6+2, descarte o menor seis vezes (valores 5-20)

### Elite (Elite)
- Role 4d6+1, descarte o menor seis vezes (valores 4-19)

### Compra de Pontos (Point-Buy)
- Começar com 15 pontos distribuíveis
- Custo: 3→1, 4→2, 5→3, 6→4, 7→5, 8→6, 9→7, 10→8, 11→9, 12→10, 13→11, 14→12, 15→13
- Máximo 15 por habilidade

## Validações
- Cada habilidade: valor >= 1 e <= 25
- Se método "compra_pontos": total pontos <= 15
- Se método diferente: valores gerados validar 3-25

## Cálculos
- **Modificador**: (valor - 10) / 2, arredondado para baixo
- Modificadores aplicados em: ataques, testes de habilidade, perícias

## Exemplos de Casos de Uso

### Método Padrão - Guerreiro Humano
- Força: 16 → Mod +3
- Destreza: 13 → Mod +1
- Constituição: 15 → Mod +2
- Total pontos gastos: 0 (geração aleatória)

### Método Compra de Pontos - Mago
- Inteligência: 16 (11 pontos) → Mod +3
- Destreza: 14 (12 pontos) → Mod +2
- Sabedoria: 12 (10 pontos) → Mod +1
- Total pontos gastos: 15

## Referência do Livro
Capítulo 1: Habilidades | Métodos de Geração
