# FEATURE: Sistema de Equipamento GURPS

## Descrição Breve
Implementar tabelas de equipamento com Armas (corpo-a-corpo, à distância, fogo), Armaduras, Escudos e Itens variados com custo, peso, e modificadores de combate.

## Regra Principal
Equipamento tem custo em pontos/moeda, peso em kg, e afeta combate (armadura reduz dano, arma define dano/alcance). Personagem começa com pontos de equipamento = riqueza × 200. Peso máximo carregável = STR × 15 kg. Encargo reduz velocidade.

## Dados/Campos Necessários

### Arma
- armaId: string
- nome: string
- tipo: enum — "corpo_a_corpo" | "distancia" | "fogo" | "pesada"
- dano: string (ex: "1d6+2" ou "2d6")
- alcance: number (em metros, 0 para corpo-a-corpo)
- peso: number (em kg)
- custo: number (em pontos ou moeda)
- tamanho: enum — "Pequeno" | "Médio" | "Grande" | "Enorme"
- modificadores: string[] (ex: "Equilibrada", "Envenenável")
- requisitos: string[] (pré-requisitos, ex: "Força 12+")

### Armadura
- armaduraId: string
- nome: string
- tipo: enum — "Roupa" | "Leve" | "Média" | "Pesada" | "Placa"
- reducao_dano: number (1-10)
- peso: number (em kg)
- custo: number
- requisitos_forca: number (STR mínima)
- penalidade_movimento: number (redução de velocidade)
- penalidade_destreza: number (penalidade em DEX)
- material: string (ex: "Couro", "Ferro", "Aço")

### Escudo
- escudoId: string
- nome: string
- tipo: enum — "Broquel" | "Ronda" | "Peltasta" | "Torre"
- bonus_defesa: number (+1 a +4 em AC)
- peso: number
- custo: number
- dano_reflexo: number (se usado como arma)

### Item Variado
- itemId: string
- nome: string
- categoria: enum — "Acampamento" | "Comunicação" | "Médico" | "Ferramentas" | "Especial"
- peso: number
- custo: number
- descricao: string
- quantidade: number

## ARMAS CORPO-A-CORPO

### Armas Pequenas

| Arma | Dano | Peso | Custo | Modificadores |
|------|------|------|-------|---------------|
| Adaga | 1d4-1 | 0.5kg | 10pt | Pequena, Duas mãos impossível |
| Espada Curta | 1d6-1 | 1kg | 30pt | Versátil |
| Cacete | 1d6 | 1kg | 5pt | Impacto |
| Clava | 1d6 | 2kg | 10pt | Impacto, Duas mãos |

### Armas Médias

| Arma | Dano | Peso | Custo | Modificadores |
|------|------|------|-------|---------------|
| Espada Longa | 1d8 | 1.5kg | 50pt | Equilibrada |
| Machado de Combate | 1d8 | 2kg | 40pt | Impacto |
| Lança | 1d8 | 1.5kg | 30pt | Alcance 2m, Duas mãos |
| Martelo de Guerra | 1d8 | 2kg | 35pt | Impacto |

### Armas Grandes

| Arma | Dano | Peso | Custo | Modificadores |
|------|------|------|-------|---------------|
| Espada Larga | 1d10 | 2kg | 70pt | Duas mãos |
| Machado Grande | 1d10 | 3kg | 60pt | Impacto, Duas mãos |
| Alabarda | 1d10 | 2.5kg | 65pt | Alcance 2m, Duas mãos |
| Montante | 1d12 | 3kg | 100pt | Duas mãos, Força 12+ |

## ARMAS À DISTÂNCIA

### Arcos

| Arma | Dano | Alcance | Peso | Custo |
|------|------|---------|------|-------|
| Arco Curto | 1d6 | 60m | 1kg | 50pt |
| Arco Longo | 1d8 | 100m | 1.5kg | 80pt |
| Besta Leve | 1d8 | 80m | 1.5kg | 120pt |
| Besta Pesada | 1d10 | 120m | 3kg | 200pt |

### Arremessos

| Arma | Dano | Alcance | Peso | Custo |
|------|------|---------|------|-------|
| Faca de Arremesso | 1d4 | 6m | 0.3kg | 15pt |
| Machado de Arremesso | 1d6 | 8m | 1kg | 30pt |
| Granada Manual | 2d6 | 10m | 0.3kg | 50pt |

## ARMAS DE FOGO

### Pistolas

| Arma | Dano | Alcance | Peso | Custo | Munição |
|------|------|---------|------|-------|---------|
| Pistola .22 | 1d6 | 30m | 0.6kg | 300pt | .22 |
| Pistola 9mm | 2d6 | 40m | 0.8kg | 400pt | 9mm |
| Revólver .38 | 2d6 | 40m | 1kg | 350pt | .38 |
| Pistola .45 | 2d6+1 | 45m | 1kg | 500pt | .45 |

### Rifles

| Arma | Dano | Alcance | Peso | Custo | Munição |
|------|------|---------|------|-------|---------|
| Carabina .22 | 1d6 | 80m | 2kg | 400pt | .22 |
| Rifle .308 | 3d6 | 300m | 3.5kg | 800pt | .308 |
| Metralhadora 9mm | 2d6 | 100m | 2.5kg | 1200pt | 9mm |
| Espingarda 12GA | 3d6 | 30m | 3.5kg | 600pt | 12GA |

## ARMADURAS

### Armaduras Leves

| Armadura | RD | Peso | Custo | Penalidade |
|----------|-----|------|-------|-----------|
| Roupa de Couro | 1 | 1kg | 50pt | Nenhuma |
| Gibão | 2 | 2kg | 100pt | -1 DEX |
| Couro Endurecido | 2 | 2.5kg | 150pt | -1 DEX |
| Chainmail Leve | 3 | 3kg | 250pt | -2 DEX, -1m movimento |

### Armaduras Médias

| Armadura | RD | Peso | Custo | Penalidade |
|----------|-----|------|-------|-----------|
| Couro Pesado | 3 | 4kg | 200pt | -2 DEX |
| Chainmail | 4 | 5kg | 400pt | -3 DEX, -1.5m movimento |
| Placa Parcial | 4 | 6kg | 500pt | -3 DEX, -2m movimento |
| Placa de Peito | 5 | 8kg | 600pt | -4 DEX, -2m movimento |

### Armaduras Pesadas

| Armadura | RD | Peso | Custo | Penalidade |
|----------|-----|------|-------|-----------|
| Placa Completa | 6 | 12kg | 1000pt | -5 DEX, -3m movimento |
| Placa Mágica | 7 | 10kg | 2000pt | -3 DEX, -1m movimento |
| Mithral | 5 | 6kg | 1500pt | -2 DEX, Nenhuma penalidade movimento |
| Adamantina | 8 | 15kg | 2500pt | -6 DEX, -3m movimento |

## ESCUDOS

| Escudo | Bonus AC | Peso | Custo | Dano Reflexo |
|--------|----------|------|-------|-------------|
| Broquel | +1 | 1kg | 50pt | 1d4-1 |
| Escudo Ronda | +2 | 2kg | 100pt | 1d6 |
| Escudo Peltasta | +2 | 2.5kg | 120pt | 1d6 |
| Torre | +3 | 4kg | 200pt | 1d8 |

## ITENS VARIADOS

### Acampamento

| Item | Peso | Custo | Descrição |
|------|------|-------|-----------|
| Mochila | 0.5kg | 30pt | Carrega 30kg |
| Barraca | 2kg | 100pt | Abrigo para 1 pessoa |
| Saco de Dormir | 1kg | 50pt | Aquecimento noturno |
| Corda (50m) | 2kg | 50pt | Resistência 200kg |
| Corrente (3m) | 3kg | 80pt | Resistência 500kg |
| Isqueiro | 0.05kg | 5pt | Acende fogo |
| Lanterna | 0.5kg | 40pt | Ilumina 10m |
| Vela (12) | 0.2kg | 5pt | Ilumina 3m |

### Comunicação

| Item | Peso | Custo | Descrição |
|------|------|-------|-----------|
| Papel (100 folhas) | 0.2kg | 20pt | Escrita |
| Tinta (frasco) | 0.1kg | 10pt | Para escrita |
| Pena | 0.01kg | 2pt | Escrita |
| Mensageiro (por km) | — | 5pt | Entrega de mensagem |

### Médico

| Item | Peso | Custo | Descrição |
|------|------|-------|-----------|
| Kit Médico | 1kg | 100pt | +2 em medicina, 10 usos |
| Antídoto Veneno | 0.05kg | 50pt | Neutraliza veneno |
| Bebida de Cura | 0.1kg | 100pt | Restaura 1d6 PV |
| Antídoto Doença | 0.05kg | 80pt | Cura doença |

### Ferramentas

| Item | Peso | Custo | Descrição |
|------|------|-------|-----------|
| Kit de Ladrão | 0.5kg | 200pt | +2 em fechaduras, 10 usos |
| Martelo/Prego | 1kg | 10pt | Construção |
| Pá | 1kg | 20pt | Escavação |
| Picareta | 2kg | 30pt | Minério |
| Chave Mestra | 0.01kg | 50pt | Abre fechaduras comuns |
| Espelho Pequeno | 0.1kg | 15pt | Reconhecimento |

## CUSTO DE EQUIPAMENTO

### Pontos de Equipamento Inicial
pontos_equip = (riqueza_pontos × 200)

### Modificadores de Custo

| Modificador | Ajuste |
|-------------|--------|
| Equilibrada (arma) | +10% custo |
| Mágica (arma) | ×2 a ×5 custo |
| Mágica (armadura) | ×3 a ×10 custo |
| Envenenável | +20% custo |
| Material Exótico (Mithral) | ×2 custo |
| Material Exótico (Adamantina) | ×5 custo |

## PESO E ENCARGO

### Limite de Carregamentopeso_máximo = STR × 15 kg

### Penalidades por Encargo

| Percentual | Penalidade |
|-----------|-----------|
| 0-50% | Nenhuma |
| 51-100% | -1 em movimento |
| 101-150% | -2 em movimento, -1 DEX |
| 151%+ | -3 em movimento, -2 DEX, impossível correr |

## VALIDAÇÕES

- Arma deve ter dano válido (1d4+0 ou superior)
- Alcance arma distância: >= 10m
- Peso: >= 0.01kg (mínimo)
- Custo: >= 1pt
- Redução dano armadura: 1-8
- Bônus AC escudo: 1-4
- Penalidade movimento: -3m máximo
- Penalidade DEX: -6 máximo

## Cálculos

### Dano Arma com Modificadoresdano_final = dano_base + modificador_atributo
### AC com Armadura + Escudoac_final = 10 + dex_mod + bonus_escudo - penalidade_armadura

### Peso Totalpeso_total = soma(peso de cada item)
encargo = peso_total / peso_máximo


## Exemplo: Guerreiro Equipado

### Setup: Guerreiro STR 15 (mod +2)

**Armas**:
- Espada Longa: 1d8 dano → 1d8+2 (com STR)
- Arco Longo: 1d8 dano → 1d8 (sem bônus DEX)

**Armadura**:
- Placa Parcial: RD 4, peso 6kg, penalidade -3 DEX, -2m movimento
- AC: 10 + 1 (DEX) - 3 (armadura) + 2 (escudo) = 10

**Escudo**:
- Ronda: +2 AC, peso 2kg

**Itens**:
- Mochila: 0.5kg
- Corda: 2kg
- Kit Médico: 1kg
- Lanterna: 0.5kg

**Peso Total**: 6 + 2 + 0.5 + 2 + 1 + 0.5 = 12kg
**Peso Máximo**: 15 × 15 = 225kg
**Encargo**: 12/225 = 5% (sem penalidade)

## Referência do Livro
GURPS 4E: Módulo Básico - Capítulo 8: Equipamento
Armas, Armaduras, Escudos, Custo, Peso



