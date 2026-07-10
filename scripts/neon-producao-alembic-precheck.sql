-- ============================================================================
-- PRE-CHECK — alinhar alembic_version no Neon PRODUÇÃO (projetoRPG_Oreon)
-- ============================================================================
-- Rode ANTES de `alembic stamp head` (NÃO use `upgrade head` neste banco).
-- Uso: psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f scripts/neon-producao-alembic-precheck.sql
-- ============================================================================

\echo '=== 1. Revisão Alembic atual ==='
SELECT version_num AS alembic_atual FROM public.alembic_version;

\echo '=== 2. Schemas (devem estar vazios: tabelas ficam em public) ==='
SELECT schema_name
FROM information_schema.schemata
WHERE schema_name IN ('auth', 'dnd35');

\echo '=== 3. Tabelas Tormenta críticas (devem existir em public) ==='
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN (
    'tormenta_personagens',
    'tormenta_campanhas',
    'tormenta_campanhas_sessoes',
    'tormenta_campanha_solicitacoes',
    'tormenta_handouts'
  )
ORDER BY table_name;

\echo '=== 4. Colunas Tormenta campanha (convite + regras opcionais) ==='
SELECT column_name
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name = 'tormenta_campanhas'
  AND column_name IN (
    'convite_token',
    'convite_ativo',
    'regras_opcionais_ativas'
  )
ORDER BY column_name;

\echo '=== 5. OAuth em usuarios ==='
SELECT column_name
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name = 'usuarios'
  AND column_name IN ('oauth_provider', 'oauth_subject')
ORDER BY column_name;

\echo '=== 6. Contagens de sanidade (não devem ser zero em prod ativa) ==='
SELECT
  (SELECT COUNT(*) FROM public.usuarios) AS usuarios,
  (SELECT COUNT(*) FROM public.tormenta_personagens) AS tormenta_personagens,
  (SELECT COUNT(*) FROM public.tormenta_campanhas) AS tormenta_campanhas;

\echo '=== 7. Validação automática (falha se pré-requisito ausente) ==='
DO $$
DECLARE
  missing_tables int;
  missing_cols int;
  extra_schemas int;
  current_rev text;
BEGIN
  SELECT COUNT(*) INTO extra_schemas
  FROM information_schema.schemata
  WHERE schema_name IN ('auth', 'dnd35');

  IF extra_schemas > 0 THEN
    RAISE EXCEPTION
      'ABORTAR: schemas auth/dnd35 existem (%). Este runbook assume tabelas em public.',
      extra_schemas;
  END IF;

  SELECT COUNT(*) INTO missing_tables
  FROM (
    VALUES
      ('tormenta_personagens'),
      ('tormenta_campanhas'),
      ('tormenta_campanhas_sessoes'),
      ('tormenta_campanha_solicitacoes'),
      ('tormenta_handouts')
  ) AS expected(name)
  WHERE NOT EXISTS (
    SELECT 1
    FROM information_schema.tables t
    WHERE t.table_schema = 'public' AND t.table_name = expected.name
  );

  IF missing_tables > 0 THEN
    RAISE EXCEPTION
      'ABORTAR: faltam % tabela(s) Tormenta em public. Corrija o schema antes do stamp.',
      missing_tables;
  END IF;

  SELECT COUNT(*) INTO missing_cols
  FROM (
    VALUES
      ('convite_token'),
      ('convite_ativo'),
      ('regras_opcionais_ativas')
  ) AS expected(col)
  WHERE NOT EXISTS (
    SELECT 1
    FROM information_schema.columns c
    WHERE c.table_schema = 'public'
      AND c.table_name = 'tormenta_campanhas'
      AND c.column_name = expected.col
  );

  IF missing_cols > 0 THEN
    RAISE EXCEPTION
      'ABORTAR: faltam % coluna(s) em tormenta_campanhas.',
      missing_cols;
  END IF;

  SELECT version_num INTO current_rev FROM public.alembic_version LIMIT 1;

  IF current_rev = 'p1q2r3s4t5u6' THEN
    RAISE NOTICE 'OK: alembic_version já está no head (p1q2r3s4t5u6). Nada a fazer.';
  ELSIF current_rev IS NULL THEN
    RAISE EXCEPTION 'ABORTAR: alembic_version vazio.';
  ELSE
    RAISE NOTICE 'OK para stamp: revisão atual=% → alvo p1q2r3s4t5u6 (head).', current_rev;
  END IF;
END $$;

\echo '=== PRE-CHECK concluído sem erros ==='
