# FEATURE: Sistema de Magia GURPS

## Descrição Breve
Implementar sistema de magia com Escolas de Magia, Pontos de Magia (Mana), Feitiços com Dificuldade, Custo em Mana, Resistência à Magia e Progressão de Feitiços.

## Regra Principal
Mago gasta Pontos de Magia para lançar feitiços. Cada feitiço tem nível (1-10), custo em mana, tempo de conjuração. Teste = 1d20 <= (Skill_Magia + modificadores) vs. Resistência do Alvo. Feitiço falha se teste falhar. Mana recupera 1 ponto/hora de descanso.

## Dados/Campos Necessários

### Conjurador
- magoId: string
- nome: string
- inteligencia: number (modificador)
- pontos_magia_max: number
- pontos_magia_atual: number
- escolas_dominadas: string[] (Evocação, Abjuração, Transmutação, Ilusão, Adivinhação, Magia Negra, etc.)
- feiticos_conhecidos: Feitico[]
- resistencia_magia: number (bônus vs. resistência)

### Feitiço (Spell)
- feiticoId: string
- nome: string
- escola: enum — "Evocacao" | "Abjuracao" | "Transmutacao" | "Ilusao" | "Adivinhacao" | "MagiaNegra" | "Divina" | "Profana"
- nivel: number (1-10)
- custo_mana: number
- tempo_execucao: enum — "acao_rapida" | "acao_padrao" | "minuto" | "10_minutos"
- alcance: string — "pessoal" | "toque" | "30m" | "1.5km" | "vista" etc.
- alvo: string — descrição do alvo/área
- duracao: string — "instantaneo" | "1_minuto" | "1_hora" | "permanente"
- teste_resistencia: enum — "nenhum" | "magia" | "vontade" | "fortitude"
- descricao: string (efeito do feitiço)

### Ponto de Magia (Mana Pool)
- magia_maxima: number (calculada: INT mod × 5 + bônus de vantagens)
- magia_atual: number (gasto em conjurações)
- taxa_recuperacao: number (pontos/hora de descanso)

## 1. ESCOLAS DE MAGIA

### Evocação
- Feitiços de dano direto
- Exemplos: Bola de Fogo, Relâmpago, Míssil Mágico
- Resistência: Reflexo (tentar esquivar)
- Custo: Normal

### Abjuração
- Feitiços de proteção e barreiras
- Exemplos: Proteção, Escudo Mágico, Dissipar Magia
- Resistência: Magia (resistência mágica)
- Custo: Normal

### Transmutação
- Feitiços que transformam objetos/pessoas
- Exemplos: Transformar, Acelerar, Levitação
- Resistência: Fortitude (resistência física)
- Custo: Alto

### Ilusão
- Feitiços que enganam os sentidos
- Exemplos: Invisibilidade, Imagem Especular, Escuridão
- Resistência: Vontade (força mental)
- Custo: Normal

### Adivinhação
- Feitiços que revelam informações
- Exemplos: Detectar Magia, Visão Verdadeira, Ler Mentes
- Resistência: Vontade (proteção mental)
- Custo: Normal

### Magia Negra
- Feitiços que ferem e desgastam
- Exemplos: Maldição, Envelhecimento, Morte Negra
- Resistência: Fortitude (constituição)
- Custo: Muito Alto
- Penalidade: -10 pontos de vontade se usar feitiço muito poderoso

### Magia Divina
- Feitiços de clérigo/paladino
- Exemplos: Cura, Ressurreição, Proteção Divina
- Resistência: Vontade ou Nenhum (depende do feitiço)
- Custo: Variável
- Requisito: Fé (deve ter ponto em Fé ou Devoção)

## 2. CUSTO EM MANA

### Tabela de Custo por Nível de Feitiço

| Nível | Custo Base | Modificador Área | Modificador Alcance |
|-------|-----------|-----------------|-------------------|
| 1 | 1 mana | +1 | +1 |
| 2 | 2 mana | +1 | +1 |
| 3 | 3 mana | +2 | +2 |
| 4 | 4 mana | +2 | +2 |
| 5 | 5 mana | +3 | +2 |
| 6 | 6 mana | +3 | +3 |
| 7 | 7 mana | +4 | +3 |
| 8 | 8 mana | +4 | +4 |
| 9 | 9 mana | +5 | +4 |
| 10 | 10 mana | +5 | +5 |

### Modificadores

**Área Expandida**:
- Dupla (2× raio): +1 mana
- Tripla (3× raio): +2 mana
- Quádrupla (4× raio): +3 mana

**Alcance Estendido**:
- 2× alcance: +1 mana
- 3× alcance: +2 mana
- 10× alcance: +3 mana
- Alcance ilimitado (vista): +4 mana

**Duração Estendida**:
- 1 hora → 1 dia: +1 mana
- 1 dia → 1 semana: +2 mana
- 1 semana → permanente: +3 mana

## 3. TESTE DE CONJURAÇÃO

### Fórmula
**Teste**: 1d20 <= (Skill_Magia_Escola + Inteligencia_Mod + Modificadores)

### Dificuldades
- **Fácil (DC -2)**: Nível 1-2, sem modificadores
- **Normal (DC 0)**: Nível 3-5, com poucos modificadores
- **Difícil (DC +2)**: Nível 6-8, com vários modificadores
- **Muito Difícil (DC +5)**: Nível 9-10, feitiços raros/perigosos

### Falha no Teste
- Feitiço **NÃO** é conjurado
- Mana gasta **NÃO** é recuperada (desperdiçada)
- Possível reação mágica caótica (a critério do mestre)

### Sucesso Crítico (20 natural)
- Efeito duplicado (dano 2×, duração 2×)
- Custos extras são pagos se feitiço for ampliado

### Falha Crítica (1 natural)
- Feitiço falha catastroficamente
- 1d6 dano ao conjurador ou algo explosivo

## 4. RESISTÊNCIA À MAGIA

### Teste de Resistência do Alvo

**Fórmula**: 1d20 vs. (Resistência_Alvo + Modificadores)

Se resistência_alvo >= conjurador_teste:
- Alvo resiste totalmente
- Feitiço não afeta

Se resistência_alvo < conjurador_teste:
- Feitiço afeta normalmente
- Ou metade do efeito se teste foi marginal

### Fontes de Resistência
- Amulete de Proteção Mágica: +2 a +5
- Armadura Mágica: +1 por nível de encantamento
- Magia de Proteção Ativa: +3 a +10
- Característica Resistência à Magia: +5 a +20

## 5. RECUPERAÇÃO DE MANA

### Taxa Base
- **Repouso Completo (Sono)**: 1 ponto mana/hora
- **Repouso Parcial**: 0,5 ponto mana/hora
- **Meditação Ativa**: 2 pontos mana/hora
- **Sem Repouso**: 0 pontos mana/hora

### Fatores que Afetam Recuperação
- Ferimento grave: -50% recuperação
- Cansaço extremo: -75% recuperação
- Magia de cura aplicada: +50% recuperação até próxima hora
- Ambiente sagrado: +50% recuperação
- Ambiente maldito: -50% recuperação

## 6. FEITIÇOS POR NÍVEL (EXEMPLOS)

### Nível 1
- Raio Mágico (Evocação): 1 mana, dano 1d6
- Proteção (Abjuração): 1 mana, +2 AC por rodada
- Detectar Magia (Adivinhação): 1 mana, detecta aura mágica
- Fogo de Palma (Evocação): 1 mana, dano 1d4

### Nível 2
- Invisibilidade (Ilusão): 2 mana, invisível 10 min
- Escudo Mágico (Abjuração): 2 mana, +4 AC
- Imagem Especular (Ilusão): 2 mana, cria copias ilusorias
- Leitura de Magia (Adivinhação): 2 mana, identifica magia

### Nível 3
- Bola de Fogo (Evocação): 3 mana, 5d6 dano, raio 6m
- Relâmpago (Evocação): 3 mana, 5d6 dano, linha 30m
- Transformar (Transmutação): 3 mana, transformar objeto
- Levitação (Transmutação): 3 mana, flutuar 3m/turno

### Nível 4
- Teleporte (Transmutação): 4 mana, tele até 300m
- Muro de Fogo (Abjuração): 4 mana, barreira dano/rodada
- Visão Verdadeira (Adivinhação): 4 mana, vê magia/disfarces

### Nível 5+
- Conjuração Planar: 5 mana, evoca criatura
- Reconfiguração Corporal: 6 mana, reconstrói corpo
- Morte Negra: 7 mana, dano massivo (Magia Negra)
- Ressurreição: 8 mana, traz morto à vida (Divina)

## 7. PROGRESSÃO DE FEITIÇOS

### Aprender Novo Feitiço
- **Custo**: 5 pontos por nível do feitiço
- **Tempo**: 1 semana de estudo por nível
- **Pré-requisito**: Deve ser da escola que o mago domina

### Aumentar Skill da Escola de Magia
- **Custo**: 1 ponto por nível
- **Bônus**: +1 em todos os testes de feitiços dessa escola

### Vantagens Mágicas
- **Aptidão Mágica**: +5 pontos de mana max (custa 5pt)
- **Regeneração de Mana**: +1 ponto mana/30min (custa 10pt)
- **Versatilidade Mágica**: Pode aprender feitiços de outra escola (custa 15pt)

## Validações

- Mana gasta: nunca negativa
- Feitiço requer mana suficiente antes de lançar
- Teste de conjuração: 1d20 <= skill + INT + modificadores
- Resistência testada contra DC apropriada
- Duração nunca infinita (exceto feitiços permanentes aprovados)
- Nível feitiço: 1-10

## Cálculos

### Mana Máxima
mana_max = (INT_mod × 5) + bônus_vantagens
### Custo Total de Feitiçocusto_total = custo_base + mod_area + mod_alcance + mod_duracao
### Teste de Conjuraçãoresultado = 1d20
sucesso = resultado <= (skill_escola + INT_mod + modificadores)
### Recuperação de Manamana_recuperada_por_hora = taxa_base × (1 + modificadores)


## Exemplo Completo: Lançar Bola de Fogo

### Setup: Mago com INT +3, Evocação 5
- Feitiço: Bola de Fogo (nível 3)
- Custo base: 3 mana
- Mana atual: 8/12
- Modificador de ambiente: nenhum

### Pré-requisitos
- Tem mana? SIM (8 >= 3)
- Conhece feitiço? SIM
- Componentes? SIM (verbal, somático)

### Teste de Conjuração
- Skill Evocação: 5
- INT mod: +3
- DC Nível 3: 0 (normal)
- Teste: 1d20 + 5 + 3 = 1d20 + 8
- Rolou: 14 → 14 + 8 = 22 → SUCESSO

### Gasto de Mana
- Mana gasta: 3
- Mana restante: 8 - 3 = 5/12

### Efeito
- Dano: 5d6 (rolou 3+4+2+5+1 = 15)
- Alvo testa Resistência: Reflexo
- DC contra-ataque: 15
- Se falhar: sofre 15 de dano
- Se suceder: sofre 7 de dano (metade)

## Referência do Livro
GURPS 4E: Módulo Básico - Capítulo 5: Magia
Escolas, Feitiços, Custo, Resistência, Progressão

