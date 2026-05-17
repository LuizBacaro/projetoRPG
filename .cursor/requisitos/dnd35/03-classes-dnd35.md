# FEATURE: Sistema de Classes D&D 3.5

## Descrição Breve
Implementar 11 classes (Bárbaro, Bardo, Clérigo, Druida, Feiticeiro, Guerreiro, Ladino, Mago, Monge, Paladino, Ranger) com dados de vida, progressão e habilidades por nível.

## Regra Principal
Cada classe define: d. vida (d8, d10, d12), habilidade primária, BAB, perícias de classe, e habilidades a cada nível. Progresso 1-20, ganho +1 atributo em níveis 4, 8, 12, 16, 20.

## Dados/Campos Necessários
- classe: enum — 11 opções acima
- nivel: number (1-20)
- experiencia: number (total XP)
- habilidades_de_classe: string[]
- proficiencias: Proficiencia[]

## Dado de Vida e Habilidade Primária

| Classe | d. Vida | Primária |
|--------|---------|----------|
| Bárbaro | d12 | STR |
| Bardo | d8 | CHA |
| Clérigo | d8 | WIS |
| Druida | d8 | WIS |
| Feiticeiro | d6 | CHA |
| Guerreiro | d10 | STR |
| Ladino | d8 | DEX |
| Mago | d6 | INT |
| Monge | d8 | DEX |
| Paladino | d10 | STR |
| Ranger | d10 | STR/DEX |

## Progressão de PV

- **Nível 1**: d[vida] + CON mod (mínimo 1)
- **Nível 2+**: PV anterior + (1d[vida] + CON mod), mínimo 1

**Exemplo Bárbaro com CON +3:**
- Nível 1: 1d12 (rolou 8) + 3 = 11 PV
- Nível 2: 11 + (1d12 (rolou 6) + 3) = 20 PV

## Tabela de XP por Nível

| Nível | XP Total | Nível | XP Total |
|-------|----------|-------|----------|
| 1 | 0 | 11 | 550.000 |
| 2 | 1.000 | 12 | 750.000 |
| 3 | 3.000 | 13 | 1.000.000 |
| 4 | 6.000 | 14 | 1.300.000 |
| 5 | 10.000 | 15 | 1.600.000 |
| 6 | 15.000 | 16 | 2.000.000 |
| 7 | 21.000 | 17 | 2.500.000 |
| 8 | 28.000 | 18 | 3.000.000 |
| 9 | 36.000 | 19 | 3.500.000 |
| 10 | 45.000 | 20 | 4.000.000 |

## Habilidades de Classe (Exemplos)

### Bárbaro
- Nível 1: Fúria, Resistência ao Ferimento
- Nível 5: Ataque Extra

### Guerreiro
- Nível 1: Estilo de Combate
- Nível 5: Ataque Extra
- Nível 9: Ataque Extra (2)

### Mago
- Nível 1: Espaços de Feitiço
- Nível 5: Especialização (opcional)

## Validações
- Classe: 11 opções válidas
- Nível: 1-20
- XP: validar contra tabela de progressão
- PV: nunca <= 0
- Proficiências: conforme classe

## Referência do Livro
Capítulo 3: Classes | Tabelas de progressão, BAB, habilidades
