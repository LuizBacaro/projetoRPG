# FEATURE: Sistema de Habilidades D&D 3.5

## Descrição Breve
Implementar as 6 habilidades core (Força, Destreza, Constituição, Inteligência, Sabedoria, Carisma) com modificadores automáticos, progressão por nível e ajustes raciais.

## Regra Principal
Valores 3-18 (base) + ajustes raciais. Modificador = (valor - 10) / 2, arredondado para baixo. Bônus atributo aumenta a cada nível (nível 4, 8, 12, 16, 20). Teste = 1d20 + modificador.

## Dados/Campos Necessários
- strength: number (1-25) — Força
- dexterity: number (1-25) — Destreza
- constitution: number (1-25) — Constituição
- intelligence: number (1-25) — Inteligência
- wisdom: number (1-25) — Sabedoria
- charisma: number (1-25) — Carisma
- nivel: number (1-20)

## Campos Calculados
- strengthMod: number
- dexterityMod: number
- constitutionMod: number
- intelligenceMod: number
- wisdomMod: number
- charismaMod: number

## Métodos de Geração

### 4d6 (padrão)
- Role 4d6, descarte menor, repita 6 vezes (valores 3-18)
- Ordene conforme preferência

### Padrão
- STR 15, DEX 14, CON 13, INT 12, WIS 10, CHA 8

## Ajustes Raciais
Aplicar PRÉ-cálculo de modificador.

**Exemplo**: Anão com STR 15
- STR 15 + 0 (racial) = 15 → Mod +2

## Validações
- Valores habilidades: 1 <= x <= 25
- Modificador = (valor - 10) / 2
- Ganho atributo: níveis 4, 8, 12, 16, 20 (+1 em um atributo)

## Referência do Livro
Capítulo 1: Habilidades | Valores, Modificadores
