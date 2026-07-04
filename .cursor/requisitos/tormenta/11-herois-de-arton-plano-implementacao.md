# SUPLEMENTO: Heróis de Arton v1.1 — Plano de Implementação

> **Fonte:** `livros/T20-Herois-de-Arton-v1-1.pdf` (332 páginas, edição maio 2025 v1.1)  
> **Método de extração:** texto nativo via `pdfplumber` (PDF selecionável); confirmado página a página.  
> **Regra base:** Tormenta20 EJA v1.3 já implementado em `backend/app/games/tormenta/`.  
> **Direitos autorais:** este doc contém estrutura, fórmulas e remissão de página — sem reprodução de texto longo nem tabelas completas do livro.

---

## Estrutura do livro

| Capítulo | Páginas | Conteúdo principal |
|----------|---------|-------------------|
| Capítulo 1 — Campeões de Arton | 6 – 101 | 5 raças, 1 classe nova, 14 classes variantes, origens, poderes |
| Distinções | 102 – 243 | 36 distinções (especializações narrativas + árvore de poderes) |
| Capítulo 3 — Arsenal dos Heróis | 214 – 277 | Equipamentos, veículos, capangas, magias arcanas, itens mágicos |
| Capítulo 4 — Regras Opcionais | 278 – 328 | 11 módulos de regras avançadas |

---

## PARTE 1 — NOVAS RAÇAS (p.8–15)

### 1.1 Resumo de modificadores e habilidades-chave

| Raça | Modificadores | Tamanho | Tipo | Destaques mecânicos |
|------|--------------|---------|------|---------------------|
| **Duende** | Modular (ver §1.2) | Variável | Espírito | Natureza, Tamanho, Dons, Presentes e Limitações — construção em 5 passos |
| **Eiradaan** | Sab +2, Car +1, For −1 | Médio | Espírito | Magia Instintiva (Sab no lugar de atributo-chave arcano); Sentidos Místicos permanentes; Canção da Melancolia (pior de 2d em Vontade vs efeitos mentais) |
| **Galokk** | For +1, Con +1, +1 livre, Car −1 | **Grande** | Humanoide (gigante) | Força dos Titãs (dado extra se dano máximo, limite = For); Meio-Gigante; treinado em 1 perícia livre |
| **Meio-Elfo** | Int +1, +1 em dois atributos (exceto Con) | Médio | Humanoide | Ambição Herdada (1 poder geral ou único de origem); +1 PM a cada nível ímpar; considerado elfo |
| **Sátiro** | Car +2, Des +1, Sab −1 | Médio | Espírito | +2 Atuação e Fortitude; Instrumentista Mágico (lança magias via instrumento) |

### 1.2 Duende — sistema modular (p.10–13)

A raça Duende é a mais complexa do livro: construção em 5 passos, todos com escolhas do jogador.

| Passo | Escolhas | Efeito |
|-------|----------|--------|
| 1 — Natureza | Animal / Vegetal / Mineral | Corpo e imunidades diferentes; Animal dá +1 em 1 atributo livre; Vegetal dá Natureza Vegetal + Florescer Feérico; Mineral dá imunidade metabolismo + RD 5 corte/fogo/perfuração |
| 2 — Tamanho | Minúsculo / Pequeno / Médio / Grande | Modificadores de Furtividade, manobra, deslocamento e Força/Destreza conforme tamanho |
| 3 — Dons | 2 atributos à escolha | +1 em cada (se Animal, pode acumular com bônus do passo 1) |
| 4 — Presentes | 3 de 12 (ver abaixo) | Poderes mágicos únicos; repetíveis por patamar no lugar de poder de classe |
| 5 — Limitações | Fixas (3) | Aversão a Ferro, Aversão a Sinos, Tabu |

**12 Presentes disponíveis (p.11–12):**
1. Afinidade Elemental (água / fogo / vegetação) — magias e movimento especial
2. Encantar Objetos — encanta itens temporariamente (PM)
3. Enfeitiçar — lança Enfeitiçar como arcanista de mesmo nível
4. Invisibilidade — lança Invisibilidade como arcanista de mesmo nível
5. Língua da Natureza — +2 Adestramento/Sobrevivência; fala com animais/plantas
6. Maldição — amaldiçoa criatura (escolher resistência + efeito; 8 opções de maldição)
7. Mais Lá do que Aqui — corpo parcialmente invisível (3 PM; camuflagem leve +5 Furtividade)
8. Metamorfose Animal — assume 1 forma selvagem de druida (fala e lança magias na forma)
9. Sonhos Proféticos — rola 1d20 antecipado; troca resultado de teste (3 PM)
10. Velocidade do Pensamento — ação padrão extra no 1º turno; pula turno na rodada 2 (2 PM)
11. Visão Feérica — visão na penumbra + Visão Mística permanente (enxergar invisíveis)
12. Voo — flutua 1,5m (deslocamento base +3m) ou voa pagando 1 PM/rodada

**3 Limitações fixas (p.13):**
- Aversão a Ferro: +1 dano/dado de armas de ferro; 1d6 dano/rodada se empunhar/vestir ferro ou aço
- Aversão a Sinos: fica alquebrado + esmorecido ao ouvir sino; rola 1d6 no início de cenas urbanas (1 = ouve sino)
- Tabu: comportamento proibido; penalidade −5 em uma das (Diplomacia, Iniciativa, Luta ou Percepção); desobedecer → fatigado → exausto → morte (dias 1-2-3)

**Geração aleatória (opcional):** rolar 1d3, 1d4, 2d6, 3d12 simultaneamente para definir natureza, tamanho, dons e 3 presentes. Recompensa: +2 PM de Nimb.

### 1.3 Impacto técnico — raças

| Implicação | Detalhe | Arquivo afetado |
|-----------|---------|----------------|
| Duende: estrutura de dados complexa | `ficha_json` precisa de sub-objeto `duende: {natureza, tamanho_raca, dons: [...], presentes: [...], tabu}` | `backend/.../schemas/` |
| Duende: Presentes substituem poder de classe | Motor de criação deve permitir trocar poder de classe por Presente (uma vez/patamar) | `rules/poderes_t20.py` |
| Galokk: tamanho Grande | Lógica de CA, manobras e armas aumentadas já implementada para tamanho | `rules/combate_t20.py` |
| Eiradaan: Magia Instintiva | `atributo_chave_magia` pode ser SAB mesmo sendo arcanista | `rules/magia_t20.py` |
| Meio-Elfo: +1 PM em níveis ímpares | Cálculo de PM máximo deve checar raça | `rules/personagem_t20.py` |
| Sátiro: Instrumentista Mágico | Habilidade condicional (requer instrumento em mãos) | `rules/combate_t20.py` |

---

## PARTE 2 — CLASSE TREINADOR (p.16–21)

### 2.1 Características da classe

| Stat | Valor |
|------|-------|
| PV base | 12 + Con; por nível: 3 + Con |
| PM por nível | 4 |
| Perícias obrigatórias | Adestramento (Car), Vontade (Sab) |
| Perícias opcionais (+4) | Atletismo, Cavalgar, Diplomacia, Guerra, Iniciativa, Intimidação, Intuição, Luta, Ofício, Percepção, Pontaria, Reflexos, Religião, Sobrevivência |
| Proficiências | Nenhuma |

### 2.2 Tabela de progressão (p.20)

| Nv | Habilidades principais |
|----|------------------------|
| 1 | Direcionar, Melhor Amigo (2 truques) |
| 2 | Domar Criatura (2d8), Poder de Treinador |
| 4 | Melhor Amigo (3 truques) |
| 5 | Domar Criatura (cena), Treino Especializado |
| 6 | Domar Criatura (4d8), Sincronia de Combate |
| 7 | Melhor Amigo (4 truques) |
| 8 | Domar Criatura (dia) |
| 10 | Domar Criatura (6d8), Melhor Amigo (5 truques) |
| 14 | Domar Criatura (8d8) |
| 18 | Domar Criatura (10d8) |
| 20 | Sincronia Perfeita |

### 2.3 Mecânicas centrais

**Melhor Amigo (p.20–23):**
- Parceiro especial tipo animal/construto/espírito/monstro/morto-vivo
- Começa com 2 truques; ganha 1 truque a cada 3 níveis
- Limite de parceiros aumenta com poderes (Coração Grande)
- Bônus por tipo: animal (+1 For/Des/Sab, faro, visão na penumbra, Percepção/Sobrevivência, margem de ameaça +1); construto (+2 Con, visão no escuro, imunidade cansaço/metabólicos); espírito, monstro, morto-vivo (ver livro)
- Truques disponíveis (15+): Alado, Amigão, Asas Aliadas, Deslocamento Especial, Magia Inata, e outros

**Domar Criatura:** teste de Adestramento oposto a Vontade; dano psíquico não letal; criatura com 0 PV se rende; a partir do 5º nível pode controlar criatura rendida (gastando PM = ND da criatura)

**Direcionar:** gasta 2 PM para somar Carisma em teste de perícia do Melhor Amigo em alcance curto

**Poderes de Treinador (~20 poderes):** Amigo Divino, Asas Aliadas, Aumento de Atributo, Bom Garoto, Comando Defensivo, Comandos Distantes, Convocar Enxame, Coração Grande, Direcionamento Marcial, Domador Cativante, Domador Lendário, Ensinar Truque, Investida Conjunta, e outros

---

## PARTE 3 — CLASSES VARIANTES (p.22–44)

Cada classe variante é uma **substituição** de uma classe core — usa a mesma progressão de PV/PM mas troca poderes específicos.

| Classe Variante | Classe Base | Tema | p. |
|----------------|-------------|------|----|
| Alquimista | Inventor | Poções e itens alquímicos; mistura básica; magia engarrafada | 22 |
| Atleta | Guerreiro | Façanhas físicas; resistência de campeão | 24 |
| Burguês | Nobre | Comércio e alta sociedade | 25 |
| Duelista | (livre) | Combate um-a-um; floretes e estilo | 27 |
| Ermitão | Druida | Reclusão; meditação; poderes de sobrevivência | 29 |
| Inovador | Inventor | Criatividade extrema; inventos únicos | 30 |
| Machado de Pedra | Guerreiro (anão) | Combate com machado e couraça pesada | 32 |
| Magimarcialista | Arcanista / Lutador | Fusão magia + combate corpo a corpo | 33 |
| Necromante | Arcanista | Magia de morte; mortos-vivos aliados | 34 |
| Santo | Clérigo | Devoção absoluta; milagres sem magia formal | 37 |
| Seteiro | Caçador | Arqueiro especializado; pontaria | 38 |
| Usurpador | Bardo / Ladino | Dissimulação política; disfarces | 40 |
| Vassalo | Cavaleiro | Serviço leal a um senhor | 41 |
| Ventanista | Caçador / Ladino | Acrobacia e armas de corda; movimentação | 44 |

**Regra de incompatibilidade:** classes variantes são mutuamente exclusivas com a classe base e entre si dentro do mesmo grupo (flag `fonte: herois_arton` no catálogo, campo `classe_variante_base`).

---

## PARTE 4 — NOVAS ORIGENS (p.48–55)

Origens especiais — ligadas a lugares, eventos ou organizações de Arton (mais específicas que origens core).

| Origem | Perícias/bônus principais | p. |
|--------|--------------------------|-----|
| Bacharel | Conhecimento, Diplomacia, Nobreza; mudar atitude como ação livre 1×/cena | 48 |
| Boticário | Alquimia, Medicina, fabricação de poções/venenos | 49 |
| Caçador de Ratos | Furtividade, Investigação, Sobrevivência; +2 vs criaturas 2 tamanhos menores | 49 |
| Cão de Briga | Ofício (artesão); RD corte 2; armas de corte ignoram 5 pontos de RD | 50 |
| Chef Hynne | Ofício (cozinheiro) aprimorado; instrumentos especiais | 50 |
| Cirurgião-Barbeiro | Medicina, Ofício (barbeiro); cura e extração | 51 |
| Coureiro | Ofício (coureiro); trabalha couro; melhora armaduras leves | 52 |
| Ferreiro Militar | Ofício (ferreiro); armas e armaduras militares | 53 |
| Freira | Religião, devoção monástica | 53 |
| Goradista | Gorad (ingrediente especial); culinária e negociação | 53 |
| Ladrão de Túmulos | Investigação, Furtividade; conhece masmorras e armadilhas | 54 |
| Menestrel | Atuação, conhecimento de histórias | 54 |
| Náufrago | Sobrevivência, Atletismo aquático; resistência | 54 |
| Servo | Diplomacia, Intuição; serventia na nobreza | 55 |

**Regra:** se benefício inclui treinamento em perícia já treinada, pode trocar por outra perícia de classe. Efeitos contam como habilidades para acúmulo.

---

## PARTE 5 — NOVOS PODERES DE CLASSE (p.56–77)

Poderes adicionais para as 14 classes core do T20 v1.3. Cada classe recebe de 2 a 8 novos poderes.

| Classe | Novos poderes (exemplos) | p. |
|--------|--------------------------|-----|
| Arcanista | Contingência Arcana, Contramágica Superior, Apoteose Feérica | 56 |
| Bárbaro | Fúria focada, resistência sanguinária | 56 |
| Bardo | Lamento, inspiração avançada | 57 |
| Bucaneiro | Manobras navais, estilo de espada | 59 |
| Caçador | Caça específica avançada, parceiro aprimorado | 61 |
| Cavaleiro | Ordens Agressivas, Arma Juramentada, Escudo Sagrado | 62 |
| Clérigo | Poderes de domínio extras, intercessão | 64 |
| Druida | Formas selvagens melhoradas | 66 |
| Guerreiro | Chuva de Golpes, Escudo Heroico, Pancada Estonteante | 68 |
| Inventor | Engenhocas avançadas, construtos melhorados | 70 |
| Ladino | Assassinato aprimorado, disfarces | 73 |
| Lutador | Estilos avançados | 73 |
| Nobre | Comando político, influência | 75 |
| Paladino | Ordens Agressivas, santidade avançada | 76 |

---

## PARTE 6 — NOVOS PODERES GERAIS (p.78–95)

### 6.1 Poderes de Combate (p.80–82)
Novos poderes na tabela 1-18. Exemplos: Chuva de Golpes (Estilo de Duas Armas), Escudo Heroico (escudo como arma de arremesso), Pancada Estonteante (alvo desprevenido 1 rodada, 2 PM), Estocada Pungente, Arremesso Devastador, Ataque com o Cabo, Estudar o Adversário.

### 6.2 Poderes de Destino (p.82)
Impostor (usa autoconfiança para "ter" habilidades que não tem).

### 6.3 Poderes de Magia (p.83–84)
Sedução Lasciva (Encantar Itens Médios); Prisão Gélida (enreda alvo com aprimoramento de magia de frio).

### 6.4 Poderes da Tormenta (p.85)
Novos poderes do grupo Tormenta (tabela 1-21).

### 6.5 Poderes de Raça (p.86–93) — NOVO GRUPO

Novo grupo de poderes gerais exclusivos por raça. Disponíveis para personagens que possuam a raça correspondente (ou arma natural fornecida por habilidade de raça).

| Raça | Poderes disponíveis (exemplos, tabela 1-22) |
|------|---------------------------------------------|
| Anão | Coração de Pedra, Coro Sibilante, Magia Ofídica, e outros |
| Dahllan | Camuflagem Mimética, Constrição Atroz |
| Gnoll, Kaijin, Lefou, Orc, Trog | Duas Cabeças (ocupa mesmo espaço que criatura maior → 25% chance de atingir a maior) |
| Qareen (Água/Ar/Fogo/Terra) | Familiar de Elemento; Fúria Natural |
| Duende, Eiradaan, Sílfide | Glamour Maior; Novo Parceiro Javali Doherita |
| Osteon | Quatro Braços (ataques extras); Ossos Afiados |
| Kaijin, Lefou, Nagah, Orc, Trog | Tradição Perdida (lança magias de membros da raça) |

### 6.6 Poderes de Grupo (p.94–97) — NOVO GRUPO

Poderes que fornecem bônus maiores quando o grupo possui o mesmo poder. Exemplos: Apontar Fraqueza, Bode Expiatório, Defesa do Mártir, Parede de Escudos.

---

## PARTE 7 — DISTINÇÕES (p.102–213)

### 7.1 Conceito e regras gerais (p.104–107)

Distinções são **especializações narrativas** com árvore de poderes própria:
- **Admissão:** conjunto de tarefas e requisitos narrativos (+ às vezes mecânicos) para entrar
- **Poderes exclusivos:** cada distinção tem uma árvore; pode escolher 1 poder por patamar no lugar de poder de classe
- **Poderes repetíveis:** alguns contam separado para efeitos de "quantidade de poderes da distinção"
- **Ação de tempo entre aventuras:** pode ser usada para partes objetivas da admissão

### 7.2 Catálogo das 36 distinções

| # | Distinção | Admissão principal | Mecânica-chave | p. |
|---|-----------|-------------------|-----------------|-----|
| 1 | Aeronauta Goblin | Ser goblin; construir uma máquina voadora | Pilota ornitóptero goblin; inventos voadores únicos | 106 |
| 2 | Algoz da Tormenta | Combater lefeu; entrar em organização de caçadores | Poderes anti-Tormenta; dano bonus a lefeu | 109 |
| 3 | Amazona | Pertencer a nação amazona ou exílio de convivência | Cavalaria; poderes de liderança feminina | 112 |
| 4 | Armadilheiro Mestre | Treinar com mestre armadilheiro | Instalar armadilhas avançadas em combate e exploração | 115 |
| 5 | Arqueiro de Lenórienn | Ser aceito por arqueiros élficos de Lenórienn | Arco élfico; poderes de precisão e natureza | 118 |
| 6 | Bruxo da Tormenta | Frequentar instituição que estuda a Tormenta; ser lefeu ou exposto a matéria vermelha | Poderes da Tormenta e lefeu; controle | 121 |
| 7 | Caçador de Cabeças | Completar contratos de recompensa; fama de caçador | Rastreamento; captura/morte de alvos | 124 |
| 8 | Caçador de Dragões | Aprendizado obrigatório com mestre caçador de dragões | Técnicas anti-dragão; itens especializados | 127 |
| 9 | Campeão de Dojo | Treinar em dojo específico; torneio | Artes marciais; combate desarmado avançado | 130 |
| 10 | Capitão do Conclave Pirata | Ter um navio + tripulação; entrar no Conclave Pirata | Comando naval; poderes de pirata | 133 |
| 11 | Carteador | Dominar jogo de cartas | Magia de cartas; sorte e destino | 136 |
| 12 | Cavaleiro do Corvo | Encontrar o Ninho do Corvo; jurar a ordem; abrir mão do nome | Língua dos Corvos (comunicação silenciosa); poderes sombrios | 139 |
| 13 | Cavaleiro Feérico | Ser aceito por Allihanna ou Rainha das Fadas; receber montaria | Montaria feérica / gamo celestial; poderes de honra | 142 |
| 14 | Chapéu-Preto | Concluir contrato de assassinato; ser aceito por organização | Assassinato; disfarce; venenos | 145 |
| 15 | Cobaia dos Médicos Monstros | Pagar ao Grêmio; passar por operação cirúrgica | Implantes/mutações cirúrgicas permanentes | 148 |
| 16 | Dracomante Real | Ter encontro com dragão; comprar direito de domesticação | Controlar e cavalgar dragões | 151 |
| 17 | Drogadora | Aprender com mestre; misturar substâncias | Venenos e drogas como arma; imunidades | 154 |
| 18 | Engenhoqueiro Goblin | Ser goblin; aprender engenhocas | Inventos goblins únicos; caos mecânico | 157 |
| 19 | Escapista Magnífico | Ser preso e escapar repetidamente | Escapar de qualquer prisão; truques de ilusionista | 160 |
| 20 | Gigante Furioso | Ter sangue de gigante ou ser de tamanho Grande | Fúria colossal; ataques devastadores | 163 |
| 21 | Ginete de Namalkah | Pertencer ao povo de Namalkah; receber montaria do deserto | Cavalaria do deserto; poderes de sobrevivência | 166 |
| 22 | Guerreiro Mágico | Aprender magia + combate fisico | Lança magias em armadura pesada; ataques mágicos | 169 |
| 23 | Infiltrador de Wynlla | Ser recrutado por espionagem de Wynlla | Espionagem; disfarce; assassinato político | 172 |
| 24 | Mago da Ordem do Vazio | Entrar na Ordem do Vazio; passar por apagamento parcial | Magia do esquecimento; apagar memórias | 175 |
| 25 | Mago de Batalha de Wynlla | Treinar com Exército de Wynlla | Magia e combate simultâneos; escudos mágicos | 178 |
| 26 | Médico de Salistick | Estudar em Salistick; aprovar em exames | Cura avançada; cirurgia em campo | 181 |
| 27 | Mestre Bêbado | Aprender com mestre; praticar estilo bêbado | Estilo de luta caótico e imprevisível; bebida como mecânica | 184 |
| 28 | Mestre Cozinheiro | Treinar com chef famoso; preparar prato impossível | Culinária como magia; pratos com efeitos mecânicos | 187 |
| 29 | Mestre dos Desejos | (ligado a Qareen ou similar) | Conceder e manipular desejos | 190 |
| 30 | Mestre Mahou-Jutsu | Aprender estilo oriental de Moreania | Arte marcial mágica; kata de magia | 193 |
| 31 | Mosqueteiro de Rishantor | Servir em Rishantor; ser aceito no corpo | Mosquete; esgrima e arma de fogo | 196 |
| 32 | Mutagenista | Realizar experimentos de alquimia no próprio corpo | Mutações alquímicas progressivas | 199 |
| 33 | Pistoleiro de Smokestone | Ser de Smokestone ou aprender lá | Pistola e armas de fogo avançadas | 202 |
| 34 | Professor de Magia | Ensinar magia a outros; criar escola | Potencia magias de aliados; poderes de instrução | 205 |
| 35 | Senador | Ser eleito ou nomeado senador | Influência política; poderes de debate | 208 |
| 36 | Vigarista | Enganar pessoas de alto escalão; ser aceito em guilda | Blefe avançado; ilusões; escapes | 211 |

### 7.3 Impacto técnico — distinções

| Implicação | Detalhe |
|-----------|---------|
| Novo tipo de vínculo em `ficha_json` | `distincao: {slug, nivel_de_entrada, poderes_adquiridos: [...]}` |
| Poderes de distinção substituem poder de classe | Motor de poderes deve suportar fonte `distincao_<slug>` |
| Admissão é narrativa | Apenas flag de status (`admissao_concluida: bool`) no backend; validação é do mestre |
| Algumas exigem pré-requisito de raça | Ex.: Aeronauta Goblin (goblin), Gigante Furioso (tamanho Grande ou sangue gigante) |
| Cavaleiro do Corvo perde o nome | Campo opcional `nome_anterior` na ficha |
| Capitão do Conclave exige navio | Vínculo com sistema de Domínios (Capítulo 4) |
| Dracomante Real exige dragão | Vínculo com sistema de Melhor Amigo do Treinador (ou entidade própria) |

---

## PARTE 8 — ARSENAL DOS HERÓIS (p.216–243)

### 8.1 Novas armas (p.216–221, Tabela 3-1)

**Armas simples:**

| Arma | Dano | Crítico | Alcance | Tipo | Preço |
|------|------|---------|---------|------|-------|
| Bastão lúdico | 1d6 | ×2 | — | Impacto | T$ 5 |
| Besta de mão | 1d6 | 19 | Curto | Perfuração | T$ 30 |

**Armas marciais (leves):**

| Arma | Dano | Crítico | Preço |
|------|------|---------|-------|
| Adaga oposta | 1d4 | 19 | T$ 12 |
| Agulha de Ahlen | 1d4 | 19 | T$ 10 |
| Cinquedea | 1d4 | 19 | T$ 18 |
| Dirk | 1d4 | 19 | T$ 15 |
| Martelo leve | 1d4 | ×4 (arremesso curto) | T$ 2 |

**Armas marciais (uma mão):**

| Arma | Dano | Crítico | Preço |
|------|------|---------|-------|
| Espada larga | 2d4 | ×2 | T$ 8 |
| Espadim | 1d8 | 20 | T$ 300 |

**Armas exóticas especiais:** Tai-Tai (lança pedras amarrado ao braço; recarregar = ação de movimento; segurar objetos com a mão), Sifão Cáustico (dispara ácido), e outras.

### 8.2 Novas armaduras e escudos (p.222–226)

**Novos escudos:**

| Escudo | RD | PV | Notas |
|--------|----|----|-------|
| Broquel | 5 | 10 | — |
| Escudo de vime | 2 | 20 | — |
| Escudo torre | 10 | 30 | — |

**Novas armaduras:** Armadura de Pedra (RD 2 extra; deslocamento reduzido pela metade, não em 3m; sem melhoria de material especial), Armadura Sensual, e outras.

### 8.3 Itens gerais e superiores (p.227–242)

- **Bebidas especiais:** Dilínio (+1 limite PM; T$ alto; não fabricável), Grogue Negro, e outras
- **Serviços:** Banho Quente (+1d6 em próximo teste de resistência até fim do dia), Bigode Encerado
- **Melhorias novas (Itens Superiores):** Balístico (escudo usa energia de bala para aumentar golpe), e outras

### 8.4 Capangas (p.240)

Regras para contratar e gerenciar capangas (NPCs aliados em combate). Integra com sistema de Domínios.

### 8.5 Veículos (p.241–243)

Regras mecânicas de pilotagem, conserto e combate com veículos:
- Embarcar/desembarcar: ação de movimento
- Conserto: teste Ofício (artesão/outro) CD 15; 1d8 PV recuperado + 1d8 por 5 acima da CD; T$ 10/d8
- Posições em veículos maiores: pode exigir mais tempo para alcançar

---

## PARTE 9 — NOVAS MAGIAS ARCANAS (p.254–257)

| Magia | Círculo | Escola | Execução | Notas |
|-------|---------|--------|----------|-------|
| Armadura Elemental | Arcana 1 | Evocação | Padrão | Escolhe tipo energia (ácido/eletricidade/fogo/frio); armadura elemental pessoal |
| Aura de Morte | Arcana 2 | Necromancia | Padrão | Esfera 6m de raio; aura de frio necrótico; duração cena |
| Distração Fugaz | Arcana 1 | Ilusão | Padrão | Alvo 1 humanoide; instantânea; Vontade anula |
| Descobrir Fraqueza | Arcana 1 | Adivinhação | Padrão | Detecta fraquezas de criaturas |
| + outras (~5) | 1–3 | Variada | — | Ver p.254–257 para texto completo |

---

## PARTE 10 — NOVOS ITENS MÁGICOS (p.252–277)

### 10.1 Mobílias (p.252–253)

Objetos mágicos para cômodos/bases. Cada cômodo pode conter 1 mobília.

| Mobília | Efeito | Preço |
|---------|--------|-------|
| Armadura Decorativa | Residentes +1 Defesa | T$ 2.000 |
| Armário de Remédios | Poções de cura recuperam +1 PV/dado | T$ 2.000 |
| Espelho de Corpo | Instalar em chapelaria; ajuste visual | T$ variável |
| Mesa Manufatureira | Tempo de fabricação ÷ 2 (itens não consumíveis não mágicos) | T$ 3.000 |

### 10.2 Armas específicas (p.258–260)

| Arma | Efeito principal |
|------|-----------------|
| Florete do Vendaval | Mitral; 3 PM → voo 12m por 2 rodadas + Defesa +5 contra ataques à distância |
| Lança da Fênix | Ao reduzir a 0 PV: recupera 10 PV; 1×/cena se reduzido a 0 PV → renascer com metade PV (5 PM) |

### 10.3 Encantos para Armaduras & Escudos (p.260–263)

| Encanto | Efeito |
|---------|--------|
| Abissal | Gravuras de demônios; RD ácido e fogo 10; 1 PM/rodada → 2d6 ácido ou fogo |
| Caridoso | Ao lançar magia em aliado gastando PM: +1 PM temporário para próxima magia na cena |
| Chocante | Magias de eletricidade causam 1 dado extra de dano |

**Escudos específicos:** Escudo da Luz Estelar (cristal; +5 Percepção; lança Luz gratuitamente; CD Int).

### 10.4 Esotéricos (p.262–268)

Encantos para esotéricos (itens não-arma não-armadura). Inclui Caridoso, Chocante, e outros.

### 10.5 Acessórios (p.268–269)

| Item | Efeito |
|------|--------|
| Instrumentos da Celeridade | Versão mágica para cada perícia de Ofício; fabrica item adicional simultaneamente |
| Lâmpada da Ilusão Impecável | Ilusões de alto nível |

### 10.6 Itens Inteligentes (p.271–273)

Itens que adquiriram consciência por evento especial. Regras:
- **Comunicação:** impulsos rudimentares → fala ou telepatia (tabela 3-12: rolar 1d%)
- **Poderes secundários:** variam por item
- **Personalidade:** definida por histórico do item

### 10.7 Itens Amaldiçoados (p.274)

| Maldição | Efeito |
|----------|--------|
| Preguiçosa | Arma só ataca em rodadas alternadas; sem outros ataques na rodada de repouso |
| Pró-Criatura | Dano a inimigo de tipo específico → cura o mesmo em vez de causar dano |
| Antipático | Todos NPCs ao primeiro encontro têm atitude 1 categoria pior |
| Carente | (efeito de vínculo obsessivo) |
| Cético | Aura de descrença |

### 10.8 Artefatos (p.274–277)

| Artefato | Efeito principal |
|----------|-----------------|
| Monóculo da Verdade | Visão da verdade; aura de desconforto em aliados; proclama verdades indesejadas automaticamente |
| + outros | Ver p.274–277 |

---

## PARTE 11 — REGRAS OPCIONAIS (p.278–328)

Cada módulo é independente e pode ser ativado por campanha/mesa via flag.

### 11.1 Atributos Variados (p.280)
Método alternativo de geração de atributos. Impacto: campo `metodo_geracao_atributos` na mesa.

### 11.2 Raças Abertas (p.281)
Criação de raças personalizadas pelo mestre. Impacto: raça com `fonte: personalizada` e campos livres.

### 11.3 Devoções Abertas (p.281)
Criação de devoções sem deus pré-definido. Impacto: `devoção_personalizada: true` na ficha.

### 11.4 Complicações (p.282–287)

Desvantagens opcionais por classe. Exemplos:
- Bardo → **Estrelismo** (−5 Diplomacia/Intuição; alquebrado se falha em Atuação)
- Bucaneiro → **Coragem Líquida** (1d4 no início de cenas perigosas; em 1 gasta ação de movimento em bebida)
- Cada classe tem 1–3 complicações específicas

Impacto: lista de complicações ativas em `ficha_json.complicacoes: [...]`.

### 11.5 Idades Variadas (p.288–291)

Faixas etárias com complicações obrigatórias:
- Adulto: 1 complicação de idade
- Maduro: 2 complicações
- Velho (60–79 anos): 3 complicações
- Ancião (80+): 4 complicações

Impacto: campo `faixa_etaria` na ficha + lista de complicações de idade.

### 11.6 Objetivos Heroicos (p.292–293)

Personagem escolhe 1 objetivo. Penalidades se ao fim de uma cena estiver mais longe do objetivo. Bônus ao progredir.

Impacto: campo `objetivo_heroico` na ficha com `descricao` e `progresso`.

### 11.7 Papéis no Grupo (p.294–295)

Papéis formais: Advogado, e outros. Cada papel dá bônus específico ao grupo.

Impacto: campo `papel_no_grupo` na ficha.

### 11.8 Combate Avançado (p.296–304)

18 módulos independentes de combate:

| Módulo | Descrição |
|--------|-----------|
| Ações Rápidas | Novas ações possíveis em combate |
| Armas Leves e Ágeis | Regras extras para armas leves |
| Ataques de Oportunidade | Expandir janelas de oportunidade |
| Ataques Mirados | Visar parte do corpo; penalidade/bônus |
| Cobertura Leve e Efeitos | Cobertura parcial |
| Defesa Progressiva | Defesa aumenta conforme ataques recebidos |
| Desafiando a Morte | Personagem não morre ao 0 PV imediatamente |
| Efeitos Críticos (tabela) | Efeitos narrativos em acertos críticos (tabela d%) |
| Escalando Criaturas | Subir em criatura maior; ataques desvantajosos para o alvo |
| Falhas Críticas (tabela) | Efeitos em falhas críticas (tabela 4-6 extensa, p.305) |
| Lesões | Dano permanente; cicatrizes mecânicas |
| Mais Armas Ágeis | Expandir lista de armas ágeis |
| Lancinante Revisado | Revisão da habilidade Lancinante |
| Morte Alternativa | Morte como resultado narrativo, não só mecânico |
| Movimento Intercalado | Movimentação entre ataques |
| Posicionamento | Bônus por posição no campo de batalha |
| RD Combinada | Como calcular RD de múltiplas fontes |
| Saque Rápido Limitado | Limitação ao poder Saque Rápido |

### 11.9 Culinária Avançada (p.305–309)

Personagem treinado em Ofício (cozinheiro) pode preparar receitas com efeitos mecânicos:
- Fabricar bebida: teste CD 20; 1 dia = 1 bebida (ou 2 com −5 penalidade)
- Exemplos: Ovo de Monstro Frito (+1d4 em testes de For/Des/Con até fim do dia), Tempero Especial, receitas de regiões específicas

Impacto: sistema de receitas em `ficha_json.receitas_conhecidas: [...]`.

### 11.10 Exploração de Masmorras (p.310–313)

Sistema completo para expedições:
- **Objetivos:** não só matar monstros; recuperar artefatos, explorar, resgatar
- **Recursos:** controle concreto de comida, luz, equipamento
- **Portas e baús:** abrir trancados é mecânica presente; teste de Ladinagem/Força
- **Domínio de masmorras:** mapa e andares

Impacto: possível módulo de missão/expedição na arena.

### 11.11 Domínios (p.314–327)

Sistema completo de gestão territorial — o mais complexo do suplemento:

**Características dos Domínios (p.314–322):**
- Domínio tem: nome, tipo (aldeia/cidade/castelo/etc.), Renda, Segurança, Influência, Conhecimento
- Personagem pode ser Regente de 1 ou mais domínios
- **Tornar-se Regente (p.314):** requisitos e processo narrativo

**Turnos de Domínio (p.323–324):**
- Cada turno = 1 mês de jogo
- Ações disponíveis por turno: Construir, Recrutar, Espionar, Negociar, etc.

**Domínios Místicos (p.325):**
- Domínios com poderes mágicos; ex.: bosque feérico, masmorra amaldiçoada

**Eventos Aleatórios (p.325–327):**
- Tabela de eventos que afetam o domínio a cada turno

Impacto: novo modelo de dados `TormentaDominio` com relacionamento a `usuario_id` e `personagem_id`.

---

## PARTE 12 — TABELAS PARA PERSONAGENS (p.98–101)

Tabelas de rolagem para dar cor ao personagem:
- Nomes por raça/região
- Trejeitos e maneirismos
- Características físicas marcantes
- Histórico de família

Impacto: dados auxiliares para geração de personagem; `ficha_json.tabelas_personagem: {...}` opcional.

---

## PLANO DE IMPLEMENTAÇÃO — BACKLOG PRIORIZADO

### Fase HA-0 — Catálogo e flags (P0)

| ID | Requisito | Critério de aceite |
|----|-----------|-------------------|
| RF-HA00a | Flag `fonte_catalogo: core \| herois_arton` nos JSON de raças/classes | Raças core e suplemento separadas na API |
| RF-HA00b | Campo `game_suplemento: herois_arton` opcional em personagens | Ficha aceita criação com conteúdo do suplemento |
| RF-HA00c | Flag `regras_opcionais_ativas: [...]` na mesa/campanha | Backend valida poderes/regras opcionais apenas se flag ativo |

---

### Fase HA-1 — Novas raças (P1)

| ID | Requisito | Prioridade |
|----|-----------|------------|
| RF-HA01a | Catálogo de raças suplemento: Eiradaan, Galokk, Meio-Elfo, Sátiro | P1 |
| RF-HA01b | Modificadores conforme §1.1: Eiradaan (Sab+2/Car+1/For−1), Galokk (For+1/Con+1/+1livre/Car−1), Meio-Elfo (Int+1/+1×2 exceto Con), Sátiro (Car+2/Des+1/Sab−1) | P1 |
| RF-HA01c | Galokk: tamanho Grande → lógica de CA/manobras/armas aumentadas | P1 |
| RF-HA01d | Meio-Elfo: +1 PM a cada nível ímpar (incluindo 1º) | P1 |
| RF-HA01e | Eiradaan: atributo-chave de magia arcana = Sab (Magia Instintiva) | P1 |
| RF-HA01f | Duende: sistema de 5 passos modulares em `ficha_json.duende` | P2 |
| RF-HA01g | Duende: 12 Presentes no catálogo; pode trocar por poder de classe | P2 |
| RF-HA01h | Duende: 3 Limitações fixas aplicadas automaticamente | P2 |
| RF-HA01i | Duende: geração aleatória opcional (+2 PM bônus) | P3 |

---

### Fase HA-2 — Classe Treinador (P2)

| ID | Requisito | Prioridade |
|----|-----------|------------|
| RF-HA02a | Classe Treinador no catálogo (PV 12+Con/3+Con, PM 4×nível, perícias) | P2 |
| RF-HA02b | Melhor Amigo: 5 tipos; bônus por tipo; truques (15+) | P2 |
| RF-HA02c | Domar Criatura: teste de Adestramento vs Vontade; dano por nível | P2 |
| RF-HA02d | Poderes de Treinador: catálogo de 20 poderes | P2 |
| RF-HA02e | Limite de parceiros e regra Coração Grande | P3 |

---

### Fase HA-3 — Classes variantes e origens (P2)

| ID | Requisito | Prioridade |
|----|-----------|------------|
| RF-HA03a | 14 classes variantes no catálogo com `classe_variante_base` | P2 |
| RF-HA03b | UI de seleção exclui classe variante e classe base do mesmo grupo | P2 |
| RF-HA03c | 14 novas origens no catálogo com `fonte: herois_arton` | P2 |
| RF-HA03d | Origens com treinamento em perícia já treinada → trocar por outra de classe | P2 |

---

### Fase HA-4 — Novos poderes de classe e gerais (P2)

| ID | Requisito | Prioridade |
|----|-----------|------------|
| RF-HA04a | Novos poderes de classe para as 14 classes core no catálogo | P2 |
| RF-HA04b | Poderes de Raça: novo grupo; filtrar por raça do personagem na UI | P2 |
| RF-HA04c | Poderes de Grupo: grupo inteiro precisa ter o mesmo poder | P3 |
| RF-HA04d | Novos Poderes de Combate, Destino, Magia, Tormenta no catálogo | P2 |

---

### Fase HA-5 — Distinções (P2)

| ID | Requisito | Prioridade |
|----|-----------|------------|
| RF-HA05a | Modelo `distincao` em `ficha_json`: slug + admissão + poderes adquiridos | P2 |
| RF-HA05b | Catálogo de 36 distinções com admissão, pré-requisitos e árvore de poderes | P2 |
| RF-HA05c | UI de distinção na ficha: seção separada do wizard de criação | P2 |
| RF-HA05d | Poderes de distinção disponíveis na seleção de poder de classe | P2 |
| RF-HA05e | Validação de pré-requisito de raça (ex.: Aeronauta = goblin) | P2 |
| RF-HA05f | Flag `admissao_concluida` controlado pelo mestre | P3 |

---

### Fase HA-6 — Arsenal e equipamentos (P2)

| ID | Requisito | Prioridade |
|----|-----------|------------|
| RF-HA06a | Novas armas no catálogo com stats completos (§8.1) | P2 |
| RF-HA06b | Novos escudos (broquel, vime, torre) com RD/PV | P2 |
| RF-HA06c | Armadura de Pedra: RD 2 extra; deslocamento ÷ 2 | P2 |
| RF-HA06d | Capangas: modelo de NPC aliado vinculado ao personagem | P3 |
| RF-HA06e | Veículos: PV de veículo; pilotagem via Ofício (artesão) | P3 |

---

### Fase HA-7 — Magias e itens mágicos (P2–P3)

| ID | Requisito | Prioridade |
|----|-----------|------------|
| RF-HA07a | ~10 novas magias arcanas no grimório (§9) | P2 |
| RF-HA07b | Itens mágicos específicos no catálogo (Florete do Vendaval, Lança da Fênix) | P3 |
| RF-HA07c | Mobílias: modelo de `TormentaCômodo` com 1 mobília por cômodo | P3 |
| RF-HA07d | Itens Inteligentes: personalidade + comunicação + poderes secundários | P3 |
| RF-HA07e | Itens Amaldiçoados: efeitos negativos; identificação difícil | P3 |
| RF-HA07f | Artefatos: poder extremo; não fabricáveis | P3 |

---

### Fase HA-8 — Regras opcionais (P3)

| ID | Requisito | Prioridade |
|----|-----------|------------|
| RF-HA08a | Flag por mesa: `regras_opcionais_ativas: ["combate_avancado", "lesoes", ...]` | P3 |
| RF-HA08b | Complicações: lista por classe no catálogo; `ficha_json.complicacoes` | P3 |
| RF-HA08c | Idades Variadas: faixa etária + complicações por faixa | P3 |
| RF-HA08d | Objetivos Heroicos: campo na ficha + tracker de progresso | P3 |
| RF-HA08e | Papéis no Grupo: campo `papel_no_grupo` na ficha | P3 |
| RF-HA08f | Tabelas de Efeitos Críticos (d%): implementar como lookup table | P3 |
| RF-HA08g | Culinária Avançada: receitas no catálogo; efeito por receita | P3 |
| RF-HA08h | Sistema de Domínios: modelo `TormentaDominio` (Regente, Características, Turnos) | P3 |

---

## MODELO DE DADOS — EXTENSÕES NECESSÁRIAS

### Extensões em `ficha_json` (personagem)

```json
{
  "distincao": {
    "slug": "cavaleiro_do_corvo",
    "admissao_concluida": true,
    "poderes_adquiridos": ["lingua_dos_corvos", "assassinato_silencioso"]
  },
  "duende": {
    "natureza": "animal",
    "tamanho_raca": "medio",
    "dons": ["des", "car"],
    "presentes": ["invisibilidade", "voo", "lingua_da_natureza"],
    "tabu": "nunca_sentar_em_cadeiras"
  },
  "complicacoes": ["estrelismo"],
  "complicacoes_idade": ["peso_da_idade"],
  "faixa_etaria": "velho",
  "objetivo_heroico": {
    "descricao": "destruir o Lich do Norte",
    "progresso": 2
  },
  "papel_no_grupo": "advogado",
  "melhor_amigo": {
    "nome": "Rex",
    "tipo": "animal",
    "truques": ["alado", "amigao"],
    "nivel": 5
  }
}
```

### Novo modelo para Domínios

```
TormentaDominio
  id, usuario_id, personagem_id (regente)
  nome, tipo (aldeia|cidade|castelo|...)
  renda, seguranca, influencia, conhecimento
  turnos_json (histórico de turnos)
  eventos_json (eventos aleatórios)
  ativo: bool
```

---

## DEPENDÊNCIAS E RISCOS

| Item | Risco | Mitigação |
|------|-------|-----------|
| Duende modular | Alta complexidade de UI no wizard de criação | Implementar como sub-wizard em passos; validar servidor |
| Distinções (36) | Volume alto de dados a catalogar | Priorizar as 10 mais comuns; rest via dados JSON externos |
| Sistema de Domínios | Sistema complexo e autossuficiente | Implementar como módulo separado (feature flag) |
| Classes variantes | Exclusão mútua com classe base | Validação no backend em `regras/classe_t20.py` |
| Itens Inteligentes | Personalidade gera estado mutável | Armazenar em `ficha_json.itens_inteligentes_estado: {...}` |
| Poderes de Raça | Filtragem por raça na UI | Lookup simples via `raça → slug` no catálogo de poderes |

---

## REFERÊNCIAS CRUZADAS

| Arquivo relacionado | Conteúdo relevante |
|--------------------|-------------------|
| [02-races-tormenta.md](02-races-tormenta.md) | Raças core v1.3 (17 raças) — base para extensão com raças suplemento |
| [03-classes-tormenta.md](03-classes-tormenta.md) | Classes core — base para classes variantes e novos poderes de classe |
| [06-magia-tormenta.md](06-magia-tormenta.md) | Grimório MB — base para novas magias arcanas deste suplemento |
| [07-equipamento-tormenta.md](07-equipamento-tormenta.md) | Arsenal core — tabelas de armas/armaduras a estender |
| [08-poderes-tormenta.md](08-poderes-tormenta.md) | Poderes gerais — grupos Combate/Destino/Magia/Tormenta a estender |
| [09-origens-divindades-tormenta.md](09-origens-divindades-tormenta.md) | Origens core — lista a estender com origens especiais deste suplemento |
| [10-suplementos-opcionais.md](10-suplementos-opcionais.md) | Visão geral de suplementos (substituída por este doc para Heróis) |

---

## PLANO DE EXECUÇÃO TÉCNICA

> Gerado em 2026-07-04.  
> Caminho de referência: `backend/app/games/tormenta/`.  
> Convenções obrigatórias: [AGENTS.md](../../../../AGENTS.md) + [backend.instructions.md](../../instructions/backend.instructions.md) + [migrations.instructions.md](../../instructions/migrations.instructions.md).

---

### Visão geral do fluxo de dependência entre fases

```
HA-0 (flags/catálogos)
 └─► HA-1 (raças)  ──────────────────────────────────────────┐
      └─► HA-2 (Treinador)                                    │
      └─► HA-3 (variantes + origens)                          │
           └─► HA-4 (poderes de classe + gerais + raça)       │
                └─► HA-5 (distinções)  ◄──────────────────────┘
                └─► HA-6 (arsenal)
                └─► HA-7 (magias + itens mágicos)
                └─► HA-8 (regras opcionais)  ← exige migration em campanha
```

Cada fase só deve começar após a anterior estar **merged e com migration aplicada** em staging.

---

### Fase HA-0 — Catálogo e flags (P0 — bloqueia tudo)

**Objetivo:** Separar conteúdo core de suplemento sem quebrar fichas existentes.

#### 0.1 Contrato de dados — campo `fonte_catalogo`

Adicionar o campo `"fonte_catalogo": "herois_arton"` em **todos** os objetos de suplemento nos JSONs de catálogo. Valor padrão implícito para itens existentes: `"core"`.

Arquivos a editar:

| Arquivo | Ação |
|---------|------|
| `data/racas_v13.json` | Adicionar `"fonte_catalogo": "core"` nas raças existentes |
| `data/classes_v13.json` | Idem para todas as classes |
| `data/origens_v13.json` | Idem para todas as origens |
| `data/talentos_mb_catalogo.json` | Idem para poderes gerais existentes |

#### 0.2 Campo `game_suplemento` na ficha

- **`models/personagem.py`** — nenhuma coluna nova; o valor fica em `ficha_json["game_suplemento"]`.
- **`schemas/personagem.py`** — adicionar campo opcional `game_suplemento: Optional[str] = None` no schema de criação.
- **`rules/regra_versao_t20.py`** — adicionar constante `SUPLEMENTO_HEROIS_ARTON = "herois_arton"`.

#### 0.3 Flag `regras_opcionais_ativas` em campanha

- **`models/campanha.py`** — adicionar coluna `regras_opcionais_ativas = Column(JSON, nullable=True, default=list)`.
- **Migration:** `alembic revision --autogenerate -m "add_regras_opcionais_to_campanha"` via `Database and Migrations Specialist`.
- **`schemas/campanha.py`** — adicionar `regras_opcionais_ativas: Optional[List[str]] = None`.
- **`services/campanha_service.py`** — CRUD passa através do campo sem lógica adicional nesta fase.

#### 0.4 API

- `GET /api/tormenta/v1/regras/racas?suplemento=herois_arton` — filtro por `fonte_catalogo` via query param.
- `GET /api/tormenta/v1/regras/classes?suplemento=herois_arton` — idem.
- Endpoint existente `GET /regras/racas` continua retornando apenas `core` por padrão (compatibilidade).

---

### Fase HA-1 — Novas raças (P1)

#### 1.1 Arquivos novos

| Arquivo | Conteúdo |
|---------|----------|
| `data/racas_herois_arton.json` | Objeto com chave `"racas": [...]`; cada raça tem `slug`, `nome`, `fonte_catalogo: "herois_arton"`, `modificadores`, `tamanho`, `tipo`, `tracos` |
| `data/tracos_mecanicos_herois_arton.json` | Traços de cada raça no mesmo formato de `tracos_mecanicos_v13.json` |

#### 1.2 Estrutura JSON de exemplo — Eiradaan

```json
{
  "slug": "eiradaan",
  "nome": "Eiradaan",
  "fonte_catalogo": "herois_arton",
  "tipo": "espirito",
  "tamanho": "medio",
  "modificadores": {"sab": 2, "car": 1, "for": -1},
  "tracos": [
    {"slug": "magia_instintiva", "nome": "Magia Instintiva"},
    {"slug": "sentidos_misticos", "nome": "Sentidos Místicos"},
    {"slug": "cancao_melancolia", "nome": "Canção da Melancolia", "penalidade": true}
  ]
}
```

#### 1.3 Arquivos a editar

| Arquivo | Mudança |
|---------|---------|
| `rules/racas_t20.py` | `_carregar_racas()` → mesclar `racas_herois_arton.json` quando `suplemento=herois_arton` solicitado; `lru_cache` separado por versão+suplemento |
| `rules/tracos_raciais_t20.py` | Nova função `tracos_herois_arton(slug_raca, regra_versao)` lendo `tracos_mecanicos_herois_arton.json`; mesclar em `tracos_de_raca()` |
| `rules/progressao_pv_t20.py` | **Meio-Elfo:** `pm_bonus_meio_elfo(nivel) → +1 PM por nível ímpar` |
| `rules/conjuracao_t20.py` | **Eiradaan:** se `raca == "eiradaan"`, substituir `atributo_chave_magia` por `"sab"` para arcanistas |
| `rules/combate_t20.py` | **Galokk:** tamanho `"grande"` já tratado em lógica de manobras; verificar caminho e cobrir com teste |

#### 1.4 Duende (P2 — fase separada dentro de HA-1)

O sistema modular requer sub-objeto na ficha. Implementar em sub-fase após as 4 raças simples:

- **Schema:** `ficha_json.duende: DuendeConfig` (natureza, tamanho_raca, dons, presentes, tabu).
- **Rule:** `rules/duende_t20.py` — `validar_duende(config)`, `calcular_modificadores_duende(config)`, `presentes_disponiveis()`.
- **Data:** `data/presentes_duende.json` (12 presentes com slugs, custo PM, efeitos).
- **Motor de poderes:** estender `rules/poderes_ficha_v13_t20.py` para permitir trocar poder de classe por Presente (campo `fonte: "presente_duende"` na lista de poderes da ficha).

---

### Fase HA-2 — Classe Treinador (P2)

#### 2.1 Dados

| Arquivo | Mudança |
|---------|---------|
| `data/classes_v13.json` | Novo objeto `{"slug": "treinador", "fonte_catalogo": "herois_arton", "pv_base": 12, "pv_por_nivel": 3, "pm_por_nivel": 4, ...}` |
| `data/truques_melhor_amigo.json` | Catálogo dos 15+ truques com `slug`, `nome`, `descricao`, `pré_requisitos` |
| `data/tipos_melhor_amigo.json` | 5 tipos (animal, construto, espírito, monstro, morto-vivo) com bônus por tipo |

#### 2.2 Regras novas

| Arquivo | Conteúdo |
|---------|---------|
| `rules/melhor_amigo_t20.py` | `bonus_por_tipo_amigo(tipo)`, `truques_disponiveis(nivel_treinador)`, `calcular_melhor_amigo(ficha_json)` |
| `rules/domar_criatura_t20.py` | `dano_domar(nivel)` → tabela de dados por nível (2d8 → 10d8); `resolver_domar(teste_ad, teste_vontade, nivel)` |

#### 2.3 Schema de ficha

```python
class MelhorAmigoSchema(BaseModel):
    nome: str
    tipo: Literal["animal", "construto", "espirito", "monstro", "morto_vivo"]
    truques: List[str] = []
    nivel: int = 1
```

Adicionado em `ficha_json["melhor_amigo"]` (opcional; só presente em fichas de Treinador).

#### 2.4 API

- `GET /api/tormenta/v1/regras/truques-melhor-amigo` — lista truques disponíveis por nível.
- `GET /api/tormenta/v1/regras/tipos-melhor-amigo` — lista tipos com bônus.

---

### Fase HA-3 — Classes variantes e Origens (P2)

#### 3.1 Classes variantes

Campo novo em cada entrada de `data/classes_v13.json`:

```json
{
  "slug": "alquimista",
  "nome": "Alquimista",
  "fonte_catalogo": "herois_arton",
  "classe_variante_base": "inventor",
  "exclusivo_com": ["inventor", "inovador"]
}
```

**Validação no backend** (`rules/classes_t20.py` — nova função):
```python
def validar_classe_variante(slug_classe: str, ficha_json: dict) -> Optional[str]:
    """Retorna mensagem de erro se classe variante incompatível com classe atual."""
```

**Endpoint de criação de ficha** (`services/personagem_service.py`) deve chamar `validar_classe_variante` ao salvar.

#### 3.2 Origens especiais

| Arquivo | Mudança |
|---------|---------|
| `data/origens_herois_arton.json` | 14 origens com `fonte_catalogo: "herois_arton"`, perícias, bônus e flag `troca_pericia_treinada: true` |
| `rules/origens_t20.py` | Mesclar origens suplemento em `listar_origens(regra_versao, suplemento=None)` |

---

### Fase HA-4 — Novos poderes (P2)

#### 4.1 Arquivos de dados

| Arquivo | Conteúdo |
|---------|---------|
| `data/poderes_herois_arton.json` | Todos os poderes novos; cada entrada com `fonte_catalogo: "herois_arton"`, `categoria` e `raca_exigida` (quando Poder de Raça) |

#### 4.2 Novas categorias de poder

Estender `CATEGORIAS_PODER_V13` em `rules/poderes_catalogo_v13_t20.py`:

```python
CATEGORIAS_PODER_V13: List[str] = [
    ...,  # existentes
    "raca",    # Poderes de Raça (§6.5) — NOVO
    "grupo",   # Poderes de Grupo (§6.6) — NOVO
    "treinador",  # poderes da classe Treinador — NOVO
    "distincao",  # poderes de Distinção — NOVO (HA-5)
]
```

#### 4.3 Filtragem por raça

Em `rules/poderes_ficha_v13_t20.py`, na função que lista poderes disponíveis para seleção:
- Se categoria `raca`: incluir apenas se `poder["raca_exigida"] == ficha_json["raca"]`.
- Novos poderes de classe para as 14 classes core: adicionados diretamente em `data/poderes_herois_arton.json` com `categoria: "classe"` e `classe_exigida: "<slug>"`.

---

### Fase HA-5 — Distinções (P2)

#### 5.1 Arquivos de dados

| Arquivo | Conteúdo |
|---------|---------|
| `data/distincoes_herois_arton.json` | Catálogo das 36 distinções: `slug`, `nome`, `pagina`, `admissao_resumo`, `pre_requisitos: {raca?, classe?, outro?}`, `poderes: [{slug, nome, ...}]` |

Estrutura JSON:

```json
{
  "distincoes": [
    {
      "slug": "cavaleiro_do_corvo",
      "nome": "Cavaleiro do Corvo",
      "pagina": 139,
      "fonte_catalogo": "herois_arton",
      "admissao_resumo": "Encontrar o Ninho do Corvo; jurar a ordem; abrir mão do nome",
      "pre_requisitos": {},
      "poderes": [
        {"slug": "lingua_dos_corvos", "nome": "Língua dos Corvos", "pm": 0},
        {"slug": "assassinato_silencioso", "nome": "Assassinato Silencioso", "pm": 2}
      ],
      "campo_extra_ficha": "nome_anterior"
    }
  ]
}
```

#### 5.2 Regra nova

| Arquivo | Conteúdo |
|---------|---------|
| `rules/distincoes_t20.py` | `listar_distincoes()`, `poderes_de_distincao(slug)`, `validar_pre_requisito_distincao(slug, ficha_json) -> Optional[str]` |

#### 5.3 Extensão do schema de ficha

```python
class DistincaoFichaSchema(BaseModel):
    slug: str
    admissao_concluida: bool = False
    poderes_adquiridos: List[str] = []

# em FichaJsonSchema:
distincao: Optional[DistincaoFichaSchema] = None
```

#### 5.4 Motor de poderes — integração

Em `rules/poderes_ficha_v13_t20.py`: ao listar poderes disponíveis por patamar, se `ficha_json["distincao"]` existe e `admissao_concluida == True`, incluir poderes da distinção como opção no lugar de poder de classe.

#### 5.5 API

- `GET /api/tormenta/v1/regras/distincoes` — lista com filtro `?pre_requisito_raca=goblin`.
- `GET /api/tormenta/v1/regras/distincoes/{slug}/poderes` — árvore de poderes da distinção.

---

### Fase HA-6 — Arsenal (P2)

#### 6.1 Armas

| Arquivo | Mudança |
|---------|---------|
| `data/armas_herois_arton.json` | Novas armas com `fonte_catalogo: "herois_arton"`; mesmo schema de `armas_v13_overlay.json` |
| `rules/catalogo_armas_v13_t20.py` | Mesclar `armas_herois_arton.json` quando `suplemento=herois_arton` |

#### 6.2 Armaduras e escudos

| Arquivo | Mudança |
|---------|---------|
| `data/armaduras_herois_arton.json` | Novos escudos (broquel, vime, torre) e Armadura de Pedra; `fonte_catalogo: "herois_arton"` |
| `rules/catalogo_armaduras_t20.py` | Mesclar ao carregar com flag suplemento |
| `rules/penalidade_armadura_t20.py` | Armadura de Pedra: `deslocamento = deslocamento_base // 2` (não `- 3m`) |

---

### Fase HA-7 — Magias e itens mágicos (P2–P3)

#### 7.1 Magias

| Arquivo | Mudança |
|---------|---------|
| `data/magias_herois_arton.json` | ~10 magias arcanas; mesmo schema de `magias_mb_catalogo.json`; `fonte_catalogo: "herois_arton"` |
| `rules/grimorio_elegibilidade_t20.py` | Incluir magias suplemento na elegibilidade quando `game_suplemento == "herois_arton"` |

#### 7.2 Itens mágicos

| Arquivo | Mudança |
|---------|---------|
| `data/itens_magicos_herois_arton.json` | Catálogo com `tipo` (arma, armadura, acessorio, esoterico, mobilia, artefato), `maldito: bool`, `inteligente: bool` |
| `data/encantos_herois_arton.json` | Encantos para armaduras/escudos/esotéricos (Abissal, Caridoso, Chocante, etc.) |

> **Itens Inteligentes e Amaldiçoados** — implementar em P3 após itens comuns estarem no catálogo. Estado mutável de item inteligente vai em `ficha_json["itens_inteligentes_estado"][slug_item]`.

---

### Fase HA-8 — Regras opcionais (P3)

#### 8.1 Complicações

| Arquivo | Mudança |
|---------|---------|
| `data/complicacoes_herois_arton.json` | Por classe: `{"classe": "bardo", "complicacoes": [{"slug": "estrelismo", ...}]}` |
| `rules/complicacoes_t20.py` | `complicacoes_por_classe(slug_classe)`, `aplicar_complicacao(slug, ficha_json)` |
| `schemas/personagem.py` | `ficha_json["complicacoes"]: List[str]` |

#### 8.2 Idades Variadas

| Arquivo | Mudança |
|---------|---------|
| `rules/idades_t20.py` | `faixa_etaria_de_idade(anos)`, `complicacoes_por_faixa(faixa)` |
| `schemas/personagem.py` | `ficha_json["faixa_etaria"]: Optional[str]`, `ficha_json["complicacoes_idade"]: List[str]` |

#### 8.3 Objetivos Heroicos e Papéis no Grupo

Campos opcionais em `ficha_json`:
```json
{
  "objetivo_heroico": {"descricao": "...", "progresso": 0},
  "papel_no_grupo": "advogado"
}
```

Sem lógica de regra — apenas armazenar e expor via API. Validação de `papel_no_grupo` contra enum (lista fixa de papéis do suplemento).

#### 8.4 Sistema de Domínios (P3 — módulo independente)

**Novo model SQLAlchemy** (`models/dominio.py`):

```python
class TormentaDominio(Base):
    __tablename__ = "tormenta_dominios"
    id              = Column(Integer, primary_key=True)
    usuario_id      = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    personagem_id   = Column(Integer, ForeignKey("tormenta_personagens.id"), nullable=True)
    nome            = Column(String(120), nullable=False)
    tipo            = Column(String(40), nullable=False)   # aldeia|cidade|castelo|...
    renda           = Column(Integer, nullable=False, default=0)
    seguranca       = Column(Integer, nullable=False, default=0)
    influencia      = Column(Integer, nullable=False, default=0)
    conhecimento    = Column(Integer, nullable=False, default=0)
    mistico         = Column(Boolean, nullable=False, default=False)
    turnos_json     = Column(JSON, nullable=True, default=list)
    eventos_json    = Column(JSON, nullable=True, default=list)
    ativo           = Column(Boolean, nullable=False, default=True)
    created_at      = Column(DateTime(timezone=True), server_default=func.now())
```

**Migration:** `alembic revision --autogenerate -m "add_tormenta_dominios"` — delegar ao `Database and Migrations Specialist`.

**API:**
- `POST /api/tormenta/v1/dominios`
- `GET /api/tormenta/v1/dominios` (filtro por `personagem_id` ou `usuario_id`)
- `PATCH /api/tormenta/v1/dominios/{id}` (turno de domínio)

---

### Resumo de arquivos novos por fase

| Fase | Arquivos novos criados |
|------|----------------------|
| HA-0 | — (só edições + migration `campanha`) |
| HA-1 | `data/racas_herois_arton.json`, `data/tracos_mecanicos_herois_arton.json`, `rules/duende_t20.py`, `data/presentes_duende.json` |
| HA-2 | `data/truques_melhor_amigo.json`, `data/tipos_melhor_amigo.json`, `rules/melhor_amigo_t20.py`, `rules/domar_criatura_t20.py` |
| HA-3 | `data/origens_herois_arton.json` |
| HA-4 | `data/poderes_herois_arton.json` |
| HA-5 | `data/distincoes_herois_arton.json`, `rules/distincoes_t20.py` |
| HA-6 | `data/armas_herois_arton.json`, `data/armaduras_herois_arton.json` |
| HA-7 | `data/magias_herois_arton.json`, `data/itens_magicos_herois_arton.json`, `data/encantos_herois_arton.json` |
| HA-8 | `data/complicacoes_herois_arton.json`, `rules/complicacoes_t20.py`, `rules/idades_t20.py`, `models/dominio.py` + migration |

---

### Resumo de arquivos existentes modificados por fase

| Fase | Arquivo | Tipo de mudança |
|------|---------|----------------|
| HA-0 | `data/racas_v13.json` | Adicionar campo `fonte_catalogo: "core"` |
| HA-0 | `data/classes_v13.json` | Idem |
| HA-0 | `data/origens_v13.json` | Idem |
| HA-0 | `models/campanha.py` | Coluna `regras_opcionais_ativas JSON` |
| HA-0 | `schemas/campanha.py` | Campo `regras_opcionais_ativas` |
| HA-0 | `rules/regra_versao_t20.py` | Constante `SUPLEMENTO_HEROIS_ARTON` |
| HA-1 | `rules/racas_t20.py` | Mesclar JSON do suplemento |
| HA-1 | `rules/tracos_raciais_t20.py` | Traços das 4 novas raças |
| HA-1 | `rules/progressao_pv_t20.py` | Bônus PM Meio-Elfo |
| HA-1 | `rules/conjuracao_t20.py` | Magia Instintiva Eiradaan |
| HA-2 | `data/classes_v13.json` | Classe Treinador |
| HA-3 | `data/classes_v13.json` | 14 classes variantes |
| HA-3 | `rules/classes_t20.py` | `validar_classe_variante()` |
| HA-3 | `rules/origens_t20.py` | Mesclar origens suplemento |
| HA-4 | `rules/poderes_catalogo_v13_t20.py` | Categorias `raca`, `grupo`, `treinador`, `distincao` |
| HA-4 | `rules/poderes_ficha_v13_t20.py` | Filtro por `raca_exigida` |
| HA-5 | `rules/poderes_ficha_v13_t20.py` | Distinção como fonte de poder de classe |
| HA-6 | `rules/catalogo_armas_v13_t20.py` | Mesclar armas suplemento |
| HA-6 | `rules/catalogo_armaduras_t20.py` | Mesclar armaduras/escudos |
| HA-6 | `rules/penalidade_armadura_t20.py` | Armadura de Pedra |
| HA-7 | `rules/grimorio_elegibilidade_t20.py` | Magias suplemento |
| HA-8 | `schemas/personagem.py` | Campos opcionais novos em `ficha_json` |

---

### Contratos de API — endpoints novos

| Método | Caminho | Fase | Parâmetros relevantes |
|--------|---------|------|-----------------------|
| GET | `/regras/racas` | HA-0 | `?suplemento=herois_arton` retorna raças do suplemento |
| GET | `/regras/classes` | HA-0 | `?suplemento=herois_arton&variante=true` |
| GET | `/regras/origens` | HA-3 | `?suplemento=herois_arton` |
| GET | `/regras/poderes` | HA-4 | `?categoria=raca&raca=eiradaan` |
| GET | `/regras/distincoes` | HA-5 | `?pre_requisito_raca=goblin` |
| GET | `/regras/distincoes/{slug}/poderes` | HA-5 | — |
| GET | `/regras/truques-melhor-amigo` | HA-2 | `?nivel_treinador=5` |
| GET | `/regras/complicacoes` | HA-8 | `?classe=bardo` |
| POST | `/dominios` | HA-8 | body: `TormentaDominioCriarSchema` |
| GET | `/dominios` | HA-8 | `?personagem_id=123` |
| PATCH | `/dominios/{id}` | HA-8 | body: turno / atributos |

> Todos os endpoints novos ficam sob o prefixo existente `/api/tormenta/v1/`.

---

### Migrations necessárias (por ordem de execução)

| # | Nome sugerido | Fase | Tabela afetada |
|---|---------------|------|----------------|
| 1 | `add_regras_opcionais_to_campanha` | HA-0 | `tormenta_campanhas` |
| 2 | `add_tormenta_dominios` | HA-8 | criação de `tormenta_dominios` |

> Delegar ao `Database and Migrations Specialist`. Seguir regras de `migrations.instructions.md`: colunas novas `nullable=True` ou com `server_default`; SQLite-compatible na dev; PostgreSQL em staging/prod.

---

### Estratégia de testes mínimos por fase

| Fase | Teste obrigatório antes de merge |
|------|----------------------------------|
| HA-0 | `tests/tormenta/test_racas.py` — GET `/regras/racas` sem suplemento retorna apenas core |
| HA-1 | `tests/tormenta/test_racas_herois.py` — Eiradaan SAB como atributo de magia; Galokk tamanho Grande; Meio-Elfo +1 PM nível ímpar |
| HA-2 | `tests/tormenta/test_treinador.py` — Classe Treinador aparece em criação de ficha; `truques_disponiveis(nivel)` retorna lista correta |
| HA-3 | `tests/tormenta/test_classes_variantes.py` — `validar_classe_variante("alquimista", ficha_inventor)` → erro esperado |
| HA-4 | `tests/tormenta/test_poderes_herois.py` — poder de raça sem raça correta é filtrado; poder de raça com raça correta aparece |
| HA-5 | `tests/tormenta/test_distincoes.py` — `validar_pre_requisito_distincao("aeronauta_goblin", ficha_humano)` → erro; ficha goblin → OK |
| HA-6 | Catálogo de armas/armaduras contém novos itens; deslocamento Armadura de Pedra dividido por 2 |
| HA-7 | Novas magias aparecem no grimório de arcanistas com `game_suplemento == "herois_arton"` |
| HA-8 | Salvar campanha com `regras_opcionais_ativas`; salvar ficha com `objetivo_heroico`; CRUD de Domínio |

---

### Riscos e mitigações (complemento técnico)

| Risco | Mitigação técnica |
|-------|-------------------|
| `lru_cache` em funções de catálogo ignora parâmetro suplemento | Incluir `suplemento` como parâmetro de chave no cache; ou usar `functools.lru_cache` com tupla de args |
| Duende: UI complexa de 5 passos pode bloquear todo HA-1 | Implementar as 4 raças simples primeiro; Duende como sub-fase separada após merge |
| 36 distinções como volume de dados | Priorizar 10 distinções mais usadas no primeiro JSON; resto em PR subsequente |
| `ficha_json` sem validação de schema no banco | Adicionar `pydantic.validate_call` ou validação explícita no service antes de salvar campos novos |
| Classes variantes exclusão mútua em fichas multiclasse | Definir que o campo `classe_nivel` tem formato `"slug_nivel"` e checar todos os slugs ativos na ficha |

---

*Documento gerado em 2026-07-03 via extração de texto nativo (pdfplumber) do PDF T20-Herois-de-Arton-v1-1.pdf (332 páginas). Confirmado página a página. Conteúdo restrito a estrutura, fórmulas e remissão de página — sem reprodução de texto longo ou tabelas protegidas.*

*Plano de Execução Técnica adicionado em 2026-07-04.*
