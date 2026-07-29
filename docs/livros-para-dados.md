# Runbook — livros locais → dados no Arena

PDFs e planilhas ficam em **`livros/`** e **`helpers/`** (`.gitignore`). Este documento mapeia **fonte → script → artefacto → código**.

**Regra legal:** não commitar PDFs nem tabelas completas protegidas; no repo vão **estrutura**, **metadados**, **referência de página** e **seeds** derivados com licença adequada (SRD/OGL ou processo privado Tormenta).

---

## Inventário de PDFs (máquina local)

| Ficheiro em `livros/` | Sistema | Uso no Arena |
|----------------------|---------|----------------|
| `D&D3_5_livro_jogador.pdf` | D&D 3.5 | Magias PHB, progressão, RF em `.cursor/requisitos/dnd35/` |
| `D&D 3.5 - Livro do Mestre.pdf` | D&D 3.5 | Consumíveis p.230; encontros/tesouros (RF-11 auxiliar) |
| `dd-3e-livro-dos-monstros-3-5.pdf` | D&D 3.5 | Bestiário MM → `bestiario_mm35.json` (RF-11) |
| `dnd-5e.pdf` | D&D 5E | Consulta narrativa; catálogo principal via 5e-database/OGL |
| `tormenta-rpg-modulo-basico.pdf` | Tormenta 20 | MB: regras, listagens; `docs/tormenta/*` |
| `tormenta-rpg-ficha.pdf` | Tormenta 20 | Referência de layout (opcional) |
| `GURPS 4E - Módulo Básico - Lite.pdf` | GURPS | Roadmap Lite — skill GURPS |
| `GURPS 4E - Módulo Básico - Personagens.pdf` | GURPS | Extração catálogo (script abaixo) |
| `GURPS 4E - Ficha de Personagem (Aprimorada 1).pdf` | GURPS | Referência UI |

---

## D&D 3.5 (PHB + DMG)

| Objetivo | Pré-requisito | Comando | Saída |
|----------|---------------|---------|--------|
| Diff magias PHB × seed | `poppler-utils` (`pdftotext`), PDF PHB | `cd backend && python3 scripts/diff_phb_seed_all_classes.py` | Terminal + opcional `--json ../docs/diff-phb-seed-all-classes.json` |
| Snapshot CI (sem PDF) | JSON acima commitado | `python3 scripts/check_phb_seed_snapshot.py` | Exit 0 se totais do seed = JSON |
| Patches de alinhamento PHB | PDF PHB | `patch_clerigo_phb_seed.py`, `patch_phb_seed_all_classes.py`, `patch_phb_bardo_mago.py` | Altera `scripts/seed_magias.py` |
| Sincronizar BD | `.env` com `DATABASE_URL` | `python3 scripts/seed_magias.py --sync --classes ...` | Tabela `magias` |
| Consumíveis DMG | PDF DMG | `python3 scripts/extrair_tabelas_consumiveis_livro_mestre.py` (raiz `scripts/`) | Excel + `backend/scripts/seed_consumiveis.py` |
| Bestiário MM (lote) | PDF Livro dos Monstros | `python3 scripts/extrair_bestiario_mm35.py --validate` (raiz) | `backend/app/games/dnd35/data/bestiario_mm35.json` |

**Bestiário — lotes (RF-M09):**

| Lote | Escopo | Estado |
|------|--------|--------|
| 0 | Pipeline + curado inicial (~51) | ✅ |
| 1 | Cap. A–Z frequentes (+53; total ~104) | ✅ |
| 2 | Animais (apêndice) (+55; ~61 animais; total ~159) | ✅ |
| 3 | Insetos / vermin (+32; ~34 insetos; total ~191) | ✅ |
| 4 | Dragões (10 espécies × 12 idades + pais; total ~317) | ✅ |

Checklist, categorias de idade e critérios de aceite por PR: **[dnd35/bestiario-lotes-mm35.md](dnd35/bestiario-lotes-mm35.md)**. Cada lote: JSON + `pytest tests/test_dnd35_bestiario.py` (contagem mínima) + smoke API. Só stats + remissão (sem prosa de Combate).

**Documentação:** [diff-phb-seed-all-classes.md](diff-phb-seed-all-classes.md), [regras-conjuracao-dnd-arena.md](regras-conjuracao-dnd-arena.md), RF [`.cursor/requisitos/dnd35/11-monstros-dnd35.md`](../.cursor/requisitos/dnd35/11-monstros-dnd35.md), lotes MM [dnd35/bestiario-lotes-mm35.md](dnd35/bestiario-lotes-mm35.md)

---

## Tormenta 20 (MB)

| Objetivo | Comando | Saída |
|----------|---------|--------|
| Catálogo magias MB (listagem) | `python3 backend/scripts/build_magias_mb_catalogo_from_listagem_txt.py` | `backend/app/games/tormenta/data/magias_mb_catalogo.json` |
| Validar JSON | `python3 backend/scripts/check_magias_mb_catalogo.py` | CI / exit 1 |
| Levantamento requisitos | — | `docs/tormenta/00–08`, `.cursor/requisitos/tormenta/` |

**Grimório:** [tormenta/grimorio-mb-mesa.md](tormenta/grimorio-mb-mesa.md), fechamento G0–G2 em [tormenta/08-grimorio-g0-g2-fechamento.md](tormenta/08-grimorio-g0-g2-fechamento.md)

---

## GURPS 4E

| Objetivo | Comando | Saída |
|----------|---------|--------|
| Extração heurística Personagens | `python3 scripts/gurps_extrair_catalogo_personagens_pdf.py` | JSON de rascunho (revisar manualmente) |

**Roadmap:** [roadmap-gurps-melhorias.md](roadmap-gurps-melhorias.md)

---

## D&D 5E

| Objetivo | Fonte | Artefacto |
|----------|-------|-----------|
| Catálogos embutidos | 5e-database (tag em `catalogo_metadata.py`) + curadoria | `backend/app/games/dnd5e/data/*_catalogo.py` |
| Magias Foundry/OGL | `foundry_spells.py` | Metadados + i18n |
| Import planilha mesa | Upload API | `magia_import_service.py` |

**Plano UI:** [dnd5e/plano-ui-dashboard.md](dnd5e/plano-ui-dashboard.md)

---

## Planilhas e pipelines na raiz

| Pasta / script | Uso |
|----------------|-----|
| `tabelas_classes_excel/`, `scripts/classes_tables_pipeline.py` | Tabelas de classe D&D 3.5 |
| `scripts/racas_catalog_pipeline.py` | Raças 3.5 |
| `scripts/habilidades_especiais_catalog_pipeline.py` | Habilidades especiais |
| `scripts/generate_requisitos_cobertura_matrix.py` | Matriz RF × código → `docs/requisitos-cobertura-matrix.md` |
| `scripts/generate-governanca-xlsx.py` | `docs/governanca-agentes-fluxos.xlsx` |

---

## Fluxo recomendado para agentes

1. Ler RF em `.cursor/requisitos/<jogo>/`.
2. Consultar PDF **local** (não versionado) só para confirmar regra/página.
3. Gerar ou atualizar JSON/seed **enxuto**.
4. Implementar em `app.games.<slug>` + teste mínimo.
5. Atualizar matriz: `python3 scripts/generate_requisitos_cobertura_matrix.py`.

---

## Ver também

- [AGENTS.md](../AGENTS.md) — skill `rpg-requirements-analysis`, PDF skill em `.github/skills/pdf/`
- [auth-sessao-oauth.md](auth-sessao-oauth.md)
