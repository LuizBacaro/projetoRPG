# ADR Fase C: Schemas Postgres (`auth`, `dnd35`)

Status: proposto (abr/2026)  
Escopo: desenho técnico + runbook de execução (sem mudança de código nesta etapa)

Inventário base desta ADR: [fase-c-inventario-tecnico-schemas.md](./fase-c-inventario-tecnico-schemas.md)

Migration base de C.2 (com ordem inicial de `SET SCHEMA` e downgrade inverso):  
`backend/alembic_migrations/versions/fase_c_schemas_auth_dnd35_skeleton.py`

Dry-run SQL para revisão pré-janela: seção "Dry-run SQL (staging review)" em  
`docs/fase-c-inventario-tecnico-schemas.md`.

Runbook operacional da janela em staging:  
`docs/fase-c-runbook-execucao-staging.md`.

## Contexto

Após a consolidação do Auth Hub em `app/shared/*` (Fase B), o banco ainda
mantém as tabelas no schema padrão (`public` no Postgres).

Para o roadmap multi-jogo, a separação lógica por schema é necessária para:

- reduzir acoplamento entre hub global e domínio de jogo;
- preparar isolamento operacional por domínio;
- facilitar futura extração de serviços (Auth Hub x Game Backends).

## Decisão proposta

Adotar dois schemas no Postgres:

- `auth`: tabelas do hub global (usuários, catálogo de jogos, memberships);
- `dnd35`: tabelas de domínio D&D 3.5 (combatentes, campanhas, magias, etc.).

Regra de ouro:

- código canônico continua por domínio em `app/shared/*` e `app/games/dnd35/*`;
- banco reflete essa separação com schemas explícitos.

## Mapeamento inicial de tabelas

### `auth`

- `usuarios`
- `games_catalog`
- `user_game_memberships`

### `dnd35`

- `campanhas`
- `sessoes_campanha`
- `combatentes`
- `combates`
- `combate_historico`
- `condicoes`
- `combatente_condicoes`
- `ataques`
- `magias`
- `magias_classes`
- `magia_slots`
- `magias_preparadas`
- `pericias`
- `pericias_classe`
- `pericias_jogador`
- `equipamentos`
- `equipamentos_jogador`
- `armaduras_protecao`
- `armaduras_protecao_jogador`
- `talentos`
- `talentos_jogador`
- `grimorio_magias`
- `grimorio_historico_trocas`
- `grimorio_notificacoes`
- `divindades_custom`

Observação: validar nomes reais em metadata/alembic antes da migration final.

## Foreign Keys cruzadas (mínimo esperado)

- `dnd35.combatentes.dono_id` -> `auth.usuarios.id`
- `dnd35.campanhas.mestre_id` -> `auth.usuarios.id`
- `auth.user_game_memberships.usuario_id` -> `auth.usuarios.id`
- `auth.user_game_memberships.game_id` -> `auth.games_catalog.id`

Toda FK nova deve usar referência qualificada por schema no Postgres.

## Estratégia de implementação (Fase C.1 -> C.4)

### C.1 - Pré-flight (sem DDL)

- snapshot de tabelas/FKs atuais;
- backup validado;
- checklist de rollback aprovado.

### C.2 - Migration Alembic de infraestrutura

- `CREATE SCHEMA IF NOT EXISTS auth;`
- `CREATE SCHEMA IF NOT EXISTS dnd35;`
- mover tabelas com `ALTER TABLE ... SET SCHEMA ...` em ordem segura.

### C.3 - Ajustes de SQLAlchemy

- definir `__table_args__ = {"schema": "auth"}` ou `{"schema": "dnd35"}`
  nos models aplicáveis;
- revisar `ForeignKey("schema.tabela.coluna")` onde necessário;
- garantir metadata/alembic consistentes.

### C.4 - Validação pós-migração

- smoke de login, seleção de jogo e rotas D&D 3.5;
- verificação de integridade referencial;
- monitoração de erros de schema/FK após deploy.

## SQLite vs Postgres (política proposta)

Para evitar complexidade artificial no ambiente local:

- manter testes unitários rápidos em SQLite sem schema físico;
- executar validação de schemas/FKs em pipeline/ambiente Postgres;
- não introduzir hacks de schema em SQLite nesta etapa.

Se necessário, criar marcador de testes Postgres para integração de Fase C.

## Runbook de execução (janela de manutenção)

1. Congelar deploys concorrentes.
2. Confirmar backup e ponto de restauração.
3. Aplicar migration de schemas em staging.
4. Rodar suíte + smoke em staging.
5. Aplicar em produção na janela aprovada.
6. Monitorar logs por 30-60 min (`relation does not exist`, FK errors, etc.).
7. Se falhar critério de aceitação, acionar rollback.

## Critérios de aceite da Fase C

- migrations aplicam em staging/prod sem perda de dados;
- rotas críticas (`auth`, `games`, `combatentes`, `campanhas`) operacionais;
- zero erro recorrente de schema/FK após deploy;
- documentação atualizada (`arquitetura-multi-jogo.md` + roteiro).

## Fora de escopo desta ADR

- split físico em múltiplos repositórios/serviços;
- mudanças de contrato HTTP/JWT;
- otimizações de performance não relacionadas a schema.

