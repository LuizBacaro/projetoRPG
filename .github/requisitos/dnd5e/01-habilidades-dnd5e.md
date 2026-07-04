# FEATURE: Sistema de Habilidades D&D 5E

## Descrição Breve
Implementar as 6 habilidades core do D&D (Força, Destreza, Constituição, Inteligência, Sabedoria, Carisma) com modificadores automáticos e progressão por nível.

## Regra Principal
Cada habilidade tem valor 3-20 (ou até 25 com itens mágicos). Modificador = (valor - 10) / 2, arredondado para baixo. Bônus proficiência aumenta em níveis específicos (nível 1, 5, 9, 13, 17).

## Dados/Campos Necessários
- strength: number (1-25) — Força
- dexterity: number (1-25) — Destreza
- constitution: number (1-25) — Constituição
- intelligence: number (1-25) — Inteligência
- wisdom: number (1-25) — Sabedoria
- charisma: number (1-25) — Carisma
- nivel: number (1-20)

## Campos Calculados (Automáticos)
- strengthMod: number
- dexterityMod: number
- constitutionMod: number
- intelligenceMod: number
- wisdomMod: number
- charismaMod: number
- bonusProficiencia: number (calculado por nível)

## Distribuição Padrão
- Método 4d6 (descarta menor): soma 4d6 seis vezes, ordena por preferência
- Método Padrão: STR 15, DEX 14, CON 13, INT 12, WIS 10, CHA 8
- Método Compra Pontos: 27 pontos para distribuir (custo aumenta acima de 15)

## Bônus Proficiência por Nível

| Nível | Bônus |
|-------|-------|
| 1-4 | +2 |
| 5-8 | +3 |
| 9-12 | +4 |
| 13-16 | +5 |
| 17-20 | +6 |

Perícias e proficiências (sem pontos por nível, 18 perícias PHB, Skilled, override): ver [10-pericias-dnd5e.md](10-pericias-dnd5e.md).

## Validações
- Valores habilidades: 1 <= x <= 25
- Modificador = (valor - 10) / 2, arredondado para baixo
- Bônus proficiência baseado em nível

## Cálculos
- **Modificador**: (valor - 10) / 2
- **Bônus Proficiência**: tabela por nível
- **Modificador Salvado (Save)**: mod + proficiência (se proficiente)

## Exemplo
- STR 16 → Mod +3
- DEX 10 → Mod 0
- CON 14 → Mod +2
- Nível 5: Bônus Proficiência +3

## Referência do Livro
Capítulo 1: Criação de Personagens | Habilidades
