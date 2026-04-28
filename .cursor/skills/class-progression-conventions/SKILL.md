---
name: class-progression-conventions
description: Implementa e evolui progressao da ficha na Arena TTRPG (BBA, resistencias, defesas, iniciativa e habilidades especiais) com contrato backend/frontend/banco e compatibilidade legada. Use quando alterar ficha por classe/nivel, parser de tabelas de classe, campos de progressao em combatentes ou regras de armadura/item de protecao.
---

# Class Progression Conventions

## Quando usar

Use esta skill quando a demanda envolver qualquer regra de progressao por classe/nivel:

- BBA (`bonus_base_ataque`)
- Resistencias base e total (`*_base`, `fortitude/reflexos/vontade`)
- Defesas automaticas (`ca`, `toque`, `surpresa`)
- Iniciativa automatica para jogador (DES + talentos)
- Habilidades Especiais por classe
- Integracao de `bonus_ca` de Armadura/Item de Protecao
- Consumo do catalogo `docs/dados/tabelas_classes_catalogo.json`

## Referencia obrigatoria

Antes de editar, leia:

- `docs/progressao-classes-bba-resistencias-habilidades.md`
- `backend/app/games/dnd35/bonus_base_ataque.py`
- `backend/app/services/combatente_service.py`
- `backend/app/services/armadura_protecao_service.py`
- `backend/app/api/v1/armaduras_protecao.py`
- `frontend/js/controllers/FichaPersonagemController.js`

## Contrato e persistencia

1. **Backend primeiro**
   - Novas regras ficam centralizadas em `backend/app/games/dnd35/bonus_base_ataque.py`.
   - O service `CombatenteService` deve ser a unica camada que aplica/calcula progressao no CRUD.

2. **Schema e compatibilidade**
   - Se houver novo campo de progressao, atualizar:
     - model (`backend/app/models/combatente.py`)
     - schema response (`backend/app/schemas/combatente.py`)
     - schema guard em `backend/app/main.py` para banco legado
     - sincronizacao de legado em `backend/app/games/dnd35/sync_progressao_combatentes.py` (startup em `main.py`)

3. **Frontend resiliente**
   - A ficha deve renderizar formato novo e fallback legado quando aplicavel.
   - Se alterar service JS importado com query param de versao (`?v=`), atualizar o versionamento para evitar cache antigo.

## Regras atuais que nao podem regredir

- BBA deve vir do catalogo por classe/nivel; fallback por progressao canonica quando faltar dado.
- Resistencias totais = base + modificador de atributo (CON, DES, SAB).
- Defesas:
  - `toque = 10 + mod DES`
  - `surpresa = 10 + bonus_ca_total_itens`
  - `ca = 10 + mod DES + bonus_ca_total_itens`
- Bonus de armadura vem de `bonus_ca` dos itens vinculados em Armadura/Item de Protecao.
- Add/remove de item deve incrementar/decrementar imediatamente `surpresa` e `ca`.
- Jogador: `iniciativa = mod DES + bonus de talento` (Iniciativa Aprimorada = +4).
- Habilidades especiais devem aceitar formato agrupado por nivel e manter compatibilidade com string legada.

## Checklist de implementacao

- [ ] Atualizou regra no backend sem duplicar logica no frontend.
- [ ] Recalculou defesa ao adicionar/remover item de protecao.
- [ ] Preservou dados legados (schema guard/backfill/sincronizacao em memoria).
- [ ] Atualizou DTO/model frontend se novo campo estiver no payload.
- [ ] Atualizou UI da ficha sem poluicao visual.
- [ ] Adicionou/ajustou testes em `backend/tests/test_combatentes_api.py`.
- [ ] Executou testes e validou linter dos arquivos alterados.

## Validacao minima

- `pytest backend/tests/test_combatentes_api.py -q`
- `pytest backend/tests/test_armaduras_protecao_api.py -q`
- Verificar na ficha:
  - BBA exibido corretamente (incluindo iterativos)
  - Toque/Surpresa/CA coerentes com DES e itens de protecao
  - breakdown de iniciativa transparente
  - bloco de habilidades especiais consistente com classe/nivel
