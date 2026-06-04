# Monstros e NPCs (Livro do Mestre) — trilha mínima D&D 3.5

**Fonte:** D&D 3.5 — Livro do Mestre (estatísticas de criaturas, desafios, tesouros). PDF local: `livros/D&D 3.5 - Livro do Mestre.pdf`.

**Escopo Arena v1:** não reproduzir blocos de estatística integrais no repo. Começar por **cadastro de monstro/NPC na mesa** (já existe tipo `monstro` em combatentes) e **bestiário mínimo** referenciado por página.

**Não confundir com:** [09-companheiro-animal-dnd35.md](09-companheiro-animal-dnd35.md), [10-familiar-dnd35.md](10-familiar-dnd35.md).

---

## Regras de produto

| ID | Requisito | Critério de aceite |
|----|-----------|-------------------|
| RF-M01 | Monstro/NPC no dashboard | CRUD combatente `tipo=monstro` com ficha 3.5 (já em produção) |
| RF-M02 | Referência DMG opcional | Campo `pagina_referencia` ou notas livres na ficha (sem importar tabela completa) |
| RF-M03 | Bestiário mínimo (seed) | ≥20 entradas **metadados**: `nome`, `nd`, `tipo`, `tamanho`, `pagina_dmg`, `slug` — sem texto de habilidades longas |
| RF-M04 | Importar monstro para arena | Fluxo existente `incluir_vinculos` / seleção arena para combatentes |
| RF-M05 | Tesouro automático | **Fora do v1** — só documentar |

---

## Dados (proposta)

Tabela futura `dnd35_bestiario_catalogo` ou JSON em `backend/app/games/dnd35/data/bestiario_dmg_minimo.json`:

```json
{
  "slug": "goblin",
  "nome": "Goblin",
  "nd": "1/3",
  "tipo": "humanoide",
  "tamanho": "pequeno",
  "pagina_referencia": "Livro do Mestre p.XXX"
}
```

Valores numéricos de combate continuam na **ficha do combatente** (PV, CA, ataques), não no catálogo público.

---

## Scripts

| Script | Estado |
|--------|--------|
| `scripts/extrair_tabelas_consumiveis_livro_mestre.py` | ✅ consumíveis p.230 |
| `scripts/extrair_bestiario_dmg.py` | ⏳ a criar — heurística `pdftotext` + revisão humana |

---

## Fases

| Fase | Entrega |
|------|---------|
| M0 | Este RF + entrada em [livros-para-dados.md](../../../docs/livros-para-dados.md) |
| M1 | JSON mínimo + `GET /dnd35/regras/bestiario` (listagem paginada) |
| M2 | UI “inserir do catálogo” no cadastro de monstro |
| M3 | Encontros / grupos (DMG) — backlog |

---

## Implementação atual relacionada

- Consumíveis DMG: `backend/scripts/seed_consumiveis.py`
- Combate e condições: [04-combate-dnd35.md](04-combate-dnd35.md)
