# FEATURE: Sistema de Talentos e Feitos D&D 5E

## Descrição Breve
Implementar Feitos (Feats) como opções de customização que aumentam habilidades, adicionam bônus especiais, ou desbloqueiam capacidades únicas. Personagem ganha 1 Feat a cada 4 níveis (4, 8, 12, 16, 19).

## Regra Principal
Feitos são opcionais no nível 1 e obrigatórios a cada aumento de habilidade (nível 4, 8, 12, 16, 19). Cada Feat adiciona uma capacidade nova ou melhora existente. Pode aumentar habilidade em +2 (ou +1/+1 em duas) ao invés de pegar Feat. Máximo 1 Feat por nível de aumento.

## Dados/Campos Necessários

### Feat
- feitId: string
- nome: string
- descricao: string
- prerequisitos: string[] (ex: "Força 13+", "Bônus Proficiência +2")
- tipoBonus: enum — "Atributo" | "Combate" | "Magia" | "Perícia" | "Utilidade"
- bonusEspecial: object (variável por Feat)
- requisitoNivel: number (nível mínimo, default 1)
- requisitoClasse: string[] (opcional, ex: ["Guerreiro"])
- requisitoRaca: string[] (opcional)

## FEITS PRINCIPAIS POR CATEGORIA

### Feitos de Atributo

| Feat | Pré-requisito | Bonus |
|------|---------------|-------|
| Ability Score Improvement | — | +2 um atributo ou +1 dois atributos |
| Alert | — | +5 iniciativa, não surpreso |
| Athlete | — | +1 STR/DEX, escalada/natação +1.5m |
| Resilient | — | +1 atributo, salvo prof em um tipo |
| War Caster | Spellcaster | advantage em concentração, somático sem mão |

### Feitos de Combate

| Feat | Pré-requisito | Efeito |
|------|---------------|--------|
| Archery | — | +2 ataque com arco |
| Blade Master | — | +2 dano com espadas |
| Charger | — | +5 dano após movimento + ataque |
| Defensive Duelist | DEX 13+ | reação AC +dex (duelo) |
| Dual Wielder | — | AC +1 duas armas, draw bonus |
| Great Weapon Master | STR 13+ | -5 ataque +10 dano com 2 mãos |
| Heavy Armor Master | — | -3 dano físico, STR +1 |
| Martial Adept | — | 2 manobras battle master |
| Medium Armor Master | DEX 13+ | AC no escudo sem penalidade DEX |
| Mounted Combatant | — | +1 AC montado, ataque extra |
| Polearm Master | — | ataque bônus com lança, reação |
| Sentinel | — | reação ataque, reduz movimento |
| Sharpshooter | — | -5 ataque +10 dano, sem desvantagem alcance |
| Two-Weapon Fighting | — | dano +mod com segunda arma |

### Feitos de Magia

| Feat | Pré-requisito | Efeito |
|------|---------------|--------|
| Eldritch Sight (Bruxo) | Spellcasting | ação bônus detectar magia a vontade |
| War Caster | Spellcasting | +advantage concentração, sem mão |
| Resilient (INT/WIS/CHA) | — | salvado prof em magia |
| Telekinetic | CHA 13+ | misterioso mágico +1 CHA |
| Telepathic | WIS 12+ | telepatia, +1 WIS |
| Magic Initiate | — | 2 truques + 1 feitiço 1º nível uma vez |
| Ritual Caster | INT/WIS 13+ | lance ritual sem espaço |
| Spell Sniper | Spellcasting | dano +1d6, alcance dobrado |

### Feitos de Perícia

| Feat | Pré-requisito | Efeito |
|------|---------------|--------|
| Acrobatics Expert | — | proficiência Acrobacia, +1 DEX |
| Animal Handler | — | proficiência Anim Handling |
| Arcana Scholar | — | proficiência Arcana |
| Athletics Trainer | STR 13+ | proficiência Athletics |
| Deception Expert | — | proficiência Deception |
| History Scholar | — | proficiência History |
| Insight Savant | — | proficiência Insight |
| Intimidation Master | — | proficiência Intimidation |
| Investigation Expert | — | proficiência Investigation |
| Medicine Expert | — | proficiência Medicine |
| Nature Scholar | — | proficiência Nature |
| Perception Expert | — | proficiência Perception |
| Performance Expert | — | proficiência Performance |
| Persuasion Master | CHA 13+ | proficiência Persuasion |
| Religion Scholar | — | proficiência Religion |
| Sleight of Hand | DEX 13+ | proficiência Sleight of Hand |
| Stealth Master | DEX 13+ | proficiência Stealth |
| Survival Trainer | WIS 13+ | proficiência Survival |

### Feitos de Utilidade

| Feat | Pré-requisito | Efeito |
|------|---------------|--------|
| Actor | CHA 13+ | +1 CHA, vantagem Performance/Deception |
| Inspiring Leader | CHA 13+ | +3 temp HP até 6 aliados |
| Keen Mind | INT 13+ | nunca se perde, recordação perfeita |
| Linguist | INT 13+ | +1 INT, aprenda 3 idiomas |
| Lightly Armored | — | proficiência armadura leve + escudo |
| Lucky | — | 3× reroll 1d20 por descanso longo |
| Moderately Armored | DEX/STR 13+ | proficiência armadura média + escudo |
| Observant | INT/WIS 13+ | +1 INT/WIS, leia lábios, veja até 1km |
| Polearm Master | — | reação ataque com lança |
| Resilient | — | +1 atributo, salvado prof |
| Savage Attacker | STR/DEX 13+ | reroll dano ataque 1× por turno |
| Sentinel | DEX 13+ | reação ataque ao mover, reduz mov |
| Tavern Brawler | STR/CON 13+ | proficiência armas improvisadas |
| Tough | — | +2 HP por nível |
| Weapon Master | — | +1 atributo, proficiência 4 armas |

## GANHO DE FEITOS POR NÍVEL

| Nível | Ação |
|-------|------|
| 1 | Nenhum (ou aumentar atributo) |
| 4 | +1 Feat ou +2 atributo |
| 8 | +1 Feat ou +2 atributo |
| 12 | +1 Feat ou +2 atributo |
| 16 | +1 Feat ou +2 atributo |
| 19 | +1 Feat ou +2 atributo |

## MULTICLASSE (OPCIONAL)

### Requisitos Multiclasse
- Nível 2+
- Todos os atributos >= 13
- Abandonar habilidades da classe anterior (BAB, salvados, proficiências)
- Ganhar proficiências da nova classe

### Exemplo Multiclasse
- Guerreiro nível 3 → Mago nível 2
- Mantém HP de Guerreiro
- Ganha espaços feitiço Mago nível 2
- Perde Ataque Extra Guerreiro

## VARIANTES E CASA RULES

### Variante: Feitos no Nível 1
Alguns GMs permitem 1 Feat no nível 1 além do método padrão de construção.

### Variante: Feitos Expandidos
Adicionar Feits de fonte externa (Xanathar's Guide, Tasha's Cauldron, etc.).

## INTERAÇÃO FEITS × CLASSES

### Guerreiro
- Feitos de Combate favorecem muito
- Great Weapon Master, Sentinel, Sharpshooter

### Mago
- Feitos de Magia prioritários
- War Caster, Magic Initiate, Ritual Caster

### Clérigo
- War Caster, Resilient (força de magia)
- Medium Armor Master (sem penalidade AC)

### Paladino
- Great Weapon Master, Two-Weapon Fighting, Mounted Combatant
- War Caster (concentração feitiços)

### Ladino
- Sentinel, Sharpshooter, Dual Wielder
- Alert (iniciativa)

## Validações

- Feat deve estar na lista
- Pré-requisitos atendidos (atributos, nível)
- Nível de obtenção: 4, 8, 12, 16, 19 (ou 1 variante)
- Máximo 1 Feat por "aumento de atributo"
- Não pode pegar Feat incompatível (proficiência armadura pesada + Medium Armor Master)

## Cálculos

### Atributo Improvement
habilidadeA += 2
OU
habilidadeA += 1
habilidadeB += 1

### Bônus Automático
Alguns Feats adicionam bônus diretos:
- +1 a +2 em atributo
- +1 a +5 em teste específico
- Vantagem em salvação
- Proficiência periférica

## Exemplo: Guerreiro com Feats

### Guerreiro Humano, Nível 12

**Nível 1**: Aumenta STR +2 (16 → 18)
**Nível 4**: Pega Feat Great Weapon Master
- Pré-req: STR 13+ ✓
- Efeito: -5 ataque, +10 dano com 2 mãos

**Nível 8**: Pega Feat Sentinel
- Efeito: reação ataque quando inimigo sai alcance

**Nível 12**: Aumenta CON +2 (14 → 16)

**Resultado Final**:
- STR 18 (mod +4)
- CON 16 (mod +3)
- 2 Feats poderosos de combate

## Referência do Livro
Capítulo 6: Opções de Personalização | Feits e Multiclasse
