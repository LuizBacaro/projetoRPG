# Requisitos funcionais — backlog Tormenta (Arena)

Prioridade: **P0** crítico para ficha utilizável; **P1** conforto; **P2** paridade com livro; **P3** arena/combate.

## P0 — Ficha e persistência

| ID | Requisito | Critérios de aceite |
|----|-----------|---------------------|
| RF-T00 | Personagem CRUD autenticado com `game_slug=tormenta` | Já coberto por testes API |
| RF-T01 | Atributos com modificador d20 coerente | Alterar valor atualiza modificador na UI |
| RF-T02 | `ficha_json` guarda perícias, ataques, equipamento, metadados de mesa | PATCH preserva chaves desconhecidas futuras |
| RF-T03 | Retrato do personagem (URL) persistido | `foto_url` preenchida na API e exibida na ficha quando HTTPS/relativo válido |

## P1 — Dados de apoio sem catálogo completo

| ID | Requisito | Critérios de aceite |
|----|-----------|---------------------|
| RF-T10 | Editor de pontos de atributo com validação por **tabela de custos** (livro) | Ficha mostra soma 8–18; **jogador**: salvar bloqueado se soma ≠ 20 ou valor fora de 8–18 (API + UI); monstro/NPC sem essa regra |
| RF-T11 | Exportar/importar JSON da ficha (backup) | Opcional; útil para mesa |

## P2 — Catálogos dinâmicos (paridade livro)

| ID | Requisito | Critérios de aceite |
|----|-----------|---------------------|
| RF-T20 | API + tabela `tormenta_pericias` (ou prefixo comum) | Listagem paginada; `pagina_referencia` opcional |
| RF-T21 | API + tabela `tormenta_poderes` (talentos T20) | Nome, tipo, pré-requisitos, texto; seed incremental |
| RF-T22 | API + tabela `tormenta_magias` | Círculo, escola/resistência, referência |
| RF-T23 | API + tabela `tormenta_equipamentos` | Slots, carga, preço em cobre |
| RF-T24 | Ligação personagem ↔ poder escolhido (N:N) | Similar `TalentoJogador` D&D |

### P2 — Grimório e conjuração MB (épico)

Rastreio detalhado (tipos/níveis, habilidade-chave, conhecidas, PM, preparar vs lançar, catálogo p.150–209): **[07-requisitos-grimorio-mb-144-209.md](07-requisitos-grimorio-mb-144-209.md)**.

| ID | Requisito | Critérios de aceite (resumo) |
|----|-----------|------------------------------|
| RF-T22 | Catálogo `tormenta_magias` / `tormenta_catalogo_magia` + API listagem | Círculo, tipo arcana/divina, metadados, `pagina_referencia`; sem texto integral protegido no repo |
| RF-T40–T47 | Motor grimório MB (círculos, chave, PM, preparação/espontâneo, UI) | Ver doc 07; fases G0–G5 |

## P3 — Combate e mestre

| ID | Requisito | Notas |
|----|-----------|--------|
| RF-T30 | Importar personagem Tormenta para arena | Depende modelo de combate T20 |
| RF-T31 | Condições e efeitos automáticos | Catálogo + motor |

## Decisões de produto em aberto

- **PM vs PA:** no modelo SQL usa-se `pa_max` / `pa_atual` para Pontos de Mana; na UI “PM”. Manter nome interno estável ou renomear coluna (migration) — documentar em ADR se mudar.
- **Multiclasse:** texto em `classe_nivel` vs tabela de classes — MVP texto.

---

## Backlog v1.3 (`REGRA_VERSAO_V13`)

Rastreio transversal da Edição Jogo do Ano. Detalhe por domínio: `.cursor/requisitos/tormenta/*.md`.

### Equipamento (Cap. 3)

| ID | Requisito | Prioridade | Critérios de aceite |
|----|-----------|------------|---------------------|
| RF-T07a-1 | Stats de **todas** as armas do catálogo MB (~100 itens) alinhadas v1.3 Tabela 3-3 | **Feito** | Core ~56 itens; legacy MB documentado (Cajado, Estilingue, Wakizashi, mangual, martelo leve, arco composto) |
| RF-T07a-2 | Modal equipamentos na ficha: exibir **espaços** e **proficiência** | **Feito** | Terceira coluna v1.3 no modal (`proficiencia`, `empunhadura`, `espacos`, CA/pen.) |
| RF-T07g-1 | **Tabela 3-1** — dinheiro inicial por nível (> 1º) | **Feito** | `dinheiro_inicial_v13.json`, API `GET /dinheiro-inicial`, wizard passo 7 e ficha nv>1 |
| RF-T07h-1 | Limite **4 vestidos / 2 empunhados** (p.141) | **Feito** | `limites_equipamento_v13_t20.py`, `t20-limites-equipamento-v13.js`, ficha |
| RF-T07e-1 | Proficiência armadura: penalidade em **todas** perícias For/Des se não proficiente | **Feito** | `proficiencia_armadura_t20.py`, API `tormenta_classe_mb_slug`, ficha + rolador |
| RF-T07d-1 | Arena/combate: CA do alvo soma armaduras do inventário equipado | **Feito** | `ca_efetiva_personagem()` + status/ataque combate |

### Construção de personagem (Cap. 1–2)

| ID | Requisito | Prioridade | Notas |
|----|-----------|------------|-------|
| RF-T01-v13 | Atributos v1.3: valor direto, compra 10 pts Tabela 1-1, 4d6 soma ≥ 6 | **Feito** | Backend + UI/mesa nativa — RF-T01-ui-a…m; RF-T01-ui-n migração pendente |
| RF-T03-v13 | **14 classes** v1.3: PV/PM por fórmula, ocultar legado MB | **Feito** | `classes_v13.json`, API `regra_versao=v13`, wizard/ficha, PM no painel classe |
| RF-T03-v13b | Arcanista: caminho Bruxo/Mago/Feiticeiro | **Feito** | Wizard + ficha + validação salvar |
| RF-T03-v13c | PM multiclasse (soma nível × pm/nível) | **Feito** | API `POST /pm-preview-multiclasse`, UI `multiclasse_v13` na ficha, soma automática PM |
| RF-T03-v13d | Subir nível multiclasse (escolha de classe, PV/PM p.34) | **Feito** | Preview/aplicar com `classe_slug`; atualiza `multiclasse_v13` e nível total |
| RF-T04-v13 | Percepção passiva na UI | **Feito** | Cartão «Pass.» + hint; `t20-percepcao-passiva.js` |
| RF-T08-v13 | Poderes (ex-talentos): nomenclatura, categorias p.124–136, PM ao ativar | **Feito** | `categoria_v13` + filtro modal; `POST /poderes/ativar`; botão Ativar na ficha |
| RF-T09-v13 | Poderes concedidos por deus (Tabela 1-20) + validação devoção | **Feito** | Catálogo Os Vinte + API identidade-mb; wizard passo 6 + ficha; clérigo/druida/paladino obrigatórios |
| RF-T02-v13 | Escolhas raciais P2 (17 raças — escolhas + traços) | **Feito** | `escolhas_raciais_v13.json`, API, ficha + wizard |
| RF-T02g | Tamanho/deslocamento automático (17 raças, exceções) | **Feito** | Preview + ficha + wizard; `tamanho_racial_*` no JSON |
| RF-T04-v13b | Ofício: especialidades múltiplas | **Feito** | `oficio_especialidades[]` + UI tags na ficha v1.3 |

### Raças — fora de escopo (habilidades avançadas P2)

| ID | Item | Prioridade |
|----|------|------------|
| RF-T02-oos1 | Golem: sem origem; pen. armadura −2; armadura acoplada | P2 |
| RF-T02-oos2 | Osteon: raça ancestral alternativa (Memória Póstuma) | P2 |
| RF-T02-oos3 | Hynne: Atletismo DES; Sorte Salvadora (PM) | P2 |
| RF-T02-oos4 | Trog: Furtividade +5 sem armadura pesada | P2 |

### Equipamento / origens / classes — próxima fila

| ID | Requisito | Prioridade | Notas |
|----|-----------|------------|-------|
| RF-T09d | Itens grátis origem no equipamento (wizard passo 7 + ficha) | **Feito** | Sync SQL + preview UI origem/kit |
| RF-T09h | Obrigações/restrições divindade (flags + p. livro) | **Feito** | `divindades_obrigacoes_v13.json`, API + wizard/ficha |

### Combate e mesa (Cap. 5)

| ID | Requisito | Prioridade | Notas |
|----|-----------|------------|-------|
| RF-T05-v13 | Condições vs lista p.394 v1.3 | **Feito** | `condicoes_v13_catalogo.json`, `condicoes_t20.py`, API `GET /condicoes`, arena |
| RF-T05-v13b | Morte / 0 PV | **P3** | Ver `05-combate-tormenta.md` |
| RF-T05-v13c | Arma não proficiente: −5 ataque | **Feito** | `proficiencia_arma_t20.py`, API `POST /ataque/ajustar-bonus`, ficha + `t20-proficiencia-arma.js` |
| RF-T30-v13 | Import personagem v1.3 para arena com stats corretos | **P3** | RF-T30 estendido |

### Magia (Cap. 4)

| ID | Requisito | Prioridade | Notas |
|----|-----------|------------|-------|
| RF-T06-v13 | CD magia / RM com **valor** de atributo (não mod MB) | **Feito** | `cd_resistencia_magia_t20` v13; preview grimório com fórmula na UI |
| RF-T06-v13b | PM universal em habilidades de classe | **Feito** | Pool `pa_atual`/`pa_max` compartilhado magias + poderes |

### Documentação / dívida técnica

| ID | Requisito | Prioridade | Notas |
|----|-----------|------------|-------|
| RF-DOC-v13 | Atualizar `_meta.fonte` e secções **Gap código** desatualizadas (ex.: `09-origens-divindades-tormenta.md`) | **P2** | Refletir wizard 8 passos e itens já feitos |

### UX mesa (benchmark Roll20)

Documento canónico: **[.cursor/requisitos/tormenta/12-inspiracao-roll20-ux-mesa.md](../.cursor/requisitos/tormenta/12-inspiracao-roll20-ux-mesa.md)**.

| ID | Requisito | Prioridade | Notas |
|----|-----------|------------|-------|
| RF-T12a | Breakdown PV/CA/perícias/ataques na ficha | **P0** | PV parcialmente feito |
| RF-T12b | Drag-and-drop catálogo → ficha | **P0** | Poderes, equipamento, grimório |
| RF-T12c | Rolagem contextual (perícia/ataque) | **P0** | API existe; UX incompleta |
| RF-T12d | Condições → rolagens arena | **P1** | Alinha RF-T05c |
| RF-T12e | Ficha NPC compacta na arena | **P1** | |
| RF-T12f | Handouts (mestre revela para jogadores) | **P1** | |
| RF-T12g–k | Monstro→NPC, sync ficha↔arena, layout compacto, log, convite | **P2** | |
| RF-T12l | Mapa VTT / tokens / fog | **P3** | Escopo separado |

### Ameaça (NPC / monstro — bloco estilo livro)

Documento canónico: **[.cursor/requisitos/tormenta/13-construcao-npc-monstro.md](../.cursor/requisitos/tormenta/13-construcao-npc-monstro.md)**.

| ID | Requisito | Prioridade | Notas |
|----|-----------|------------|-------|
| RF-T13a–e | `ficha_json.ameaca`, motor bloco, GET/POST API, UI ficha | **P0** | **Feito** (sem tabela nova; sem LLM) |
| RF-T13f | Converter PJ → cópia ameaça | **P1** | **Feito** |
| RF-T13g | Dashboard + ND na arena compacta | **P2** | **Feito** |
