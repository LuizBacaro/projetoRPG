# Issue: conjuração Paladino e Patrulheiro (D&D 5e PHB)

**Status: fechada** (backend + arena helper; ficha web 5e pode evoluir separadamente).

## Regras PHB (referência)

| Classe      | Mecânica   | Limite diário / lista                                      | Atributo |
|------------|------------|------------------------------------------------------------|----------|
| Mago       | Preparada  | mod INT + nível (mín. 1)                                   | INT      |
| Clérigo    | Preparada  | mod SAB + nível (mín. 1)                                   | SAB      |
| Druida     | Preparada  | mod SAB + nível (mín. 1)                                   | SAB      |
| Paladino   | Preparada  | mod CAR + **floor(nível/2)** (mín. 1); lista da classe      | CAR      |
| Patrulheiro| Conhecida  | tabela **Spells Known** do patrulheiro (≠ bardo/feiticeiro) | SAB      |

## Implementado

- `PREPARED_CLASSES` = full casters ∪ `{paladino}`; fórmulas em `conjuracao_shared.magias_preparadas_max`.
- Patrulheiro: `KNOWN_SPELLS_HALF_CASTER` + limite no grimório (só magias nível ≥ 1 contam).
- Paladino: grimório sem teto de “conhecidas”; preparação diária com teto PHB.
- Arena: `Dnd5eArenaMagiasHelper` — paladino em preparadores (fallback); `prepara_magias` do API prevalece.
- Testes: `test_dnd5e_conjuracao_ficha.py`, `test_dnd5e_grimorio_api.py`.

## Arquivos principais

- `backend/app/games/dnd5e/data/spell_tables.py`
- `backend/app/games/dnd5e/services/conjuracao_shared.py`
- `backend/app/games/dnd5e/services/conjuracao_ficha_service.py`
- `backend/app/games/dnd5e/services/grimorio_service.py`
- `frontend/games/dnd5e/js/arena/Dnd5eArenaMagiasHelper.js`
