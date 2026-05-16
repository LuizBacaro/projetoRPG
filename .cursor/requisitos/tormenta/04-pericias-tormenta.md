
# FEATURE: Sistema de Perícias Tormenta RPG

## Descrição Breve
Implementar 19 perícias com modificadores automáticos, DCs variáveis e cálculo de bônus por classe/nível.

## Regra Principal
Cada perícia se vincula a uma habilidade core. Bônus = Modificador da Habilidade + Graduações + Bônus de Classe. Teste = 1d20 + Bônus vs. DC.

## Dados/Campos Necessários
- skillId: enum — Uma de 19 perícias (ver lista abaixo)
- skillName: string
- baseAbility: enum — Habilidade vinculada (STR, DEX, CON, INT, WIS, CHA)
- ranks: number — Graduações investidas (0-20)
- classBonus: number — Bônus de classe (0, +2, +4, etc.)
- characterLevel: number — Nível do personagem (1-20)

## As 19 Perícias do Tormenta

| # | Perícia | Habilidade-Chave | Usar sem Graduação? |
|----|---------|------------------|---------------------|
| 1 | Acrobacia | DEX | Não |
| 2 | Adestrar Animais | CHA | Não |
| 3 | Atletismo | STR | Sim |
| 4 | Atuação | CHA | Sim |
| 5 | Cavalgar | DEX | Não |
| 6 | Conhecimento | INT | Não |
| 7 | Cura | WIS | Sim |
| 8 | Diplomacia | CHA | Sim |
| 9 | Enganação | CHA | Sim |
| 10 | Furtividade | DEX | Sim |
| 11 | Identificar Magia | INT | Não |
| 12 | Iniciativa | DEX | Sim (em combate) |
| 13 | Intimidação | CHA | Sim |
| 14 | Intuição | WIS | Sim |
| 15 | Ladinagem | DEX | Não |
| 16 | Obter Informação | CHA | Sim |
| 17 | Ofício | INT | Não |
| 18 | Percepção | WIS | Sim |
| 19 | Sobrevivência | WIS | Sim |

## Cálculo do Bônus de Perícia

### Exemplo: Ladino, Nível 5, Ladinagem
- Destreza: 16 → Mod +3
- Graduações: 5
- Bônus de Classe: +3 (perícia de classe para Ladino)
- **Bônus Total**: +3 + 5 + 3 = +11
- Teste para abrir fechadura DC 15: 1d20 + 11 (precisa >= 4 no d20)

## Detalhes por Perícia

### 1. ACROBACIA (DEX)
- **Uso**: Saltos, piruetas, movimento em terreno difícil
- **DC Básico**: 10 (terreno normal), 15 (acelerado), 20 (perseguição)
- **Falha Crítica**: Cai ou sofre 1d6 dano
- **Sem Graduação**: Não, aplica penalidade -4

### 2. ADESTRAR ANIMAIS (CHA)
- **Uso**: Treinar, acalmar, montar criatura
- **DC Básico**: 10 (animal domesticado), 15 (selvagem), 20 (perigoso)
- **Sem Graduação**: Não
- **Componente**: Tempo (dias/semanas)

### 3. ATLETISMO (STR)
- **Uso**: Nadar, escalar, saltar, arremessar
- **DC Básico**: 10 (básico), 15 (desafiador), 20 (heroico)
- **Sem Graduação**: Sim, usa STR mod direto
- **Especial**: Cansaço físico em falhas críticas

### 4. ATUAÇÃO (CHA)
- **Uso**: Atuar, cantar, dançar, disfarçar
- **DC Básico**: 10 (improviso simples), 15 (convinção), 20 (completo engano)
- **Sem Graduação**: Sim
- **Nota**: Oposição é INT do observador para "enganação"

### 5. CAVALGAR (DEX)
- **Uso**: Montar, controlar cavalgadura, manobras em combate
- **DC Básico**: 10 (deslocamento normal), 15 (combate), 20 (terreno perigoso)
- **Sem Graduação**: Não, aplica penalidade -4
- **Especial**: Falha em combate derruba cavaleiro

### 6. CONHECIMENTO (INT)
- **Uso**: Lembrar fatos, história, magia, natureza, nobresa, alquimia
- **DC Básico**: 10 (comum), 15 (especializado), 20 (obscuro)
- **Sem Graduação**: Não (DC aumenta +5 sem graduação)
- **Subtipo**: Escolher especialização no nível (História, Magia, Natureza, etc.)

### 7. CURA (WIS)
- **Uso**: Diagnosticar doença, parar sangramento, curar ferimento
- **DC Básico**: 10 (primeiro socorro), 15 (doença), 20 (veneno)
- **Sem Graduação**: Sim, apenas primeiros socorros
- **Especial**: Parar sangramento salva 1 vida/rodada

### 8. DIPLOMACIA (CHA)
- **Uso**: Negociar, convencer, mudar atitude NPC
- **DC Básico**: 10 (receptivo), 15 (neutro), 20 (hostil)
- **Sem Graduação**: Sim
- **Tabela de Atitude**: Hostil → Indiferente → Receptivo → Amigável

### 9. ENGANAÇÃO (CHA)
- **Uso**: Mentir, blefar, disfarçar verdade
- **DC Básico**: Oposto a Intuição do alvo
- **Sem Graduação**: Sim
- **Bônus**: +1 por meia-verdade, +3 por coisa plausível

### 10. FURTIVIDADE (DEX)
- **Uso**: Esconder-se, mover-se silenciosamente, emboscar
- **DC Básico**: 10 (escuridão), 15 (à luz do dia), 20 (em aberto)
- **Sem Graduação**: Sim
- **Oposição**: Percepção do observador
- **Emboscada**: Tiro furtivo ignora armadura parcialmente

### 11. IDENTIFICAR MAGIA (INT)
- **Uso**: Reconhecer magia, identificar tipo de feitiço, ler magia
- **DC Básico**: 10 (magia 1º nível), +2 por nível de magia
- **Sem Graduação**: Não
- **Especial**: Precisa de contato ou visão do efeito mágico

### 12. INICIATIVA (DEX)
- **Uso**: Determinar ordem de ação em combate
- **Cálculo**: 1d20 + DEX mod + Bônus de Classe (se houver)
- **Sem Graduação**: Sim, usa DEX mod direto
- **Tipo**: Não é perícia tradicional, mas segue mesma mecânica

### 13. INTIMIDAÇÃO (CHA)
- **Uso**: Assustar, coagir, intimidar inimigo
- **DC Básico**: 10 (inferior em poder), 15 (igual), 20 (superior)
- **Sem Graduação**: Sim
- **Duração**: Efeito dura cena ou até ação contrária

### 14. INTUIÇÃO (WIS)
- **Uso**: Detectar mentira, ler intenções, notar malícia
- **DC Básico**: Oposto a Enganação do alvo
- **Sem Graduação**: Sim
- **Especial**: Sucesso em 5+ pontos revela mentira

### 15. LADINAGEM (DEX)
- **Uso**: Abrir fechaduras, desativar armadilhas, batedores de bolsa
- **DC Básico**: 10 (fechadura simples), 15 (complexa), 20 (magistral)
- **Sem Graduação**: Não, aplica penalidade -4
- **Ferramenta**: Precisa kit de ladinagem
- **Falha Crítica**: Prende ferramenta ou ativa armadilha

### 16. OBTER INFORMAÇÃO (CHA)
- **Uso**: Coletar rumores, suborno, interrogatório
- **DC Básico**: 10 (informação comum), 15 (secreta), 20 (muito confidencial)
- **Sem Graduação**: Sim, mas com penalidade -2
- **Componente**: Tempo e dinheiro (suborno)

### 17. OFÍCIO (INT)
- **Uso**: Criar objeto, consertar equipamento, trabalho manual
- **DC Básico**: 10 (comum), 15 (intrincado), 20 (magistral)
- **Sem Graduação**: Não
- **Especificar**: Ofício do Vidro, Ofício do Metal, Ofício Alquímico, etc.
- **Componente**: Tempo e materiais

### 18. PERCEPÇÃO (WIS)
- **Uso**: Notar detalhes, buscar, ouvir sons, procurar emboscadas
- **DC Básico**: 10 (óbvio), 15 (fácil), 20 (bem escondido)
- **Sem Graduação**: Sim
- **Passivo**: PC = 10 + WIS mod + graduações (não testa, usa valor fixo)

### 19. SOBREVIVÊNCIA (WIS)
- **Uso**: Seguir trilhas, acampar, caçar, navegar, previsão climática
- **DC Básico**: 10 (trilha fresca), 15 (antiga), 20 (apagada)
- **Sem Graduação**: Sim
- **Componente**: Tempo (horas/dias)

## Tabela de DCs Padrão (Referência)

| Dificuldade | DC | Descrição |
|-------------|-----|-----------|
| Muito Fácil | 5 | Até um iniciante consegue |
| Fácil | 10 | Nível de treinamento básico |
| Moderado | 15 | Treinamento competente |
| Difícil | 20 | Altamente treinado/experiente |
| Muito Difícil | 25 | Desafiador para o melhor |
| Quase Impossível | 30 | Apenas heróis conseguem |

## Bônus de Classe por Perícia (Exemplo: Ladino)

Algumas classes recebem +2 ou +3 em certas perícias:
- **Ladino**: Acrobacia, Furtividade, Ladinagem, Obter Informação (+2-3)
- **Bardo**: Atuação, Diplomacia, Obter Informação (+2-3)
- **Ranger**: Cavalgar, Percepção, Sobrevivência (+2-3)
- **Clérigo**: Cura, Conhecimento (Religião) (+2)

## Validações
- Perícia deve estar em enum de 19
- Graduações: 0-20 (máximo)
- Teste: resultado 1d20 + bônus total >= DC
- Se "Sem Graduação" = Não e ranks = 0: penalidade -4 ou falha automática

## Cálculos
- **Bônus**: Mod Habilidade + Graduações + Bônus Classe
- **Teste Perícia**: 1d20 + Bônus
- **Passivo (Percepção)**: 10 + Bônus (para PNJs procurarem escondidos)
- **Oposição**: Perícias opostas (Enganação vs. Intuição) usam 1d20 de cada lado

## Exemplo Completo: Teste de Ladinagem

### Cenário: Ladino abrindo baú trancado (DC 15)
- **Personagem**: Ladino humano, nível 5
- **Destreza**: 16 → Mod +3
- **Ladinagem Graduações**: 5 (investiu todos os pontos nela)
- **Bônus de Classe**: +3 (Ladino é classe de perícia)
- **Bônus Total**: +3 + 5 + 3 = **+11**
- **Teste**: 1d20 + 11
  - Precisa rolar 4 ou mais no d20 (4 + 11 = 15)
  - Chance de sucesso: 85%

### Falha Crítica (1 natural):
- 1 + 11 = 12 (falhou)
- Ferramenta fica presa
- Inimigos ouvem barulho

## Referência do Livro
Capítulo 4: Perícias | Descrições detalhadas de cada perícia com DCs e usos
