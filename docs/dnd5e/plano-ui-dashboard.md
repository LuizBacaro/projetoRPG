# D&D 5E — plano de UI e catálogos

**Estado:** backend e páginas base existem (`frontend/games/dnd5e/pages/`); paridade visual/comportamental com 3.5 é incremental.

**Fonte de dados:** ADR [0003-dnd5e-fonte-dados-5e-database.md](../adr/0003-dnd5e-fonte-dados-5e-database.md) — tag `DND5E_DATABASE_VERSION` em `backend/app/games/dnd5e/data/catalogo_metadata.py` (**atual: v5.7.0**).

---

## O que já existe

| Área | Backend | Frontend |
|------|---------|----------|
| Personagens | `dnd5e/personagens` | `pages/ficha-personagem.html` |
| Combate / arena | `dnd5e/combate` | `pages/arena.html` |
| Conjuração / grimório | `conjuracao`, `grimorio` | módulo `spellcasting/` (TS → `js/spellcasting/`) |
| Regras / catálogos | `regras`, data `*_catalogo.py` | consumo via services na ficha |
| Seletor | `games_catalog` status `disponivel` | `/games/dnd5e/pages/dashboard.html` |

Rewrites Vercel: `/dnd5e/dashboard`, `/dnd5e/ficha`, `/dnd5e/arena` (ver `vercel.json`).

---

## Fases de produto (UI)

| Fase | Entrega | Prioridade |
|------|---------|------------|
| **U0** | Dashboard 5e: lista personagens + link arena + troca de jogo | Alta |
| **U1** | Ficha: atributos, proficiência, salvaguardas alinhados API `dnd5e` | Alta |
| **U2** | Grimório: paridade UX com 3.5 (filtros, preparação, slots) | Média |
| **U3** | Raças/classes: picker com catálogo API + tooltips SRD | Média |
| **U4** | Equipamento e inventário estruturado | Baixa |
| **U5** | Antecedentes / feats na criação guiada | Baixa |

---

## Tooling de catálogo (dev)

1. Clonar [5e-bits/5e-database](https://github.com/5e-bits/5e-database) na tag `DND5E_DATABASE_VERSION`.
2. Gerar JSON enxuto por domínio (`spells`, `races`, `classes`) **fora** do commit principal ou em branch de tooling.
3. Mapear para `*_catalogo.py` / seeds Alembic `dnd5e_*`.
4. Atualizar `catalogo_metadata.py` e notas neste doc no PR.

**Não** importar automaticamente descrições longas EN para o repo sem camada `spell_i18n` / resumo PT.

---

## Build frontend spellcasting

```bash
cd frontend/games/dnd5e/spellcasting
npm ci && npm run build && npm test
```

Ver [spellcasting/README.md](../../frontend/games/dnd5e/spellcasting/README.md).

---

## Testes backend de referência

```bash
cd backend
python3 -m pytest tests/test_dnd5e_personagens_api.py tests/test_dnd5e_conjuracao_ficha.py tests/test_dnd5e_grimorio_api.py -q
```

---

## Critério “paridade com 3.5” no seletor

- Mesmo fluxo: login → seletor → `POST /games/selecionar` → dashboard do jogo.
- Regras e números **sempre** 5e; nunca reutilizar `combat-rules.js` do `dnd35`.
