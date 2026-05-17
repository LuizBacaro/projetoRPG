# FEATURE: Sistema de Talentos e Feitos D&D 3.5

## Descrição Breve
Implementar Talentos (Feats) como opções de customização que aumentam habilidades, desbloqueiam capacidades ou fornecem bônus especiais. Personagem ganha 1 Talento a cada 3 níveis (1, 3, 6, 9, 12, 15, 18).

## Regra Principal
Talentos são ganhos nos níveis 1, 3, 6, 9, 12, 15, 18, 20. Cada Talento requer pré-requisitos (nível mínimo, perícias, habilidades). Pode ser geral ou específico de classe. Efeito varia: +2 bonus, nova capacidade, múltiplos usos por dia.

## Dados/Campos Necessários

### Talento
- talentoid: string
- nome: string
- descricao: string
- categoria: enum — "Combate" | "Perícia" | "Magia" | "Metamagia" | "Item" | "Geral"
- prerequisitos: string[] (pré-requisitos)
- beneficio: string (descrição do bônus)
- especial: string (uso especial, se aplicável)
- nivelMinimo: number
- requisitoClasse: string[] (opcional)
- requisitoRaca: string[] (opcional)
- requisitoPericia: object (perícia: graduações mínimas)

## Ganho de Talentos por Nível

| Nível | Talento |
|-------|---------|
| 1 | ✓ (1º talento) |
| 3 | ✓ |
| 6 | ✓ |
| 9 | ✓ |
| 12 | ✓ |
| 15 | ✓ |
| 18 | ✓ |
| 20 | ✓ (último talento) |

**Total**: 7 talentos por personagem (níveis 1-20)

## TALENTOS PRINCIPAIS

### Talentos de Combate

| Talento | Pré-requisito | Benefício |
|---------|---------------|-----------|
| Arma Focada | BAB +1, proficiência arma | +1 ataque com arma específica |
| Arma Especializada | BAB +4, Arma Focada | +2 dano com arma específica |
| Ataque Múltiplo | BAB +5 | Ataque bônus com segunda arma |
| Defesa Aprimorada | BAB +1 | +1 AC quando defende (ação bônus) |
| Derrubada Aprimorada | BAB +1, Atletismo 3 | +2 em testes derrubar |
| Desarmamento Aprimorado | BAB +1 | Desarma sem -4 penalidade |
| Evasão | DEX 13+, Acrobacia 3 | Reflexo = sem dano |
| Foco em Perícia | — | +3 em uma perícia específica |
| Golpe Atordoante | BAB +8, CON 13+ | Dano extra 1d6 se acertar |
| Lança em Movimento | STR 13+, BAB +1 | Atacar com lança enquanto se move |
| Toque de Oportunidade | CHA 13+, BAB +1 | Ataque bônus contra flanqueado |

### Talentos de Perícia

| Talento | Pré-requisito | Benefício |
|---------|---------------|-----------|
| Acrobacia Aprimorada | Acrobacia 3 | +2 em testes Acrobacia |
| Adestrador | Adestrar Animais 3 | Treina animais mais rápido |
| Combatente Versátil | BAB +3 | Proficiência com arma adicional |
| Diplomacia Aprimorada | Diplomacia 3 | +2 em testes Diplomacia |
| Especialista em Ladinagem | Ladinagem 3 | +2 em testes Ladinagem |
| Foco em Conhecimento | Conhecimento (tipo) 3 | +3 em Conhecimento específico |
| Identificador Aprimorado | Identificar Magia 3 | Identifica magia automaticamente |
| Línguas Extras | INT 13+ | Aprende 3 idiomas extras |
| Mapeador | Conhecimento (Geografia) 3 | +2 em navegação |
| Ninja | Furtividade 6 | +4 em Furtividade, indetectável |
| Observador | Observação 3 | Não surpreendido |
| Orador Inspirador | Oratória 3 | Aliados ganham +1 moral |
| Rastreador | Sobrevivência 3 | +2 em rastreamento |
| Renascença | INT 13+ | Pode usar perícia adicional como treinado |

### Talentos de Magia

| Talento | Pré-requisito | Benefício |
|---------|---------------|-----------|
| Aprimorar Conjuração | Magia | +1 DC das próprias magias |
| Conjuração em Armadura | Proficiência armadura | Pode conjurar em armadura |
| Espaço Aprimorado | Spellcraft 5 | +1 espaço feitiço por nível |
| Foco em Escola | Mago ou Feiticeiro | +1 DC com escola específica |
| Mágica Ampliada | Metamagia | Duplica alcance da magia |
| Mágica Apressada | Metamagia | Reduz tempo execução em 1 ação |
| Mágica Quieta | Metamagia | Sem componente verbal |
| Mágica Sombra | Metamagia | Sem componente somático |
| Resistência à Magia | WIS 13+ | Aumenta resistência magia +2 |
| Spell Penetration | Spellcraft 3 | +2 vs. resistência magia |

### Talentos Gerais

| Talento | Pré-requisito | Benefício |
|---------|---------------|-----------|
| Aumento de Habilidade | — | +2 em uma habilidade (pode repetir) |
| Boa Saúde | — | +1 PV por nível |
| Esquiva | DEX 13+ | +1 AC reflex |
| Fé Fervorosa | CHA 13+ | Bônus +1 em salvação vontade |
| Força Extra | STR 13+ | +2 dano com armas STR |
| Iniciativa Aprimorada | DEX 13+ | +4 iniciativa |
| Inspiração | CHA 13+ | Rolar 1d6 extras uma vez/dia |
| Liderança | CHA 13+, nível 6+ | Recruta companheiros |
| Magia de Ferro | CON 13+ | -1 CD contra magia/dia |
| Morte Súbita | STR 13+ | Crítico = morte automática |
| Reflexos Rápidos | DEX 13+ | +2 em evasão |
| Resiliência | CON 13+ | Salva contra veneno +4 |
| Tenacidade | CON 13+, nível 6+ | Sobrevive após morte física |
| Último Suspiro | — | +5 teste quando HP < 0 |
| Versatilidade de Arma | BAB +1 | Proficiência arma adicional |

## Talentos de Metamagia

Aumentam nível de magia (máximo +4):

| Talento | Custo | Efeito |
|---------|-------|--------|
| Mágica Ampliada | +1 nível | Duplica alcance |
| Mágica Apressada | +1 nível | Ação bônus ao invés de ação padrão |
| Mágica Quieta | +1 nível | Sem componente verbal |
| Mágica Sombra | +1 nível | Sem componente somático |
| Mágica Flexível | +2 níveis | Muda alvos após lançar |
| Mágica Maximizada | +3 níveis | Máximo dano (20 no dado) |
| Mágica Potencializada | +1 nível | Reroll de salvação: toma pior |

## Pré-requisitos Comuns

| Pré-requisito | Tipo |
|---------------|------|
| BAB +X | Nível mínimo baseado em BAB |
| STR/DEX/CON/INT/WIS/CHA 13+ | Atributo mínimo |
| Perícia X 3+ | Perícia com 3+ graduações |
| Proficiência arma | Tem treinamento com arma |
| Nível X+ | Nível mínimo do personagem |
| Talento (outro) | Requer talento anterior |

## Validações

- Talento deve estar na lista
- Pré-requisitos checados (atributos, nível, perícias)
- Nível ganho: 1, 3, 6, 9, 12, 15, 18
- Máximo talentos: 7 (níveis 1-20)
- Não pode repetir talento (exceto Aumento de Habilidade)

## Cálculos

### Bônus Talento
- Alguns talentos adicionam bônus direto (+1 a +4)
- Alguns desbloqueiam novas capacidades
- Alguns multiplicam efeitos existentes (crítico ×2)

### Aumento de Habilidade
habilidadeA += 2
(pode ser repetido em talentos diferentes)


## Exemplo: Guerreiro com Talentos

### Setup: Guerreiro nível 9, STR 16, DEX 14

**Talentos Ganhos**:
- **Nível 1**: Foco em Arma (Espada Longa)
  - Pré-req: BAB +1 ✓
  - Efeito: +1 ataque com Espada Longa

- **Nível 3**: Arma Especializada
  - Pré-req: BAB +4, Foco em Arma ✓
  - Efeito: +2 dano com Espada Longa

- **Nível 6**: Força Extra
  - Pré-req: STR 13+ ✓
  - Efeito: +2 dano com armas STR

- **Nível 9**: Defesa Aprimorada
  - Pré-req: BAB +1 ✓
  - Efeito: +1 AC quando defende

**Resultado Final**:
- Ataque Espada Longa: BAB +6 + 1 (talento) + 3 (STR) = +10
- Dano Espada Longa: 1d8 + 3 (STR) + 2 (talento nível 3) + 2 (talento nível 6) = 1d8 + 7

## Referência do Livro
Capítulo 5: Talentos | Pré-requisitos, Benefícios, Descrições
