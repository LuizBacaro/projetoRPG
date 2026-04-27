# Fase C: Inventário técnico pré-migration (`auth` / `dnd35`)

Status: levantamento inicial (abr/2026)

## Objetivo

Registrar o estado real do metadata SQLAlchemy antes da migration de schemas
Postgres, para reduzir risco de omissão de tabela/FK e orientar a ordem de
`ALTER TABLE ... SET SCHEMA ...`.

## Fonte do inventário

Extraído de `Base.metadata` com carregamento dos modelos canônicos via
`app.models` (que agrega hub + D&D 3.5 para metadata/Alembic).

## Tabelas detectadas (29)

### Bucket `auth`

- `usuarios`
- `games_catalog`
- `user_game_memberships`

### Bucket `dnd35`

- `armaduras_protecao`
- `armaduras_protecao_jogador`
- `ataques`
- `campanhas`
- `campanhas_sessoes`
- `combatente_condicoes`
- `combatentes`
- `combates`
- `combates_historico`
- `condicoes`
- `divindades_custom`
- `equipamentos`
- `equipamentos_jogador`
- `grimorio_historico_troca`
- `grimorio_magias`
- `grimorio_notificacoes`
- `magia_historico`
- `magias`
- `magias_classes`
- `magias_preparadas`
- `magias_slots`
- `pericia_jogadores`
- `pericias`
- `pericias_classes`
- `talentos`
- `talentos_jogador`

## Foreign keys detectadas (28)

### Internas ao bucket `auth`

- `user_game_memberships.game_id -> games_catalog.id`
- `user_game_memberships.usuario_id -> usuarios.id`

### Cruzadas `dnd35 -> auth`

- `campanhas.mestre_id -> usuarios.id`
- `divindades_custom.criado_por_id -> usuarios.id`

### Internas ao bucket `dnd35`

- `armaduras_protecao_jogador.item_id -> armaduras_protecao.id`
- `armaduras_protecao_jogador.combatente_id -> combatentes.id`
- `ataques.combatente_id -> combatentes.id`
- `campanhas_sessoes.campanha_id -> campanhas.id`
- `combatente_condicoes.condicao_id -> condicoes.id`
- `combatente_condicoes.combatente_id -> combatentes.id`
- `combatentes.campanha_id -> campanhas.id`
- `equipamentos_jogador.combatente_id -> combatentes.id`
- `equipamentos_jogador.equipamento_id -> equipamentos.id`
- `grimorio_historico_troca.magia_removida_id -> magias.id`
- `grimorio_historico_troca.magia_adicionada_id -> magias.id`
- `grimorio_historico_troca.combatente_id -> combatentes.id`
- `grimorio_magias.magia_id -> magias.id`
- `grimorio_magias.combatente_id -> combatentes.id`
- `grimorio_notificacoes.combatente_id -> combatentes.id`
- `magias_classes.magia_id -> magias.id`
- `magias_preparadas.combatente_id -> combatentes.id`
- `magias_preparadas.magia_id -> magias.id`
- `magias_slots.combatente_id -> combatentes.id`
- `pericia_jogadores.combatente_id -> combatentes.id`
- `pericia_jogadores.pericia_id -> pericias.id`
- `pericias_classes.pericia_id -> pericias.id`
- `talentos_jogador.combatente_id -> combatentes.id`
- `talentos_jogador.talento_id -> talentos.id`

## Ordem sugerida para migração `SET SCHEMA`

### Fase 1 (`auth`)

1. `usuarios`
2. `games_catalog`
3. `user_game_memberships`

### Fase 2 (`dnd35` - raízes sem dependência de outras tabelas dnd35)

1. `condicoes`
2. `equipamentos`
3. `armaduras_protecao`
4. `magias`
5. `pericias`
6. `talentos`
7. `campanhas` (depende de `auth.usuarios`)
8. `divindades_custom` (depende de `auth.usuarios`)

### Fase 3 (`dnd35` - tabelas dependentes)

1. `combatentes` (depende de `dnd35.campanhas`)
2. `combates`
3. `combates_historico`
4. `campanhas_sessoes`
5. `combatente_condicoes`
6. `ataques`
7. `equipamentos_jogador`
8. `armaduras_protecao_jogador`
9. `magias_classes`
10. `magias_slots`
11. `magias_preparadas`
12. `pericias_classes`
13. `pericia_jogadores`
14. `talentos_jogador`
15. `grimorio_magias`
16. `grimorio_historico_troca`
17. `grimorio_notificacoes`
18. `magia_historico`

## Pré-checklist para migration real

- Confirmar nomes de constraints/fks no Postgres de staging.
- Definir estratégia explícita para FKs cruzadas `dnd35 -> auth`.
- Validar scripts Alembic em staging com backup e rollback testado.
- Executar smoke pós-migration: login, seleção de jogo, campanhas e combatentes.

## Observações

- Este inventário é de metadata SQLAlchemy; usar como baseline antes de gerar
  a migration final.
- Pode haver diferenças pontuais de nomes físicos de constraints no banco
  existente; validar via catálogo do Postgres durante C.2.

## Dry-run SQL (staging review)

Comandos previstos para revisão em staging (não executados por este documento).

### Upgrade (public -> auth/dnd35)

```sql
CREATE SCHEMA IF NOT EXISTS auth;
CREATE SCHEMA IF NOT EXISTS dnd35;

ALTER TABLE "public"."usuarios" SET SCHEMA "auth";
ALTER TABLE "public"."games_catalog" SET SCHEMA "auth";
ALTER TABLE "public"."user_game_memberships" SET SCHEMA "auth";

ALTER TABLE "public"."condicoes" SET SCHEMA "dnd35";
ALTER TABLE "public"."equipamentos" SET SCHEMA "dnd35";
ALTER TABLE "public"."armaduras_protecao" SET SCHEMA "dnd35";
ALTER TABLE "public"."magias" SET SCHEMA "dnd35";
ALTER TABLE "public"."pericias" SET SCHEMA "dnd35";
ALTER TABLE "public"."talentos" SET SCHEMA "dnd35";
ALTER TABLE "public"."campanhas" SET SCHEMA "dnd35";
ALTER TABLE "public"."divindades_custom" SET SCHEMA "dnd35";

ALTER TABLE "public"."combatentes" SET SCHEMA "dnd35";
ALTER TABLE "public"."combates" SET SCHEMA "dnd35";
ALTER TABLE "public"."combates_historico" SET SCHEMA "dnd35";
ALTER TABLE "public"."campanhas_sessoes" SET SCHEMA "dnd35";
ALTER TABLE "public"."combatente_condicoes" SET SCHEMA "dnd35";
ALTER TABLE "public"."ataques" SET SCHEMA "dnd35";
ALTER TABLE "public"."equipamentos_jogador" SET SCHEMA "dnd35";
ALTER TABLE "public"."armaduras_protecao_jogador" SET SCHEMA "dnd35";
ALTER TABLE "public"."magias_classes" SET SCHEMA "dnd35";
ALTER TABLE "public"."magias_slots" SET SCHEMA "dnd35";
ALTER TABLE "public"."magias_preparadas" SET SCHEMA "dnd35";
ALTER TABLE "public"."pericias_classes" SET SCHEMA "dnd35";
ALTER TABLE "public"."pericia_jogadores" SET SCHEMA "dnd35";
ALTER TABLE "public"."talentos_jogador" SET SCHEMA "dnd35";
ALTER TABLE "public"."grimorio_magias" SET SCHEMA "dnd35";
ALTER TABLE "public"."grimorio_historico_troca" SET SCHEMA "dnd35";
ALTER TABLE "public"."grimorio_notificacoes" SET SCHEMA "dnd35";
ALTER TABLE "public"."magia_historico" SET SCHEMA "dnd35";
```

### Rollback (auth/dnd35 -> public)

```sql
ALTER TABLE "dnd35"."magia_historico" SET SCHEMA "public";
ALTER TABLE "dnd35"."grimorio_notificacoes" SET SCHEMA "public";
ALTER TABLE "dnd35"."grimorio_historico_troca" SET SCHEMA "public";
ALTER TABLE "dnd35"."grimorio_magias" SET SCHEMA "public";
ALTER TABLE "dnd35"."talentos_jogador" SET SCHEMA "public";
ALTER TABLE "dnd35"."pericia_jogadores" SET SCHEMA "public";
ALTER TABLE "dnd35"."pericias_classes" SET SCHEMA "public";
ALTER TABLE "dnd35"."magias_preparadas" SET SCHEMA "public";
ALTER TABLE "dnd35"."magias_slots" SET SCHEMA "public";
ALTER TABLE "dnd35"."magias_classes" SET SCHEMA "public";
ALTER TABLE "dnd35"."armaduras_protecao_jogador" SET SCHEMA "public";
ALTER TABLE "dnd35"."equipamentos_jogador" SET SCHEMA "public";
ALTER TABLE "dnd35"."ataques" SET SCHEMA "public";
ALTER TABLE "dnd35"."combatente_condicoes" SET SCHEMA "public";
ALTER TABLE "dnd35"."campanhas_sessoes" SET SCHEMA "public";
ALTER TABLE "dnd35"."combates_historico" SET SCHEMA "public";
ALTER TABLE "dnd35"."combates" SET SCHEMA "public";
ALTER TABLE "dnd35"."combatentes" SET SCHEMA "public";
ALTER TABLE "dnd35"."divindades_custom" SET SCHEMA "public";
ALTER TABLE "dnd35"."campanhas" SET SCHEMA "public";
ALTER TABLE "dnd35"."talentos" SET SCHEMA "public";
ALTER TABLE "dnd35"."pericias" SET SCHEMA "public";
ALTER TABLE "dnd35"."magias" SET SCHEMA "public";
ALTER TABLE "dnd35"."armaduras_protecao" SET SCHEMA "public";
ALTER TABLE "dnd35"."equipamentos" SET SCHEMA "public";
ALTER TABLE "dnd35"."condicoes" SET SCHEMA "public";

ALTER TABLE "auth"."user_game_memberships" SET SCHEMA "public";
ALTER TABLE "auth"."games_catalog" SET SCHEMA "public";
ALTER TABLE "auth"."usuarios" SET SCHEMA "public";
```

