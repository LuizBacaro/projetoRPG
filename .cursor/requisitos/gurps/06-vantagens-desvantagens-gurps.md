# FEATURE: Sistema de Vantagens e Desvantagens GURPS

## Descrição Breve
Implementar sistema de Vantagens (bônus pagos em pontos) e Desvantagens (pontos ganhos) do GURPS com custo variável, modificadores, e progressão de personagem.

## Regra Principal
Vantagens custam pontos (5-50+). Desvantagens geram pontos (-5 a -50). Modificadores ajustam custos (ex: Visão Noturna +5pt base, pode ter mods de -30% a +100%). Limite: máximo 50 pontos de desvantagens. Personagem começa com 100 pontos base + bônus de vantagens - desvantagens.

## Dados/Campos Necessários

### Vantagem
- vantagemId: string
- nome: string
- custo_base: number (5, 10, 15, 25, 50, 100+)
- categoria: enum — "Mental" | "Física" | "Social" | "Sobrenatural" | "Profissional"
- modificadores: Modificador[] (opcional)
- descricao: string
- requisitos: string[] (pré-requisitos)
- nivel_maximo: number (para vantagens que podem ser compradas múltiplas vezes)
- custo_nivel_adicional: number (custo de cada compra adicional)

### Desvantagem
- desvantaemId: string
- nome: string
- pontos_ganhos: number (-5, -10, -15, -25, -50)
- categoria: enum — "Mental" | "Física" | "Social" | "Limitação"
- modificadores: Modificador[] (opcional)
- descricao: string
- conflitos: string[] (outras desvantagens incompatíveis)
- frequencia_manifestacao: enum — "Sempre" | "Frequente" | "Ocasional" | "Rara"
- limite_personagem: number (máximo por personagem, default 50 pontos)

### Modificador
- nome: string
- modificador_percentual: number (-50 a +100)
- descricao: string

## VANTAGENS PRINCIPAIS POR CATEGORIA

### Vantagens Mentais

| Vantagem | Custo Base | Descrição |
|----------|-----------|-----------|
| Inteligência Aguçada | 10 | +1 em testes de INT |
| Memória Eidética | 25 | Lembra de tudo perfeitamente |
| Genialidade Matemática | 20 | +3 em cálculos |
| Ambidestria | 10 | Usa ambas mãos com eficiência |
| Resistência Mental | 15 | Imunidade a alguns efeitos mentais |
| Vontade de Ferro | 15 | +3 em testes de Vontade |
| Rápido Raciocínio | 10 | Toma ações antes que normal |
| Possuidor de Segredos | 20 | Conhecimento sobre mistérios ocultos |
| Senso de Localização | 10 | Nunca se perde |
| Empatia Animal | 5 | Comunica-se com animais |

### Vantagens Físicas

| Vantagem | Custo Base | Descrição |
|----------|-----------|-----------|
| Força Aumentada | 10/nível | +2 por nível (máximo 4 níveis) |
| Agilidade Aumentada | 10/nível | +2 DEX por nível (máximo 4 níveis) |
| Resistência Aumentada | 10/nível | +1 CON por nível (máximo 3 níveis) |
| Velocidade Aumentada | 25 | +3 em velocidade de movimento |
| Recuperação Rápida | 25 | Cura o dobro normal |
| Visão Noturna | 5 | Enxerga perfeitamente no escuro |
| Audição Aguçada | 5 | +2 em testes de audição |
| Olfato Aguçado | 2 | Rastreia por cheiro |
| Imunidade a Doença | 25 | Não pode ser envenenado/doente |
| Resistência ao Frio | 5 | -50% dano de frio |
| Resistência ao Calor | 5 | -50% dano de calor |
| Resistência a Veneno | 15 | +3 em testes contra veneno |
| Regeneração | 50 | Recupera 1 PV/min |
| Vôo | 50 | Pode voar a até 30m/rodada |

### Vantagens Sociais

| Vantagem | Custo Base | Descrição |
|----------|-----------|-----------|
| Aliados | 5-50 | Contatos poderosos |
| Contatos | 5-15 | Conhece pessoas influentes |
| Fama | 5-25 | Reconhecido em público |
| Fortuna | 25-50 | Riqueza significativa |
| Influência | 10-30 | Poder em grupos específicos |
| Prestígio | 10-25 | Respeito em área de expertise |
| Reputação | 5-15 | Conhecido por feito específico |
| Título Nobre | 15-30 | Posição de nobreza |
| Patrono | 25-75 | Alguém poderoso o protege |

### Vantagens Sobrenaturais

| Vantagem | Custo Base | Descrição |
|----------|-----------|-----------|
| Magia | 100 | Pode aprender e lançar feitiços |
| Psionismo | 75 | Poderes psíquicos |
| Dominação | 50 | Controla aspectos da realidade |
| Imortalidade | 100 | Vive eternamente |
| Ressurreição | 75 | Pode voltar à vida |
| Cura Mágica | 40 | Cura via magia/milagres |
| Ligação Demoníaca | 50 | Contrato com ser sobrenatural |
| Herança Mágica | 25 | Pode aprender magia ancestral |

## DESVANTAGENS PRINCIPAIS POR CATEGORIA

### Desvantagens Mentais

| Desvantagem | Pontos | Frequência | Descrição |
|-------------|--------|-----------|-----------|
| Fobia | -5 a -15 | Frequente | Medo irracional |
| Mania | -10 | Frequente | Comportamento obsessivo |
| Impulsividade | -10 | Ocasional | Age sem pensar |
| Secretos Perigosos | -5 a -30 | Ocasional | Conhecimento que coloca em risco |
| Loucura | -15 a -50 | Rara | Transtorno mental |
| Compulsão | -5 a -15 | Frequente | Precisa fazer algo regularmente |
| Dependência | -5 a -25 | Frequente | Viciado em substância/atividade |
| Distúrbio de Sono | -5 | Frequente | Insônia ou pesadelos |
| Memória Fraca | -10 | Frequente | Esquece detalhes facilmente |
| Falta de Senso de Humor | -10 | Sempre | Não entende piadas |

### Desvantagens Físicas

| Desvantagem | Pontos | Frequência | Descrição |
|-------------|--------|-----------|-----------|
| Deficiência Visual | -10 a -25 | Sempre | Cego ou míope |
| Deficiência Auditiva | -10 a -20 | Sempre | Surdo ou parcialmente |
| Doença Crônica | -15 a -50 | Frequente | Afecção permanente |
| Fraqueza | -5 a -50 | Frequente | -1 a -5 em STR em situação específica |
| Alergias | -5 a -15 | Ocasional | Reação a substância |
| Envelhecimento Acelerado | -25 | Sempre | Envelhece 2× mais rápido |
| Lentidão | -5 a -10 | Sempre | -3m em movimento |
| Hemofilia | -30 | Sempre | Sangra até morrer |
| Mutismo | -25 | Sempre | Não pode falar |
| Deficiência Motora | -15 a -50 | Sempre | Paralisia parcial |

### Desvantagens Sociais

| Desvantagem | Pontos | Frequência | Descrição |
|-------------|--------|-----------|-----------|
| Inimigos | -5 a -50 | Ocasional | Tem adversários poderosos |
| Maldição | -10 a -30 | Frequente | Está amaldiçoado |
| Reputação Ruim | -5 a -25 | Frequente | Conhecido por ato negativo |
| Dívida | -5 a -50 | Frequente | Deve dinheiro/favores |
| Servil | -5 | Sempre | Submisso por natureza |
| Honra Duvidosa | -5 a -15 | Frequente | Questionado moralmente |
| Segredo Embaraçoso | -5 a -20 | Ocasional | Se descobrir, prejudica |

## MODIFICADORES DE CUSTO

### Exemplos de Modificadores

| Modificador | % | Aplicação |
|-------------|---|-----------|
| Requer Ritual | -10% | Precisa de preparação |
| Fadiga Mgica | -50% | Exaure quando usado |
| Limitação Severa | -30% | Só funciona em certas condições |
| Visibilidade | -20% | Óbvio que está usando |
| Alcance Limitado | -20% | Funciona apenas perto |
| Frágil | -10% | Desativa facilmente |
| Incompatibilidade Social | -10% | Rejeitado por usar |
| Custo Contínuo | -5% a -50% | Precisa gastar pontos regularmente |
| Melhorado | +20% a +100% | Versão superior do padrão |
| Ilimitado | +100% | Sem restrições |

## CUSTO TOTAL DE VANTAGEM/DESVANTAGEM

### Cálculo com Modificadores
custo_final = custo_base × (1 + soma_modificadores_percentuais)


**Exemplo Visão Noturna com Modificador Melhorado (+20%)**:
- Base: 5 pontos
- Modificador: +20%
- Final: 5 × 1.20 = 6 pontos

**Exemplo Fobia com Modificador Fadiga Mágica (-50%)**:
- Base: -10 pontos
- Modificador: -50%
- Final: -10 × 0.50 = -5 pontos

## LIMITAÇÕES E REGRAS

### Limite de Desvantagens
- Máximo 50 pontos de desvantagens por personagem
- Alguns GMs permitem até 75 em campanhas específicas
- Não pode vender mais de 50 pontos em desvantagens

### Vantagens Múltiplas
Algumas vantagens podem ser compradas múltiplas vezes:
- **Força Aumentada**: até 4 níveis (40 pontos máximo)
- **Agilidade Aumentada**: até 4 níveis
- **Resistência Aumentada**: até 3 níveis
- **Aliados**: cada compra adicional

### Desvantagens Incompatíveis
Não pode ter simultaneamente:
- Visão Normal + Visão Noturna
- Memória Eidética + Memória Fraca
- Magia + Imunidade a Magia

## PROGRESSÃO DE PERSONAGEM

### Gastando Pontos Obtidos em Campanha
Durante a campanha, personagem ganha pontos. Pode gastar em:
- **Aumentar Vantagem**: paga diferença até novo nível
- **Comprar Vantagem Nova**: custo integral
- **Remover Desvantagem**: paga pontos ganhos (inverso)
- **Aumentar Skill**: 1 ponto por nível
- **Aumentar Atributo**: 10 pontos por +1

## Validações

- Custo vantagem: >= 0 (exceto modificadores)
- Custo desvantagem: <= 0 (sempre negativo)
- Total desvantagens por personagem: <= 50 (ou 75 em campanha específica)
- Modificadores: -50% a +100% (máximo)
- Não pode ter vantagens/desvantagens incompatíveis
- Nível múltiplo: respeita limite máximo

## Cálculos

### Custo de Vantagem com Modificador
custo_final(custo_base, modificadores) =
custo_base × (1 + sum(modificadores))

### Pontos Ganhos em Desvantagempontos_ganhos(custo_desvantagem, modificadores) =
abs(custo_desvantagem × (1 + sum(modificadores)))

### Validação de Limitetotal_desvantagens = sum(abs(custo) para todas desvantagens)
válido = total_desvantagens <= 50


## Exemplo Completo: Personagem com Vantagens e Desvantagens

### Setup: Guerreiro Misterioso

**Vantagens**:
- Força Aumentada nível 2: 10 × 2 = 20 pontos
- Recuperação Rápida: 25 pontos
- Senso de Localização: 10 pontos
- Contatos (Crime Organizado): 10 pontos

**Total Vantagens**: 65 pontos

**Desvantagens**:
- Segredo Embaraçoso (trabalhou para vilão): -15 pontos
- Inimigos (crime rival): -20 pontos
- Fobia (Heights): -10 pontos

**Total Desvantagens**: -45 pontos (dentro do limite de 50)

**Cálculo Final**:
- Pontos Base: 100
- + Vantagens: 65
- - Desvantagens: 45
- **Total Disponível**: 120 pontos para skills/atributos

## Referência do Livro
GURPS 4E: Módulo Básico - Capítulo 2: Vantagens
GURPS 4E: Módulo Básico - Capítulo 3: Desvantagens
Custo, Modificadores, Limite de Desvantagens

