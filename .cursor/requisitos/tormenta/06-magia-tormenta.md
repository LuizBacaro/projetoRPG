# FEATURE: Sistema de Magia Tormenta RPG

## Descrição Breve
Implementar o sistema completo de magia com Espaços de Feitiço, cálculo de Conjuração (testes de concentração), Magias por Nível (0-9), e progressão de feiticeiros.

## Regra Principal
Magias arcanas e divinas funcionam via espaços de feitiço. Conjurador prepara ou conhece magias. Cada magia consome 1 espaço do seu nível. Conjuração requer teste de concentração se interrompido. Magias por nível 0-9 com dificuldade progressiva.

## Dados/Campos Necessários

### Conjurador
- conjuradorId: string
- nome: string
- classe: enum — "Mago" | "Feiticeiro" | "Clérigo" | "Druida" | "Bardo" | "Paladino" | "Ranger"
- nivel: number (1-20)
- intMod: number (modificador de inteligência) — para Mago
- chaMod: number (modificador de carisma) — para Feiticeiro
- wisMod: number (modificador de sabedoria) — para Clérigo/Druida
- tipoMagia: enum — "arcana" | "divina" (ou ambas para multiclasse)

### Espaços de Feitiço
- espacosPorNivel: number[] (array de 10 posições: nível 0-9)
- espacosUsadosPorNivel: number[] (rastreamento de uso)
- magiasConhecidas: Magia[] (lista de magias que o conjurador conhece)
- magiasPreparadas: Magia[] (apenas para Mago/Clérigo)

### Magia (Spell)
- magiaid: string
- nome: string
- nivel: number (0-9)
- tipo: enum — "arcana" | "divina"
- tempoExecucao: enum — "acao_padrao" | "acao_movimento" | "acao_livre" | "reacao"
- alcance: string — "pessoal" | "toque" | "18m" | "1.5km" etc.
- alvo: string — descrição do alvo/área
- duracao: string — "instantâneo" | "1 minuto" | "1 hora" | "permanente" etc.
- testeResistencia: enum — "nenhum" | "reflexos" | "fortitude" | "vontade"
- custoMana: number (0 para truques)
- descricao: string (efeito da magia)
- componentes: enum[] — "verbal" | "somatico" | "material"

## 1. ESPAÇOS DE FEITIÇO

### Tabela de Espaços por Nível e Classe

#### Mago (Inteligência)
| Nível | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|-------|---|---|---|---|---|---|---|---|---|---|
| 1 | 3 | 1 | — | — | — | — | — | — | — | — |
| 2 | 4 | 2 | — | — | — | — | — | — | — | — |
| 3 | 4 | 2 | 1 | — | — | — | — | — | — | — |
| 4 | 4 | 3 | 2 | — | — | — | — | — | — | — |
| 5 | 4 | 3 | 2 | 1 | — | — | — | — | — | — |
| 6 | 4 | 3 | 3 | 2 | — | — | — | — | — | — |
| 7 | 4 | 4 | 3 | 2 | 1 | — | — | — | — | — |
| 8 | 4 | 4 | 3 | 3 | 2 | — | — | — | — | — |
| 9 | 4 | 4 | 4 | 3 | 2 | 1 | — | — | — | — |
| 10 | 4 | 4 | 4 | 3 | 3 | 2 | — | — | — | — |
| 11 | 4 | 4 | 4 | 4 | 3 | 2 | 1 | — | — | — |
| 12 | 4 | 4 | 4 | 4 | 3 | 3 | 2 | — | — | — |
| 13 | 4 | 4 | 4 | 4 | 4 | 3 | 2 | 1 | — | — |
| 14 | 4 | 4 | 4 | 4 | 4 | 3 | 3 | 2 | — | — |
| 15 | 4 | 4 | 4 | 4 | 4 | 4 | 3 | 2 | 1 | — |
| 16 | 4 | 4 | 4 | 4 | 4 | 4 | 3 | 3 | 2 | — |
| 17 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 3 | 2 | 1 |
| 18 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 3 | 3 | 2 |
| 19 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 3 | 3 |
| 20 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 |

#### Feiticeiro (Carisma)
Mesma tabela que Mago, mas espaços recebem bônus de CHA mod (mínimo 0)

#### Clérigo (Sabedoria)
Recebe espaços até nível 9. Magia mínima nivel 1 (sem truques). Espaços adicionais = WIS mod

#### Druida (Sabedoria)
Idêntico ao Clérigo

#### Bardo (Carisma)
Espaços até nível 6. Bônus = CHA mod

#### Paladino (Sabedoria)
Espaços apenas a partir nível 4. Nível 4-5: 1 espaço de nível 1

#### Ranger (Sabedoria)
Espaços apenas a partir nível 4. Nível 4-5: 1 espaço de nível 1

### Bônus de Espaços por Modificador de Habilidade

Se o modificador da habilidade primária >= 1:
- Adicione 1 espaço do nível = (modificador_habilidade - 1)
- Repita para cada nível de magia disponível

**Exemplo Feiticeiro com CHA +3:**
- Nível 1: tem 1 espaço base, +1 espaço adicional (CHA+3) = 2 espaços de nível 1
- Nível 2: tem 1 espaço base, +1 espaço adicional = 2 espaços de nível 2

### Recuperação de Espaços
- **Descanso Noturno Completo**: restaura TODOS os espaços de feitiço
- **Mago**: pode preparar novamente via ritual diário
- **Feiticeiro**: recuperação automática ao acordar
- **Clérigo/Druida**: oração matinal + descanso noturno

## 2. CONJURAÇÃO (SPELLCASTING)

### Pré-requisitos para Conjurar
1. **Magia Conhecida**: conjurador deve ter a magia em sua lista (ou ter preparado, se Mago/Clérigo)
2. **Espaço Disponível**: espaço do nível da magia não foi usado ainda
3. **Componentes**: possuir componentes exigidos (verbal, somático, material)
4. **Concentração**: se interrompido durante conjuração, fazer teste de concentração

### Tempo de Execução

| Tempo | Descrição | Permite Ação Padrão Adicional |
|-------|-----------|------|
| Ação Padrão | Magia mais comum (maioria do nível 1-3) | Não, é a ação padrão |
| Ação Movimento | Magia rápida (alguns truques, magias de buff) | Sim, tem ação padrão livre |
| Ação Livre | Muito rápida (raro, alguns feitos especiais) | Sim, de novo |
| Reação | Resposta rápida (pré-requisito de feito) | Não, consome reação |
| 1 Rodada | Ritual (magia complexa, nível 6+) | Não, ocupa rodada inteira |
| 10 Minutos | Ritual (magia muito complexa, ritual especial) | Não, requer concentração |

### Componentes de Magia

- **Verbal (V)**: requer fala. Se silenciado, não pode usar esta magia
- **Somático (S)**: requer movimento das mãos/corpo. Se preso, não pode usar
- **Material (M)**: item específico. Se não tiver, não pode usar (exceto foco universal)

**Foco**: alguns materiais podem ser substituídos por foco mágico (bastão, varinha, cristal)

### Teste de Concentração

Se atingido durante conjuração ou manutenção de magia:
**Fórmula**: 1d20 + WIS mod ou 1d20 + INT mod (conforme classe) >= 10 + dano recebido

- **Sucesso**: magia mantém-se
- **Falha**: magia é cancelada, espaço de feitiço é consumido mesmo assim

**Exemplo**:
- Mago está conjurando Raio Mágico
- Leva 8 de dano de um goblin
- Teste: 1d20 (rolou 10) + 2 (INT mod) = 12 >= 10 + 8 = 18? NÃO
- Magia cancelada, espaço desperdiçado

## 3. RESISTÊNCIA À MAGIA

Algumas criaturas/itens têm Resistência à Magia (RM).
- **Teste de Resistência**: 1d20 vs. RM (CA da magia = 10 + nível da magia + mod da habilidade primária)
- **Sucesso**: criatura resiste, magia não afeta
- **Falha**: magia afeta normalmente

**Exemplo**:
- Demônio tem RM 20
- Mago lança Bola de Fogo (nível 3) com INT +3
- CA da magia: 10 + 3 + 3 = 16
- 16 < 20 → Resistência bem-sucedida, demônio não é afetado

## 4. MAGIAS POR NÍVEL (PROGRESSÃO)

### Nível 0 (Truques / Cantrips)
- **Sem limite de uso**: podem ser conjurados quantas vezes quiser
- **Sem espaço consumido**: grátis
- **Exemplos**: Raio Mágico (Mago), Chamado (Clérigo), Luz, Prestidigitação
- **Dano típico**: 1d4 a 1d6
- **Efeito**: de suporte, dano menor ou utilidade

### Nível 1
- **Espaços**: 1-4 (dependendo do nível do conjurador)
- **Tempo**: ação padrão
- **Exemplos**: Míssil Mágico, Proteção, Alarme, Escudo Mágico
- **Efeito**: dano 1d4 a 2d4, buff/debuff simples
- **DC típico**: 11-12

### Nível 2
- **Espaços**: 1-4
- **Tempo**: ação padrão
- **Exemplos**: Invisibilidade, Levantar Terra, Bola de Fogo (preparação)
- **Efeito**: dano 3d6, transformação, teleporte curto
- **DC típico**: 12-13

### Nível 3
- **Espaços**: 1-4
- **Tempo**: ação padrão
- **Exemplos**: Bola de Fogo, Relâmpago, Voo
- **Efeito**: dano 5d6, transformações maiores
- **DC típico**: 13-14

### Nível 4
- **Espaços**: 1-3
- **Tempo**: ação padrão
- **Exemplos**: Teleporte, Muro de Fogo, Visão Verdadeira
- **Efeito**: dano 6d6, exploração, testes menores
- **DC típico**: 14-15

### Nível 5
- **Espaços**: 1-3
- **Tempo**: ação padrão
- **Exemplos**: Teleporte em Grupo, Comunhão, Contato Planar
- **Efeito**: dano 7d6, comunicação planar, mudanças maiores
- **DC típico**: 15-16

### Nível 6+
- **Espaços**: 1-2
- **Tempo**: 1 rodada (ritual)
- **Exemplos**: Viagem Planar, Prisão Mágica, Sequestro Planar
- **Efeito**: efeitos permanentes ou semi-permanentes
- **DC típico**: 16+
- **Restrições**: Disponível apenas em níveis altos (12+)

## 5. SALVAÇÃO DE MAGIA

Se a magia causa dano ou efeito prejudicial, a criatura alvo pode fazer teste de salvação:

### Tipos de Salvação

| Tipo | Defesa | Modificador |
|------|--------|------------|
| Reflexos | Evasão, agilidade | DEX mod |
| Fortitude | Resistência física | CON mod |
| Vontade | Força de mente | WIS mod |

### Sucesso vs. Falha

- **Falha**: magia tem efeito total
- **Sucesso**: dano reduzido à metade (geralmente) ou sem efeito

**Exemplo**:
- Mago lança Bola de Fogo (dano 5d6)
- Resultado: 18 de dano
- Inimigo tenta salvar em Reflexos (DEX +2): 1d20 + 2 = 15
- DC da magia: 10 + 3 (nível) + 3 (INT) = 16
- 15 < 16 → Falha, sofre 18 de dano total
- Se tivesse 16+: sofreria 9 de dano (metade)

## 6. DESAFIO DAS MAGIAS (DC)

Quando a magia permite salvação, calcule DC:

**DC = 10 + Nível da Magia + Modificador da Habilidade Primária**

| Classe | Habilidade Primária |
|--------|-------------------|
| Mago | Inteligência |
| Feiticeiro | Carisma |
| Clérigo | Sabedoria |
| Druida | Sabedoria |
| Bardo | Carisma |
| Paladino | Carisma |
| Ranger | Sabedoria |

**Exemplo DC**:
- Feiticeiro nível 8 com CHA +4
- Magia nível 3: 10 + 3 + 4 = **DC 17**

## 7. TABELA RÁPIDA: MAGIAS COMUNS POR NÍVEL

### Nível 0 (Truques)
- Raio Mágico (Mago): dano 1d4, alcance 36m
- Chamado (Clérigo): dano 1d4, alcance 18m
- Luz: ilumine um objeto
- Prestidigitação: pequeno efeito cosmético

### Nível 1
- Míssil Mágico: 1d4+1 dano, 5 mísseis
- Proteção: +1 AC por rodada
- Escudo Mágico: +4 AC por rodada
- Alarme: detecta entrada em área

### Nível 2
- Invisibilidade: invisível por 10 minutos
- Escuridão: área de escuridão mágica
- Levantar Terra: telekinesis pequena
- Aceleração: +30 movimento

### Nível 3
- Bola de Fogo: 5d6 dano, raio 6m
- Relâmpago: 5d6 dano, linha 36m
- Voo: voe por 1 hora

### Nível 4
- Teleporte: viaje até 180km
- Muro de Fogo: dano contínuo
- Visão Verdadeira: veja através de disfarces

### Nível 5+
- Teleporte em Grupo
- Comunhão com deidade
- Evocação de elemental

## Validações

- Espaços de feitiço: nunca negativo
- Magia conhecida ou preparada obrigatória
- Componentes checados antes de conjuração
- Teste de concentração se interrompido
- Salvação rolada para cada alvo
- DC = 10 + nível + habilidade_mod

## Cálculos

### Espaços por Nível

espacoNivel(classe, nivel, habilidadeMod) =
tabela_base[classe][nivel][spellLevel] + max(0, habilidadeMod - 1)markdown
### DC de Magiadc(nivelMagia, habilidadeMod) =
10 + nivelMagia + habilidadeModmarkdown
### Dano de Magiadano(dados, habilidadeMod, efeito) =
rolar_dados(dados) + bônus_especial



## Exemplo Completo: Lançamento de Bola de Fogo

### Setup: Mago nível 5, INT +3
- Magia: Bola de Fogo (nível 3)
- Espaços de nível 3 disponíveis: 1
- DC: 10 + 3 + 3 = 16

### Pré-requisitos
- Magia conhecida? SIM (tem na lista)
- Espaço disponível? SIM (tem 1 espaço nível 3)
- Componentes? SIM (verbal, somático)

### Execução
- Tempo de execução: ação padrão
- Alvo: point 15m away, raio 6m
- Dano: 5d6 (para nível 3)
- Roll: 1d6 + 1d6 + 1d6 + 1d6 + 1d6 = 3+2+4+1+5 = **15 de dano**

### Salvação (inimigos na área)
- Todos na área fazem teste de Reflexo vs. DC 16
- Inimigo 1: 1d20 + 2 (DEX) = 14 → Falha → sofre 15
- Inimigo 2: 1d20 + 2 = 18 → Sucesso → sofre 7 (metade)

### Resultado
- Espaço de nível 3 consumido
- Inimigo 1 perde 15 HP
- Inimigo 2 perde 7 HP

## Referência do Livro
Capítulo 8: Magia | Espaços de Feitiço, Conjuração, Magias por Nível 0-9
Páginas ~140-180

