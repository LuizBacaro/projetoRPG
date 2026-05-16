# Grimório Tormenta 20 (MB) — requisitos e âmbito p.144–209

Este documento alinha a **implementação futura do grimório** na Arena TTRPG com o **Módulo Básico (MB)** de Tormenta 20, espelhando a **maturidade do fluxo D&D 3.5** do repositório, com as **particularidades T20** (PM, círculos, habilidade-chave, preparação vs espontâneo).

**Referência de páginas:** conforme o utilizador (Cap. magia): **144–145** (regras gerais), **150** (início da lista de magias), **150–209** (lista estendida). Confirmar numeração no vosso exemplar físico/PDF licenciado.

**Direitos:** não copiar texto longo nem tabelas completas do livro no repositório; manter **estrutura**, **RFS**, **campos** e **remissões de página**. Conteúdo de magias → processo privado / seed conforme `docs/tormenta/00-visao-e-fontes-legais.md`.

---

## 1. Paridade com D&D 3.5 (o que reutilizar como padrão)

| Área D&D 3.5 (implementado) | Caminhos / contratos |
|----------------------------|----------------------|
| UI modal grimório + filtros + slots | `frontend/games/dnd35/js/controllers/GrimorioController.js`, `grimorio.css` |
| API grimório por combatente | `GrimorioService.js` → `GET/POST /grimorio/{combatenteId}`, preparadas, etc. |
| Magias catálogo + vínculo | Backend D&D: modelos `Magia`, preparação, slots por classe |

**Tormenta:** personagem = `tormenta_personagens` (não `combatentes` D&D). O grimório deve usar **`personagem_id` Tormenta** + rotas `/api/v1/tormenta/...` (prefixo e `requer_game_tormenta`), **não** reutilizar `/grimorio/` do D&D sem adaptação.

---

## 2. Extração de regras — MB p.144–145 (requisitos de domínio)

### 2.1 Tipos e níveis de magia (≈ p.144)

| Conceito MB | RF | Notas de implementação |
|-------------|-----|-------------------------|
| **Truques** (efeitos de 0º “círculo” / sem custo como magia de nível) | RF-T40a | Distinguir truque vs magia com custo em PM; não “gastar slot” de círculo como D&D, seguir MB para custo e aprimoramento |
| **Magias por círculo** (truque + círculos 1+ conforme MB; no MB base tipicamente até **5º círculo** — confirmar no exemplar) | RF-T40b | UI e API: filtro por **círculo**; expansões podem acrescentar círculos superiores |
| **Tipos** (arcana, divina, etc., conforme MB) | RF-T40c | Campo `tipo` ou `origem_magia` no catálogo + regras de lista para classe |
| **Execução ritual / tempo / alcance** (resumo) | RF-T40d | Catálogo: campos estruturais; motor de combate fora do MVP grimório |

### 2.2 Habilidade-chave (≈ p.144)

| Classe / conjuração | Habilidade-chave (MB) | RF |
|---------------------|----------------------|-----|
| Arcanista (mago) | Inteligência | RF-T41a |
| Bardo / Feiticeiro | Carisma | RF-T41b |
| Clérigo / Druida / Paladino / Ranger (com magias) | Sabedoria | RF-T41c |
| **CD** e testes que dependem da chave | RF-T41d | Função única `habilidade_chave_conjuracao(slug_classe_mb)` alinhada a `classes_mb.json` + livro |

### 2.3 Magias conhecidas (≈ p.145)

| Regra | RF |
|-------|-----|
| Classes **espontâneas**: conjunto fixo de magias conhecidas por nível/círculo (evolui com nível) | RF-T42a |
| Progressão por tabela de classe (não duplicar tabela no repo — referência + dados mínimos ou importação privada) | RF-T42b |
| Bardo: troca de magias conhecidas (regra MB) | RF-T42c |

### 2.4 Pontos de mana (PM) (≈ p.145)

| Regra | RF |
|-------|-----|
| PM base por classe + modificador da habilidade-chave; ganho por nível (MB) | RF-T43a |
| Custo em PM para lançar magia por círculo (tabela MB) | RF-T43b |
| Sincronizar com ficha: já existem `pa_max` / `pa_atual` como PM na UI | RF-T43c |
| Truques: regra de custo adicional / aprimoramento (MB) — não assumir modelo D&D | RF-T43d |

### 2.5 Preparar ou lançar magias (≈ p.145)

| Modo | Classe (típico MB) | RF |
|------|-------------------|-----|
| **Preparar** (lista diária / descanso) | Clérigo, Druida, Mago, Paladino, Ranger (quando aplicável) | RF-T44a |
| **Espontâneo** (slots flexíveis nas conhecidas) | Bardo, Feiticeiro | RF-T44b |
| **Grimório físico** (mago): livro de magias + preparação | RF-T44c |
| **Domínio** (clérigo: truque de domínio sem custo, etc.) | RF-T44d | Afinar com `dnd-spellcasting-conventions` **só** onde a regra T20 for análoga; preferir doc T20 dedicado |

---

## 3. Lista de magias MB p.150–209 (catálogo)

| RF | Descrição | Critérios de aceite |
|----|-------------|---------------------|
| RF-T45 | **Catálogo** de magias com metadados mínimos: `nome`, `círculo`, `tipo` (arcana/divina), `escola` ou equivalente MB, `resistência`, `execução`, `alcance`, `alvo`, `duração`, `referência_pagina_mb` | `GET /tormenta/regras/magias` ou tabela `tormenta_catalogo_magia` + seed; paginação e busca como talentos/equipamentos |
| RF-T46 | **Sem texto integral** da descrição da magia no repo público | Resumo curto opcional + página; ou só nome + círculo + tags até processo licenciado |
| RF-T47 | **Filtros** na UI grimório: círculo, tipo, escola, nome, “preparadas”, favoritas | Paridade UX com `GrimorioController` D&D onde fizer sentido |

---

## 4. Arquitetura alinhada ao projeto (skills Arena + Tormenta)

1. **Regras e listagens de referência** (progressões genéricas, custos PM por círculo se forem dados tabulares curtos): preferir **`backend/app/games/tormenta/data/*.json`** + **`GET /api/v1/tormenta/regras/*`**, como talentos e identidade MB (`tormenta-20-arena-arquitetura-e-regras`).
2. **Instância por personagem** (magias conhecidas, preparadas hoje, gastos de PM): **PostgreSQL** + rotas sob `/tormenta/personagens/{id}/...` (ou sub-recurso `grimorio`), com migrações Alembic.
3. **Frontend:** nova página ou modal em `frontend/games/tormenta/` — `getApiUrl` / boot de API conforme **`arena-ttrpg-architecture`** (nunca `origin` Vercel para `/api/v1` em produção).
4. **vercel.json:** quando existir `grimorio-tormenta.html` (ou rota), adicionar rewrite `/grimorio-tormenta` → ficheiro em `/games/tormenta/...` (espelho do padrão D&D).

---

## 5. Fases de implementação sugeridas

| Fase | Entrega | Dependências |
|------|---------|--------------|
| **G0** | Este doc + RFs no backlog + skill atualizada | — |
| **G1** | JSON **metadados** + `GET /tormenta/regras/magias` (paginação, `q`, `circulo`, `tipo`, `escola`) + stubs em `magias_mb_catalogo.json` | RF-T45–T46 — **feito no repo**; substituir `itens` por seed MB via pipeline privado |
| **G2** | Motor PM + habilidade-chave + custo PM/círculo em `rules/conjuracao_t20.py` + `GET /tormenta/regras/conjuracao-mb` | RF-T41–T43 — **feito**; multiclasse e ajustes finos → backlog |
| **G3** | SQL `tormenta_magias_personagem` + `GET/POST/DELETE .../personagens/{id}/magias` + `magias` no `GET` personagem | **Feito**; migrar `ficha_json.magias_texto` → opcional (G4) |
| **G4** | `TormentaGrimorioService.js` + UI (modal ou página) + botão na ficha (substituir placeholder `btnT20Grimorio`) | Paridade G0–G3 |
| **G5** | Lista completa p.150–209 no catálogo (importação privada / seed) | Licença + pipeline |

---

## 6. Rastreabilidade rápida MB ↔ código (a preencher)

| Página MB | Tópico | Artefacto alvo |
|-----------|--------|----------------|
| 144 | Tipos e níveis | `rules/magia_t20.py` (futuro), `data/` |
| 144 | Habilidade-chave | `rules/magia_t20.py` + `classes_mb` |
| 145 | Conhecidas / PM / Preparar ou lançar | API personagem + grimório |
| 150–209 | Lista de magias | `tormenta_catalogo_magia` ou `regras/magias` JSON |

---

## 7. Critérios globais de aceite (épico grimório)

1. Jogador com classe conjuradora MB consegue **abrir grimório**, ver **magias do catálogo** filtráveis e **marcar/preparar** conforme o modo da classe (MVP: uma classe MB por ficha se simplificar).
2. **PM** gasto ao “lançar” ou registrar uso respeita tabela MB (MVP pode ser só registo manual + validação de teto).
3. **Persistência** em Postgres; `ficha_json.magias_texto` permanece legado ou export até migração completa.
4. **Testes** `pytest` para regras de PM/CD e testes de integração para `GET` regras magias.

---

## 8. Referências internas

- Contrato ficha: `docs/tormenta/05-contrato-dados-ficha-json-e-api.md`
- Roadmap catálogos: `docs/tormenta/04-catalogos-dinamicos-roadmap.md`
- Backlog IDs: `docs/tormenta/03-requisitos-funcionais-backlog.md` (secção P2 grimório)
