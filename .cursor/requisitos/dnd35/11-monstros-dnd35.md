# Monstros e NPCs (Livro dos Monstros) — D&D 3.5

**Fonte principal:** D&D 3.5 — Livro dos Monstros (Devir). PDF local: `livros/dd-3e-livro-dos-monstros-3-5.pdf`.

**Fonte auxiliar (remissão):** Livro do Mestre — encontros/tesouros (não substitui o MM).

**Escopo Arena v1:** catálogo JSON com **stats estruturados** (sem prosa longa de Combate) + listagem/import na UI do mestre, no padrão do bestiário Tormenta, respeitando regras 3.5 (CA/toque/surpresa, BBA, ND).

**Não confundir com:** [09-companheiro-animal-dnd35.md](09-companheiro-animal-dnd35.md), [10-familiar-dnd35.md](10-familiar-dnd35.md).

---

## Regras de produto

| ID | Requisito | Critério de aceite |
|----|-----------|-------------------|
| RF-M01 | Monstro/NPC no dashboard | CRUD combatente `tipo=monstro` com ficha 3.5 (já em produção) |
| RF-M02 | Referência de página | `pagina_referencia` preenchida no import a partir do catálogo |
| RF-M03 | Catálogo MM (JSON) | `bestiario_mm35.json` com lotes 0–4 (≥300 entradas; stats + remissão; sem texto longo) |
| RF-M04 | API de catálogo | `GET /api/v1/dnd35/regras/bestiario` e `GET .../bestiario/{slug}` autenticados |
| RF-M05 | Importar do bestiário | `POST /api/v1/combatentes/importar-bestiario` cria monstro com HP, CA/toque/surpresa, saves, attrs e ataques |
| RF-M06 | UI mestre | Modal listar/filtrar/preview/import (dashboard) |
| RF-M07 | Bloco de estatísticas | Gerador no cliente (template 3.5) a partir do detalhe do catálogo |
| RF-M08 | Tesouro automático | **Fora do v1** — só documentar |
| RF-M09 | Lotes seguintes | ✅ Lotes 0–4 entregues (A–Z, animais, insetos, dragões). Refinos pontuais / raros restantes = PRs incrementais. Detalhe em [docs/dnd35/bestiario-lotes-mm35.md](../../../docs/dnd35/bestiario-lotes-mm35.md) |

---

## Contrato de dados (catálogo)

Arquivo: `backend/app/games/dnd35/data/bestiario_mm35.json`.

Campos principais: `slug`, `nome`, `nd` (float), `nd_rotulo`, `tipo_criatura`, `subtipos[]`, `tamanho`, `dv`, `hp_maximo`, `iniciativa`, `deslocamento`, `ca`, `toque`, `surpresa`, `ataque_base`, `agarrar`, saves, atributos, `ataques[]`, `ataque_total`, `espaco_alcance`, `ataques_especiais[]`, `qualidades_especiais[]`, resumos curtos, `pagina_referencia`, `fonte: "mm35"`, `especie_pai`, `categoria_idade`, `aliases[]`.

**Dragões:** espécie lógica + linhas por idade (`especie_pai` + `categoria_idade`; slug ex. `dragao-azul-jovem`).

**Legal:** stats estruturados + remissão de página; **não** copiar prosa longa de Combate do livro.

---

## Scripts

| Script | Estado |
|--------|--------|
| `scripts/extrair_tabelas_consumiveis_livro_mestre.py` | ✅ consumíveis DMG |
| `scripts/extrair_bestiario_mm35.py` | ✅ rascunho OCR + validação de sanity do JSON |
| Revisão humana por lote | obrigatória (PDF escaneado / OCR fraco) |

---

## Fases

| Fase | Entrega |
|------|---------|
| M0 | RF + `docs/livros-para-dados.md` |
| M1 | JSON lote inicial + `GET /dnd35/regras/bestiario` |
| M2 | `POST /combatentes/importar-bestiario` + testes |
| M3 | UI modal import + bloco de estatísticas no cliente |
| M4 | Lotes seguintes (backlog contínuo) — ver abaixo |

### Backlog de lotes (RF-M09)

Documento canónico de execução: **[docs/dnd35/bestiario-lotes-mm35.md](../../../docs/dnd35/bestiario-lotes-mm35.md)**.

| Lote | Conteúdo | Estado |
|------|----------|--------|
| **0** | Pipeline + ~40–80 curados (goblin/orc/ogro, mortos-vivos, animais básicos, elementais, demônios comuns, 1 dragão com idades) | ✅ (~51 no JSON) |
| **1** | Cap. A–Z frequentes (exceto apêndices deferidos) | ✅ (+53; total ~104; teste ≥90) |
| **2** | Animais (apêndice) | ✅ (+55; ~61 animais; catálogo ~159; teste ≥140) |
| **3** | Insetos / vermin | ✅ (+32; ~34 insetos; catálogo ~191; teste ≥180) |
| **4** | Dragões — todas as espécies × categorias de idade | ✅ (10×12 idades + 10 pais; catálogo ~317; teste ≥300) |

**Por PR:** JSON revisado + `extrair_bestiario_mm35.py --validate` + bump de contagem mínima em `tests/test_dnd35_bestiario.py` + smoke API. Só stats + remissão de página.

---

## Implementação relacionada

- Combatentes: `backend/app/games/dnd35/api/v1/combatentes.py`
- Catálogo: `backend/app/games/dnd35/rules/bestiario_mm35.py`
- Import: `backend/app/games/dnd35/rules/bestiario_import_dnd35.py`
- UI: `frontend/games/dnd35/js/dnd35-arena-bestiario-import.js`
- Bloco 3.5: `frontend/games/dnd35/js/dnd35-bloco-monstro.js`
- Lotes: [docs/dnd35/bestiario-lotes-mm35.md](../../../docs/dnd35/bestiario-lotes-mm35.md)
- Combate: [04-combate-dnd35.md](04-combate-dnd35.md)
