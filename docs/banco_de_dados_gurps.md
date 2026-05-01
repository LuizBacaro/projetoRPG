# Banco de dados — GURPS

Documento de referência para **espelhar o schema GURPS no PostgreSQL** (ex.: Neon) e manter o mesmo critério de migrações do restante da plataforma (Alembic).

## Segurança (credenciais)

- **Nunca** commite `DATABASE_URL` com usuário/senha no repositório.
- **Nunca** cole strings de conexão completas em chats, issues ou tickets: trate como segredo; se vazou, **gire a senha** no Neon (Reset password) e atualize o segredo no Render/CI.
- Para rodar Alembic localmente contra o Neon, use `export DATABASE_URL='…'` só no seu terminal ou um ficheiro `.env` **fora** do Git (já no `.gitignore`).

## 1. O que existe no schema

A revisão Alembic **`b1a2c3d4e5f6`** (`backend/alembic_migrations/versions/b1a2c3d4e5f6_add_gurps_core_tables.py`) cria:

| Tabela | Função |
|--------|--------|
| `gurps_campanhas` | Campanhas (mestre, nome, descrição). |
| `gurps_personagens` | Ficha: atributos, PV/fadiga, defesas, danos, totais de pontos, etc. |
| `gurps_personagem_vantagens` | Linhas de vantagens (nome, custo). |
| `gurps_personagem_desvantagens` | Linhas de desvantagens. |
| `gurps_personagem_pericias` | Perícias (nome, tipo, NH, custo). |
| `gurps_combates` | Arena: fila de IDs, turno, rodada, ativo. |

Os modelos SQLAlchemy vivem em `backend/app/games/gurps/models/`. O `env.py` do Alembic usa o mesmo **`search_path`** que a API em Postgres (`auth, dnd35, public`).

## 2. Aplicar migrações no Neon (produção ou staging)

O Alembic **não lê o arquivo `.env` automaticamente**. Ele usa a variável de ambiente **`DATABASE_URL`**, sobrescrita em `backend/alembic_migrations/env.py` (função `_get_database_url()`).

### Passos

1. No painel **Neon**, copie a connection string do branch desejado (**staging** primeiro, depois **produção**).
2. No diretório **`backend`** (onde está `alembic.ini`):

```bash
cd backend

export DATABASE_URL='postgresql://USUARIO:SENHA@ep-xxx.region.aws.neon.tech/neondb?sslmode=require'

python3 -m alembic current
python3 -m alembic upgrade head
```

3. Confirme que `alembic current` mostra a revisão esperada (ex.: `b1a2c3d4e5f6 (head)` após aplicar tudo).

### Notas

- Strings que começam com `postgres://` são normalizadas para `postgresql://` no `env.py`.
- Não commite a URL com senha; use apenas `export` local ou segredo no CI.
- **Ordem recomendada:** branch de staging → validar API → repetir em produção com o `DATABASE_URL` correto do Render/Neon de produção.

## 3. Checklist alinhado ao projeto

- Checklist geral de deploy e dados: [PRE_DEPLOY_CHECKLIST.md](../PRE_DEPLOY_CHECKLIST.md) (proteção de dados, Neon, Render).
- Política de branches e backups: skill **arena-producao-dados-neon-render** (`.cursor/skills/arena-producao-dados-neon-render/SKILL.md`).

## 4. Catálogo e membership

O jogo `gurps` é sincronizado no startup via `GAME_CATALOG_SEED` em `backend/app/shared/startup/game_catalog.py`. Membership automático para usuários existentes segue `AUTO_ENROLL_MEMBERSHIP_GAME_SLUGS` em `backend/app/shared/constants.py` (junto com `dnd35`), via `GameService.garantir_auto_enroll_memberships`.

## 5. API após migrar

Endpoints sob `/api/v1/gurps/...` exigem JWT com `game_slug=gurps` quando `MULTI_GAME_STRICT_MODE=true`. Detalhes: `backend/app/games/gurps/README.md`.
