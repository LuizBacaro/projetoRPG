# FEATURE: Sistema de Equipamento D&D 3.5

## Descrição Breve
Implementar tabelas de equipamento com Armas (corpo-a-corpo, à distância), Armaduras, Escudos e Itens variados com custo, peso, e modificadores de combate.

## Regra Principal
Equipamento tem custo em ouro (gp), peso em libras (lb), e afeta AC/dano. Personagem começa com ouro baseado em classe. Peso máximo = STR × 15 lb. Encargo reduz velocidade.

## Dados/Campos Necessários

### Arma
- armaId: string
- nome: string
- tipo: enum — "corpo_a_corpo" | "distancia"
- dano: string (ex: "1d6" ou "1d8+2")
- tipoDano: enum — "corte" | "perfuracao" | "impacto"
- alcance: string ("toque", "5 pés", "30/60 pés")
- peso: number (em lb)
- custo: number (em gp)
- propriedades: string[] (ex: "versátil", "duas mãos", "leve")
- crítico: string (ex: "19-20/×2", "20/×3")

### Armadura
- armaduraId: string
- nome: string
- tipoArmadura: enum — "roupa" | "leve" | "média" | "pesada"
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

| Arma | Dano | Crítico | Peso | Custo | Propriedades |
|------|------|---------|------|-------|-------------|
| Cacete | 1d4 | 20/×2 | 1 lb | 1 gp | — |
| Adaga | 1d4 | 19-20/×2 | 1 lb | 2 gp | Leve, finesse, arremessável |
| Foice | 1d4 | 20/×2 | 2 lb | 1 gp | Leve |
| Lança | 1d6 | 20/×2 | 3 lb | 1 gp | Versátil, arremessável |
| Martelo Pequeno | 1d4 | 20/×2 | 2 lb | 1 gp | Leve, arremessável |
| Clava | 1d6 | 20/×2 | 2 lb | 1 gp | — |
| Borrete | 1d8 | 20/×2 | 4 lb | 2 gp | Versátil |
| Cimitarra | 1d6 | 19-20/×2 | 2 lb | 10 gp | Leve, finesse |

### Armas Marciais

| Arma | Dano | Crítico | Peso | Custo | Propriedades |
|------|------|---------|------|-------|-------------|
| Machado de Batalha | 1d8 | 20/×3 | 4 lb | 10 gp | Versátil |
| Machado Duplo | 1d12 | 20/×3 | 7 lb | 30 gp | Duas mãos |
| Espada Curta | 1d6 | 19-20/×2 | 2 lb | 10 gp | Finesse, leve |
| Espada Longa | 1d8 | 19-20/×2 | 3 lb | 15 gp | Versátil |
| Espada Larga | 1d10 | 19-20/×2 | 6 lb | 30 gp | Duas mãos |
| Lança de Guerra | 1d12 | 20/×3 | 6 lb | 25 gp | Duas mãos |
| Martelo de Guerra | 1d8 | 20/×3 | 2 lb | 15 gp | Versátil |
| Picareta de Guerra | 1d8 | 20/×4 | 6 lb | 25 gp | — |
| Tridente | 1d8 | 20/×2 | 4 lb | 15 gp | Versátil, arremessável |

## ARMAS À DISTÂNCIA

### Arcos

| Arma | Dano | Crítico | Alcance | Peso | Custo |
|------|------|---------|---------|------|-------|
| Arco Curto | 1d6 | 20/×3 | 60 pés | 2 lb | 25 gp |
| Arco Longo | 1d8 | 20/×3 | 100 pés | 2 lb | 50 gp |
| Besta Leve | 1d8 | 19-20/×2 | 80 pés | 5 lb | 25 gp |
| Besta Pesada | 1d10 | 19-20/×2 | 120 pés | 18 lb | 50 gp |

### Armas Arremessáveis

| Arma | Dano | Crítico | Alcance | Peso | Custo |
|------|------|---------|---------|------|-------|
| Faca | 1d4 | 19-20/×2 | 10 pés | 1 lb | 2 gp |
| Machado Mão | 1d6 | 20/×3 | 10 pés | 2 lb | 5 gp |
| Dardo | 1d4 | 20/×2 | 20 pés | 0.25 lb | 0.05 gp |
| Azagaia | 1d6 | 20/×2 | 20 pés | 2 lb | 2 gp |

## ARMADURAS

### Armaduras Leves

| Armadura | CA | Peso | Custo | Penalidade DEX | Furtividade |
|----------|-----|------|-------|----------------|------------|
| Gibão | 11 | 10 lb | 5 gp | 0 | Não |
| Couro | 11 | 10 lb | 10 gp | 0 | Não |
| Couro Endurecido | 12 | 13 lb | 15 gp | 0 | Não |

### Armaduras Médias

| Armadura | CA | Peso | Custo | Penalidade DEX | Furtividade |
|----------|-----|------|-------|----------------|------------|
| Couro Escamado | 13 | 20 lb | 50 gp | -2 | Sim |
| Cota de Malha | 14 | 20 lb | 50 gp | -2 | Sim |
| Cota Meia | 15 | 25 lb | 75 gp | -2 | Sim |
| Brigandine | 14 | 20 lb | 75 gp | -2 | Sim |

### Armaduras Pesadas

| Armadura | CA | Peso | Custo | Furtividade |
|----------|-----|------|-------|------------|
| Correntes | 16 | 55 lb | 75 gp | Sim |
| Escamas | 18 | 45 lb | 200 gp | Sim |
| Placa Meia | 17 | 40 lb | 400 gp | Sim |
| Placa Completa | 18 | 65 lb | 1.500 gp | Sim |

## ESCUDOS

| Escudo | AC | Peso | Custo | Dano Reflexo |
|--------|-----|------|-------|------------|
| Escudo Leve | +1 | 3 lb | 5 gp | 1d3 |
| Escudo Pesado | +2 | 6 lb | 10 gp | 1d4 |

## ITENS VARIADOS

### Acampamento

| Item | Peso | Custo | Descrição |
|------|------|-------|-----------|
| Mochila | 2 lb | 2 gp | Carrega até 50 lb |
| Barraca | 20 lb | 10 gp | Abrigo para 1 pessoa |
| Saco Dormir | 3 lb | 1 gp | Aquecimento noturno |
| Corda (50 pés) | 5 lb | 1 gp | Resistência 200 lb |
| Lanterna | 2 lb | 0.1 gp | Ilumina 20 pés |
| Óleo Lanterna | 0.5 lb | 0.01 gp | 6 horas de luz |
| Vela (1) | — | 0.01 gp | Ilumina 5 pés |

### Ferramentas

| Item | Peso | Custo | Perícia |
|------|------|-------|---------|
| Kit Ladrão | 1 lb | 30 gp | Arrombar Fechaduras |
| Kit Escalada | 5 lb | 80 gp | Atletismo |
| Kit Medicina | 1 lb | 50 gp | Cura |
| Kit Disfarce | 3 lb | 50 gp | Disfarce |
| Kit Alquimista | 8 lb | 500 gp | Spellcraft |

### Medicinal

| Item | Peso | Custo | Efeito |
|------|------|-------|--------|
| Poção Cura Menor | — | 25 gp | +1d8+1 PV |
| Poção Cura Média | — | 100 gp | +2d8+2 PV |
| Poção Cura Maior | — | 500 gp | +4d8+4 PV |
| Antídoto Veneno | — | 50 gp | Neutraliza veneno |

## DINHEIRO INICIAL POR CLASSE

| Classe | Ouro |
|--------|------|
| Bárbaro | 3d4 × 10 gp |
| Bardo | 5d4 × 10 gp |
| Clérigo | 4d4 × 10 gp |
| Druida | 2d4 × 10 gp |
| Feiticeiro | 3d4 × 10 gp |
| Guerreiro | 6d4 × 10 gp |
| Ladino | 4d4 × 10 gp |
| Mago | 3d4 × 10 gp |
| Monge | 1d4 × 10 gp |
| Paladino | 5d4 × 10 gp |
| Ranger | 5d4 × 10 gp |

## PESO E ENCARGO

### Limite Carregamento
peso_máximo = STR × 15 lb


### Velocidade por Encargo

| Encargo | Velocidade |
|---------|-----------|
| 0-1/3 × STR | Normal (30 pés) |
| 1/3 - 2/3 × STR | Normal (30 pés) |
| 2/3 - STR | -10 pés |
| STR - 1.5 × STR | -20 pés |

## PROPRIEDADES ESPECIAIS

| Propriedade | Efeito |
|------------|--------|
| Versátil | 1d6 uma mão, 1d8 duas mãos |
| Finesse | Use STR ou DEX (escolha) |
| Duas Mãos | Requer ambas mãos |
| Leve | +1 em testes com arma |
| Arremessável | Pode lançar arma |

## Validações

- Arma deve ter dano válido (1d4+)
- Alcance arma distância: >= 20 pés
- Peso: >= 0.01 lb
- Custo: >= 0.01 gp
- AC armadura: 11-18
- Peso máximo: nunca negativo
- Encargo: reduz velocidade se > STR × 15 lb

## Referência do Livro
Capítulo 7: Equipamento | Armas, Armaduras, Itens, Custo
