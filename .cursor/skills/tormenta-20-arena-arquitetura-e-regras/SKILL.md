---
name: tormenta-20-arena-arquitetura-e-regras
description: >-
  Tormenta 20 no Arena TTRPG: arquitetura de dados (Postgres vs JSON de regras),
  rotas `/tormenta/regras/*`, catálogos MB (equipamento, talentos, magias/grimório,
  classes, raças, tendências e divindades em `identidade-mb`), ficha web e contratos `ficha_json`.
  Regras de jogo alinhadas ao Módulo Básico (MB) e documentação em docs/tormenta.
  Usar ao implementar ou alterar ficha Tormenta, API de personagens, motor de regras
  T20, seeds, modais/overlays Tormenta, combos de alinhamento ou panteão, ou quando
  o utilizador pedir manutenção ou novas funcionalidades Tormenta 20, grimório ou conjuração MB.
disable-model-invocation: false
---

# Tormenta 20 — arquitetura Arena + regras (MB)

## Fonte de verdade por tipo de dado

| Tipo | Onde vive | Notas |
|------|-----------|--------|
| **Dados do personagem** (atributos, PV, PM, vínculos a talentos/equipamentos/consumíveis, `ficha_json`, etc.) | **PostgreSQL** (Neon em produção) | CRUD em `tormenta_*`; migrações Alembic quando o schema muda. |
| **Catálogos e tabelas de regra MB** (raças, classes, benefícios por nível, equipamentos MB, talentos MB enriquecidos, **magias MB** (metadados + remissão), perícias base, atributos compra, **tendências e divindades**) | **JSON versionado** em `backend/app/games/tormenta/data/` + **código** em `app.games.tormenta.rules.*` | Servidos pela API autenticada `GET /api/v1/tormenta/regras/...`. |
| **Conteúdo editorial longo** (traços de raça, textos de habilidade) | Resumos em JSON + remissão ao livro; não copiar tabelas completas sem licença | Ver `docs/tormenta/00-visao-e-fontes-legais.md`. |

### Decisão explícita: não duplicar catálogos no frontend

- **Manter:** uma única fonte nos JSON do backend + exposição via **`/tormenta/regras/*`** (ex.: equipamentos, talentos, magias quando existir endpoint, raças, classes). A ficha Tormenta consome a API com JWT (`TormentaRegrasService`, etc.).
- **Evitar:** copiar o mesmo catálogo para `frontend/games/tormenta/data/` salvo necessidade futura comprovada de **modo totalmente offline** (hoje não é o padrão do projeto).
- **Motivos:** deploy simples, sem divergência entre ficheiros, sem migração Alembic por cada linha de livro; conteúdo de referência segue o git e o mesmo pipeline que o backend.

Se no futuro um catálogo precisar de **CRUD administrativo**, **multi-ambiente com conteúdo distinto** ou **consultas SQL pesadas**, aí sim considerar tabela dedicada + seed a partir do mesmo JSON (repo continua fonte editorial).

## Rotas e ficheiros-chave

| Área | Caminhos |
|------|----------|
| Router regras | `backend/app/games/tormenta/api/v1/regras.py` — inclui **`GET .../magias`** |
| Router personagens | `backend/app/games/tormenta/api/v1/personagens.py` |
| Catálogos MB (filtro, merge JSON + classes) | `backend/app/games/tormenta/rules/catalogo_t20.py` — `equipamentos_mb_catalogo.json`, `talentos_mb_catalogo.json`, **`magias_mb_catalogo.json`**, **`bestiario_v13.json`** (RF-T12g; stub legado só fallback) |
| Tendências (alinhamento) e divindades (Os Vinte) | `data/tendencias_divindades_mb.json` (`divindades`: `slug` + `rotulo`), `rules/tendencias_divindades_t20.py`, `GET /tormenta/regras/identidade-mb` (ficha: combos; MB p.116–119 e p.120–126) |
| Classes / BBA / PV MB | `backend/app/games/tormenta/rules/classes_t20.py`, `data/classes_mb.json`, `beneficios_nivel_mb.json` |
| **Conjuração MB (PM, chave, custo/círculo)** | `data/conjuracao_classe_mb.json`, `rules/conjuracao_t20.py`, **`GET /tormenta/regras/conjuracao-mb`** |
| Schemas payload regras | `backend/app/games/tormenta/schemas/regras_ficha.py` (`TormentaCatalogoItem`, etc.) |
| Ficha web | `frontend/games/tormenta/pages/ficha-personagem.html`, CSS em `frontend/games/tormenta/css/` |
| Contrato dados | `docs/tormenta/05-contrato-dados-ficha-json-e-api.md` |
| README módulo | `backend/app/games/tormenta/README.md` |
| Grimório MB (RFs, fases, MB p.144–209) | `docs/tormenta/07-requisitos-grimorio-mb-144-209.md`, backlog `docs/tormenta/03-requisitos-funcionais-backlog.md` (RF-T22, RF-T40–T47); **vínculos** `tormenta_magias_personagem` + rotas `/personagens/{id}/magias` |

## Grimório e conjuração MB (planeamento / implementação)

- **Documento canónico de RFs:** `docs/tormenta/07-requisitos-grimorio-mb-144-209.md` — círculos e truques, **habilidade-chave** por classe, **magias conhecidas**, **PM**, **preparar vs lançar**, catálogo **p.150–209** (metadados; sem texto longo do livro no repo).
- **Paridade D&D 3.5 (referência UX/API):** `frontend/games/dnd35/js/controllers/GrimorioController.js`, `frontend/games/dnd35/js/services/GrimorioService.js` — em Tormenta usar **`personagem_id`** e rotas **`/api/v1/tormenta/...`**, não `/grimorio/{combatenteId}` do D&D.
- **Catálogo:** `GET /tormenta/regras/magias` (JSON `magias_mb_catalogo.json` + `filtrar_magias_mb` em `catalogo_t20.py`) — ou futura tabela `tormenta_catalogo_magia` + seed a partir do mesmo JSON.
- **Persistência por personagem:** conhecidas / preparadas / grimório em SQL (`tormenta_magias_personagem`) + rotas **`GET/POST/DELETE /tormenta/personagens/{id}/magias`**; campo `magias` no `GET` personagem (enriquecido com catálogo JSON). Alinhar `pa_max` / `pa_atual` com o motor de PM do MB.
- **Deploy:** ao existir página dedicada, alinhar `vercel.json` (rewrite) e `getApiUrl` conforme skill `arena-ttrpg-architecture`.
- **Testes:** após endpoints regras/magias ou motor PM, estender `tests/test_tormenta_regras_api.py` (e testes de personagem se CRUD grimório).

## Regras de jogo (MB) na implementação

- **BBA:** derivado de classe MB (`bba_tipo`: plein / tres_quartos / meio) e nível — ver `bbaTbNivel` / `atualizarResumoClasseMb` na ficha; planilha de ataque espelha o BBA calculado, não valores “soltos” gravados à parte do motor MB.
- **Atributos:** compra por pontos (8–18) e modificadores — `atributos_t20` + `atributos_compra_pontos.json`; paridade backend/JS descrita no README do módulo.
- **Perícias / resistências / iniciativa:** seguir docs em `docs/tormenta/` e testes `tests/test_tormenta_*.py` quando existirem para a área.
- **Tendência e divindade (MB):** listas em `tendencias_divindades_mb.json` (divindades com **`slug`** estável + **`rotulo`** persistido em `divindade`); endpoint **`GET /tormenta/regras/identidade-mb`**; na ficha, `<select>` com `option.value = rotulo` e `data-slug` para uso futuro no cliente.
- **Talentos na ficha:** vínculo em SQL (`tormenta_talentos` + `tormenta_talentos_personagem`); autocomplete de catálogo MB vem de **`/tormenta/regras/talentos`** (lista enriquecida, não obrigatório duplicar em BD).
- **Magias / grimório:** seguir doc 07; conjuração MB difere de D&D 3.5 (**PM**, **círculos**, preparação/espontâneo por classe); não assumir slots D&D sem mapear para T20. **PM máximos e custo por círculo:** `conjuracao_t20.py` + `GET /tormenta/regras/conjuracao-mb`.
- **Ameaça (NPC/monstro):** metadados em `ficha_json.ameaca` (ND, papel Solo/Lacaio/Especial, ações); motor determinístico `rules/ameaca_bloco_t20.py`; `GET .../bloco-ameaca`, `POST .../converter-ameaca`; UI na ficha (`t20-ameaca-bloco.js`). Import do bestiário: `POST .../importar-bestiario` + `rules/bestiario_import_t20.py` (`bestiario_fonte: t20_v13`, ND fracionário). Ver RF-13 / RF-T12g.

## UI Tormenta (padrões)

- Modais estilo `equipamentos-overlay`: no CSS, ocultar overlay **sem** `.is-open` (`display: none`); abrir/fechar só via classe `is-open` + `aria-hidden`. Ver `.github/instructions/frontend.instructions.md` (secção overlays Tormenta).
- **Deslocamento / tamanho:** valores em `<input type="hidden" id="f_desl">` / `f_tam` para o payload; no cabeçalho mostrar como **`span.t20-ficha-tag`** (`t20TagDesl`, `t20TagTam`), texto atualizado em `atualizarTagsHeader()`; edição só no diálogo (`f_dlg_desl`, `f_dlg_tam`).
- Campos de identidade no cabeçalho: muitos são só leitura na folha e editáveis no diálogo «Editar ficha» — ao adicionar campos semelhantes, seguir o mesmo fluxo (sync diálogo ↔ cabeçalho ↔ `payloadBase`).

## Testes e alterações seguras

- Após mudar `catalogo_t20.py` ou schemas de regras: correr `pytest` em `tests/test_tormenta_regras_api.py` (e outros `test_tormenta_*` relevantes).
- Dados de produção: skill `arena-producao-dados-neon-render` quando tocar migrações ou deploy.

## Ordem sugerida para nova funcionalidade Tormenta

1. Ler `docs/tormenta/README.md` e o RF/backlog correspondente.
2. Decidir: dado **persistente por personagem** → API + modelo + migration se necessário; dado **de livro/catálogo** → JSON + `rules/` + endpoint regras.
3. Alinhar frontend à API existente; não introduzir segundo ficheiro de catálogo no `frontend/` sem decisão documentada.
