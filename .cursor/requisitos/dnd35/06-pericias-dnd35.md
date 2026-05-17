# FEATURE: Sistema de Perícias D&D 3.5

## Descrição Breve
Implementar sistema de perícias com 36 perícias, graduações (ranks), bônus de classe, progressão por nível e modificadores automáticos.

## Regra Principal
Perícia = 1d20 + modificador habilidade + graduações + bônus de classe. Máximo graduações por nível = nível do personagem. Custo: 1 ponto de perícia = 1 graduação (4 para classe oposta). Teste = 1d20 + (graduações + mod habilidade + bônus classe).

## Dados/Campos Necessários

### Perícia
- periciaid: string
- nome: string
- habilidadeBase: enum — "STR" | "DEX" | "CON" | "INT" | "WIS" | "CHA"
- graduacoes: number (0-X)
- bonusClasse: number (+2 se treinado em classe)
- modificadorHabilidade: number (automático)
- dificuldade: string ("Fácil" | "Normal" | "Difícil")
- sinergias: string[] (outras perícias que dão bônus)

## Lista de 36 Perícias

| # | Perícia | Habilidade | Bônus Classe |
|----|---------|-----------|------------|
| 1 | Acrobacia | DEX | — |
| 2 | Adestrar Animais | CHA | Ranger, Druida |
| 3 | Apreciação de Arte | INT | Bardo |
| 4 | Arqueologia | INT | — |
| 5 | Arrombar Fechaduras | DEX | Ladino |
| 6 | Atletismo | STR | Monge, Ranger |
| 7 | Atuação | CHA | Bardo |
| 8 | Avaliação | INT | — |
| 9 | Bravura | CON | Bárbaro, Guerreiro |
| 10 | Cálculos | INT | Mago |
| 11 | Camuflagem | DEX | Ranger |
| 12 | Cavalgar | DEX | Paladino, Ranger |
| 13 | Conhecimento (Arcano) | INT | Mago, Feiticeiro |
| 14 | Conhecimento (Arquitetura e Engenharia) | INT | — |
| 15 | Conhecimento (Dungeon) | INT | — |
| 16 | Conhecimento (Geografia) | INT | — |
| 17 | Conhecimento (História) | INT | Clérigo |
| 18 | Conhecimento (Natureza) | INT | Druida, Ranger |
| 19 | Conhecimento (Nobreza) | INT | Paladino |
| 20 | Conhecimento (Planos) | INT | Clérigo |
| 21 | Conhecimento (Religião) | INT | Clérigo |
| 22 | Corda | DEX | — |
| 23 | Cura | WIS | Clérigo, Paladino |
| 24 | Decifragem | INT | Mago |
| 25 | Decifrar Escritas | INT | — |
| 26 | Diplomacia | CHA | Bardo, Paladino |
| 27 | Disfarce | CHA | Bardo |
| 28 | Evasão | DEX | Ladino, Monge |
| 29 | Foco | WIS | — |
| 30 | Furtividade | DEX | Ladino, Monge, Ranger |
| 31 | Ganhar a Vida | CHA | — |
| 32 | Identificar Magia | INT | Mago, Feiticeiro |
| 33 | Intimidação | CHA | Bárbaro |
| 34 | Intuição | WIS | — |
| 35 | Ladinagem | DEX | Ladino |
| 36 | Línguas | INT | — |
| 37 | Loucura | WIS | — |
| 38 | Natação | STR | Monge, Ranger |
| 39 | Noção de Direção | WIS | Ranger |
| 40 | Observação | WIS | — |
| 41 | Ofício (qualquer) | INT | — |
| 42 | Oratória | CHA | Bardo, Paladino |
| 43 | Paisagem | WIS | Druida |
| 44 | Paranóia | WIS | — |
| 45 | Percepção de Profundidade | WIS | — |
| 46 | Projeção Planar | INT | — |
| 47 | Realizar Ritual | WIS | Clérigo, Druida |
| 48 | Reparação de Itens | INT | — |
| 49 | Resistência | CON | Bárbaro |
| 50 | Saltar | STR | Monge |
| 51 | Seduction | CHA | Bardo |
| 52 | Sentir Intenção | WIS | — |
| 53 | Sobrevivência | WIS | Ranger, Druida |
| 54 | Spellcraft | INT | Mago, Feiticeiro |
| 55 | Tremelique | WIS | — |
| 56 | Usar Corda | DEX | — |
| 57 | Usar Magia Arcana | INT | Mago |
| 58 | Usar Objeto Mágico | CHA | Ladino |
| 59 | Ventrilóquio | CHA | Bardo |
| 60 | Vontade | WIS | Paladino |

## Custo de Graduações

### Para Classe de Perícia
- 1 ponto = 1 graduação

### Para Perícia Fora da Classe
- 4 pontos = 1 graduação

### Máximo por Nível
- Máximo graduações = nível do personagem + 3

## Teste de Perícia

**Fórmula**: 1d20 + (graduações + modificador habilidade + bônus classe + sinergias)

### Dificuldade Comum (DC)

| Dificuldade | DC |
|------------|-----|
| Muito Fácil | 5 |
| Fácil | 10 |
| Normal | 15 |
| Difícil | 20 |
| Muito Difícil | 25 |
| Quase Impossível | 30+ |

### Exemplo Teste
- Ladino com DEX 16 (mod +3), 5 graduações em Furtividade, bônus classe +2
- Teste: 1d20 (14) + 3 (DEX) + 5 (graduações) + 2 (classe) = 24
- DC 20 (difícil)
- 24 >= 20 → **SUCESSO**

## Sinergias Entre Perícias

| Perícia Relacionada | Bônus |
|-------------------|-------|
| Conhecimento (Natureza) 5+ ranks → Adestrar Animais | +2 |
| Spellcraft 5+ ranks → Identificar Magia | +2 |
| Diplomacia 5+ ranks → Intimidação | +2 |
| Atletismo 5+ ranks → Saltar | +2 |

## Validações

- Graduações: 0 <= graduações <= (nível + 3)
- Custo: 1 pt (classe) ou 4 pts (fora classe)
- Perícia deve estar na lista de 36+
- Modificador = valor habilidade mod automático
- Bônus classe aplicado apenas se treinado

## Cálculos

### Teste de Perícia
resultado = 1d20 + graduacoes + modHabilidade + bonusClasse + sinergias
sucesso = resultado >= dc


## Exemplo: Ladino com Perícias

### Setup: Ladino nível 5, DEX 16 (mod +3), INT 14 (mod +2)

**Perícias de Classe**:
- Furtividade: 5 graduações
- Acrobacia: 3 graduações
- Ladinagem: 4 graduações
- Arrombar Fechaduras: 2 graduações

**Total Pontos Perícia**: 5 + 3 + 4 + 2 = 14 pts
**Máximo Permitido**: (5 + 3) × número_perícias_classe = 24 pts

**Testes**:
- Furtividade: 1d20 + 3 (DEX) + 5 + 2 (classe) = +10 modificador
- Arrombar Fechaduras: 1d20 + 3 (DEX) + 2 + 2 (classe) = +7 modificador

## Referência do Livro
Capítulo 4: Perícias | Descrições, Graduações, DC


