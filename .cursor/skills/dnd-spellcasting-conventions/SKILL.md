---
name: dnd-spellcasting-conventions
description: >-
  Regras D&D 3.5 do projeto Arena para conjuração: atributo por classe (INT Mago;
  CAR Feiticeiro/Bardo; SAB Clérigo/Druida/Paladino/Ranger), Tabela 1-1 de magias
  adicionais, planilhas Excel de referência, clérigo (truques sem slot de domínio),
  troca de magias Bardo/Feiticeiro e onde está no código. Usar ao alterar slots,
  grimório, ficha, seed ou API de magias.
---

# D&D 3.5 — conjuração no Arena (convenções de código)

## Quando usar esta skill

- Mudanças em **slots**, **magias por dia**, **modificador de atributo** ou **clérigo + domínio**.
- **Troca de magia** (Bardo/Feiticeiro), notificações ou `grimorio_historico_troca`.
- Dúvidas sobre **planilhas** `tabela1-1_mod_habilidades_e_magias.xlsx` e `Magias por dia clerigo.xlsx`.

## Atributo de conjuração (magias adicionais / Tabela 1-1)

| Classe | Atributo |
|--------|----------|
| Mago | Inteligência |
| Feiticeiro, Bardo | Carisma |
| Clérigo, Druida, Paladino, Ranger | Sabedoria |

- **Frontend:** `frontend/js/utils/combat-rules.js` — `SPELLCASTING_ABILITY_BY_CLASS`, `SPELL_BONUS_BY_MODIFIER`, `getFallbackSpellSlots`, `resolveCombatenteSpellSlots`.
- **Backend:** `backend/app/services/combatente_service.py` — `ATRIBUTO_CHAVE`, `_SPELL_BONUS_BY_MODIFIER`, `_linha_slots_clerigo`, `inicializar_slots_magia`.

A Tabela **1-1** (vetor 0–9 por modificador) deve permanecer **idêntica** em JS e Python ao alterar a planilha fonte.

## Clérigo

- Planilha: `Magias por dia clerigo.xlsx` — coluna **C** só truques; **D–E** = nível 1 Normal/Domínio; **sem** +1 de domínio em truques.
- Tabelas: `CLERIC_SPELLS_PER_DAY_NORMAL` + `CLERIC_SPELLS_PER_DAY_DOMINIO` (primeira entrada de domínio = **0**).
- UI: `textoSlotsClerigoBreakdown`; mesclagem de slots persistidos com tabela em `resolveCombatenteSpellSlots` (não inflar total com valor antigo do banco para clérigo).

## Catálogo vs slots

- **Lista de magias:** Feiticeiro consulta como **MAGO** no `MagiaService` / API (`FEITICEIRO` → `MAGO`).
- **Slots:** tabela própria de Feiticeiro em `inicializar_slots_magia`.

## Troca de magia (Bardo / Feiticeiro)

- **Feiticeiro:** níveis **pares** ≥ **4**.
- **Bardo:** níveis **5, 8, 11, 14, 17, 20**.
- **Código:** `backend/app/services/grimorio_service.py` — `trocar_magia`; API `POST .../grimorio/{id}/troca`.

## Documentação longa

Ver `docs/regras-conjuracao-dnd-arena.md` no repositório.
