-- Hotfix seguro para alinhamento parcial do schema/dados de producao
-- Banco alvo: neondb (Neon)
-- Objetivo:
-- 1. Popular magias_classes de forma idempotente
-- 2. Criar indices compostos pendentes e seguros
-- 3. Validar o resultado sem mexer na tabela alembic_version
--
-- Observacao importante:
-- - Este script NAO cria a constraint unica em magias.nome.
-- - Existem duplicatas reais de nomes em magias; forcar essa parte agora alteraria nomes visiveis.
-- - Este script tambem NAO atualiza alembic_version; o historico Alembic continua pendente,
--   mas as migrations posteriores sao majoritariamente idempotentes.

-- =========================
-- PRE-CHECK
-- =========================
SELECT
	COUNT(*) AS total_magias_elegiveis
FROM public.magias
WHERE classe IS NOT NULL
	AND TRIM(classe) <> ''
	AND nivel IS NOT NULL;

SELECT
	COUNT(*) AS total_magias_classes_antes
FROM public.magias_classes;

-- =========================
-- BACKFILL DE magias_classes
-- =========================
INSERT INTO public.magias_classes (
	magia_id,
	classe,
	nivel
)
SELECT
	m.id,
	UPPER(TRIM(m.classe)),
	m.nivel
FROM public.magias AS m
WHERE m.classe IS NOT NULL
	AND TRIM(m.classe) <> ''
	AND m.nivel IS NOT NULL
	AND NOT EXISTS (
		SELECT 1
		FROM public.magias_classes AS mc
		WHERE mc.magia_id = m.id
			AND mc.classe = UPPER(TRIM(m.classe))
	);

-- =========================
-- INDICES COMPOSTOS PENDENTES
-- =========================
CREATE INDEX IF NOT EXISTS ix_grimorio_notificacoes_comb_classe_lida
	ON public.grimorio_notificacoes (combatente_id, classe, lida);

CREATE INDEX IF NOT EXISTS ix_grimorio_notificacoes_comb_classe_tipo
	ON public.grimorio_notificacoes (combatente_id, classe, tipo);

CREATE INDEX IF NOT EXISTS ix_pericias_classes_classe_nome_pericia
	ON public.pericias_classes (classe_nome, pericia_id);

CREATE INDEX IF NOT EXISTS ix_pericia_jogadores_combatente_pericia
	ON public.pericia_jogadores (combatente_id, pericia_id);

CREATE INDEX IF NOT EXISTS ix_magias_classes_classe_nivel_magia
	ON public.magias_classes (classe, nivel, magia_id);

CREATE INDEX IF NOT EXISTS ix_magias_slots_combatente_nivel
	ON public.magias_slots (combatente_id, nivel);

CREATE INDEX IF NOT EXISTS ix_magias_preparadas_combatente_slot_magia
	ON public.magias_preparadas (combatente_id, nivel_slot, magia_id);

CREATE INDEX IF NOT EXISTS ix_grimorio_magias_combatente_classe_adicionada
	ON public.grimorio_magias (combatente_id, classe, adicionada_em);

CREATE INDEX IF NOT EXISTS ix_equipamentos_ativo_deleted_nome
	ON public.equipamentos (ativo, deleted_at, nome);

CREATE INDEX IF NOT EXISTS ix_talentos_ativo_deleted_nome
	ON public.talentos (ativo, deleted_at, nome);

CREATE INDEX IF NOT EXISTS ix_combatentes_tipo_deleted_dono
	ON public.combatentes (tipo, deleted_at, dono_id);

-- =========================
-- POS-CHECK
-- =========================
SELECT
	COUNT(*) AS total_magias_classes_depois
FROM public.magias_classes;

SELECT
	indexname,
	indexdef
FROM pg_indexes
WHERE schemaname = 'public'
	AND indexname IN (
		'ix_grimorio_notificacoes_comb_classe_lida',
		'ix_grimorio_notificacoes_comb_classe_tipo',
		'ix_pericias_classes_classe_nome_pericia',
		'ix_pericia_jogadores_combatente_pericia',
		'ix_magias_classes_classe_nivel_magia',
		'ix_magias_slots_combatente_nivel',
		'ix_magias_preparadas_combatente_slot_magia',
		'ix_grimorio_magias_combatente_classe_adicionada',
		'ix_equipamentos_ativo_deleted_nome',
		'ix_talentos_ativo_deleted_nome',
		'ix_combatentes_tipo_deleted_dono'
	)
ORDER BY indexname;

-- =========================
-- VALIDACAO DE CONSULTAS CRITICAS
-- =========================
EXPLAIN (ANALYZE, BUFFERS)
SELECT
	id,
	combatente_id,
	magia_id,
	classe,
	adicionada_em
FROM public.grimorio_magias
WHERE combatente_id = 3
	AND classe = 'CLERIGO'
ORDER BY adicionada_em DESC;

EXPLAIN (ANALYZE, BUFFERS)
SELECT
	id,
	nome,
	nivel,
	classe
FROM public.magias
WHERE classe = 'CLERIGO'
	AND nivel = 2
ORDER BY nome;