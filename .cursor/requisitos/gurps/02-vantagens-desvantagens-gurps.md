# FEATURE: Sistema de Vantagens e Desvantagens GURPS 4E

## Descrição Breve
Implementar vantagens (advantages) e desvantagens (disadvantages) com custo em pontos, modificadores e efeitos especiais. Inclui 50+ vantagens e 40+ desvantagens categorizadas.

## Regra Principal
Vantagens custam pontos positivos. Desvantagens fornecem pontos negativos (descontos). Cada vantagem/desvantagem tem efeitos mecânicos específicos (bônus em perícias, redução de dano, limitações, etc.).

## Dados/Campos Necessários

### Vantagem/Desvantagem
- traitId: string (identificador único)
- nome: string
- tipo: enum — "vantagem" | "desvantagem"
- categoria: enum — "Mental" | "Física" | "Social" | "Sobrenatural" | "Profissão"
- custo: number (positivo para vantagens, negativo para desvantagens)
- modificadores: object[] — lista de modificadores mecânicos
- niveis: number (0 = sem níveis, 1+ = tem níveis)
- custoPorNivel: number (se aplicável)
- prerequisitos: string[] (lista de vantagens/atributos necessários)
- descricao: string

## Vantagens Principais (Categorias)

### Vantagens Mentais (Exemplos)
- **Absoluto Senso de Direção**: 5-10 pts — nunca se perde
- **Alter Egos**: 10+ pts — personalidades alternativas
- **Analítico**: 5 pts — +1 em testes de análise
- **Inteligência Artificial**: 40 pts — para máquinas/robôs
- **Lerdo/Rápido de Raciocínio**: ±5-10 pts — modificador em perícias técnicas

### Vantagens Físicas (Exemplos)
- **Agilidade Aumentada**: 5 pts/nível — +1 a DX para acrobacias
- **Armadura Inerente**: 3-5 pts/nível — reduz dano
- **Recuperação Acelerada**: 5-15 pts — cura mais rápido
- **Sentidos Aprimorados**: 2 pts/sentido — visão noturna, olfato aguçado
- **Fôlego**: 2 pts/nível — resistência em esforços

### Vantagens Sociais (Exemplos)
- **Aliados**: 5-15 pts — personagens que ajudam
- **Patrocínio**: 5-30 pts — suporte de organização
- **Reputação**: 5-15 pts — fama/infâmia
- **Riqueza**: 10-50+ pts — possui muito dinheiro
- **Status Social**: 5-40 pts — posição na sociedade

### Vantagens Sobrenaturais (Exemplos)
- **Magia**: 25-40 pts — acesso ao sistema de magia
- **Poderes Psíquicos**: 15-50+ pts — telepatia, telecinese, etc.
- **Imunidade**: 3-15 pts/tipo — não afetado por X
- **Regeneração**: 25-50 pts — recupera até morte
- **Voo**: 40+ pts — pode voar

## Desvantagens Principais (Exemplos)

### Desvantagens Mentais
- **Analfabeto**: -5 pts — não consegue ler/escrever
- **Avarento**: -5 pts — obsessão com dinheiro
- **Fobia**: -5 a -15 pts — medo irracional (varia com tipo)
- **Impulsivo**: -10 pts — age sem pensar
- **Loucura**: -10 a -30 pts — transtorno mental

### Desvantagens Físicas
- **Cegueira**: -50 pts — não vê
- **Surdez**: -20 pts — não ouve
- **Doença Crônica**: -20 a -50 pts — afeta saúde
- **Fraco**: -5 a -30 pts — reduz ST efetiva
- **Lento**: -5 a -10 pts — reduz DX efetiva

### Desvantagens Sociais
- **Anacrônico**: -10 pts — fora de seu tempo
- **Inimigo**: -5 a -100 pts — alguém quer te derrotar
- **Maldição**: -5 a -50 pts — azar ou efeito negativo
- **Notoriedade**: -5 a -20 pts — infâmia
- **Servil**: -5 a -15 pts — deve obediência

## Modificadores de Vantagens

Algumas vantagens permitem modificadores que alteram custo e efeito:

| Modificador | Custo | Efeito |
|-------------|-------|--------|
| +Ilimitado | +20% | Sem limite de uso |
| +Aprimorado | +10% | Efeito aumentado |
| +Restrito | -20% | Limitado a condições |
| +Custodiado | -30% | Depende de outras pessoas |

## Validações
- Vantagens custam positivos, desvantagens custam negativos
- Cada vantagem/desvantagem aplicada uma vez (exceto com níveis)
- Total de pontos: positivos (vantagens) + negativos (desvantagens) = pontos líquidos
- Máximo -75 pts em desvantagens mentais/físicas
- Máximo -50 pts em desvantagens sociais

## Cálculos

### Custo Total
custoTotal =
soma(vantagens.custo) + soma(desvantagens.custo)

markdown
### Aplicação de ModificadorescustoFinal(custo, modificador%) =
custo × (1 + modificador% / 100)


## Exemplos de Combinações

### Mago Ofensivo
- Magia: +25 pts
- Inteligência: +10 (alguns níveis)
- Foco Mágico: +5 pts
- Total: ~40 pts vantagens

### Ladino Furtivo
- Agilidade Aumentada +2: 10 pts
- Sentidos Aprimorados (visão noturna): 2 pts
- Fôlego +3: 6 pts
- Total: ~18 pts vantagens

### Guerreiro Defensivo
- Armadura Inerente +3: 15 pts
- Recuperação Acelerada: 5 pts
- Status Social +2: 10 pts
- Total: ~30 pts vantagens

## Referência do Livro
Capítulo 2: Vantagens | Capítulo 3: Desvantagens

