# Conjuração D&D 3.5 no Arena — referência para evolução

Este documento fixa as regras implementadas no código para **atributo de conjuração**, **magias adicionais (Tabela 1-1)**, **clérigo (magias por dia + domínio)** e **troca de magias (Bardo / Feiticeiro)**, alinhadas às planilhas de referência no repositório.

## Fontes de dados (Excel)

| Arquivo | Uso |
|--------|-----|
| `tabela1-1_mod_habilidades_e_magias.xlsx` | **Tabela 1-1**: magias adicionais por nível de magia (0–9) conforme o **modificador** do atributo de conjuração. |
| `Magias por dia clerigo.xlsx` | Tabela de **magias por dia** do clérigo: coluna **C** = apenas truques (nível 0); a partir de **D–E** vêm pares **Normal / Domínio** para os níveis 1–9. |

> **Truques e domínio:** na planilha do clérigo não existe coluna “Domínio” para o nível 0 — só um valor para truques. O **+1 de domínio** aplica-se a partir do **nível de magia 1**. O código reflete isso em `CLERIC_SPELLS_PER_DAY_DOMINIO` (primeira posição = 0).

---

## Atributo de conjuração por classe

O **modificador** usado para **magias adicionais** (e, na UI, para o texto de slots no grimório/ficha) é sempre \(\lfloor (\text{atributo} - 10) / 2 \rfloor\) do atributo indicado abaixo.

| Classe (UI) | Atributo no combatente | Onde está no código |
|-------------|-------------------------|----------------------|
| Mago | Inteligência | `SPELLCASTING_ABILITY_BY_CLASS` / `ATRIBUTO_CHAVE` |
| Feiticeiro | Carisma | idem |
| Bardo | Carisma | idem |
| Clérigo | Sabedoria | idem |
| Druida | Sabedoria | idem |
| Paladino | Sabedoria | idem |
| Ranger | Sabedoria | idem |

**Arquivos:**

- Frontend: `frontend/js/utils/combat-rules.js` — `SPELLCASTING_ABILITY_BY_CLASS`, `bonusMagiasPorNivelDoModificador`, `getFallbackSpellSlots`.
- Backend: `backend/app/services/combatente_service.py` — `ATRIBUTO_CHAVE`, `_bonus_magias_por_modificador`, `inicializar_slots_magia`.

---

## Tabela 1-1 — magias adicionais por modificador

- Vetor de **10 inteiros** (índices **0–9** = níveis de magia **0–9**): quantos **slots extras** aquele modificador concede em cada nível.
- Implementação espelhada: `SPELL_BONUS_BY_MODIFIER` (JS) e `_SPELL_BONUS_BY_MODIFIER` (Python).
- Modificador efetivo é limitado (ex.: **−5** a **+45** no JS) para evitar valores absurdos.

Ao alterar a planilha oficial, **atualizar os dois arquivos** (JS e Python) e os testes que dependem dos totais.

---

## Clérigo — slots (normal + domínio + Tabela 1-1)

1. **Base:** `CLERIC_SPELLS_PER_DAY_NORMAL` + `CLERIC_SPELLS_PER_DAY_DOMINIO` por **nível de personagem** (1–20), 10 colunas (níveis de magia 0–9).
2. **Magias adicionais:** somam-se à parte “normal” conforme Sabedoria (`SPELL_BONUS_BY_MODIFIER` por nível de magia).
3. **Total exibido:** normal (com bônus) + domínio; na ficha/grimório o texto discrimina quando `total_dominio > 0`.

**Backend** persiste só `total` por linha em `magias_slots`; o detalhe normal/domínio na UI vem do cálculo em `getFallbackSpellSlots` + `resolveCombatenteSpellSlots` (priorizar totais recalculados para clérigo, não `Math.max` cego com valor antigo do banco).

---

## Troca de magias conhecida — Bardo e Feiticeiro

Regra **só** para essas classes (preparadas no grimório com essa classe).

| Classe | Quando pode trocar (nível de personagem) |
|--------|-------------------------------------------|
| **Feiticeiro** | Níveis **pares** a partir do **4º** (4, 6, 8, …). |
| **Bardo** | Níveis **5, 8, 11, 14, 17, 20**. |

**Regras da troca** (resumo; ver `GrimorioService.trocar_magia`):

- Endpoint: `POST /api/v1/grimorio/{combatente_id}/troca`.
- A magia **nova** deve estar na lista da classe; nível da nova ≤ nível da removida e ≤ **(nível máximo conjurável − 1)** para aquela classe/nível de personagem.
- Histórico em `grimorio_historico_troca`; notificação `TROCA_DISPONIVEL` quando o nível do personagem permite.

**Arquivo principal:** `backend/app/services/grimorio_service.py` (`trocar_magia`, `_garantir_notificacoes_sistema`).

---

## Lista de magias no catálogo (Feiticeiro = Mago)

Na API e no `MagiaService.js`, **Feiticeiro** usa a mesma lista que **Mago** para busca (`FEITICEIRO` → `MAGO`). Os **slots** de Feiticeiro usam a tabela própria de Feiticeiro no `CombatenteService`.

---

## Manutenção: checklist ao mudar regras

1. Planilhas Excel atualizadas no repositório.
2. Sincronizar **Tabela 1-1** em `combat-rules.js` e `combatente_service.py`.
3. Clérigo: ajustar `CLERIC_SPELLS_PER_DAY_*` se a planilha `Magias por dia clerigo.xlsx` mudar; manter truques **sem** slot de domínio na coluna 0.
4. Rodar testes relevantes (`test_pagination`, grimório, combatente slots).
5. Atualizar este documento e a skill `.cursor/skills/dnd-spellcasting-conventions/SKILL.md` se o comportamento mudar.

---

*Última revisão alinhada ao código em abril/2026.*
