# ⚔️ Arena de Combate TTRPG

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6-yellow)
![Vercel](https://img.shields.io/badge/Frontend-Vercel-black)
![Render](https://img.shields.io/badge/API-Render-46E3B7)
![Neon](https://img.shields.io/badge/DB-Neon-00E5B4)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

Plataforma web fullstack para gerenciamento de combates de **D&D 3.5** (Tabletop RPG),
com autenticação JWT, sistema de magias completo (grimório + preparação diária),
fichas de personagem interativas e arena de combate em tempo real.

---

## 🌐 Produção:

| URL | Descrição |
|---|---|
| `https://arena-de-combate-rpg.com.br` | Aplicação |
| `https://arena-de-combate-rpg.com.br/docs` | Swagger API |

Checklist de deploy e smoke test (Neon, Render, Vercel): **[docs/runbook-deploy-smoke.md](docs/runbook-deploy-smoke.md)**.

**Credenciais do admin inicial** — definidas no `backend/.env` (veja `backend/.env.example`). No **primeiro startup** do backend, se ambas estiverem preenchidas, é criado um usuário administrador com esse e-mail e senha.

```env
ADMIN_EMAIL=admin@arena-rpg.com.br
ADMIN_PASSWORD=TroquePorSenhaForte123!
ADMIN_USERNAME=Administrador
```

Para **testes locais**, copie o exemplo: com `ADMIN_EMAIL` e `ADMIN_PASSWORD` preenchidos (como no bloco acima), ao subir o `uvicorn` o admin é criado se ainda não existir — use **esse e-mail e essa senha** no login. Se `ADMIN_EMAIL` ou `ADMIN_PASSWORD` estiverem **vazios**, o admin **não** é criado; aí precisa criar um usuário por outro meio ou preencher o `.env` e reiniciar.

---

## ✨ Funcionalidades

### Acesso e Usuários
- Login com e-mail e senha (JWT — 24h de validade)
- 3 perfis: **Administrador**, **Mestre**, **Jogador**
- CRUD completo de usuários com exclusão lógica
- Auditoria: usuário responsável + data da ação

### Dashboard
- Cadastro de **Jogadores**, **Monstros** e **NPCs**
- Ficha completa: 6 atributos D&D, defesa (CA/Toque/Surpresa), resistências, foto
- Filtros por tipo, cards de resumo, edição e exclusão inline

### Ficha do Personagem
- Layout 3 colunas: atributos, foto + identidade, equipamentos/ataques/perícias
- Atributos em círculos com modificadores calculados
- Boxes de defesa (CA, PV com barra, Iniciativa)
- Resistências (Fortitude, Reflexos, Vontade)
- Talentos e Equipamentos com CRUD
- Perícias com cálculo automático de modificadores e custo por classe (1 pt = classe, 2 pts = fora da classe)
- Editor inline de ataques (adicionar/remover diretamente na ficha)
- Slots de magia por nível com barras de progresso (visível apenas para classes conjuradoras)
- Sincronização em tempo real via `BroadcastChannel` com a Arena

### Tormenta 20 (Módulo Básico)

- Ficha e grimório MB: **[docs/tormenta/grimorio-mb-mesa.md](docs/tormenta/grimorio-mb-mesa.md)** (catálogo, filtros por classe/nível, `ficha_json`, API de regras).

### Arena de Combate
- Seleção de combatentes e ordem de iniciativa automática
- Controle de turnos e rodadas
- Aplicar dano e cura (em massa)
- 25 condições D&D 3.5 com duração em turnos
- HP visível apenas para jogadores no modal de dano/cura

### Grimório de Magias
- Catálogo de ~400+ magias D&D 3.5 (todas as classes)
- Filtros por nível (0-9), escola e busca por nome
- Tabelas de slots por classe (Mago, Clérigo, Druida, Bardo, Paladino, Ranger)
- Clérigo e Druida exibem catálogo completo automaticamente
- Filtro "Preparadas" para classes que preparam magias (Clérigo, Mago, Druida, Ranger, Paladino)
- Preparação diária de magias com controle de uso
- Descanso longo: reset automático de slots e preparações

---

## 🗺️ Fluxo de Navegação

```
/  (raiz)
└── redireciona para ──► /pages/login.html
                              │
                         [Login JWT → seletor de jogo]
                              │
                              ▼
                      /dashboard              ← vercel.json → games/dnd35/pages/dashboard.html
                   ┌──────────┼───────────┐
                   │          │           │
              [Combatentes] [Arena]   [Usuários]
                   │          │        (Admin)
                   ▼          ▼
         /pages/ficha-       /arena      ← vercel.json → games/dnd35/arena.html
         personagem.html
              │
         [Grimório]    [Perícias]
         (modal)       /pericias         ← vercel.json → games/dnd35/pages/pericias.html
```

---

## 🛠️ Stack Tecnológico

### Backend
| Tecnologia | Versão | Uso |
|---|---|---|
| Python | 3.11.9 | Runtime |
| FastAPI | 0.104.1 | Framework web assíncrono |
| SQLAlchemy | 2.0.36 | ORM com suporte a migrations |
| Alembic | — | Controle de migrações de schema |
| Pydantic | 2.x | Validação e serialização (DTOs) |
| python-jose | — | Geração e validação de JWT |
| passlib + bcrypt | — | Hash de senhas |
| Uvicorn | 0.24.0 | Servidor ASGI |
| SQLite | — | Banco de dev local |
| PostgreSQL | — | Banco de produção (Neon) |

### Frontend
| Tecnologia | Uso |
|---|---|
| HTML5 + CSS3 | Estrutura e estilos temáticos (medieval/pergaminho) |
| JavaScript ES6 | Lógica de UI — vanilla, sem frameworks |
| ES Modules | Arquitetura modular com imports |
| Google Fonts | Cinzel, MedievalSharp, IM Fell English |
| BroadcastChannel API | Sync em tempo real entre páginas |

### Infraestrutura
| Serviço | Uso |
|---|---|
| **Vercel** | Frontend estático (HTML/CSS/JS) — CDN global |
| **Render.com** | Backend FastAPI (processo persistente) |
| **Neon** | PostgreSQL gerenciado (serverless, connection pooling) |
| **Cloudinary** | Armazenamento de imagens de personagens — CDN global permanente |
| **Cloudflare** | DNS + CDN |
| **Registro.br** | Domínio |

---

## 🏛️ Arquitetura

**Multi-jogo e modularização D&D 3.5:** conta global, `game_slug` no JWT, guards e a reorganização do backend em `backend/app/games/dnd35/` (com shims nos paths legados) estão descritos em [`docs/arquitetura-multi-jogo.md`](docs/arquitetura-multi-jogo.md). A **11ª onda** migrou o domínio **ficha** (`Combatente` e router `/combatentes`); o inventário por onda e convenções de import vivem em [`backend/app/games/dnd35/README.md`](backend/app/games/dnd35/README.md).

**Clean Architecture + SOLID** — separação estrita em 4 camadas:

```
Routes (API) → Services (regras de negócio) → Repositories (acesso a dados) → Models (ORM)
```

### Backend

```
backend/
├── app/
│   ├── main.py                    # Entry point: CORS, seeds, montagem dos routers em api/v1
│   │
│   ├── games/                     # Código por sistema de RPG (multi-jogo)
│   │   ├── dnd35/                 # D&D 3.5 — implementação canônica (ondas 1–11; ver games/dnd35/README.md)
│   │   │   ├── api/v1/            # Routers FastAPI do jogo (combatentes, combate, grimorio, magias, …)
│   │   │   ├── models/            # ORM por domínio (combatente, magia, combate, equipamento, …)
│   │   │   ├── schemas/           # Pydantic (request/response) alinhados aos models
│   │   │   ├── repositories/      # Acesso a dados (DIP)
│   │   │   ├── services/          # Regras de negócio D&D 3.5
│   │   │   ├── catalogs/          # Loaders PHB (raças, talentos, tabelas de classe, habilidades especiais)
│   │   │   └── seeds/             # ex.: pericias_seed
│   │   ├── dnd5e/                 # Reservado (em breve)
│   │   └── gurps/                 # Reservado (em breve)
│   │
│   ├── api/v1/                    # Onde o main registra os routers
│   │   ├── auth.py                # Hub — login, refresh JWT (implementação neste pacote)
│   │   ├── usuarios.py            # Hub — CRUD utilizadores
│   │   ├── games.py               # Hub — catálogo de jogos + POST selecionar (`game_slug` no token)
│   │   └── …                      # D&D 3.5: em regra [SHIM] — reexportam `router` de `games.dnd35.api.v1.*`
│   │                              # (combatentes, campanhas, combate, condicoes, divindades_custom,
│   │                              #  equipamentos, grimorio, habilidades_especiais, magias,
│   │                              #  magias_preparadas, pericias, racas, tabelas_classes, talentos,
│   │                              #  armaduras_protecao, ataques)
│   │
│   ├── core/                      # Infraestrutura partilhada
│   │   ├── config.py              # Settings via Pydantic + .env
│   │   ├── database.py            # Engine + sessão SQLAlchemy
│   │   ├── security.py            # JWT
│   │   ├── deps.py                # get_usuario_atual, requer_game_dnd35, …
│   │   ├── dependencies.py        # Factories de services (get_combate_service, …)
│   │   ├── mixins.py              # SoftDeleteMixin (models D&D 3.5 importam daqui)
│   │   # Seeds de arranque: `main.py` → `app/shared/startup/`, `app/games/dnd35/`
│   │
│   ├── models/                    # usuario, game (hub); demais → shims → games/dnd35/models
│   ├── schemas/                   # usuario, game, auth (hub); demais → shims → games/dnd35/schemas
│   ├── repositories/              # usuario_repository, game_repository (hub); demais → shims
│   ├── services/                  # usuario_service, game_service, file_service (hub); demais → shims
│   ├── seeds/                     # Legado + suporte a seeds (ver também games/dnd35/seeds)
│   ├── shared/                    # README / placeholder (futura separação Auth Hub vs jogo)
│   └── exceptions/                # Exceções customizadas
│
├── scripts/                       # Scripts de seed/import (magias, perícias, equipamentos, …)
├── alembic_migrations/versions/   # Migrações Alembic (histórico versionado)
├── tests/                         # pytest (domínio + API; e2e opcional em tests/e2e com Playwright)
└── requirements.txt
```

### Frontend

```
frontend/
├── pages/                         # Shell global — URLs /pages/*.html
│   ├── login.html, selecionar-jogo.html
│   ├── ficha-personagem.html, magias.html, usuarios.html, …
│   └── …                          # Outras telas ainda servidas desta pasta
│
├── games/                         # Bundle por jogo (multi-jogo)
│   ├── dnd35/                     # D&D 3.5 — arena, dashboard e perícias canônicos no deploy
│   │   ├── arena.html             #   Vercel: rewrite /arena → /games/dnd35/arena.html
│   │   ├── pages/                 #   dashboard, pericias, ficha, magias, … (ex.: /dashboard → …/dashboard.html)
│   │   ├── js/                    #   controllers/, services/, ui/, utils/, config/
│   │   └── css/                   #   Estilos do jogo (layout, arena, ficha, …)
│   ├── dnd5e/em-breve.html        #   Placeholder “em breve”
│   └── gurps/em-breve.html        #   idem
│
├── assets/brand/                  # Logos do seletor (hub)
├── arena.html                     # Raiz (legado ou espelho; produção usa rewrite em vercel.json)
├── index.html
└── sw.js                          # Service Worker (cache offline)
```

**Rotas curtas (Vercel):** em `vercel.json`, `/dashboard`, `/arena` e `/pericias` apontam para arquivos em `frontend/games/dnd35/`. O **shell** (login, escolha de jogo) permanece em `frontend/pages/`. Logos do hub em **`frontend/assets/brand/`** (`/assets/brand/*.png`); com FastAPI em dev a pasta é montada em `/assets`; no deploy o `outputDirectory` é `frontend/`.

**Assets compartilhados:** as páginas **em breve** (`games/dnd5e`, `games/gurps`) importam o toast de **`/games/dnd35/js/ui/toast.module.js`** (mesmo pacote D&D 3.5). A pasta **`frontend/css/`** na raiz, se existir clone antigo, não é usada pelos HTML atuais.

### Princípios SOLID Aplicados

| Princípio | Aplicação |
|---|---|
| **SRP** | Cada classe/arquivo tem uma única responsabilidade |
| **OCP** | Novos tipos de combatente/perfil sem alterar código existente |
| **LSP** | Repositories respeitam contrato do `BaseRepository[T]` |
| **ISP** | Schemas Pydantic separados por operação (`Create`, `Update`, `Response`) |
| **DIP** | Services dependem de Repositories via injeção (Factory em `deps.py`) |

---

## ✅ Checklist Obrigatório (PR)

Antes de implementar ou aprovar qualquer melhoria/correção/feature, validar:

- [ ] Requisitos funcionais do fluxo impactado foram verificados e priorizados antes de qualquer refatoração.
- [ ] Leitura do contexto funcional no `README.md` (fluxo afetado + contratos existentes).
- [ ] Leitura das instruções aplicáveis em `.github/instructions/*.md` (backend, frontend e/ou migrations).
- [ ] Quando a mudança envolver arquitetura, infra, deploy, dados ou fluxo crítico, leitura do `HISTORICO_EVOLUCAO.md`.
- [ ] Reuso e modularidade preservados: sem duplicação de regra e com fonte de verdade única.
- [ ] Aplicação de SOLID/Clean Code: SRP, baixo acoplamento, alta coesão, nomes claros e sem efeitos colaterais ocultos.
- [ ] Compatibilidade preservada: evitar breaking changes em API/contratos sem necessidade explícita.
- [ ] Em fluxos sensíveis (auth, cache, listagens, migrations, startup), impacto validado e risco residual documentado quando faltar teste automatizado.

---

## 🗄️ Modelo de Dados

```
Usuario (perfil: admin/mestre/jogador)
├── id, nome, email (único), senha_hash
├── ativo (exclusão lógica)
└── usuario_responsavel, data_acao

Combatente (tipo: jogador/monstro/npc)
├── id, nome, classe, nivel, raca
├── hp_maximo, hp_atual, iniciativa
├── forca, destreza, constituicao, inteligencia, sabedoria, carisma
├── ca, toque, surpresa
├── fortitude, reflexos, vontade
├── foto_url
├── ──(N) Ataques
├── ──(N) Perícias
├── ──(N) MagiaSlots (nível 0-9, total/usados)
├── ──(N) MagiasPreparadas → Magia
├── ──(N) Equipamentos
├── ──(N) Talentos
└── ──(N:N) Condições (via CombatenteCondicao + duração em turnos)

Combate (encontro ativo)
├── combatentes_ids (JSON array)
├── turno_atual, rodada_atual
└── ativo (boolean)

Magia (~400+ registros)
├── nome, nivel (0-9), escola, classe
├── tempo_conjuracao, alcance, duracao
└── descricao, componentes

Condicao (25 condições D&D 3.5)
└── nome, descricao, icone

Pericia (54 perícias D&D 3.5)
├── nome, atributo (FOR/DES/CON/INT/SAB/CAR)
└── ──(N:N) PericiaClasse → classe_nome, is_default (custo 1 = da classe / 2 = fora)
```

---

## 📡 Endpoints da API

### Autenticação (`/api/v1/auth`)
| Método | Rota | Auth | Descrição |
|---|---|---|---|
| `POST` | `/auth/login` | ❌ | Login — retorna JWT |
| `POST` | `/auth/logout` | ✅ | Invalidar sessão |
| `POST` | `/auth/refresh` | ✅ | Renovar token |

### Usuários (`/api/v1/usuarios`)
| Método | Rota | Auth | Descrição |
|---|---|---|---|
| `GET` | `/usuarios` | Admin | Listar usuários |
| `POST` | `/usuarios` | Admin | Criar usuário |
| `GET` | `/usuarios/{id}` | Admin | Obter por ID |
| `PATCH` | `/usuarios/{id}` | Admin | Atualizar |
| `DELETE` | `/usuarios/{id}` | Admin | Desativar |

### Combatentes (`/api/v1/combatentes`)
| Método | Rota | Auth | Descrição |
|---|---|---|---|
| `GET` | `/combatentes` | ✅ | Listar (filtro `?tipo=`) |
| `POST` | `/combatentes` | ✅ | Criar com stats completos |
| `GET` | `/combatentes/{id}` | ✅ | Ficha completa |
| `PATCH` | `/combatentes/{id}` | ✅ | Atualizar atributos |
| `DELETE` | `/combatentes/{id}` | ✅ | Remover |
| `POST` | `/combatentes/{id}/foto` | ✅ | Upload de retrato (max 5MB) |

### Combate (`/api/v1/combate`)
| Método | Rota | Auth | Descrição |
|---|---|---|---|
| `POST` | `/combate/iniciar` | ✅ | Iniciar encontro |
| `GET` | `/combate` | ✅ | Estado atual do combate |
| `POST` | `/combate/avancar-turno` | ✅ | Próximo turno |
| `POST` | `/combate/avancar-rodada` | ✅ | Próxima rodada |
| `POST` | `/combate/aplicar-dano` | ✅ | Dano/cura |
| `POST` | `/combate/finalizar` | ✅ | Encerrar encontro |

### Ataques (`/api/v1/combatentes/{id}/ataques`)
| Método | Rota | Auth | Descrição |
|---|---|---|---|
| `GET` | `/combatentes/{id}/ataques` | ✅ | Listar ataques |
| `POST` | `/combatentes/{id}/ataques` | ✅ | Adicionar (bulk) |
| `PUT` | `/combatentes/{id}/ataques` | ✅ | Substituir lista completa (editor inline) |
| `DELETE` | `/ataques/{id}` | ✅ | Remover ataque |

### Magias (`/api/v1/magias`)
| Método | Rota | Auth | Descrição |
|---|---|---|---|
| `GET` | `/magias` | ✅ | Filtrar `?classe=&nivel=&escola=` |

### Slots de Magia (`/api/v1/combatentes/{id}/magias-slots`)
| Método | Rota | Auth | Descrição |
|---|---|---|---|
| `GET` | `/combatentes/{id}/magias-slots` | ✅ | Slots por nível |
| `POST` | `/combatentes/{id}/magias-slots` | ✅ | Criar/atualizar |

### Magias Preparadas (`/api/v1/magias-preparadas`)
| Método | Rota | Auth | Descrição |
|---|---|---|---|
| `GET` | `/combatentes/{id}/magias-preparadas` | ✅ | Listar preparadas |
| `POST` | `/combatentes/{id}/magias-preparadas` | ✅ | Preparar magia |
| `POST` | `/magias-preparadas/descanso` | ✅ | Descanso longo (reset) |

### Condições (`/api/v1/condicoes`)
| Método | Rota | Auth | Descrição |
|---|---|---|---|
| `GET` | `/condicoes` | ✅ | Todas as 25 condições |
| `GET` | `/condicoes/combatente/{id}` | ✅ | Ativas no combatente |
| `POST` | `/condicoes/combatente/{id}` | ✅ | Aplicar condição |
| `DELETE` | `/condicoes/combatente/{id}` | ✅ | Remover condição |

### Perícias, Talentos, Equipamentos
| Método | Rota | Auth | Descrição |
|---|---|---|---|
| `GET/POST` | `/pericias/{id}/*` | ✅ | CRUD de perícias |
| `GET/POST` | `/talentos/{id}/*` | ✅ | CRUD de talentos |
| `GET/POST` | `/equipamentos/{id}/*` | ✅ | CRUD de equipamentos |

> 💡 Todos os endpoints protegidos exigem `Authorization: Bearer <token>`.

---

## 🔐 Autenticação

```
1. POST /auth/login (email + senha)
2. Backend: bcrypt verify → JWT (user_id, perfil, 24h expiry)
3. Frontend: sessionStorage (AuthService.TOKEN_KEY)
4. Todas as requisições: Authorization: Bearer {token}
5. Backend: deps.py → extrair_token → decodificar → get_usuario_atual
```

**Perfis de acesso:**
- **Administrador** — acesso total + gestão de usuários
- **Mestre** — gestão de combatentes + arena
- **Jogador** — visualização + edição do próprio personagem

---

## ⚙️ Workflows Principais

### Fluxo de Combate
1. Mestre cria combatentes no Dashboard
2. Inicia combate: `POST /combate/iniciar` com IDs dos combatentes
3. Ordem de iniciativa calculada automaticamente
4. Loop de turnos: `POST /combate/avancar-turno`
5. Aplicar dano/cura: `POST /combate/aplicar-dano`
6. Gerenciar condições (25 condições com duração em turnos)
7. Conjurar magias preparadas, controlar slots
8. Encerrar: `POST /combate/finalizar`

### Preparação de Magias (D&D 3.5)
1. Slots calculados por classe + nível (tabelas hardcoded)
2. Classes suportadas: Mago, Clérigo, Druida, Bardo, Paladino, Ranger
3. Preparação diária: escolher magias do catálogo
4. Uso: marcar `usada=true` ao conjurar
5. Descanso longo: reset de todos os slots e preparações

### Sistema de Condições
1. 25 condições D&D 3.5 (Abalado, Cego, Exausto, etc.)
2. Aplicar com duração em turnos (`-1` = permanente)
3. Auto-decremento a cada turno
4. Remoção automática quando expira

---

## 🚀 Como Executar Localmente

```bash
# 1. Clone o repositório
git clone https://github.com/LuizBacaro/projetoRPG.git
cd projetoRPG

# 2. Setup do backend
cd backend
python -m venv .venv
source .venv/bin/activate       # Linux/Mac
# .venv\Scripts\activate        # Windows
pip install -r requirements.txt

# 3. Variáveis de ambiente
cp .env.example .env
# Edite .env no mínimo:
#   DATABASE_URL=sqlite:///./rpg_arena.db
#   SECRET_KEY=sua-chave-secreta-aqui   # em dev pode ficar vazio (gerada ao arrancar)
#   ADMIN_EMAIL=admin@arena-rpg.com.br
#   ADMIN_PASSWORD=TroquePorSenhaForte123!
# (sem ADMIN_EMAIL + ADMIN_PASSWORD o usuário admin não é criado no startup)

# 4. Rodar seeds (opcional — popula magias, perícias, equipamentos)
python -m scripts.seed_magias
python -m scripts.seed_pericias
python -m scripts.seed_equipamentos

# 5. Iniciar o servidor
uvicorn app.main:app --reload --port 8000

# 6. Acesse
# http://127.0.0.1:8000 → redireciona para login
# http://127.0.0.1:8000/docs → Swagger UI
```

### Rodar Testes

```bash
cd backend
pytest tests/ -v --cov=app
```

### Backup e Restore de Personagens

Para preservar os personagens salvos no banco atual e reimportar depois em um banco recriado:

```bash
# Exportar snapshot completo dos personagens ativos
DATABASE_URL="postgresql://..." make backup-personagens \
     SNAPSHOT=backend/scripts/generated/personagens_producao.json

# Restaurar em outro banco ja migrado
DATABASE_URL="postgresql://..." make restore-personagens \
     SNAPSHOT=backend/scripts/generated/personagens_producao.json

# Se o banco de destino ja tiver personagens com a mesma chave natural,
# execute o comando direto para sobrescrever relacionamentos existentes
cd backend
python3 -m scripts.restore_personagens_snapshot \
     --input ../backend/scripts/generated/personagens_producao.json \
     --replace-existing
```

O snapshot inclui combatentes e relacionamentos associados: ataques, slots de magia, magias preparadas, pericias, equipamentos, armaduras/protecao, condicoes e dados de grimorio. Para uso recorrente em producao, gere o JSON e versione esse arquivo em local seguro fora do banco.

---

## 🌐 Deploy em Produção

### Arquitetura

```
Registro.br (domínio) → Cloudflare (DNS + CDN) → Vercel (frontend)
                                                 → Render.com (API FastAPI) → Neon (PostgreSQL)
```

### Passo a Passo

#### 1. Banco de Dados — Neon
1. Crie conta em [neon.tech](https://neon.tech) (gratuito)
2. Crie um projeto → copie a **Connection string** (painel: Connection Details)
3. Guarde a URL no formato: `postgresql://user:pass@ep-xxx.region.aws.neon.tech/neondb?sslmode=require`

#### 2. Backend — Render.com
1. Crie conta em [render.com](https://render.com) → New → **Web Service**
2. Conecte o repositório GitHub
3. Configure:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Python Version**: `3.11`
   - **Health Check Path** (recomendado): `/health/live` — `200` sem esperar migrations/seeds; reduz **Deploy timed out** no Render enquanto o Postgres inicializa.
4. Adicione as variáveis de ambiente:

| Variável | Valor |
|---|---|
| `DATABASE_URL` | Connection string do Neon |
| `SECRET_KEY` | `python -c "import secrets; print(secrets.token_hex(32))"` |
| `ENVIRONMENT` | `production` |
| `ADMIN_EMAIL` | seu e-mail de admin |
| `ADMIN_PASSWORD` | senha forte |
| `ALLOWED_ORIGINS` | `["https://arena-de-combate-rpg.com.br","https://seu-app.vercel.app"]` |

5. Após o deploy, copie a URL do Render (ex.: `https://projetorpg-7ih3.onrender.com`) — o `vercel.json` já referencia o proxy `/api` para essa API; não é obrigatório hardcodar URL no frontend.

#### 3. Frontend — Vercel
1. Crie conta em [vercel.com](https://vercel.com) → New Project → importe o repositório
2. **Não altere** o diretório raiz — o `vercel.json` na raiz já configura tudo
3. Nenhuma variável de ambiente necessária (frontend é estático)
4. Após deploy, Vercel gera uma URL `.vercel.app`

#### 4. Domínio Próprio (Registro.br → Cloudflare → Vercel)
1. No **Cloudflare**: adicione registro `CNAME` apontando `arena-de-combate-rpg.com.br` para `cname.vercel-dns.com`
2. No **Vercel**: Project Settings → Domains → adicione `arena-de-combate-rpg.com.br`
3. Atualize `ALLOWED_ORIGINS` no Render para incluir o domínio final

#### 5. Anti-sleep no Render (gratuito)
O Render free tier dorme após 15 min de inatividade. Para evitar cold start:
1. Crie conta gratuita em [cron-job.org](https://cron-job.org)
2. Novo cron job → URL: `https://projetorpg-7ih3.onrender.com/health`
3. Schedule: `*/10 * * * *` (a cada 10 min) — mantém a API sempre acordada
4. O endpoint `/health` retorna 200 instantaneamente sem tocar no banco

> ℹ️ Job já configurado em produção: [console.cron-job.org/jobs](https://console.cron-job.org/jobs)

---

### Alterações no código: o que você precisa fazer para refletir em produção

Existem **dois lugares** onde o código “sobe”: **Vercel** (site: HTML, CSS, JS) e **Render** (API Python). O domínio **`www.arena-de-combate-rpg.com.br`** precisa ser atendido pelo **Vercel**. Se o DNS mandar o tráfego para o **Render**, você verá HTML antigo mesmo com deploy novo no Render — a API atualiza, a interface não.

| O que você mudou | Onde fazer deploy | O que fazer na prática |
|------------------|-------------------|-------------------------|
| `frontend/`, `vercel.json`, páginas `.html` | **Vercel** | `git push` na branch ligada ao Vercel (ex.: `feature/salva`) → esperar o deploy **Ready** no painel Vercel. |
| `backend/`, API FastAPI | **Render** | `git push` → deploy automático no Render (ou redeploy manual). |
| Dados no Postgres | **Neon** | Scripts SQL ou `importar_talentos_catalogo.py` com `DATABASE_URL` do Neon (não é deploy). |

**Checklist para o site público mostrar sua alteração de frontend**

1. Subir o commit: `git push origin <sua-branch-de-produção>`.
2. Abrir [Vercel](https://vercel.com) → seu projeto → **Deployments** → confirmar **Ready** no commit certo.
3. Confirmar que **`arena-de-combate-rpg.com.br`** (e `www`) está em **Settings → Domains** desse mesmo projeto Vercel.
4. No **Cloudflare** (DNS): `www` deve ser **CNAME** para `cname.vercel-dns.com` (como na documentação do Vercel). **Não** use o mesmo hostname apontando para o Render se quiser o frontend do Vercel.
5. O `vercel.json` já encaminha `/api` e `/health` para a API no Render — o navegador continua em `https://seu-dominio` e as chamadas vão para a API.
6. Se ainda aparecer versão antiga: **Cloudflare → Caching → Purge Everything** (uma vez) e testar em aba anônima.

**Como conferir rapidamente:** a URL **`https://projeto-rpg-two.vercel.app`** (projeto no Vercel) deve mostrar o mesmo HTML novo; se o **www** estiver diferente, o problema é **DNS** (domínio não está no Vercel).

---

## 👤 Autor

**Luiz Salvador** — GitHub: [@LuizBacaro](https://github.com/LuizBacaro)
