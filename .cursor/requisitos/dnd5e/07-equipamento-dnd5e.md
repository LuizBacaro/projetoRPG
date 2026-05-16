# FEATURE: Sistema de Equipamento D&D 5E

## Descrição Breve
Implementar tabelas de equipamento com Armas (corpo-a-corpo, à distância), Armaduras, Escudos e Itens variados com custo, peso e modificadores de combate.

## Regra Principal
Equipamento tem custo em ouro (gp), peso em libras (lb), e afeta AC/dano. Personagem começa com ouro baseado em classe. Peso máximo = STR × 15 lb. Encargo reduz velocidade.

## Dados/Campos Necessários

### Arma
- armaId: string
- nome: string
- tipo: enum — "corpo_a_corpo" | "distancia"
- dano: string (ex: "1d6" ou "1d8+2")
- tipoDAno: enum — "corte" | "perfuracao" | "impacto"
- alcance: string ("toque", "5m", "20/60m")
- peso: number (em lb)
- custo: number (em gp)
- propriedades: string[] (ex: "versatil", "alerta", "leve", "pesada")
- requisitos: string[] (opcional)

### Armadura
- armaduraId: string
- nome: string
- tipoArmadura: enum — "roupa" | "leve" | "media" | "pesada"
- ca: number (classe de armadura)
- peso: number (em lb)
- custo: number (em gp)
- requisitosForça: number (STR mínima)
- penalizacaoDEX: number | "nenhuma" | "limitada"
- desvantaemFurtividade: boolean

### Escudo
- escudoId: string
- nome: string
- bonusAC: number (+1 a +2)
- peso: number
- custo: number
- danoReflexo: string (se usado como arma)

### Item Variado
- itemId: string
- nome: string
- categoria: enum — "acampamento" | "ferramentas" | "medicinal" | "roupa" | "especial"
- peso: number
- custo: number
- quantidade: number
- descricao: string

## ARMAS CORPO-A-CORPO

### Armas Simples

| Arma | Dano | Peso | Custo | Propriedades |
|------|------|------|-------|-------------|
| Cacete | 1d4 | 1 lb | 1 gp | Leve |
| Adaga | 1d4 | 1 lb | 2 gp | Leve, finesse, arremessável |
| Escada Leve | 1d4 | 2 lb | 5 gp | Leve, finesse |
| Clava | 1d6 | 2 lb | 1 gp | — |
| Raiva Pequeno | 1d4 | 1 lb | 2 gp | Leve, finesse |
| Foice | 1d4 | 2 lb | 1 gp | Leve |
| Lança | 1d6 | 3 lb | 1 gp | Versatil, arremessável |
| Martelo Pequeno | 1d4 | 2 lb | 2 gp | Leve, arremessável |
| Cimitarra Curta | 1d6 | 2 lb | 10 gp | Leve, finesse |
| Borrete | 1d8 | 4 lb | 2 gp | Versatil |

### Armas Marciais

| Arma | Dano | Peso | Custo | Propriedades |
|------|------|------|-------|-------------|
| Machado Batalha | 1d8 | 4 lb | 10 gp | Versatil |
| Machado Duplo | 1d12 | 7 lb | 30 gp | Peso pesado, duas mãos |
| Bec Pesado | 1d10 | 10 lb | 25 gp | Peso pesado, duas mãos |
| Espada Curta | 1d6 | 2 lb | 10 gp | Finesse, leve |
| Espada Comprida | 1d8 | 3 lb | 15 gp | Versatil |
| Espada Larga | 1d10 | 6 lb | 30 gp | Peso pesado, duas mãos |
| Falchion | 1d6 | 3 lb | 8 gp | — |
| Lança Comprida | 1d12 | 6 lb | 25 gp | Peso pesado, duas mãos, alerta |
| Martelo Guerra | 1d8 | 2 lb | 15 gp | Versatil |
| Picareta Guerra | 1d8 | 6 lb | 25 gp | — |
| Tridente | 1d6 | 4 lb | 5 gp | Versatil, arremessável |

## ARMAS À DISTÂNCIA

### Arcos e Balestras

| Arma | Dano | Alcance | Peso | Custo |
|------|------|---------|------|-------|
| Arco Curto | 1d6 | 80/320 ft | 2 lb | 25 gp |
| Arco Longo | 1d8 | 150/600 ft | 2 lb | 50 gp |
| Besta Leve | 1d8 | 80/320 ft | 5 lb | 25 gp |
| Besta Pesada | 1d10 | 100/400 ft | 18 lb | 50 gp |

### Armas Arremessáveis

| Arma | Dano | Alcance | Peso | Custo |
|------|------|---------|------|-------|
| Faca | 1d4 | 20/60 ft | 1 lb | 2 gp |
| Machado Mão | 1d6 | 20/60 ft | 2 lb | 5 gp |
| Adaga Arremesso | 1d4 | 20/60 ft | 1 lb | 2 gp |
| Dardo | 1d4 | 20/60 ft | 0.25 lb | 0.05 gp |
| Azagaia | 1d6 | 30/120 ft | 2 lb | 2 gp |

## ARMADURAS

### Armaduras Leves

| Armadura | CA | Peso | Custo | DEX | Furtividade |
|----------|-----|------|-------|-----|------------|
| Gibão de Couro | 11 + DEX | 10 lb | 5 gp | Sim | Não |
| Couro | 11 + DEX | 10 lb | 10 gp | Sim | Não |
| Couro Endurecido | 12 + DEX | 13 lb | 15 gp | Sim | Não |

### Armaduras Médias

| Armadura | CA | Peso | Custo | DEX | Furtividade |
|----------|-----|------|-------|-----|------------|
| Couro Escamado | 13 + DEX (máx +2) | 20 lb | 50 gp | Limitada | Desvantagem |
| Cota de Malha | 14 + DEX (máx +2) | 20 lb | 50 gp | Limitada | Desvantagem |
| Cota Meia | 15 + DEX (máx +2) | 25 lb | 75 gp | Limitada | Desvantagem |
| Placa Peito | 16 + DEX (máx +2) | 20 lb | 400 gp | Limitada | Desvantagem |
| Brigandine | 14 + DEX (máx +2) | 20 lb | 75 gp | Limitada | Desvantagem |

### Armaduras Pesadas

| Armadura | CA | Peso | Custo | Furtividade |
|----------|-----|------|-------|------------|
| Anéis | 17 | 40 lb | 150 gp | Desvantagem |
| Correntes | 16 | 55 lb | 75 gp | Desvantagem |
| Escamas | 18 | 45 lb | 200 gp | Desvantagem |
| Placa Meia | 17 | 40 lb | 400 gp | Desvantagem |
| Placa Completa | 18 | 65 lb | 1500 gp | Desvantagem |

## ESCUDOS

| Escudo | AC | Peso | Custo | Notas |
|--------|-----|------|-------|-------|
| Escudo | +2 | 6 lb | 10 gp | Use como ação bônus, +2 AC |

## ITENS VARIADOS

### Acampamento

| Item | Peso | Custo | Quantidade |
|------|------|-------|-----------|
| Mochila | 5 lb | 2 gp | — |
| Barraca | 20 lb | 2 gp | — |
| Saco Dormir | 3 lb | 1 gp | — |
| Colchão Rolo | 8 lb | 1 gp | — |
| Corda (50 ft) | 10 lb | 1 gp | — |
| Lanterna | 1 lb | 5 gp | — |
| Óleo Lanterna | 1 lb | 0.5 gp | 1 pint |
| Vela (1) | — | 0.01 gp | — |
| Isqueiro | — | 5 gp | — |
| Fogueira (gravetos) | — | — | — |

### Ferramentas

| Item | Peso | Custo | Perícia |
|------|------|-------|---------|
| Kit Ladrão | 1 lb | 25 gp | Destreza |
| Kit Escalada | 5 lb | 25 gp | Força |
| Kit Medicina | 3 lb | 50 gp | Sabedoria |
| Kit Disfarce | 3 lb | 25 gp | Carisma |
| Kit Alquimista | 8 lb | 50 gp | Inteligência |
| Kit Cartógrafο | 6 lb | 15 gp | Inteligência |

### Medicinal

| Item | Peso | Custo | Efeito |
|------|------|-------|--------|
| Poção Cura Menor | — | 50 gp | +1d4 + 1 HP |
| Poção Cura Média | — | 100 gp | +2d4 + 2 HP |
| Poção Cura Maior | — | 500 gp | +4d4 + 4 HP |
| Antídoto Veneno | — | 50 gp | Neutraliza veneno |
| Ungüento | — | 25 gp | Recuperação +1d4 |

### Roupa

| Item | Peso | Custo |
|------|------|-------|
| Roupa Nobre | 6 lb | 75 gp |
| Roupa Viajante | 4 lb | 2 gp |
| Roupa Disfarce | 3 lb | 25 gp |
| Capa/Capa | 1 lb | 5 gp |
| Botas | 1 lb | 5 gp |

## DINHEIRO INICIAL POR CLASSE

| Classe | Ouro |
|--------|------|
| Bárbaro | 2d4 × 10 gp |
| Bardo | 5d4 × 10 gp |
| Bruxo | 4d4 × 10 gp |
| Clérigo | 5d4 × 10 gp |
| Druida | 2d4 × 10 gp |
| Feiticeiro | 3d4 × 10 gp |
| Guerreiro | 5d4 × 10 gp |
| Ladino | 4d4 × 10 gp |
| Mago | 4d4 × 10 gp |
| Monge | 5d4 gp |
| Paladino | 5d4 × 10 gp |
| Patrulheiro | 5d4 × 10 gp |

## PESO E ENCARGO

### Limite Carregamento
peso_máximo = STR × 15 lb

### Velocidade por Encargo

| Encargo | Velocidade |
|---------|-----------|
| 0-5 × STR | Normal |
| 5-10 × STR | Normal |
| 10-15 × STR | -10 ft |
| 15+ × STR | -20 ft (movimento lento) |

## PROPRIEDADES ESPECIAIS

| Propriedade | Efeito |
|------------|--------|
| Alerta | +5 ft alcance |
| Versátil | 1d6 uma mão, 1d8 duas mãos |
| Finesse | Use STR ou DEX (escolha) |
| Leve | +1 em testes com essa arma |
| Peso Pesado | STR 13+ para usar |
| Arremessável | Alcance 5/30 ft |
| Alcance | Alcance adicional diferente |
| Munição | Requer munição para disparar |

## MUNIÇÃO

| Tipo | Peso | Custo | Quantidade |
|------|------|-------|-----------|
| Flecha | 0.05 lb | 0.05 gp | 20 |
| Virote Besta | 0.075 lb | 0.075 gp | 20 |
| Pedra (funda) | 0.075 lb | — | — |

## Validações

- Arma deve ter dano válido (1d4+)
- Alcance arma distância: >= 20 ft
- Peso: >= 0.01 lb
- Custo: >= 0.01 gp
- AC armadura: 10-18
- Peso máximo: nunca negativo
- Encargo: reduz velocidade se > 5×STR lb

## Cálculos

### AC com Armadura + Escudoac_final = ca_armadura + escudo_bonus
(se DEX limitada, máximo +2)

### Peso Total e Encargopeso_total = soma(peso itens)
encargo = peso_total / (STR × 15)
penalidade = floor(encargo / 0.5) × 10 ft

## Exemplo: Guerreiro Equipado

### Setup: Guerreiro STR 16, DEX 10

**Armadura**:
- Placa Completa: AC 18, 65 lb, sem DEX

**Escudo**:
- Escudo: +2 AC
- **AC Final**: 18 (placa) + 2 (escudo) = 20

**Armas**:
- Espada Larga: 1d10 + STR +3 dano
- Arco Longo: 1d8 dano

**Itens**:
- Mochila, corda, lanterna, barraca
- Total itens: ~30 lb

**Peso Total**: 65 (armadura) + 6 (escudo) + 30 (itens) = 101 lb
**Peso Máximo**: 16 × 15 = 240 lb
**Encargo**: 101/240 = 42% (sem penalidade)

## Referência do Livro
Capítulo 5: Equipamento | Armas, Armaduras, Itens, Custo

