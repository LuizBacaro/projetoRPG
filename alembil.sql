-- ============================================================================
-- RECONCILIACAO ALEMBIC - 14 hashes pendentes
-- ============================================================================

-- PRE-CHECK
SELECT COUNT(*) AS total_antes FROM public.alembic_version;

-- Insercoes idempotentes (14 hashes)
INSERT INTO public.alembic_version (version_num) SELECT 'd5f9a2c1b8e7' WHERE NOT EXISTS (SELECT 1 FROM public.alembic_version WHERE version_num = 'd5f9a2c1b8e7');
INSERT INTO public.alembic_version (version_num) SELECT '8d9c1b7a4f21' WHERE NOT EXISTS (SELECT 1 FROM public.alembic_version WHERE version_num = '8d9c1b7a4f21');
INSERT INTO public.alembic_version (version_num) SELECT '9f3c2f7b1a01' WHERE NOT EXISTS (SELECT 1 FROM public.alembic_version WHERE version_num = '9f3c2f7b1a01');
INSERT INTO public.alembic_version (version_num) SELECT 'a1c9f4e7d233' WHERE NOT EXISTS (SELECT 1 FROM public.alembic_version WHERE version_num = 'a1c9f4e7d233');
INSERT INTO public.alembic_version (version_num) SELECT 'a35b1f4c9d10' WHERE NOT EXISTS (SELECT 1 FROM public.alembic_version WHERE version_num = 'a35b1f4c9d10');
INSERT INTO public.alembic_version (version_num) SELECT 'a5c3f8b2e1d9' WHERE NOT EXISTS (SELECT 1 FROM public.alembic_version WHERE version_num = 'a5c3f8b2e1d9');
INSERT INTO public.alembic_version (version_num) SELECT 'b7c2d11f93a4' WHERE NOT EXISTS (SELECT 1 FROM public.alembic_version WHERE version_num = 'b7c2d11f93a4');
INSERT INTO public.alembic_version (version_num) SELECT 'c1b7e4d2a9f0' WHERE NOT EXISTS (SELECT 1 FROM public.alembic_version WHERE version_num = 'c1b7e4d2a9f0');
INSERT INTO public.alembic_version (version_num) SELECT 'c8d4e2f7a901' WHERE NOT EXISTS (SELECT 1 FROM public.alembic_version WHERE version_num = 'c8d4e2f7a901');
INSERT INTO public.alembic_version (version_num) SELECT 'd21fe43b8aa9' WHERE NOT EXISTS (SELECT 1 FROM public.alembic_version WHERE version_num = 'd21fe43b8aa9');
INSERT INTO public.alembic_version (version_num) SELECT 'e4a1f9c8d2b3' WHERE NOT EXISTS (SELECT 1 FROM public.alembic_version WHERE version_num = 'e4a1f9c8d2b3');
INSERT INTO public.alembic_version (version_num) SELECT 'ef91a3b2c774' WHERE NOT EXISTS (SELECT 1 FROM public.alembic_version WHERE version_num = 'ef91a3b2c774');
INSERT INTO public.alembic_version (version_num) SELECT 'f2a7b1c4d9e0' WHERE NOT EXISTS (SELECT 1 FROM public.alembic_version WHERE version_num = 'f2a7b1c4d9e0');
INSERT INTO public.alembic_version (version_num) SELECT 'f31aa2bc1d55' WHERE NOT EXISTS (SELECT 1 FROM public.alembic_version WHERE version_num = 'f31aa2bc1d55');

-- POS-CHECK
SELECT COUNT(*) AS total_depois FROM public.alembic_version;
SELECT version_num FROM public.alembic_version ORDER BY version_num;