# Status de Otimizacao — Local x Producao

Data: 2026-04-12

## 1) O que foi feito agora (local)

- Hardening da migration antiga de indices para evitar falha por indice existente:
  - backend/alembic_migrations/versions/66fcb1736292_add_composite_indexes_grimorio_.py
- Nova migration incremental de performance aplicada localmente:
  - backend/alembic_migrations/versions/8d9c1b7a4f21_add_performance_indexes_catalogs.py
- Otimizacao de filtro de magias por classe para priorizar tabela normalizada (`magias_classes`) e usar fallback legado apenas quando necessario:
  - backend/app/repositories/magia_repository.py

## 2) Validacao executada

- Alembic upgrade local: OK ate head
- Testes focados: OK
  - tests/test_magias_api.py
  - tests/test_pericia_service.py
  - tests/test_catalog_cache_api.py

Resultado: 12 passed

## 3) Ganhos observados em plano de execucao (SQLite local)

Consultas que passaram a usar indice adequado:

- Pericias por classe
  - antes: SCAN em `pericias_classes`
  - depois: SEARCH com indice de cobertura em `classe_nome`

- Slots de magia por combatente
  - antes: SCAN em `magias_slots`
  - depois: SEARCH por `combatente_id` com indice composto

- Magias preparadas por combatente/slot
  - antes: indice pouco aderente a ordenacao
  - depois: SEARCH com indice composto (`combatente_id`, `nivel_slot`, `magia_id`)

- Equipamentos e talentos ativos
  - antes: filtro por `ativo` + ordenacao custosa
  - depois: indice de cobertura para (`ativo`, `deleted_at`, `nome`)

## 4) O que falta para comparativo com producao Neon

Comparativo com producao concluido em leitura.

Conexao validada no Neon:

- Banco: `neondb`
- Usuario: `neondb_owner`
- PostgreSQL: `17.8`

Heads Alembic registradas em producao:

- `2f9b6c4a8e11`
- `5e72b9a1c4d0`
- `7c1e8b4d9a2f`

Interpretacao:

- Producao esta exatamente nas tres heads que antecedem a merge revision `a5c3f8b2e1d9`.
- Isso significa que as migrations posteriores ainda nao entraram no Neon:
  - `a5c3f8b2e1d9_normalize_magias_classe.py`
  - `66fcb1736292_add_composite_indexes_grimorio_.py`
  - `8d9c1b7a4f21_add_performance_indexes_catalogs.py`

Achados reais em producao:

- `magias_classes` existe, mas esta vazia (`COUNT(*) = 0`).
- `grimorio_notificacoes` ainda usa apenas indice simples por `combatente_id`.
- `grimorio_magias` ainda faz `Seq Scan` para filtro por `combatente_id + classe`.
- `magias` usa `BitmapAnd` entre indices simples de `classe` e `nivel`; funciona, mas ainda sem indice composto ou tabela normalizada populada.

Planos medidos no Neon:

- `grimorio_notificacoes`
  - usa `Index Scan` em `ix_grimorio_notificacoes_combatente_id`
  - aplica filtro residual em `classe` e `lida`
  - ainda faz `Sort` por `criada_em DESC`

- `grimorio_magias`
  - faz `Seq Scan` com filtro em `combatente_id` e `classe`
  - ainda faz `Sort` por `adicionada_em DESC`

- `magias`
  - faz `Bitmap Heap Scan`
  - combina `ix_magias_nivel` + `ix_magias_classe`
  - ordena por `nome` fora do indice

## 5) Como fechar o comparativo Local x Producao

Proximos passos recomendados:

1. Aplicar em producao a cadeia pendente a partir de `a5c3f8b2e1d9`, validando antes a arvore Alembic para evitar drift entre heads.
2. Executar backfill idempotente de `magias_classes` antes de depender dela como fonte principal de consulta.
3. Aplicar os indices compostos pendentes de grimorio e catalogos.
4. Reexecutar `EXPLAIN (ANALYZE, BUFFERS)` nas consultas criticas apos rollout.

## 6) Risco residual

- O volume atual de `grimorio_notificacoes` (6 linhas) e `grimorio_magias` (129 linhas) ainda e pequeno; alguns ganhos de indice vao aparecer de forma mais clara conforme a base crescer.
- O principal risco remanescente deixou de ser dados ausentes e passou a ser a reconciliacao futura do historico Alembic com o estado material do schema em producao.

## 7) Rollout executado em producao

Script executado manualmente no editor SQL conectado ao Neon em 2026-04-12.

Resultado validado:

- `magias_classes` foi populada com `1035` linhas.
- `1035` magias distintas ficaram cobertas pela tabela normalizada.
- Os 11 indices compostos previstos no hotfix existem no schema `public`.
- `alembic_version` permaneceu inalterada, com as heads:
  - `2f9b6c4a8e11`
  - `5e72b9a1c4d0`
  - `7c1e8b4d9a2f`

Indices confirmados em producao:

- `ix_grimorio_notificacoes_comb_classe_lida`
- `ix_grimorio_notificacoes_comb_classe_tipo`
- `ix_pericias_classes_classe_nome_pericia`
- `ix_pericia_jogadores_combatente_pericia`
- `ix_magias_classes_classe_nivel_magia`
- `ix_magias_slots_combatente_nivel`
- `ix_magias_preparadas_combatente_slot_magia`
- `ix_grimorio_magias_combatente_classe_adicionada`
- `ix_equipamentos_ativo_deleted_nome`
- `ix_talentos_ativo_deleted_nome`
- `ix_combatentes_tipo_deleted_dono`

## 8) Efeito medido apos rollout

### 8.1 Consulta normalizada de magias

Plano observado no Neon:

- `Bitmap Index Scan` em `ix_magias_classes_classe_nivel_magia`
- `Bitmap Heap Scan` em `magias_classes`
- `Hash Join` com `magias`

Conclusao:

- O backfill tornou viavel a estrategia normalizada do backend.
- O filtro por `classe + nivel` agora usa o indice composto novo na tabela relacional.

### 8.2 Grimorio e notificacoes

Planos observados no Neon:

- `grimorio_magias`: ainda faz `Seq Scan`
- `grimorio_notificacoes`: ainda faz `Seq Scan`

Interpretacao:

- Isso nao indica falha do indice.
- As duas tabelas ainda sao muito pequenas no ambiente atual e o otimizador prefere varredura sequencial pelo custo estimado.
- Conforme o volume crescer, a tendencia e o planner passar a usar os indices compostos com mais frequencia.

## 9) Pendencia remanescente

- O estado funcional do banco melhorou e agora esta alinhado com a estrategia de consulta do backend.
- O historico Alembic de producao continua defasado em relacao ao estado material do schema.
- Essa reconciliacao deve ser tratada em uma etapa separada, com cuidado, porque envolve historico de migracao e nao apenas dados/indices.
