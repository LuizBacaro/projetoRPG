# FEATURE: Sistema de Atributos GURPS 4E

## Descrição Breve
Implementar os 4 atributos core do GURPS (Força, Destreza, Constituição, Inteligência) com pontos de personagem e cálculo de modificadores derivados.

## Regra Principal
Cada atributo começa em 10 (média). Custa 10 pontos de personagem para elevar de 9-10 para 11-12 (custo aumenta com o nível). Modificador = (atributo - 10). Atributos afetam perícias, dano, defesa e movimentação.

## Dados/Campos Necessários
- strength: number (3-20+) — Força (ST)
- dexterity: number (3-20+) — Destreza (DX)
- constitution: number (3-20+) — Constituição (HT)
- intelligence: number (3-20+) — Inteligência (IQ)
- pontosCustos: object — rastreamento de pontos gastos por atributo

## Custos de Pontos de Atributo

Custo para elevar cada atributo de nível X para X+1:

| Nível | Custo por Ponto |
|-------|-----------------|
| 3-7 | 10 pts |
| 8-9 | 20 pts |
| 10 | Base (0 pts) |
| 11-12 | 10 pts |
| 13-14 | 20 pts |
| 15+ | 20 pts por nível |

**Exemplo - Elevar ST de 10 para 14:**
- 10 → 11: 10 pontos
- 11 → 12: 10 pontos
- 12 → 13: 20 pontos
- 13 → 14: 20 pontos
- **Total: 60 pontos**

## Modificadores Derivados por Atributo

### Força (ST)
- Modificador: (ST - 10) × 10 kg — aumenta carga máxima
- Bônus de Dano: +1d6 a cada +2 em ST (acima de 10)
- Penalidade de Dano: -1d6 a cada -2 em ST (abaixo de 10)

### Destreza (DX)
- Modificador: (DX - 10) — bônus em ataques e defesa
- Iniciativa: +1 para cada ponto acima de 10
- Velocidade Base: 5 + (DX mod / 4)

### Constituição (HT)
- Modificador: (HT - 10) — bônus em resistências
- PV Base: 3 + (HT mod)
- Fadiga: 3 (modificável com Vantagens)

### Inteligência (IQ)
- Modificador: (IQ - 10) — bônus em perícias técnicas
- Perícias de Intelecto: +1 por ponto acima de 10
- Will (Vontade): IQ (pode ser modificado)

## Validações
- Atributos mínimo 3, máximo 20 (sem vantagens)
- Custo de pontos cumulativo
- Bônus derivados recalculam automaticamente

## Cálculos

### Custo Total de Atributo
custoTotal(atributo_novo, atributo_atual) =
soma de custos para cada ponto de 11 até atributo_novomarkdown
### Modificador Simplesmodificador(valor) = valor - 10markdown
### Bônus de DanobonusDano(ST) =
Math.floor((ST - 10) / 2) × 1d6


## Exemplo Completo: Guerreiro com ST 14, DX 12, HT 13, IQ 10

### Cálculo de Custos
- ST 10→14: (10 + 10 + 20 + 20) = 60 pts
- DX 10→12: (10 + 10) = 20 pts
- HT 10→13: (10 + 20) = 30 pts
- IQ 10→10: 0 pts
- **Total: 110 pontos de atributo**

### Derivações
- **Bônus de Dano (ST 14)**: +(14-10)/2 = +2d6
- **Iniciativa (DX 12)**: +1 (12 > 10)
- **PV Base (HT 13)**: 3 + (13-10) = 6 PV
- **Will (IQ 10)**: 10

## Referência do Livro
Capítulo 1: Criação de Personagens | Atributos, Custos, Modificadores
