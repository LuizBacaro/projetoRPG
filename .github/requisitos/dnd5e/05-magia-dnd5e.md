# FEATURE: Sistema de Magia D&D 5E

## Descrição Breve
Implementar sistema de magia com Espaços de Feitiço (spell slots), Conjuração (DC = 8 + proficiência + mod), Magias por Nível (0-9), e progressão por classe.

## Regra Principal
Conjurador gasta espaço de feitiço para lançar magia. Espaços recuperam ao repouso longo. Teste de salvação do alvo = 1d20 + mod vs. DC (8 + proficiência + mod conjurador). Magia acerta se resultado >= DC.

## Dados/Campos Necessários

### Conjurador
- conjuradorId: string
- nome: string
- classe: enum — "Bardo" | "Clérigo" | "Druida" | "Feiticeiro" | "Mago" | "Bruxo" | "Monge" | "Paladino" | "Patrulheiro"
- nivel: number (1-20)
- habilidadePrimaria: enum — "INT" (Mago) | "WIS" (Clérigo, Druida, Patrulheiro) | "CHA" (Bardo, Feiticeiro, Paladino, Bruxo) | "DEX" (Monge)
- modHabilidade: number
- bonusProficiencia: number
- espacosPorNivel: number[] (array 10 posições: nível 0-9)
- espacosUsadosPorNivel: number[]
- magiasConhecidas: Magia[]
- magiasPreparadas: Magia[] (apenas Mago, Clérigo, Druida, Patrulheiro)

### Magia (Spell)
- magiaid: string
- nome: string
- nivel: number (0-9)
- escola: string (Evocação, Abjuração, Transmutação, Ilusão, Adivinhação, Encantamento, Necromancia, Convocação)
- tempoExecucao: enum — "acao" | "acao_bonus" | "reacao" | "minuto" | "10_minutos"
- alcance: string ("pessoal", "toque", "9m", "30m", "90m", "150m", "vista", "ilimitado")
- alvo: string (descrição do alvo/área)
- duracao: string ("instantâneo", "concentração 1 minuto", "1 hora", "permanente")
- testeResistencia: enum — "nenhum" | "reflexos" | "fortitude" | "vontade"
- descricao: string
- componentes: enum[] — "verbal" | "somatico" | "material"
- componenteMaterial: string (se requer material específico)

## 1. ESPAÇOS DE FEITIÇO POR CLASSE E NÍVEL

### Tabela de Espaços (Mago, Clérigo, Druida)

| Nível | 1º | 2º | 3º | 4º | 5º | 6º | 7º | 8º | 9º |
|-------|-----|-----|-----|-----|-----|-----|-----|-----|-----|
| 1 | 2 | — | — | — | — | — | — | — | — |
| 2 | 3 | — | — | — | — | — | — | — | — |
| 3 | 4 | 2 | — | — | — | — | — | — | — |
| 4 | 4 | 3 | — | — | — | — | — | — | — |
| 5 | 4 | 3 | 2 | — | — | — | — | — | — |
| 6 | 4 | 3 | 3 | — | — | — | — | — | — |
| 7 | 4 | 4 | 3 | 2 | — | — | — | — | — |
| 8 | 4 | 4 | 3 | 3 | — | — | — | — | — |
| 9 | 4 | 4 | 4 | 3 | 2 | — | — | — | — |
| 10 | 4 | 4 | 4 | 3 | 3 | — | — | — | — |
| 11 | 4 | 4 | 4 | 4 | 3 | 2 | — | — | — |
| 12 | 4 | 4 | 4 | 4 | 3 | 3 | — | — | — |
| 13 | 4 | 4 | 4 | 4 | 4 | 3 | 2 | — | — |
| 14 | 4 | 4 | 4 | 4 | 4 | 3 | 3 | — | — |
| 15 | 4 | 4 | 4 | 4 | 4 | 4 | 3 | 2 | — |
| 16 | 4 | 4 | 4 | 4 | 4 | 4 | 3 | 3 | — |
| 17 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 3 | 2 |
| 18 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 3 | 3 |
| 19 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 3 |
| 20 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 |

### Bardo (Tabela Reduzida até 6º nível)

| Nível | 1º | 2º | 3º | 4º | 5º | 6º |
|-------|-----|-----|-----|-----|-----|-----|
| 1 | 2 | — | — | — | — | — |
| 2 | 3 | — | — | — | — | — |
| 3 | 4 | 2 | — | — | — | — |
| 4 | 4 | 3 | — | — | — | — |
| 5 | 4 | 3 | 2 | — | — | — |
| 6 | 4 | 3 | 3 | — | — | — |
| 9 | 4 | 4 | 4 | 3 | 2 | — |
| 20 | 4 | 4 | 4 | 4 | 4 | 4 |

### Feiticeiro (Espaços = Magia de Feiticeiro)

| Nível | 1º | 2º | 3º | 4º | 5º | 6º | 7º | 8º | 9º |
|-------|-----|-----|-----|-----|-----|-----|-----|-----|-----|
| 1 | 2 | — | — | — | — | — | — | — | — |
| 2 | 3 | — | — | — | — | — | — | — | — |
| 3 | 4 | 2 | — | — | — | — | — | — | — |
| 20 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 |

### Bruxo (Pacto de Magia do Bruxo - recupera em descanso curto)

| Nível | Espaços | Nível Magia |
|-------|---------|------------|
| 1-2 | 1 | 1º |
| 3-4 | 2 | 2º |
| 5-6 | 2 | 3º |
| 7-8 | 2 | 4º |
| 9+ | 2 | 5º+ |

### Monge (Ki Points = Espaços de Feitiço para Magia Mística)

| Nível | Pontos Ki | Máximo Nível |
|-------|----------|------------|
| 1 | — | — |
| 3 | 3 | 1º |
| 5 | 5 | 2º |
| 13 | 13 | 3º |

## 2. RECUPERAÇÃO DE ESPAÇOS

### Repouso Longo (8 horas)
- Recupera TODOS os espaços de feitiço
- Mago, Clérigo, Druida, Bardo, Feiticeiro, Paladino, Patrulheiro

### Repouso Curto (1 hora)
- Bruxo recupera espaços de feitiço (via Pacto de Magia)
- Monge recupera 1d4 pontos Ki

## 3. DESAFIO DE MAGIA (DC)

**Fórmula DC**: 8 + bônus proficiência + modificador da habilidade primária

| Classe | Habilidade |
|--------|-----------|
| Mago | INT |
| Clérigo | WIS |
| Druida | WIS |
| Bardo | CHA |
| Feiticeiro | CHA |
| Paladino | CHA |
| Patrulheiro | WIS |
| Bruxo | CHA |
| Monge | WIS |

### Exemplo DC
- Mago nível 5 (prof +3) com INT +4
- DC = 8 + 3 + 4 = **15**

## 4. TESTE DE SALVAÇÃO

Se alvo pode tentar resistir:

**Teste**: 1d20 + modificador (Reflexo/Fortitude/Vontade) vs. DC magia

- **Sucesso**: reduz efeito (metade dano) ou sem efeito
- **Falha**: efeito completo

## 5. MAGIAS POR NÍVEL

### Nível 0 (Truques - Cantrips)
- **Sem limite**: podem ser lançados infinitas vezes
- **Exemplos**: Raio Mágico, Fogo Mágico, Prestidigitação, Luz
- **Dano típico**: 1d4-1d10 (aumenta com nível)

### Nível 1
- **Espaços**: 2-4 conforme nível
- **Exemplos**: Míssil Mágico, Proteção, Alarme, Identificação
- **Efeito**: dano 1d6-2d6 ou buff/debuff simples

### Nível 2
- **Espaços**: 2-3
- **Exemplos**: Invisibilidade, Levantar Terra, Bola de Fogo (prep)
- **Efeito**: dano 3d6, transformação, teleporte curto

### Nível 3
- **Espaços**: 2-3
- **Exemplos**: Bola de Fogo, Relâmpago, Voo
- **Efeito**: dano 5d6-6d6, transformações

### Nível 4
- **Espaços**: 1-2
- **Exemplos**: Teleporte, Muro de Fogo, Visão Verdadeira
- **Efeito**: dano 6d6-7d6

### Nível 5
- **Espaços**: 1-2
- **Exemplos**: Teleporte em Grupo, Comunhão, Evocação
- **Efeito**: dano 7d6-8d6, efeitos permanentes

### Nível 6+
- **Espaços**: 1
- **Exemplos**: Viagem Planar, Prisão Mágica, Desejo Limitado
- **Efeito**: efeitos únicos muito poderosos

## 6. CONJURAÇÃO E CONCENTRAÇÃO

### Concentração
Algumas magias requerem **concentração**. Enquanto concentra:
- Não pode concentrar em outra magia simultaneamente
- Se sofrer dano: teste DC 10 ou DC (metade dano recebido), o que for maior
- Se falhar: magia termina

### Componentes
- **Verbal**: precisa falar
- **Somático**: precisa gesticular (mão livre)
- **Material**: precisa componente específico (foco mágico substitui maioria)

## 7. TRUQUES (CANTRIPS) - DANO POR NÍVEL

| Nível | Dano | Exemplo |
|-------|------|---------|
| 1-4 | 1d4 | Raio Mágico |
| 5-10 | 1d6 | Raio Mágico |
| 11-16 | 1d8 | Raio Mágico |
| 17-20 | 1d10 | Raio Mágico |

## Validações

- Espaço feitiço: nunca negativo
- Magia conhecida ou preparada obrigatória
- Teste salvação: 1d20 + mod vs. DC
- Concentração: falha em teste = magia termina
- Duração concentração: máximo 10 minutos
- DC = 8 + prof + mod

## Cálculos

### DC de Magia

dc = 8 + bonusProficiencia + modHabilidadePrimaria
### Teste de SalvaçãotesteAlvo = 1d20 + modSalvacao
sucesso = testeAlvo >= dc

### Recuperação Espaços(repouso longo) → todos espaços restaurados
(repouso curto) → bruxo apenas


## Exemplo Completo: Lançar Bola de Fogo

### Setup: Mago nível 5, INT +4
- Magia: Bola de Fogo (nível 3)
- Espaços nível 3: 2 disponíveis
- DC: 8 + 3 (prof) + 4 (INT) = 15

### Conjuração
- Tempo: ação padrão
- Componentes: verbal, somático
- Alcance: 30m + 1.5m raio

### Resolução
1. Gasta 1 espaço de nível 3
2. Alvo testa salvação Reflexo
3. Dano: 5d6 (para nível 3)
4. Resultado: 18 de dano
   - Falha: 18 dano
   - Sucesso: 9 dano (metade)

## Referência do Livro
Capítulo 10: Conjuração | Espaços, DC, Magias
Capítulo 11: Magias | Descrições completas


