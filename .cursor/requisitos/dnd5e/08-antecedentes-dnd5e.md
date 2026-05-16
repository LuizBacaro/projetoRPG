# FEATURE: Sistema de Antecedentes D&D 5E

## Descrição Breve
Implementar 13 Antecedentes (Backgrounds) que fornecem proficiências, perícias, idiomas e características pessoais (personalidade, ideais, laços, fraquezas).

## Regra Principal
Cada personagem escolhe 1 Antecedente no nível 1. Fornece: 2 proficiências em perícias, 1 idioma extra, equipamento inicial, e traços de personalidade. Antecedente não afeta mecanicamente (exceto perícias), mas define história e roleplay.

## Dados/Campos Necessários

### Antecedente
- antecedenteId: string
- nome: string
- descricao: string
- pericias: string[] (2 perícias ganhas)
- idiomas: string[] (quantidade e tipos)
- equipamento: string[] (itens iniciais)
- ouroExtra: number (gp adicionais)
- tracos: Traco[]

### Traços de Personalidade
- personalidade: string[] (2 traços de personalidade)
- ideais: string[] (2 ideais do personagem)
- lacos: string[] (2 laços com mundo/pessoas)
- fraquezas: string[] (2 fraquezas/medos)

## ANTECEDENTES PRINCIPAIS

### Acolito (Acolyte)
**Descrição**: Servidor religioso em um templo ou santuário.

**Perícias**: Insight, Religião
**Idiomas**: 1 extra
**Equipamento**: Sagrado símbolo, livro de preces, 5 velas, roupa religiosa, bolsa de moedas (15 gp)
**Ouro Extra**: 0 gp

**Traços**:
- Personalidade: "Sou inabalável na fé" / "Questiono tudo, até meus superiores"
- Ideais: "Tradição é sagrada" / "Igualdade deve ser protegida"
- Laços: "Meu templo é minha vida" / "Devo meu life a um sacerdote"
- Fraquezas: "Sou intolerante com outras crenças" / "Tenho dúvidas secretas"

### Artesão (Artisan Guild Member)
**Descrição**: Membro de uma guilda de artesãos ou comércio.

**Perícias**: Insight, Deception
**Idiomas**: Idioma da guilda (conta como 1)
**Equipamento**: Kit de ferramentas profissionais, carta de membro da guilda, roupa de trabalho, bolsa com moedas (15 gp)
**Ouro Extra**: 0 gp

### Assassino (Criminal)
**Descrição**: Criminoso ou membro de organização criminosa.

**Perícias**: Deception, Stealth
**Idiomas**: 1 extra
**Equipamento**: Roupa de viagem obscura, kit de disfarce, ferramenta de roubo, bolsa (15 gp)
**Ouro Extra**: 0 gp

**Contato Criminal**: Acesso a rede criminal

### Aventureiro (Outlander)
**Descrição**: Viajante selvagem, caçador ou nômade.

**Perícias**: Athletics, Survival
**Idiomas**: 1 extra
**Equipamento**: Roupa de viagem, kit de sobrevivência, corda, mochila, bolsa (10 gp)
**Ouro Extra**: 5 gp

### Bondoso (Folk Hero)
**Descrição**: Herói popular de uma aldeia/região.

**Perícias**: Animal Handling, Survival
**Idiomas**: Nenhum
**Equipamento**: Arma simples, roupa de trabalho, ferramenta de ofício, bolsa (10 gp)
**Ouro Extra**: 0 gp

**Benefício**: Pessoas simples ajudam você (comida, abrigo, etc.)

### Cavaleiro (Soldier)
**Descrição**: Militar experiente ou veterano de guerra.

**Perícias**: Athletics, Intimidation
**Idiomas**: Nenhum
**Equipamento**: Arma marcial, uniforme militar, diamante de jogador, bolsa (10 gp)
**Ouro Extra**: 0 gp

**Especialidade Militar**: Escolha especialidade (infantaria, cavalaria, artilharia)

### Charlatão (Charlatan)
**Descrição**: Vigarista, enganador ou mentiroso profissional.

**Perícias**: Deception, Sleight of Hand
**Idiomas**: Nenhum
**Equipamento**: Kit de disfarce, kit de "ferramenta de estafa", roupa elegante, bolsa (15 gp)
**Ouro Extra**: 0 gp

**Identidade Falsa**: Pode criar identidades falsas

### Culto (Cult Initiate)
**Descrição**: Membro de um culto ou sociedade secreta.

**Perícias**: Arcana, Deception
**Idiomas**: 1 extra
**Equipamento**: Livro de rituais, símbolo culto, roupa cerimonial, bolsa (10 gp)
**Ouro Extra**: 0 gp

### Espião (Spy)
**Descrição**: Agente secreto ou informante.

**Perícias**: Deception, Stealth
**Idiomas**: 1 extra
**Equipamento**: Kit de disfarce, kit de roubo, roupa de viagem, bolsa (15 gp)
**Ouro Extra**: 0 gp

**Contato de Espionagem**: Acesso a rede de espiões

### Estudioso (Scholar)
**Descrição**: Acadêmico, bibliotecário ou pesquisador.

**Perícias**: Arcana, History
**Idiomas**: 2 extras
**Equipamento**: Livro especializado, tinta, pena, fogo, mochila, roupa de estudioso, bolsa (10 gp)
**Ouro Extra**: 0 gp

**Pesquisa Acadêmica**: Acesso a bibliotecas e universidades

### Garoto de Rua (Urchin)
**Descrição**: Órfão, mendigo ou rejeitado da sociedade.

**Perícias**: Sleight of Hand, Stealth
**Idiomas**: Nenhum
**Equipamento**: Faca pequena, mapa da cidade, cinto com moedas (5 gp)
**Ouro Extra**: 0 gp

**Contatos de Rua**: Acesso a rede de mendigos/crianças de rua

### Marinheiro (Sailor)
**Descrição**: Tripulante de navio ou trabalhador portuário.

**Perícias**: Athletics, Perception
**Idiomas**: Nenhum
**Equipamento**: Corda de 50 ft, âncora, roupa de marinheiro, bolsa (10 gp)
**Ouro Extra**: 0 gp

**Viajante do Mar**: Conhece portos e rotas marítimas

### Nobre (Noble)
**Descrição**: Membro da nobreza ou família respeitada.

**Perícias**: Insight, Persuasion
**Idiomas**: 1 extra
**Equipamento**: Roupa fina, selado familiar, bolsa com moedas (25 gp)
**Ouro Extra**: 25 gp

**Privilégio Nobre**: Acesso a círculos sociais altos

### Sábio (Sage)
**Descrição**: Mago, erudito ou mestre de conhecimento arcano.

**Perícias**: Arcana, History
**Idiomas**: 2 extras
**Equipamento**: Livro de conhecimento, tinta, pena, roupas de sábio, mochila, bolsa (10 gp)
**Ouro Extra**: 0 gp

**Conhecimento Mágico**: Especialista em lore e tradição arcana

## TRAÇOS DE PERSONALIDADE GENÉRICOS

### Personalidades (escolha 2)
- Sou naturalmente cauteloso
- Sou corajoso até recklessness
- Sou honesto até faltar sutileza
- Sou cínico sobre o mundo
- Sou otimista sobre o futuro
- Sou sarcástico em comportamento
- Sou silencioso e pensativo
- Sou tímido com estranhos
- Sou extrovertido e jovial
- Sou temperamental e impulsivo

### Ideais (escolha 2)
- Bondade: devo proteger o fraco
- Justiça: as leis devem ser justas
- Liberdade: ninguém deve ser escravizado
- Poder: mereço ser o melhor
- Ambição: farei grande nome para mim
- Lealdade: meus amigos antes de tudo
- Honra: minha palavra é meu laço
- Compaixão: sofro com o sofrimento alheio
- Conhecimento: entender tudo é poder

### Laços (escolha 2)
- Estou perseguindo alguém
- Tenho dívida com alguém
- Estou buscando vendetta
- Devo meu sucesso a alguém
- Sou amigo leal de alguém
- Amo alguém profundamente
- Sou pai/mãe de alguém
- Tenho promessa a cumprir
- Estou fugindo de algo

### Fraquezas (escolha 2)
- Tenho vício (álcool, jogo, drogas)
- Sou ganancioso por dinheiro
- Sou envergonhado secretamente
- Sou covarde sob pressão
- Tenho fobia específica
- Sou preconceituoso contra grupo
- Sou intolerante com crenças diferentes
- Sou vaidoso demais
- Tenho dúvida constante
- Sou rancoroso com inimigos

## GANHO POR ANTECEDENTE

| Ganho | Quantidade |
|-------|-----------|
| Perícias | 2 |
| Idiomas | 1-2 (depende antecedente) |
| Ouro | 10-25 gp (depende antecedente) |
| Equipamento | Lista específica |
| Traços de Personalidade | 2 opções |
| Ideais | 2 opções |
| Laços | 2 opções |
| Fraquezas | 2 opções |

## APLICAÇÃO DE ANTECEDENTE

### No Nível 1
1. Escolha antecedente
2. Ganhe 2 perícias (proficiência)
3. Ganhe idiomas
4. Ganhe equipamento + ouro
5. Defina personalidade, ideais, laços, fraquezas

### Durante Campanha
- Traços podem mudar conforme desenvolvimento
- Ideais podem ser desafiados/reafirmados
- Laços podem evoluir com eventos
- Fraquezas podem ser superadas ou piorar

## Validações

- Antecedente deve estar na lista de 13
- Perícias ganhas: 2 sempre
- Idiomas: validar idiomas existentes
- Equipamento: listar itens
- Ouro: >= 0 gp


## Cálculos

### Ouro Total Inicial
ouro_total = ouro_classe + ouro_antecedente

### Perícias Proficientespericias_proficientes = pericias_classe + pericias_antecedente
(máximo 2 por fonte, sem duplicatas)


## Exemplo: Nobre Paladino

### Setup: Paladino com Antecedente Nobre

**Perícias Paladino**: Insight, Medicine
**Perícias Nobre**: Insight (já tem), Persuasion (nova)
**Perícias Finais**: Insight, Medicine, Persuasion

**Idiomas**: Comum + 1 extra (Nobre)
**Ouro Classe**: 5d4 × 10 = 80 gp (ex)
**Ouro Nobre**: +25 gp
**Ouro Total**: 105 gp

**Equipamento**:
- Classe: Arma marcial, armadura média, escudo
- Nobre: Roupa fina, brasão familiar

**Traços**:
- Personalidade: "Sou honesto demais" / "Sou cínico"
- Ideais: "Justiça acima de tudo" / "Lealdade à minha casa"
- Laços: "Devo meu sucesso ao meu pai" / "Estou fugindo do escândalo familiar"
- Fraquezas: "Sou vaidoso demais" / "Sou intolerante com riqueza mal usada"

## Referência do Livro
Capítulo 4: Personalidades e Antecedentes | Antecedentes e Traços
