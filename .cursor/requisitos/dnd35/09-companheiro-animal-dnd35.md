# Companheiro Animal - Regras Completas D&D 3.5

## Sumário

1. [Quem Pode Ter Companheiro Animal](#quem-pode)
2. [Seleção do Companheiro](#seleção)
3. [Ganho de Dados de Vida](#hd-bônus)
4. [Bônus de Atributos](#atributos)
5. [Armadura Natural](#armadura)
6. [Estatísticas de Combate](#combate)
7. [Talentos](#talentos)
8. [Perícias](#perícias)
9. [Truques Bônus](#truques)
10. [Habilidade Link](#link)
11. [Vínculo Compartilhado](#vínculo)
12. [Habilidades Especiais](#habilidades)
13. [Restrições e Regras](#restrições)
14. [Tabela de Progressão](#tabela)
15. [Exemplos de Cálculo](#exemplos)

---

## 1. Quem Pode Ter Companheiro Animal {#quem-pode}

**Classes beneficiárias:**

- **Druida**: Recebe um companheiro animal no 1º nível de classe
  - Nível efetivo = Nível de Druida (total)
  - Pode atrair um novo companheiro em 24 horas após morte do anterior

- **Ranger**: Recebe a habilidade no 4º nível
  - Nível efetivo = Nível de Ranger - 3
  - Exemplos:
    - Ranger 4 = Nível efetivo 1
    - Ranger 7 = Nível efetivo 4
    - Ranger 10 = Nível efetivo 7

**Pré-requisitos:**
- Manter conduta alinhada com sua classe
- Druidas devem manter neutralidade (certos alinhamentos podem perder o vínculo)
- O companheiro deve ser escolhido de uma lista oficial

---

## 2. Seleção do Companheiro {#seleção}

**Lista de espécies permitidas (nível inicial):**

| Tipo | Espécies |
|------|----------|
| **Terrestres** | Texugo (Badger), Camelo (Camel), Rato Gigante (Dire Rat), Cão (Dog), Cão de Montaria (Riding Dog), Cavalo - Leve ou Pesado (Horse - Light/Heavy), Lobo (Wolf), Pônei (Pony) |
| **Aéreos** | Águia (Eagle), Falcão (Hawk), Coruja (Owl) |
| **Répteis** | Serpente Pequena (Small Viper), Serpente Média (Medium Viper) |
| **Aquáticos** | Golfinho (Porpoise), Tubarão Médio (Medium Shark), Lula (Squid) |

**Requisitos de seleção:**
- Animal deve ser um exemplar "completamente típico" de sua espécie
- Sem mutações mágicas no momento da aquisição
- Escolha é permanente até morte ou libertação voluntária
- Animais mais poderosos podem ser obtidos em níveis superiores (com redutores ao nível efetivo)

---

## 3. Ganho de Dados de Vida (HD Bônus) {#hd-bônus}

**Fórmula:**

$$HD_{Bônus} = \left\lfloor \frac{\text{Nível Efetivo}}{3} \right\rfloor$$

**Tabela de progressão:**

| Nível Efetivo | HD Bônus | Exemplo |
|---------------|----------|---------|
| 1-2 | +0 | Druida 1-2 ganha 0 HD |
| 3-5 | +2 | Druida 3-5 ganha 2 HD |
| 6-8 | +4 | Druida 6-8 ganha 4 HD |
| 9-11 | +6 | Druida 9-11 ganha 6 HD |
| 12-14 | +8 | Druida 12-14 ganha 8 HD |
| 15-17 | +10 | Druida 15-17 ganha 10 HD |
| 18+ | +12 | Druida 18+ ganha 12 HD |

**Cálculo total de HD:**
- `HD Total = HD Original + HD Bônus`
- Cada HD bônus é um `d8` (dado de 8 faces)
- Aplicar modificador de Constituição do animal em cada HD

> **Exemplo:** Um lobo (2 HD originais) com druida nível 7 recebe +4 HD bônus = 6 HD totais

---

## 4. Bônus de Atributos {#atributos}

**Distribuição por nível efetivo:**

| Nível Efetivo | Distribuição |
|---------------|--------------|
| 1-2 | +2 em um atributo à escolha |
| 3-5 | +2 em dois atributos à escolha |
| 6-8 | +3 em dois atributos + +2 em um atributo |
| 9+ | +3 em três atributos à escolha |

**Atributos do animal:**
- Força (For/Str)
- Destreza (Des/Dex)
- Constituição (Con/Con)
- Inteligência (Int/Int)
- Sabedoria (Sab/Wis)
- Carisma (Car/Cha)

> **Nota:** Geralmente é vantajoso aumentar **Força**, **Destreza** e **Constituição** para melhorar combate e sobrevivência.

---

## 5. Armadura Natural {#armadura}

**Fórmula:**

$$Bônus_{AN} = \left\lfloor \frac{\text{Nível Efetivo}}{3} \right\rfloor + 1$$

**Tabela de progressão:**

| Nível Efetivo | Bônus de Armadura Natural |
|---------------|--------------------------|
| 1-2 | +1 |
| 3-5 | +2 |
| 6-8 | +4 |
| 9-11 | +4 |
| 12-14 | +5 |
| 15-17 | +6 |
| 18+ | +6 |

**Aplicação:**
- Bônus somado à CA (Class Armor) do animal
- Refleti a proteção mágica do vínculo
- Cálculo: `CA = 10 + Bônus AN + Modificador de Destreza`

---

## 6. Estatísticas de Combate {#combate}

### 6.1 Bônus de Ataque Base (BAB)

$$BAB = HD_{Total}$$

O BAB é igual ao número total de Dados de Vida (original + bônus).

**Exemplo:** Lobo com 6 HD totais tem BAB +6

### 6.2 Testes de Resistência

**Fortitude:**
$$Fort = 2 + \left\lfloor \frac{HD_{Total}}{2} \right\rfloor$$

**Reflexos:**
$$Ref = 2 + \left\lfloor \frac{HD_{Total}}{2} \right\rfloor$$

**Vontade:**
$$Von = 1 + \left\lfloor \frac{HD_{Total}}{3} \right\rfloor$$

**Tabela de exemplo (Lobo com HD originais de 2):**

| HD Total | BAB | Fort | Ref | Von |
|----------|-----|------|-----|-----|
| 2 | +2 | +3 | +3 | +1 |
| 4 | +4 | +4 | +4 | +2 |
| 6 | +6 | +5 | +5 | +3 |
| 8 | +8 | +6 | +6 | +3 |
| 10 | +10 | +7 | +7 | +4 |
| 12 | +12 | +8 | +8 | +5 |

---

## 7. Talentos {#talentos}

**Fórmula de ganho de talentos:**

$$Total_{Talentos} = 1 + \left\lfloor \frac{HD_{Total} - 1}{3} \right\rfloor$$

**Progressão:**

| HD Total | Talentos |
|----------|----------|
| 1 | 1 |
| 2 | 1 |
| 3 | 1 |
| 4 | 2 |
| 5 | 2 |
| 6 | 2 |
| 7 | 3 |
| 8 | 3 |
| 9 | 3 |
| 10+ | +1 a cada 3 HD |

**Talentos disponíveis:**
- Alertness (Atenção)
- Evasion (Evasão)
- Improved Evasion (Evasão Melhorada)
- Dodge (Esquiva)
- Weapon Finesse (Arma Aprimorada)
- Power Attack (Ataque Potente)
- Cleave (Golpe Limpador)
- Great Cleave (Golpe Limpador Maior)

> **Nota:** Animais têm restrições a talentos que requerem linguagem ou inteligência superior a 3.

---

## 8. Perícias {#perícias}

**Pontos de perícia por HD:**

$$Pontos = (2 + Mod_{Int}) \times \text{multiplicador}$$

Onde:
- `2 + Mod_Int` = pontos básicos por HD (mínimo 1)
- No **1º HD**: multiplicador = 4 (quadruplicado)
- Nos **HD subsequentes**: multiplicador = 1

**Exemplo:**
- Animal com INT 2 (modificador -4, mínimo 1):
  - 1º HD: 4 × 1 = 4 pontos
  - 2º HD: 1 × 1 = 1 ponto
  - 3º HD: 1 × 1 = 1 ponto
  - Total em 3 HD: 6 pontos

**Perícias permitidas para animais:**
- Acrobacias (Acrobatics)
- Furtividade (Stealth)
- Escalar (Climb)
- Natação (Swim)
- Ouvir (Listen)
- Observar (Spot)
- Sobrevivência (Survival)
- Equilíbrio (Balance)

> **Restrição:** Perícias que exigem mãos humanas ou raciocínio abstrato ficam indisponíveis.

---

## 9. Truques Bônus {#truques}

**Truques aprendidos automaticamente (não contam para o limite máximo):**

| Nível Efetivo | Truques Bônus |
|---------------|---------------|
| 1 | 1 truque |
| 4+ | 2 truques |
| 7+ | 3 truques |
| 10+ | 4 truques |
| 13+ | 5 truques |
| 16+ | 6 truques |
| 19+ | 7 truques |

**Truques comuns (exemplos):**
- Sit (Senta)
- Stay (Fica)
- Come (Vem)
- Down (Deita)
- Heel (Anda junto)
- Fetch (Busca)
- Guard (Guarda)
- Attack (Ataca - requer Handle Animal DC 20)

**Truques adicionais:**
- O mestre pode ensinar novos truques através de teste de Adestrar Animais (Handle Animal)
- Limite máximo de truques = Inteligência do animal
- Truques bônus **ignoram** este limite

---

## 10. Habilidade Link (Elo) {#link}

**Características:**

- O animal obedece a comandos do mestre **sem necessidade de testes** de Handle Animal para truques que já conhece
- Dar uma instrução é uma **ação de movimento** para o mestre
- Funciona através de **entendimento empático**, mesmo sem linguagem comum verbal
- Alcance: até **1,5 quilômetro** de distância
- Não requer linguagem falada ou escrita

**Efeitos mecânicos:**

- Truques conhecidos: sucesso automático em comandos do mestre
- Truques desconhecidos: requerem teste normal de Handle Animal (DC varia)
- Trabalho independente: animal pode executar tarefas sozinho
- Coordenação: animal e mestre agem em perfeita sincronia

> **Não funciona:** Em combate descontrolado ou quando o animal está em pânico (requer teste em tais situações).

---

## 11. Vínculo Compartilhado {#vínculo}

**Capacidades:**

1. **Compartilhamento de Magias**
   - Qualquer magia conjurada pelo mestre em si mesmo afeta o animal
   - Animal deve estar a até **1,5 metro** no momento da conjuração
   - Exemplos: *Bless*, *Shield*, *Protection from Evil*

2. **Magias Benéficas**
   - Mestre pode conjurar magias com alvo "Você" no companheiro
   - Funciona como magia de toque
   - Exemplos: *Cure Wounds*, *Heal*

3. **Itens de Consumo**
   - Mestre pode dividir poção de cura com o animal
   - Efeito é dividido igualmente entre ambos
   - Exemplos: *Potion of Healing*, *Elixir of Health*

4. **Resistência Mágica**
   - Animal usa a **maior** resistência entre:
     - Resistência do mestre
     - Resistência do animal
   - Aplicável em magias compartilhadas

**Limitações:**

- ❌ Não afeta magias com alvo "Criatura" ou "Criatura viva"
- ❌ Não compartilha dano (apenas efeitos benéficos)
- ❌ Animal não ganha bônus do mestre em testes de resistência

---

## 12. Habilidades Especiais {#habilidades}

**Progressão de habilidades por nível efetivo:**

### Nível 1: Link e Vínculo Compartilhado

- Elo telepático básico
- Compartilhamento de magias pessoais
- Obediência sem testes

### Nível 3: Compreensão de Linguagem

- Animal entende o idioma nativo do mestre
- Compreende ordens complexas em linguagem natural
- Não consegue falar, apenas entender

### Nível 5: Comunicação Telepática

- Troca de impressões mentais simples
- Alcance: até 1,5 quilômetro
- Funciona em silêncio absoluto
- Transmissão de emoções e sensações básicas

### Nível 7: Sentidos Aguçados

- **Ver Invisibilidade**: Enxerga criaturas invisíveis
- **Detectar Movimento**: Identifica qualquer movimento num raio de 30 metros
- **Visão Noturna**: Enxerga em escuridão absoluta
- **Olfato Aprimorado**: Rastreia criaturas pela trilha de cheiro

### Nível 9: Compreensão de Idiomas

- Animal compreende **qualquer idioma** falado em sua presença
- Ainda não consegue falar
- Funciona apenas para linguagem falada e gestual

### Nível 11: Falar um Idioma

- Animal ganha capacidade vocal ou gestual de se comunicar em uma língua
- Escolher qual idioma no momento do nível
- Pode mudar o idioma a cada nova sessão (a critério do mestre)

### Nível 13: Inumanidade

- Imunidade a efeitos de envelhecimento (age normal, mas não envelhece magicamente)
- Continua envelhecendo naturalmente se não for ressuscitado
- Não afeta morte natural por velhice

### Nível 15: Comunhão Distante

- Mestre pode ver através dos olhos do animal (como *Scrying*)
- Alcance: qualquer distância no mesmo plano
- Duração: concentração do mestre (até 10 minutos por nível)
- Animal deve estar consciente

---

## 13. Restrições e Regras {#restrições}

### Restrições de Posse

- ❌ **Não pode ter simultaneamente:** Familiar de Mago, Montaria de Paladino ou outro Companheiro Animal
- ❌ **Exclusividade:** Uma entidade mágica de vínculo por personagem
- ✅ **Exceção:** Talentos específicos podem permitir múltiplas entidades

### Morte e Ressurreição

- **Morte do animal:** Personagem pode realizar novo ritual em 24 horas em ambiente natural
- **Novo companheiro:** Pode escolher espécie diferente da anterior
- **Ressurreição:** Conjurar *Ressurreição* ou *Ressurreição Verdadeira*
  - Custo normal de XP
  - Requer corpo ou partes do corpo
- **Morte do mestre:** Companheiro geralmente permanece protegendo o corpo ou retorna à natureza

### Comportamento

- ✅ Animal é **extremamente leal**
- ✅ Executa tarefas a contento do mestre
- ❌ Não realizará ações **claramente suicidas** sem teste de Handle Animal muito difícil (DC 25+)
- ❌ Não é mindless (controle absoluto requer testes em situações extremas)

### Substituição

| Situação | Permitido? | Requisitos |
|----------|-----------|-----------|
| Animal morto | ✅ Sim | Ritual de 24h em ambiente natural |
| Animal libertado | ✅ Sim | Cerimônia formal; 1 semana de espera |
| Animal vivo e saudável | ❌ Não | Sem justificativa válida (decisão do mestre) |
| Troca de espécie | ✅ Sim | Após morte ou libertação anterior |

---

## 14. Tabela de Progressão Completa {#tabela}

| Nível | HD Bônus | HD Total (Lobo) | BAB | Fort | Ref | Von | Arm. Nat | Talentos | Truques | Habilidades Especiais |
|-------|----------|-----------------|-----|------|-----|-----|----------|----------|--------|----------------------|
| 1-2 | +0 | 2 | +2 | +3 | +3 | +1 | +1 | 1 | 1 | Link, Vínculo |
| 3-5 | +2 | 4 | +4 | +4 | +4 | +2 | +2 | 2 | 2 | + Comp. Linguagem |
| 6-8 | +4 | 6 | +6 | +5 | +5 | +3 | +4 | 2 | 3 | + Telepatia, Sentidos |
| 9-11 | +6 | 8 | +8 | +6 | +6 | +3 | +4 | 3 | 4 | + Mov. Relacionados |
| 12-14 | +8 | 10 | +10 | +7 | +7 | +4 | +5 | 3 | 5 | + Evasão Aprox. |
| 15-17 | +10 | 12 | +12 | +8 | +8 | +5 | +6 | 4 | 6 | + Comunhão |
| 18+ | +12 | 14+ | +14 | +9 | +9 | +5+ | +6 | 4+ | 7 | + Vínculo Inquebrantável |

> **Nota:** Valores baseados em lobo (2 HD originais). Outros animais terão HD originais diferentes.

---

## 15. Exemplos de Cálculo {#exemplos}

### Exemplo 1: Druida Nível 7 com Lobo

**Dados iniciais:**
- Classe: Druida
- Nível: 7
- Animal: Lobo (estatísticas base: 2 HD, For 15, Des 12, Con 13, Int 2, Sab 12, Car 6)

**Cálculos:**

**1. HD Bônus:**
$$HD_{Bônus} = \left\lfloor \frac{7}{3} \right\rfloor = 2$$

**2. HD Total:**
$$HD_{Total} = 2 + 2 = 4$$

**3. BAB:**
$$BAB = 4 = +4$$

**4. Resistências:**
$$Fort = 2 + \left\lfloor \frac{4}{2} \right\rfloor = 2 + 2 = +4$$
$$Ref = 2 + \left\lfloor \frac{4}{2} \right\rfloor = 2 + 2 = +4$$
$$Von = 1 + \left\lfloor \frac{4}{3} \right\rfloor = 1 + 1 = +2$$

**5. Armadura Natural:**
$$AN = \left\lfloor \frac{7}{3} \right\rfloor + 1 = 2 + 1 = +3$$

**6. Atributos:**
- Nível 3-5: +2 em dois atributos
- Escolha: +2 Força, +2 Constituição
- Nova Força: 15 + 2 = 17 (modificador +3)
- Nova Constituição: 13 + 2 = 15 (modificador +2)

**7. Talentos:**
$$Talentos = 1 + \left\lfloor \frac{4-1}{3} \right\rfloor = 1 + 1 = 2$$

**8. Truques Bônus:**
- Nível 7 → 3 truques

**9. Habilidades Especiais:**
- Nível 1: Link, Vínculo Compartilhado
- Nível 3: Compreensão de Linguagem
- Nível 5: Comunicação Telepática

**Resultado final:**
- CA: 10 + 3 (AN) + 1 (Des mod) = 14
- Ataque de Garra: +4 (BAB) + 3 (For mod) = +7 para atingir
- Dano de Garra: 1d4 + 3 (For mod) + 2 (aprimoramento) = 1d4 + 5
- Resistências: Fort +4, Ref +4, Von +2
- Pontos de Vida: 4d8 + 8 (2 por HD) = média 26 PV
- Habilidades: Entende comum, pode se comunicar telepaticamente

---

### Exemplo 2: Ranger Nível 10 com Falcão

**Dados iniciais:**
- Classe: Ranger
- Nível: 10
- Nível Efetivo: 10 - 3 = 7
- Animal: Falcão (estatísticas base: 1 HD, For 10, Des 15, Con 10, Int 2, Sab 14, Car 6)

**Cálculos:**

**1. HD Bônus:**
$$HD_{Bônus} = \left\lfloor \frac{7}{3} \right\rfloor = 2$$

**2. HD Total:**
$$HD_{Total} = 1 + 2 = 3$$

**3. BAB:**
$$BAB = +3$$

**4. Resistências:**
$$Fort = 2 + \left\lfloor \frac{3}{2} \right\rfloor = +3$$
$$Ref = 2 + \left\lfloor \frac{3}{2} \right\rfloor = +3$$
$$Von = 1 + \left\lfloor \frac{3}{3} \right\rfloor = +2$$

**5. Armadura Natural:**
$$AN = \left\lfloor \frac{7}{3} \right\rfloor + 1 = 2 + 1 = +3$$

**6. Atributos:**
- Nível 6-8 (efetivo 7): +3 em dois, +2 em um
- Escolha: +3 Destreza, +3 Sabedoria, +2 Constituição
- Nova Destreza: 15 + 3 = 18 (modificador +4)
- Nova Sabedoria: 14 + 3 = 17 (modificador +3)
- Nova Constituição: 10 + 2 = 12 (modificador +1)

**7. Habilidades Especiais:**
- Nível 1: Link, Vínculo
- Nível 3: Compreensão de Linguagem
- Nível 5: Comunicação Telepática
- Nível 7: Sentidos Aguçados

**Resultado:**
- CA: 10 + 3 (AN) + 4 (Des) = 17
- Ataque de Garras: +3 (BAB) + 4 (Des) = +7
- Visão Noturna e Detecção de Movimento ativada
- Perícia Listen +8 (Sab +3, bônus racial)

---

## Referência Rápida de Fórmulas

$$HD_{Bônus} = \left\lfloor \frac{\text{Nível}}{3} \right\rfloor$$

$$Bônus_{AN} = \left\lfloor \frac{\text{Nível}}{3} \right\rfloor + 1$$

$$BAB = HD_{Total}$$

$$Fort/Ref = 2 + \left\lfloor \frac{HD_{Total}}{2} \right\rfloor$$

$$Von = 1 + \left\lfloor \frac{HD_{Total}}{3} \right\rfloor$$

$$Talentos = 1 + \left\lfloor \frac{HD_{Total} - 1}{3} \right\rfloor$$

---

**Documento gerado em:** 17 de maio de 2026
**Sistema:** D&D 3.5 edição
**Tradução:** Português Brasileiro
