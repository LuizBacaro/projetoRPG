# ⚔️ Arena de Combate TTRPG

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6-yellow)
![Railway](https://img.shields.io/badge/Deploy-Railway-purple)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

Plataforma web fullstack para gerenciamento de combates de **D&D 3.5** (Tabletop RPG),
com autenticação JWT, sistema de magias completo (grimório + preparação diária),
fichas de personagem interativas e arena de combate em tempo real.

---

## 🌐 Produção

| URL | Descrição |
|---|---|
| `https://arena-de-combate-rpg.com.br` | Aplicação |
| `https://arena-de-combate-rpg.com.br/docs` | Swagger API |

**Credenciais padrão** (criadas no primeiro startup):

```
E-mail: admin@rpg.com
Senha:  admin123  ← altere após o primeiro acesso
```

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
- Perícias com cálculo automático de modificadores
- Slots de magia por nível com barras de progresso
- Sincronização em tempo real via `BroadcastChannel` com a Arena

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
- Preparação diária de magias com controle de uso
- Descanso longo: reset automático de slots e preparações

---

## 🗺️ Fluxo de Navegação

```
/  (raiz)
└── redireciona para ──► /pages/login.html
                              │
                         [Login JWT]
                              │
                              ▼
                      /pages/dashboard.html
                   ┌──────────┼───────────┐
                   │          │           │
              [Combatentes] [Arena]   [Usuários]
                   │          │        (Admin)
                   ▼          ▼
         /pages/ficha-   /pages/arena-
         personagem.html combate.html
              │
         [Grimório]    [Perícias]
         (modal)       /pages/pericias.html
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
| PostgreSQL | — | Banco de produção (Railway) |

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
| **Railway** | Backend + PostgreSQL gerenciado |
| **Cloudflare** | DNS + CDN |
| **Registro.br** | Domínio |

---

## 🏛️ Arquitetura

**Clean Architecture + SOLID** — separação estrita em 4 camadas:

```
Routes (API) → Services (regras de negócio) → Repositories (acesso a dados) → Models (ORM)
```

### Backend

```
backend/
├── app/
│   ├── main.py                    # Entry point + CORS + seeds + rotas estáticas
│   │
│   ├── api/v1/                    # 12 Routers HTTP (SRP por domínio)
│   │   ├── auth.py                #   Login, logout, refresh JWT
│   │   ├── usuarios.py            #   CRUD de usuários
│   │   ├── combatentes.py         #   CRUD combatentes + upload de foto
│   │   ├── combate.py             #   Iniciar, avançar turno/rodada, dano/cura
│   │   ├── condicoes.py           #   25 condições D&D
│   │   ├── ataques.py             #   Ataques corpo-a-corpo/distância
│   │   ├── magias.py              #   Catálogo de ~400 magias
│   │   ├── magias_preparadas.py   #   Preparação diária + descanso
│   │   ├── pericias.py            #   37 perícias D&D 3.5
│   │   ├── talentos.py            #   Talentos/feats
│   │   └── equipamentos.py        #   Inventário
│   │
│   ├── core/                      # Infraestrutura
│   │   ├── config.py              #   Settings via Pydantic + .env
│   │   ├── database.py            #   Engine + sessão SQLAlchemy
│   │   ├── security.py            #   JWT — geração e validação
│   │   ├── deps.py                #   Dependências FastAPI (get_usuario_atual)
│   │   ├── dependencies.py        #   Factory de services com injeção
│   │   └── init_db.py             #   Seed do admin padrão
│   │
│   ├── models/                    # 11 modelos SQLAlchemy
│   │   ├── usuario.py             #   Perfis: admin/mestre/jogador
│   │   ├── combatente.py          #   Ficha completa D&D
│   │   ├── combate.py             #   Encontro ativo (JSON combatentes_ids)
│   │   ├── ataque.py              #   Ataques vinculados a combatente
│   │   ├── magia.py               #   Catálogo de magias (nome, nível, escola, classe)
│   │   ├── pericia.py             #   Perícias D&D 3.5
│   │   ├── condicao.py            #   25 condições
│   │   ├── combatente_condicao.py #   N:N com duração em turnos
│   │   ├── equipamento.py         #   Itens de inventário
│   │   └── talento.py             #   Feats/talentos
│   │
│   ├── repositories/              # Acesso a dados (DIP)
│   │   ├── base.py                #   BaseRepository[T] genérico
│   │   ├── usuario_repository.py
│   │   ├── combatente_repository.py
│   │   ├── combate_repository.py
│   │   ├── ataque_repository.py
│   │   ├── condicao_repository.py
│   │   ├── pericia_repository.py
│   │   ├── equipamento_repository.py
│   │   └── talento_repository.py
│   │
│   ├── services/                  # Regras de negócio (SRP)
│   │   ├── usuario_service.py
│   │   ├── combatente_service.py
│   │   ├── combate_service.py
│   │   ├── ataque_service.py
│   │   ├── condicao_service.py
│   │   ├── pericia_service.py
│   │   ├── equipamento_service.py
│   │   ├── talento_service.py
│   │   └── file_service.py        #   Upload de imagens
│   │
│   ├── schemas/                   # Pydantic DTOs (request/response)
│   ├── seeds/                     # Dados iniciais (condições, admin)
│   └── exceptions/                # Exceções customizadas
│
├── scripts/                       # Seeds de dados D&D
│   ├── seed_magias.py             #   ~400+ magias todas as classes
│   ├── seed_pericias.py           #   37 perícias
│   ├── seed_equipamentos.py       #   Equipamentos (PHB p.120-126)
│   ├── seed_database.py           #   Combatentes de exemplo
│   └── seed_dominios.py           #   Domínios de clérigo
│
├── alembic_migrations/            # Migrações de schema
│   └── versions/
│       ├── 001_initial_schema.py
│       ├── 002_add_pagina_referencia.py
│       └── 630072bd328c_add_new_spell_columns.py
│
├── tests/                         # Testes unitários (pytest)
│   ├── conftest.py                #   SQLite in-memory fixture
│   ├── test_combate_service.py
│   └── test_combatente_service.py
│
└── requirements.txt
```

### Frontend

```
frontend/
├── index.html                     # Redireciona para login
│
├── pages/                         # 7 páginas HTML
│   ├── login.html                 #   Tela de login
│   ├── dashboard.html             #   Gestão de combatentes
│   ├── ficha-personagem.html      #   Ficha completa do personagem
│   ├── arena-combate.html         #   Arena de combate em tempo real
│   ├── pericias.html              #   Alocação de perícias
│   ├── pericias-ficha.html        #   Perícias (visão ficha)
│   └── usuarios.html              #   Admin de usuários
│
├── js/
│   ├── config.js                  # Detecção automática dev/prod
│   ├── main.js                    # Entry point
│   │
│   ├── controllers/               # 9 controllers (SRP por página)
│   │   ├── ArenaController.js     #   Orquestração de combate
│   │   ├── DashboardController.js #   CRUD combatentes + filtros
│   │   ├── FichaPersonagemController.js  # Ficha interativa
│   │   ├── GrimorioController.js  #   Preparação de magias
│   │   ├── PericiaController.js   #   Tabela de perícias
│   │   ├── PericiaFichaController.js
│   │   ├── CondicaoController.js  #   Gerenciamento de condições
│   │   ├── ConfiguracaoController.js
│   │   └── UsuarioController.js   #   CRUD usuários
│   │
│   ├── services/                  # 15 services HTTP
│   │   ├── AuthService.js         #   JWT, perfil, sessão
│   │   ├── CombatenteService.js   #   CRUD combatentes
│   │   ├── CombateService.js      #   Fluxo de combate
│   │   ├── MagiaService.js        #   Consulta de magias
│   │   ├── MagiaSlotService.js    #   Slots por nível
│   │   ├── MagiaPreparadaService.js  # Magias preparadas
│   │   ├── CondicaoService.js     #   Condições D&D
│   │   ├── AtaqueService.js       #   Ataques
│   │   ├── EquipamentoService.js  #   Inventário
│   │   ├── TalentoService.js      #   Talentos
│   │   ├── PericiaService.js      #   Perícias
│   │   ├── DanoCuraService.js     #   Dano/cura
│   │   ├── UsuarioService.js      #   CRUD usuários
│   │   ├── UploadService.js       #   Upload de imagens
│   │   └── NotificationService.js #   Toast notifications
│   │
│   ├── ui/                        # 14 componentes visuais
│   │   ├── ModalCadastro.js       #   Modal de criação
│   │   ├── ModalEdicao.js         #   Modal de edição
│   │   ├── ModalDanoCura.js       #   Aplicar dano/cura
│   │   ├── ModalCondicao... (UI)  #   Modal de condições
│   │   ├── ModalConfirm.js        #   Confirmação genérica
│   │   ├── ModalUsuario.js        #   CRUD usuário em modal
│   │   ├── CombatenteCard.js      #   Card de combatente
│   │   ├── CombatenteAtivoView.js #   Combatente ativo na arena
│   │   ├── ArenaView.js           #   UI principal da arena
│   │   ├── ArenaAtaquesMagias.js  #   Painel de ataques e magias
│   │   ├── OrdemIniciativa.js     #   Lista de iniciativa
│   │   ├── CondicaoUI.js          #   Badges de condições
│   │   ├── TipoSelector.js        #   Filtro por tipo
│   │   └── Toast.js               #   Notificações toast
│   │
│   ├── models/                    # Entidades do domínio
│   ├── utils/                     # Utilitários
│   └── config/                    # Configurações
│
├── css/                           # Estilos temáticos (medieval)
│   ├── variables.css              #   Tokens de design + reset
│   ├── layout.css                 #   Layout base
│   ├── ficha-personagem.css       #   Ficha do personagem (~2300 linhas)
│   ├── grimorio.css               #   Grimório de magias
│   ├── arena.css                  #   Arena de combate
│   ├── dashboard.css              #   Dashboard
│   ├── pericias.css               #   Tela de perícias
│   ├── modais.css                 #   Modais genéricos
│   ├── responsivo.css             #   Media queries
│   └── ...                        #   Outros componentes
│
└── sw.js                          # Service Worker (cache offline)
```

### Princípios SOLID Aplicados

| Princípio | Aplicação |
|---|---|
| **SRP** | Cada classe/arquivo tem uma única responsabilidade |
| **OCP** | Novos tipos de combatente/perfil sem alterar código existente |
| **LSP** | Repositories respeitam contrato do `BaseRepository[T]` |
| **ISP** | Schemas Pydantic separados por operação (`Create`, `Update`, `Response`) |
| **DIP** | Services dependem de Repositories via injeção (Factory em `deps.py`) |

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

Pericia (37 perícias D&D 3.5)
└── nome, atributo (FOR/DES/CON/INT/SAB/CAR)
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
# Edite .env:
#   DATABASE_URL=sqlite:///./rpg_arena.db
#   SECRET_KEY=sua-chave-secreta-aqui

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

---

## 🌐 Deploy em Produção

### Infraestrutura

```
Registro.br (domínio) → Cloudflare (DNS + CDN) → Railway (FastAPI + PostgreSQL)
```

### Railway

Deploy automático a cada push na branch de produção. O Railway detecta o `Procfile`:

```
web: uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
```

**Variáveis de ambiente no Railway:**

| Variável | Descrição |
|---|---|
| `DATABASE_URL` | URL do PostgreSQL (gerada pelo Railway) |
| `SECRET_KEY` | Chave para JWT |
| `PROJECT_NAME` | Arena de Combate TTRPG |
| `ALLOWED_ORIGINS` | `["https://arena-de-combate-rpg.com.br"]` |

---

## 👤 Autor

**Luiz Salvador** — GitHub: [@LuizBacaro](https://github.com/LuizBacaro)
