# FEATURE: Sistema de Magia D&D 3.5

## Descrição Breve
Implementar sistema de magia com Espaços de Feitiço (spell slots), DC (10 + nível + mod), Magias por Nível (0-9), e progressão por classe.

## Regra Principal
Conjurador gasta espaço de feitiço para lançar magia. Espaços recuperam ao repouso (8 horas). DC = 10 + nível magia + modificador habilidade. Teste salvação = 1d20 + mod vs. DC.

## Dados/Campos Necessários

### Conjurador
- conjuradorId: string
- nome: string
- classe: enum — "Bardo" | "Clérigo" | "Druida" | "Feiticeiro" | "Mago" | "Paladino" | "Ranger"
- nivel: number (1-20)
- habilidadePrimaria: enum — "INT" (Mago) | "WIS" (Clérigo, Druida, Ranger) | "CHA" (Bardo, Feiticeiro, Paladino)
- modHabilidade: number
- espacosPorNivel: number[] (array 10 posições: nível 0-9)
- espacosUsadosPorNivel: number[]
- magiasConhecidas: Magia[]
- magiasPreparadas: Magia[] (Mago, Clérigo, Druida apenas)

### Magia
- magiaid: string
- nome: string
- nivel: number (0-9)
- escola: string (Evocação, Abjuração, Transmutação, Ilusão, Adivinhação, Encantamento, Necromancia, Convocação)
- tempoExecucao: string ("ação padrão", "ação livre", "reação", "rodada")
- alcance: string ("pessoal", "toque", "6m", "30m", "ilimitado")
- alvo: string
- duracao: string ("instantâneo", "concentração 1 minuto", "1 hora", "permanente")
- testeResistencia: string ("nenhum", "reflexo", "fortitude", "vontade")
- componentes: string[] (V, G, M)

## 1. ESPAÇOS DE FEITIÇO

### Bardo (até 6º nível de magia)
| Nível | 1º | 2º | 3º | 4º | 5º | 6º |
|-------|-----|-----|-----|-----|-----|-----|
| 1 | 0 | — | — | — | — | — |
| 2 | — | — | — | — | — | — |
| 3 | 1 | — | — | — | — | — |
| 4 | 1 | — | — | — | — | — |
| 5 | 2 | 0 | — | — | — | — |
| 6 | 2 | 1 | — | — | — | — |
| 20 | 4 | 4 | 4 | 4 | 4 | 4 |

### Clérigo/Druida (até 9º nível)
| Nível | 1º | 2º | 3º | 4º | 5º | 6º | 7º | 8º | 9º |
|-------|-----|-----|-----|-----|-----|-----|-----|-----|-----|
| 1 | 0 | — | — | — | — | — | — | — | — |
| 5 | 2 | 1 | — | — | — | — | — | — | — |
| 10 | 4 | 3 | 2 | 1 | — | — | — | — | — |
| 15 | 4 | 4 | 4 | 3 | 2 | 1 | — | — | — |
| 20 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 |

### Feiticeiro (até 9º nível)
Mesma tabela que Mago, espaços menores em níveis baixos.

### Mago (até 9º nível)
| Nível | 1º | 2º | 3º | 4º | 5º | 6º | 7º | 8º | 9º |
|-------|-----|-----|-----|-----|-----|-----|-----|-----|-----|
| 1 | 1 | — | — | — | — | — | — | — | — |
| 5 | 4 | 2 | 1 | — | — | — | — | — | — |
| 10 | 4 | 3 | 3 | 2 | 1 | — | — | — | — |
| 15 | 4 | 4 | 4 | 3 | 2 | 1 | — | — | — |
| 20 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 |

### Paladino/Ranger (até 4º nível a partir nível 4)
| Nível | 1º | 2º | 3º | 4º |
|-------|-----|-----|-----|-----|
| 4 | — | — | — | — |
| 5 | 1 | — | — | — |
| 10 | 2 | 1 | — | — |
| 15 | 2 | 2 | 1 | — |
| 20 | 2 | 2 | 2 | 1 |

## 2. DESAFIO DE MAGIA (DC)

**Fórmula DC**: 10 + nível magia + modificador habilidade primária

| Classe | Habilidade |
|--------|-----------|
| Bardo | CHA |
| Clérigo | WIS |
| Druida | WIS |
| Feiticeiro | CHA |
| Mago | INT |
| Paladino | CHA |
| Ranger | WIS |

### Exemplo DC
- Mago nível 5 (INT +3) lança magia nível 2
- DC = 10 + 2 + 3 = **15**

## 3. TESTE DE SALVAÇÃO

Alvo testa salvação:

**Teste**: 1d20 + modificador (Reflexo/Fortitude/Vontade) vs. DC magia

- **Sucesso**: reduz efeito (metade dano) ou sem efeito
- **Falha**: efeito completo

## 4. MAGIAS POR NÍVEL

### Nível 0 (Truques)
- **Sem limite**: podem ser lançados infinitas vezes
- **Exemplos**: Raio Mágico, Luz, Prestigidigitação, Detectar Magia
- **Dano**: 1d3-1d4 (aumenta com nível)

### Nível 1
- **Espaços**: 1-4 conforme nível
- **Exemplos**: Míssil Mágico, Proteção, Alarme, Identificação
- **Efeito**: dano 1d4-1d6 ou buff/debuff

### Nível 2
- **Espaços**: 1-3
- **Exemplos**: Invisibilidade, Bola de Fogo, Escuridão
- **Efeito**: dano 2d6-3d6

### Nível 3
- **Espaços**: 1-3
- **Exemplos**: Bola de Fogo, Relâmpago, Voo
- **Efeito**: dano 4d6-5d6

### Nível 4+
- **Espaços**: 1-2
- **Exemplos**: Teleporte, Muro de Fogo, Desejo Limitado
- **Efeito**: efeitos únicos muito poderosos

## 5. RECUPERAÇÃO DE ESPAÇOS

### Repouso (8 horas)
- Recupera TODOS os espaços de feitiço
- Mago/Clérigo/Druida: repouso + oração/estudo
- Bardo/Feiticeiro: repouso automático
- Paladino/Ranger: repouso automático (não prepara)

## 6. COMPONENTES DE MAGIA

| Componente | Requisito |
|-----------|-----------|
| Verbal (V) | Falar (silenciado = falha) |
| Somático (G) | Gesticular (preso = falha) |
| Material (M) | Item específico (foco substitui maioria) |

## Validações

- Espaço feitiço: nunca negativo
- Magia conhecida ou preparada obrigatória
- Teste salvação: 1d20 + mod vs. DC
- DC = 10 + nível + mod
- Duração concentração: máximo 10 minutos

## Cálculos

### DC de Magia
dc = 10 + nivelMagia + modHabilidadePrimaria

### Teste de SalvaçãotesteAlvo = 1d20 + modSalvacao
sucesso = testeAlvo >= dc


## Exemplo: Lançar Bola de Fogo

### Setup: Mago nível 5, INT +3
- Magia: Bola de Fogo (nível 3)
- Espaços nível 3: 1 disponível
- DC: 10 + 3 + 3 = 16

### Conjuração
- Tempo: ação padrão
- Componentes: V, G
- Alcance: 30m + raio 6m

### Resolução
1. Gasta 1 espaço nível 3
2. Alvo testa salvação Reflexo
3. Dano: 5d6 (nível 3)
4. Resultado: 20 dano
   - Falha: 20 dano
   - Sucesso: 10 dano (metade)

## Referência do Livro
Capítulo 10: Mágicas | Espaços, DC, Conjuração
Capítulo 11: Magias | Descrições completas


## Exemplo: Lançar Bola de Fogo

### Setup: Mago nível 5, INT +3
- Magia: Bola de Fogo (nível 3)
- Espaços nível 3: 1 disponível
- DC: 10 + 3 + 3 = 16

### Conjuração
- Tempo: ação padrão
- Componentes: V, G
- Alcance: 30m + raio 6m

### Resolução
1. Gasta 1 espaço nível 3
2. Alvo testa salvação Reflexo
3. Dano: 5d6 (nível 3)
4. Resultado: 20 dano
   - Falha: 20 dano
   - Sucesso: 10 dano (metade)

## Referência do Livro
Capítulo 10: Mágicas | Espaços, DC, Conjuração
Capítulo 11: Magias | Descrições completas

