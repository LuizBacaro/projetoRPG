# FEATURE: Sistema de Classes Tormenta RPG

## Descrição Breve
Implementar 13 classes jogáveis (Bárbaro, Bardo, Clérigo, Druida, Feiticeiro, Guerreiro, Ladino, Mago, Monge, Paladino, Ranger, Samurai, Swashbuckler) com progressão, dados de vida e habilidades de classe.

## Regra Principal
Cada classe define: dado de vida (d8, d10, d12), habilidade primária, BAB, perícias de classe, e habilidades especiais de nível.

## Dados/Campos Necessários
- playerClass: enum — "Barbaro" | "Bardo" | "Clerico" | "Druida" | "Feiticeiro" | "Guerreiro" | "Ladino" | "Mago" | "Monge" | "Paladino" | "Ranger" | "Samurai" | "Swashbuckler"
- className: string
- level: number (1-20)

## Dados de Vida e Habilidade Primária

| Classe | Dado Vida | Habilidade Primária | Perícias Base |
|--------|-----------|-------------------|---------------|
| Bárbaro | d12 | Força | 4 + INT mod |
| Bardo | d8 | Carisma | 8 + INT mod |
| Clérigo | d8 | Sabedoria | 2 + INT mod |
| Druida | d8 | Sabedoria | 4 + INT mod |
| Feiticeiro | d6 | Carisma | 2 + INT mod |
| Guerreiro | d10 | Força | 2 + INT mod |
| Ladino | d8 | Destreza | 8 + INT mod |
| Mago | d6 | Inteligência | 2 + INT mod |
| Monge | d8 | Sabedoria | 4 + INT mod |
| Paladino | d10 | Força | 2 + INT mod |
| Ranger | d10 | Destreza | 4 + INT mod |
| Samurai | d10 | Força | 4 + INT mod |
| Swashbuckler | d8 | Destreza | 6 + INT mod |

## Tabela de Bônus de Ataque Base (BAB) por Classe

### Progressor Rápido (d10, d12)
Guerreiro, Bárbaro, Paladino, Ranger, Samurai

| Nível | BAB |
|-------|-----|
| 1 | +1 |
| 2 | +2 |
| 3 | +3 |
| 4 | +4 |
| 5 | +5 |
| *cada +1 por 5 níveis* | |

### Progressor Médio (d8)
Bardo, Clérigo, Druida, Ladino, Monge, Swashbuckler

| Nível | BAB |
|-------|-----|
| 1 | +0 |
| 2 | +1 |
| 3 | +2 |
| 4 | +3 |
| 5 | +3 |
| *cada +1 a cada 5-6 níveis* | |

### Progressor Lento (d6)
Feiticeiro, Mago

| Nível | BAB |
|-------|-----|
| 1 | +0 |
| 2 | +1 |
| 3 | +1 |
| 4 | +2 |
| 5 | +2 |

## Pontos de Vida por Nível

- **Nível 1**: Dado de vida + CON mod (mínimo 1)
- **Nível 2+**: PV anterior + (1d[dado] + CON mod), mínimo 1

**Exemplo Bárbaro com CON +3:**
- Nível 1: 1d12 + 3 = (ex. 7) = 10 PV
- Nível 2: 10 + (1d12 + 3) = 10 + (ex. 8) = 18 PV

## Habilidades Especiais de Classe (Resumo)

### Bárbaro
- **Fúria**: Ativa em combate, +2 ataque e dano, reduz AC

### Bardo
- **Inspiração Bardica**: Bônus a aliados (d6 + nível/4)

### Clérigo
- **Canalizar Energia**: Cura ou dano baseado em CHA mod

### Druida
- **Forma Selvagem**: Transformação em animal (nível 5+)

### Feiticeiro
- **Espaços de Feitiço**: Por nível + CHA mod

### Guerreiro
- **Ataque Extra**: Nível 5, 9, 13, 17

### Ladino
- **Ataque Furtivo**: +1d6 dano quando alvo surpreso/acuado

### Mago
- **Espaços de Feitiço**: Por nível + INT mod

### Monge
- **Desarmado Aprimorado**: Dano aumenta por nível

### Paladino
- **Imposição das Mãos**: Cura (CHA mod × nível)

### Ranger
- **Inimigo Predileto**: +1 dano vs. tipo específico

### Samurai
- **Honra**: Bônus em testes de Intimidação e Cavalgar

### Swashbuckler
- **Ataque Preciso**: Ignora parte da penalidade de defesa

## Validações
- Classe deve estar na lista de 13
- Nível entre 1-20
- PV nunca negativo (mínimo 1 por nível)
- BAB deve corresponder à tabela da classe

## Cálculos
- **PV Total**: Soma de aumentos por nível
- **Bônus de Ataque Base**: Tabela por classe/nível
- **Perícias Iniciais**: Base da classe + INT mod

## Exemplo de Caso de Uso

### Guerreiro Humano, Nível 5
- Força: 16 → Mod +3
- Constituição: 15 → Mod +2
- Classe: Guerreiro (BAB Rápido)
- PV: (1d10 + 2) + (1d10 + 2) × 4 ≈ 12 + 11 + 10 + 11 + 13 = 57 PV
- BAB: +5
- Ataque com Espada Longa: +5 (BAB) + 3 (STR) = +8
- **Ataque Extra**: Pode atacar 2 vezes por rodada (nível 5)

## Referência do Livro
Capítulo 3: Classes | Tabelas de progressão e habilidades especiais
