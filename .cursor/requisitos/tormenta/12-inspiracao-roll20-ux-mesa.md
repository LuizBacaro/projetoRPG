# FEATURE: Inspiração Roll20 — UX de mesa e ficha (Tormenta 20 v1.3)

> **Referência externa:** [Roll20](https://roll20.net) — VTT comercial (Journal, Compendium, Character Builder, automação na ficha).  
> **Escopo Arena:** absorver **padrões de UX e automação** alinhados ao T20 v1.3; **não** replicar mapa/token/iluminação como produto principal nesta fase.  
> **Código:** `frontend/games/tormenta/`, `backend/app/games/tormenta/`, arena no `dashboard.html`.

## Descrição

Documento de benchmark e backlog para aproximar a experiência de mesa do Arena à de plataformas VTT maduras (Roll20 como referência), **sem** copiar assets, texto de livros ou fichas proprietárias de terceiros.

Objetivo: mesa mais fluida (menos digitação manual, mais regras aplicadas na UI) mantendo a arquitetura atual — motor em `rules/` + catálogos JSON + API `/tormenta/regras/*` + Postgres por personagem.

## O que o Roll20 oferece (resumo para benchmark)

| Área Roll20 | Comportamento típico |
|-------------|---------------------|
| **Compendium** | Busca de regras/itens/magias/monstros; drag-and-drop para ficha ou mesa |
| **Character Builder** | Wizard passo a passo; opções filtradas pelo conteúdo licenciado |
| **Ficha automatizada** | Equipado/atado altera bônus; condições ligam a rolagens; breakdown visível |
| **Journal / Handouts** | Mestre revela texto/imagem para um ou todos os jogadores |
| **NPC sheet** | Vista compacta para inimigos (stats + ataques + iniciativa) |
| **Chat / macros** | Rolagens com contexto; botões na ficha disparam no chat |
| **VTT** | Mapa, tokens, grid, fog of war, iluminação dinâmica |
| **API Pro** | Scripts do mestre (automação avançada) |

## Arena hoje (baseline)

| Área | Estado Tormenta |
|------|-----------------|
| Ficha v1.3 + wizard dashboard | **Feito** (raça, origem, classe, atributos, kit, grimório parcial) |
| Motor regras backend | **Forte** — PV/PM, perícias, conjuração, equipamento, poderes |
| Catálogo via API | **Feito** — sem duplicar JSON no frontend |
| PV automático por classe/CON | **Feito** — cálculo local na ficha (`t20-progressao-pv.js`) |
| PM multiclasse | **Feito** — `multiclasse_v13` + preview API |
| Arena combate | **Parcial** — iniciativa, ataque, dano, condições MB, concentração |
| Drag-and-drop compendium → ficha | **Feito** (equip, poder, magia, consumível) |
| Handouts / revelar para jogadores | **Não feito** |
| Sincronização ficha ↔ arena tempo real | **Parcial** (D&D 3.5 `BroadcastChannel`; Tormenta limitado) |
| Mapa / tokens / iluminação | **Fora de escopo** neste RF |

## Princípios de implementação

1. **Fonte de verdade:** catálogos em `backend/app/games/tormenta/data/` + `GET /tormenta/regras/*`; ficha consome API autenticada.
2. **Automação = motor existente:** UI chama `rules/`; evitar fórmulas duplicadas divergentes (paridade JS só para preview instantâneo, como PV).
3. **Licença:** metadados e remissão ao livro; sem colar texto longo do Roll20 nem de PDFs no repo.
4. **MVP incremental:** cada RF entrega valor na ficha ou na arena sem exigir VTT completo.

## Requisitos funcionais

| ID | Requisito | Prioridade | Inspiração Roll20 |
|----|-----------|------------|-------------------|
| RF-T12a | **Breakdown visível** em PV, CA, perícias e ataques (fórmula expandida + hint) | P0 | Efeitos ativos / tooltip de cálculo |
| RF-T12b | **Catálogo → ficha por drag-and-drop** (poder, magia, equipamento) com preenchimento automático | P0 | Compendium drag to sheet |
| RF-T12c | **Rolagem contextual** — clicar perícia/ataque na ficha ou arena dispara `pericias/rolar` / combate com bônus já aplicados | P0 | Macro / botão na ficha |
| RF-T12d | **Condições alteram rolagens** na arena (ataque, CA, perícias afetadas) conforme p.394 v1.3 | P1 | Condition toggles |
| RF-T12e | **Ficha NPC compacta** na arena (PV, CA, ataques, iniciativa; sem wizard) | P1 | NPC Compact view |
| RF-T12f | **Handouts** — mestre cria/revela notas ou imagem para jogador(es) da campanha | P1 | Journal handouts + Show to players |
| RF-T12g | **Import monstro/catálogo → combatente** na arena (a partir de entrada futura `tormenta_bestiary` ou stub) | P2 | Drag monster to tabletop |
| RF-T12h | **Sincronização ficha ↔ arena** (PV/PM/condições) via `BroadcastChannel` ou WebSocket leve | P2 | Token HP sync |
| RF-T12i | **Layout ficha compacto** (toggle vista resumida vs completa) | P2 | Condensed player sheet |
| RF-T12j | **Log de mesa** — histórico de rolagens e ações na sessão de combate | P2 | Chat log |
| RF-T12k | **Convite de campanha** — link com token; jogador entra na campanha/mesa do mestre | P2 | Join link |
| RF-T12l | **Mapa + tokens + fog of war** | P3 | Tabletop core (escopo separado) |
| RF-T12m | **Marketplace / conteúdo pago** | — | Fora de escopo Arena |

### RF-T12a — Breakdown visível (detalhe)

- PV: `#fichaPvBreakdown` (fórmula classe + CON + multiclasse).
- **CA** (`#fichaCaBreakdown` + `title` em `#fichaCa`) — base 10 + DES + cada item de proteção por nome; pesada zera DES.
- **Perícias** — coluna **Σ** com bônus total; fórmula expandida no `title` da célula (atributo + ½ nv + treino + outros + racial − pen.).
- **Ataques** — planilha CAC/Dist (`#t20AtqCacBreakdown`, `#t20AtqDistBreakdown`) e tooltip por arma na lista.
- Critério: alterar CON, classe ou equipamento atualiza breakdown **sem** salvar a ficha.

### RF-T12b — Drag-and-drop compendium (detalhe)

- Modais existentes (equipamentos, poderes, grimório, consumíveis) aceitam **arrastar** item da lista para zona de destino na ficha.
- **Duplo clique** na linha do catálogo equivale ao botão «Adicionar».
- Zonas de drop: `#fichaEquipamentos`, `#t20FichaTalentosMb`, `#t20FichaConsumiveis`, `#t20GrimorioDropZone`, `#grimorioTormentaListaVinculos`.
- Payload mínimo: `nome` / `slug` + metadados do catálogo; vínculo persiste via handlers existentes (`adicionarEquip…`, `adicionarTalento`, `grimorioSvc.adicionarVinculo`).
- Fallback: botão «Adicionar» e fluxo modal permanecem.
- Implementação: `frontend/games/tormenta/js/t20-compendium-dnd.js`.

### RF-T12c — Rolagem contextual (detalhe)

- Reutiliza `POST /tormenta/regras/pericias/rolar`, `/ataque/rolar`, `/iniciativa/rolar` e rotas `combate/rolar-*` na arena.
- **Ficha:** clique no nome ou Σ (perícia), linha 🎲 da planilha CAC/Dist, linha de arma, cartão Iniciativa.
- CA/CD via diálogo reutilizado (`#t20ModalPericiaDc`); CA opcional em ataques.
- Resultado: toast + última rolagem em `#fichaUltimaRolagem` (buffer `window.__t20LogMesa` para RF-T12j).

### RF-T12f — Handouts (detalhe)

- Modelo sugerido: `tormenta_handouts` ou `ficha_json.handouts[]` com `{ id, titulo, corpo_md, imagem_url, visivel_para: user_ids[] }`.
- Mestre: CRUD no dashboard da campanha.
- Jogador: painel lateral «Mesa» com handouts revelados.
- **Não** copiar formato Journal Roll20; contrato próprio documentado em `05-contrato-dados-ficha-json-e-api.md` quando implementar.

## Fases sugeridas

| Fase | RFs | Entrega |
|------|-----|---------|
| **F1 — Ficha inteligente** | T12a, T12b (equip + poder), T12c (perícias) | Menos cliques na ficha; paridade com «sheet automation» |
| **F2 — Mesa** | T12d, T12e, T12f | Arena + handouts utilizáveis em sessão |
| **F3 — Campanha** | T12g, T12h, T12i, T12j, T12k | Fluxo mestre↔jogador mais próximo de VTT |
| **F4 — VTT** | T12l | Projeto separado; não bloquear F1–F3 |

## Estado de implementação

| Item | Estado |
|------|--------|
| RF-T12a breakdown | **Feito** | PV, CA, perícias (Σ) e ataques (`t20-breakdown-ficha.js`) |
| RF-T12b DnD compendium | **Feito** | Equipamento, poder/talento, magia (grimório), consumível; duplo clique; `t20-compendium-dnd.js` |
| RF-T12c Rolagem contextual | **Feito** (ficha) | Perícias, planilha/arma, iniciativa; log `#fichaUltimaRolagem`; arena já tinha modais |
| RF-T12d Condições → rolagens | **Feito** (arena) | Atq/CA; perícias; Reflexos (SR); iniciativa; breakdown na UI |
| RF-T12e NPC compacto | **Feito** | Ataques inline; ini clicável; PM oculto se 0; preset 🎲 |
| RF-T12j Log de mesa | **Feito** (arena) | Painel lateral; ataque/dano/perícia/ini/SR/PV/turno/condição |
| RF-T12f Handouts | **Feito** | API `tormenta_handouts`; mestre CRUD; jogador lê em Campanhas + arena |
| RF-T12h Sync ficha↔arena | **Feito** | `BroadcastChannel` `tormenta-t20-sync`; PV/PM/condições arena→ficha e ficha→arena |
| RF-T12i Layout compacto | **Feito** | Toggle «Vista compacta» + `localStorage`; oculta equipamento, grimório, retrato, etc. |
| RF-T12l Mapa VTT | **Fora de escopo** |

## Gap código / dependências

| Dependência | Notas |
|-------------|-------|
| `05-combate-tormenta.md` | RF-T12d alinha com RF-T05c |
| `06-magia-tormenta.md` | RF-T12b grimório; drag magia → slots |
| `07-equipamento-tormenta.md` | RF-T12b equipamento; limites v1.3 já feitos |
| `08-poderes-tormenta.md` | RF-T12b poderes; ativar com PM |
| Campanha | `ficha_json.campanha` hoje é string; RF-T12f/k podem exigir entidade `tormenta_campanhas` |

## Critérios de aceite (F1)

- Bárbaro 1, CON +2: ficha exibe **26/26** PV ao carregar (sem botão manual); breakdown mostra `24 + 2 (CON)`.
- Arrastar um poder do modal para a lista na ficha cria vínculo sem redigitar nome/slug.
- Clicar «rolar» em Percepção envia bônus correto (treinado + meio nível + SAB/INT conforme perícia v1.3).

## Fora de escopo (explícito)

- Login ou scraping em contas Roll20 de terceiros.
- Import direto de `.json` exportado do Roll20 (sem demanda formal).
- Iluminação dinâmica, pathfinding, video/voice integrados (usar Discord/externo).

## Referência

- Arena README: ficha, arena, grimório Tormenta.
- Skill: `.cursor/skills/tormenta-20-arena-arquitetura-e-regras/SKILL.md`.
- Combate: [05-combate-tormenta.md](05-combate-tormenta.md).
- Backlog transversal: [docs/tormenta/03-requisitos-funcionais-backlog.md](../../docs/tormenta/03-requisitos-funcionais-backlog.md).
