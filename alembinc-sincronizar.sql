-- ============================================================================
-- RECONCILIACAO ALEMBIC - Sincronizar historico com estado material
-- ============================================================================
-- Banco alvo: neondb (Neon producao)
-- Objetivo: Registrar 14 hashes de migration pendentes em alembic_version
--           SEM re-executar qualquer SQL de migration (materialized state only)
-- Idempotency: INSERT com WHERE NOT EXISTS para evitar duplicatas
-- Data: 2026-04-12
-- ============================================================================

-- PRE-CHECK: Ver estado atual
SELECT 'ANTES' AS status, COUNT(*) AS total_hashes_registrados
FROM public.alembic_version;

-- Hashes atualmente registrados
SELECT version_num FROM public.alembic_version ORDER BY version_num;

-- ============================================================================
-- INSERCOES IDEMPOTENTES - 14 hashes pendentes (ordem topologica)
-- ============================================================================

-- d5f9a2c1b8e7 (d5f9a2c1b8e7_hp_negativo_regras_morte)
INSERT INTO public.alembic_version (version_num)
SELECT 'd5f9a2c1b8e7'
WHERE NOT EXISTS (SELECT 1 FROM public.alembic_version WHERE version_num = 'd5f9a2c1b8e7');

-- 8d9c1b7a4f21 (add_performance_indexes_catalogs)
INSERT INTO public.alembic_version (version_num)
SELECT '8d9c1b7a4f21'
WHERE NOT EXISTS (SELECT 1 FROM public.alembic_version WHERE version_num = '8d9c1b7a4f21');

-- 9f3c2f7b1a01 (add_combatente_owner)
INSERT INTO public.alembic_version (version_num)
SELECT '9f3c2f7b1a01'
WHERE NOT EXISTS (SELECT 1 FROM public.alembic_version WHERE version_num = '9f3c2f7b1a01');

-- a1c9f4e7d233 (add_magia_historico_table)
INSERT INTO public.alembic_version (version_num)
SELECT 'a1c9f4e7d233'
WHERE NOT EXISTS (SELECT 1 FROM public.alembic_version WHERE version_num = 'a1c9f4e7d233');

-- a35b1f4c9d10 (backfill_legacy_nulls)
INSERT INTO public.alembic_version (version_num)
SELECT 'a35b1f4c9d10'
WHERE NOT EXISTS (SELECT 1 FROM public.alembic_version WHERE version_num = 'a35b1f4c9d10');

-- a5c3f8b2e1d9 (normalize_magias_classe)
INSERT INTO public.alembic_version (version_num)
SELECT 'a5c3f8b2e1d9'
WHERE NOT EXISTS (SELECT 1 FROM public.alembic_version WHERE version_num = 'a5c3f8b2e1d9');

-- b7c2d11f93a4 (expand_magias_catalog_and_classes)
INSERT INTO public.alembic_version (version_num)
SELECT 'b7c2d11f93a4'
WHERE NOT EXISTS (SELECT 1 FROM public.alembic_version WHERE version_num = 'b7c2d11f93a4');

-- c1b7e4d2a9f0 (add_data_constraints)
INSERT INTO public.alembic_version (version_num)
SELECT 'c1b7e4d2a9f0'
WHERE NOT EXISTS (SELECT 1 FROM public.alembic_version WHERE version_num = 'c1b7e4d2a9f0');

-- c8d4e2f7a901 (add_combatente_alinhamento_dominios)
INSERT INTO public.alembic_version (version_num)
SELECT 'c8d4e2f7a901'
WHERE NOT EXISTS (SELECT 1 FROM public.alembic_version WHERE version_num = 'c8d4e2f7a901');

-- d21fe43b8aa9 (add_grimorio_magias_table)
INSERT INTO public.alembic_version (version_num)
SELECT 'd21fe43b8aa9'
WHERE NOT EXISTS (SELECT 1 FROM public.alembic_version WHERE version_num = 'd21fe43b8aa9');

-- e4a1f9c8d2b3 (add_soft_delete_columns)
INSERT INTO public.alembic_version (version_num)
SELECT 'e4a1f9c8d2b3'
WHERE NOT EXISTS (SELECT 1 FROM public.alembic_version WHERE version_num = 'e4a1f9c8d2b3');

-- ef91a3b2c774 (add_grimorio_historico_troca_table)
INSERT INTO public.alembic_version (version_num)
SELECT 'ef91a3b2c774'
WHERE NOT EXISTS (SELECT 1 FROM public.alembic_version WHERE version_num = 'ef91a3b2c774');

-- f2a7b1c4d9e0 (add_combate_historico_table)
INSERT INTO public.alembic_version (version_num)
SELECT 'f2a7b1c4d9e0'
WHERE NOT EXISTS (SELECT 1 FROM public.alembic_version WHERE version_num = 'f2a7b1c4d9e0');

-- f31aa2bc1d55 (add_grimorio_notificacoes_table)
INSERT INTO public.alembic_version (version_num)
SELECT 'f31aa2bc1d55'
WHERE NOT EXISTS (SELECT 1 FROM public.alembic_version WHERE version_num = 'f31aa2bc1d55');

-- ============================================================================
-- POS-CHECK: Validar estado final
-- ============================================================================
SELECT 'DEPOIS' AS status, COUNT(*) AS total_hashes_registrados
FROM public.alembic_version;

-- Todos os hashes finais (em ordem)
SELECT version_num FROM public.alembic_version ORDER BY version_num;

-- Confirmar que nenhuma duplicata foi criada
SELECT version_num, COUNT(*) AS duplicatas
FROM public.alembic_version
GROUP BY version_num
HAVING COUNT(*) > 1;
