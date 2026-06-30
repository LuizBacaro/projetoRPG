# FEATURE: Origens, Divindades e Identidade (T20 v1.3)

> **Fontes:**  
> - `Tormenta20-Edicao-Jogo-do-Ano-v1.3.pdf` — Origens p.85–105 (**Tabela 1-19**); Deuses p.96–109 (**Tabela 1-20**); Alinhamento p.109–111  
> - `T20-Deuses-de-Arton-v1-1.pdf` — Panteão expandido, devoção, Frade, distinções p.142+

## Descrição

Passo de **origem** na construção (passo 6); **devoção** opcional a um de **Os Vinte**; **alinhamento** como guia narrativo. Origem concede itens, perícias treinadas e poderes gerais.

## Origens — regras (p.85)

| Regra | Detalhe |
|-------|---------|
| Escolha | Uma origem além de raça e classe |
| **Benefícios** | Escolher **2** da lista: 2 perícias, 2 poderes, ou **1 perícia + 1 poder** |
| Perícia | Torna-se **treinada** (+2/+4/+6 conforme nível — ver `04-pericias-tormenta.md`) |
| Poder | Poder geral da lista; cumprir pré-requisitos |
| **Poder único** | Cada origem tem 1 poder exclusivo; **pode** ser um dos 2 benefícios |
| **Itens** | Itens listados na origem **grátis** (não pagar preço de tabela) |
| Regras rápidas | Mesa pode limitar a só perícias |
| **Amnésico** | Exceção: mestre escolhe 1 perícia + 1 poder + poder **Lembranças Graduais** |
| Origem custom | «Sua Própria Origem» (p.94–95): negociar com mestre — trocar perícias, itens, inventar poder único |

## Tabela 1-19 — 35 origens (p.86)

Índice para catálogo JSON (`slug`, `itens[]`, `beneficios_pericias[]`, `beneficios_poderes[]`, `poder_unico`, `pagina`). Texto flavor no PDF — não replicar no repo.

| Origem | slug | Benefícios (resumo) |
|--------|------|---------------------|
| Acólito | `acolito` | Cura, Religião, Vontade; Medicina, Membro da Igreja, Vontade de Ferro |
| Amigo dos Animais | `amigo_animais` | Adestramento, Cavalgar; Amigo Especial |
| Amnésico | `amnesico` | Mestre escolhe 1 perícia + 1 poder + Lembranças Graduais |
| Aristocrata | `aristocrata` | Diplomacia, Enganação, Nobreza; Comandar, Sangue Azul |
| Artesão | `artesao` | Ofício, Vontade; Frutos do Trabalho, Sortudo |
| Artista | `artista` | Atuação, Enganação; Atraente, Dom Artístico, Sortudo, Torcida |
| Assistente de Laboratório | `assistente_laboratorio` | Ofício (alquimista), Misticismo; Esse Cheiro..., Venefício, 1 poder da Tormenta |
| Batedor | `batedor` | Furtividade, Percepção, Sobrevivência; À Prova de Tudo, Estilo de Disparo, Sentidos Aguçados |
| Capanga | `capanga` | Luta, Intimidação; Confissão, 1 poder de combate |
| Charlatão | `charlatao` | Enganação, Jogatina; Alpinista Social, Aparência Inofensiva, Sortudo |
| Circense | `circense` | Acrobacia, Atuação, Reflexos; Acrobático, Torcida, Truque de Mágica |
| Criminoso | `criminoso` | Enganação, Furtividade, Ladinagem; Punguista, Venefício |
| Curandeiro | `curandeiro` | Cura, Vontade; Medicina, Médico de Campo, Venefício |
| Eremita | `eremita` | Misticismo, Religião, Sobrevivência; Busca Interior, Lobo Solitário |
| Escravo | `escravo` | Atletismo, Fortitude, Furtividade; Desejo de Liberdade, Vitalidade |
| Estudioso | `estudioso` | Conhecimento, Guerra, Misticismo; Aparência Inofensiva, Palpite Fundamentado |
| Fazendeiro | `fazendeiro` | Adestramento, Cavalgar, Ofício (fazendeiro), Sobrevivência; Água no Feijão, Ginete |
| Forasteiro | `forasteiro` | Cavalgar, Pilotagem, Sobrevivência; Cultura Exótica, Lobo Solitário |
| Gladiador | `gladiador` | Atuação, Luta; Atraente, Pão e Circo, Torcida, 1 poder de combate |
| Guarda | `guarda` | Investigação, Luta, Percepção; Detetive, Investigador, 1 poder de combate |
| Herdeiro | `herdeiro` | Misticismo, Nobreza, Ofício; Comandar, Herança |
| Herói Camponês | `heroi_campones` | Adestramento, Ofício; Coração Heroico, Sortudo, Surto Heroico, Torcida |
| Marujo | `marujo` | Atletismo, Jogatina, Pilotagem; Acrobático, Passagem de Navio |
| Mateiro | `mateiro` | Atletismo, Furtividade, Sobrevivência; Lobo Solitário, Sentidos Aguçados, Vendedor de Carcaças |
| Membro de Guilda | `membro_guilda` | Diplomacia, Enganação, Misticismo, Ofício; Foco em Perícia, Rede de Contatos |
| Mercador | `mercador` | Diplomacia, Intuição, Ofício; Negociação, Proficiência, Sortudo |
| Minerador | `minerador` | Atletismo, Fortitude, Ofício (minerador); Ataque Poderoso, Escavador, Sentidos Aguçados |
| Nômade | `nomade` | Cavalgar, Pilotagem, Sobrevivência; Lobo Solitário, Mochileiro, Sentidos Aguçados |
| Pivete | `pivete` | Furtividade, Iniciativa, Ladinagem; Acrobático, Aparência Inofensiva, Quebra-Galho |
| Refugiado | `refugiado` | Fortitude, Reflexos, Vontade; Estoico, Vontade de Ferro |
| Seguidor | `seguidor` | Adestramento, Ofício; Antigo Mestre, Proficiência, Surto Heroico |
| Selvagem | `selvagem` | Percepção, Reflexos, Sobrevivência; Lobo Solitário, Vida Rústica, Vitalidade |
| Soldado | `soldado` | Fortitude, Guerra, Luta, Pontaria; Influência Militar, 1 poder de combate |
| Taverneiro | `taverneiro` | Diplomacia, Jogatina, Ofício (cozinheiro); Gororoba, Proficiência, Vitalidade |
| Trabalhador | `trabalhador` | Atletismo, Fortitude; Atlético, Esforçado |

Persistir em `ficha_json`: `origem.slug`, `origem_beneficios: ["pericia:furtividade", "poder:lobo_solitario"]` (exemplo).

## Deuses e devoção (p.96–109)

### Regras

| Regra | Detalhe |
|-------|---------|
| Devoto | Personagem que serve a uma divindade — **opcional** (exceto clérigo, druida, paladino: devoto automático) |
| Quando escolher | Criação ou ao subir de nível |
| **Uma devoção** | Não muda (salvo critério do mestre) |
| Elegibilidade | Raça **ou** classe na lista «Devotos» do deus; **humanos** e **clérigos** = qualquer deus |
| Benefício | **1 poder concedido** da lista do deus + cumprir **Obrigações & Restrições** |
| Violação | Perde **todos** PM; recupera no dia seguinte; 2ª violação na mesma aventura → penitência (Religião) |
| Multiclasse | Classe com menos opções de devoção impõe limite; incompatível = multiclasse bloqueada |
| Paladino | Devoto de deus disponível para paladinos; campeão **bem e ordem** (Introdução item 17) |

### Campos por divindade (catálogo)

`slug`, `rotulo`, `energia` (positiva/negativa/qualquer), `poderes_concedidos[]` (4 slugs), `devotos` (raças/classes resumidas), `obrigacoes_flags[]`, `pagina`. Texto de crenças/obrigações: remissão PDF, não no repo.

### Tabela 1-20 — Os Vinte (p.96)

| Divindade | slug | Energia | Poderes concedidos (índice) |
|-----------|------|---------|----------------------------|
| Aharadak | `aharadak` | Negativa | Afinidade com a Tormenta, Êxtase da Loucura, Percepção Temporal, Rejeição Divina |
| Allihanna | `allihanna` | Positiva | Compreender os Ermos, Dedo Verde, Descanso Natural, Voz da Natureza |
| Arsenal | `arsenal` | Qualquer | Conjurar Arma, Coragem Total, Fé Guerreira, Sangue de Ferro |
| Azgher | `azgher` | Positiva | Espada Solar, Fulgor Solar, Habitante do Deserto, Inimigo de Tenebra |
| Hyninn | `hyninn` | Qualquer | Apostar com o Trapaceiro, Farsa do Fingidor, Forma de Macaco, Golpista Divino |
| Kallyadranoch | `kallyadranoch` | Negativa | Aura de Medo, Escamas Dracônicas, Presas Primordiais, Servos do Dragão |
| Khalmyr | `khalmyr` | Positiva | Coragem Total, Dom da Verdade, Espada Justiceira, Reparar Injustiça |
| Lena | `lena` | Positiva | Ataque Piedoso, Aura Restauradora, Cura Gentil, Curandeira Perfeita |
| Lin-Wu | `lin_wu` | Qualquer | Coragem Total, Kiai Divino, Mente Vazia, Tradição de Lin-Wu |
| Marah | `marah` | Positiva | Aura de Paz, Dom da Esperança, Palavras de Bondade, Talento Artístico |
| Megalokk | `megalokk` | Negativa | Olhar Amedrontador, Presas Primordiais, Urro Divino, Voz dos Monstros |
| Nimb | `nimb` | Qualquer | Êxtase da Loucura, Poder Oculto, Sorte dos Loucos, Transmissão da Loucura |
| Oceano | `oceano` | Qualquer | Anfíbio, Arsenal das Profundezas, Mestre dos Mares, Sopro do Mar |
| Sszzaas | `sszzaas` | Negativa | Astúcia da Serpente, Familiar Ofídico, Presas Venenosas, Sangue Ofídico |
| Tanna-Toh | `tanna_toh` | Qualquer | Conhecimento Enciclopédico, Mente Analítica, Pesquisa Abençoada, Voz da Civilização |
| Tenebra | `tenebra` | Negativa | Carícia Sombria, Manto da Penumbra, Visão nas Trevas, Zumbificar |
| Thwor | `thwor` | Qualquer | Almejar o Impossível, Fúria Divina, Olhar Amedrontador, Tropas Duyshidakk |
| Thyatis | `thyatis` | Positiva | Ataque Piedoso, Dom da Imortalidade, Dom da Profecia, Dom da Ressurreição |
| Valkaria | `valkaria` | Positiva | Almejar o Impossível, Armas da Ambição, Coragem Total, Liberdade Divina |
| Wynna | `wynna` | Qualquer | Bênção do Mana, Centelha Mágica, Escudo Mágico, Teurgista Místico |

> **Panteão MB antigo:** Keenn, Tauron, Ragnar etc. **fora** do core v1.3; **Aharadak**, **Arsenal**, **Thwor** **entram**. Backend `tendencias_divindades_mb.json` já lista Os Vinte com slugs — revisar `_meta.fonte` e poderes concedidos.

## Alinhamento (p.109–111)

| Aspecto | Regra v1.3 |
|---------|------------|
| Efeito mecânico | **Nenhum** — guia de interpretação |
| Eixos | Ético (Bem / Neutro / Mal) × Moral (Leal / Neutro / Caótico) → 9 tendências |
| Classe | Sem restrição por alinhamento (**exceto paladino** = bem e ordem) |
| Devoção | Obedecer deus **>** compatibilidade de alinhamento |
| UI | Combo opcional; persistir `tendencia` como rótulo (9 valores MB compatíveis) |

## Suplemento Deuses de Arton (escopo estendido)

| Conteúdo | p. | Prioridade Arena |
|----------|-----|------------------|
| Novos Poderes Concedidos | 42 | P1 |
| Deuses e Avatares (20 maiores) | 142–224 | P1 |
| Campeões / classes divinas | 8–32 | P2 |
| Classe **Frade** | 38 | P3 |
| Deuses Menores / Antigos | 228+ | P3 |
| Distinções | 66–139 | P3 |

## Requisitos funcionais

| ID | Requisito | Prioridade |
|----|-----------|------------|
| RF-T09a | Campo `origem` em `ficha_json` + UI passo construção | P1 |
| RF-T09b | Catálogo **35 origens** v1.3 + endpoint `GET /tormenta/regras/origens` | P1 |
| RF-T09c | Escolha de 2 benefícios + validação perícia/poder | P1 |
| RF-T09d | Itens de origem na criação (grátis) | **Feito** |
| RF-T09e | `GET /tormenta/regras/identidade-mb` → tendências + divindades v1.3 | P0 |
| RF-T09f | Select divindade (`slug` + `rotulo`); flag `devoto: boolean` | P0 |
| RF-T09g | Poder concedido vinculado à divindade escolhida | P1 |
| RF-T09h | Obrigações/restrições (flags + link página PDF) | **Feito** |
| RF-T09i | `_meta` e listas alinhadas Tabela 1-20 (Os Vinte) | P1 |
| RF-T09j | Amnésico + origem custom (modo Mesa / notas) | P3 |
| RF-T09k | Suplemento: distinções, Frade, deuses menores | P3 |

## Estado de implementação

| Item | Estado |
|------|--------|
| Tendências + divindades JSON (20 entradas) | **Feito** |
| API identidade-mb (`poderes_concedidos[]`, `energia`, truque devoção) | **Feito** |
| UI combos tendência/divindade + poder concedido filtrado | **Feito** |
| Validação devoção v1.3 (backend + wizard + ficha) | **Feito** |
| Clérigo/druida/paladino: devoção obrigatória | **Feito** |
| Sync SQL poder concedido (`auto:v13:concedido:*`) | **Feito** |
| **Origens** (35) catálogo + API | **Feito** |
| Origem UI wizard/ficha + benefícios | **Feito** |
| Itens grátis origem na criação | **Feito** (RF-T09d) |
| Obrigações/restrições (flags + link PDF) | **Feito** (RF-T09h) |
| `_meta.fonte` v1.3 | **Feito** |

## Gap código

- Paladino: aviso narrativo «bem e ordem» na UI (não bloqueio rígido) — **Feito** (hint wizard + ficha).

## Critérios de aceite

- Divindade persistida como `rotulo` + `slug` estável (Os Vinte v1.3).
- Origem persistida com slug + 2 benefícios rastreáveis.
- Lista de divindades na ficha = 20 deuses da Tabela 1-20 (não panteão pré-Jogo do Ano).
- Sem texto longo de preces/obrigações no repositório.
- Poder concedido selecionado ⊆ lista do deus escolhido.

## Referência

- Dados: `tendencias_divindades_mb.json`, `rules/tendencias_divindades_t20.py`
- Cross-ref: `08-poderes-tormenta.md`, `07-equipamento-tormenta.md` (itens iniciais)
- Docs: `docs/tormenta/00-visao-e-fontes-legais.md`
