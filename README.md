# ⚔️ Arena de Combate TTRPG

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6-yellow)
![Railway](https://img.shields.io/badge/Deploy-Railway-purple)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

Plataforma web fullstack para gerenciamento de combates de TTRPG
(Tabletop RPG / Dungeons & Dragons), com autenticação JWT,
controle de perfis de usuário e arena de combate em tempo real.

---

## 🌐 Produção

| URL | Descrição |
|---|---|
| `https://arena-de-combate-rpg.com.br` | Aplicação |
| `https://arena-de-combate-rpg.com.br/docs` | Swagger API |

---

## ✨ Funcionalidades

### Acesso e Usuários
- Login com e-mail e senha (JWT — 8h)
- 3 perfis: **Administrador**, **Mestre**, **Jogador**
- CRUD completo de usuários (exclusão lógica por Status)
- Auditoria automática: usuário responsável + data da ação

### Dashboard
- Cadastro de **Jogadores**, **Monstros** e **NPCs**
- Ficha completa: atributos D&D, defesa, resistências, foto
- Filtros por tipo, cards de resumo, edição e exclusão inline

### Arena de Combate
- Seleção de combatentes e ordem de iniciativa
- Aplicar dano e cura em massa
- 25 Condições D&D 5e
- HP visível apenas para Jogadores no modal de dano/cura

---

## 🗺️ Fluxo de navegação

/  (raiz)
└── redireciona para ──► /pages/login.html
│
┌─────────┴──────────┐
│                    │
[Entrar]         [Criar nova conta]
│                    │
JWT gerado        POST /api/auth/registro
│           (perfil Jogador, público)
│                    │
└────────┬───────────┘
▼
/dashboard
┌────────────────────────────────┐
│  Aba Combatentes                │
│  ├── Cadastrar Jogador          │
│  ├── Cadastrar Monstro          │
│  ├── Cadastrar NPC              │
│  └── Editar / Excluir           │
│                                 │
│  Aba Arena ──► /arena           │
│                                 │
│  Header                         │
│  ├── 👤 Usuários  (só Admin)    │
│  └── Sair                       │
└────────────────────────────────┘
│
/arena
┌────────────────────────────────┐
│  Seleção de combatentes         │
│  Ordem de iniciativa            │
│  Dano / Cura em massa           │
│  Condições D&D 5e               │
│  ← Voltar ao Dashboard          │
└────────────────────────────────┘/pages/usuarios.html  ──  restrito a Administrador
**Credencial padrão** criada no primeiro startup:E-mail: admin@rpg.com
Senha:  admin123   ← altere após o primeiro acesso
---

## 🏛️ Arquitetura

Clean Architecture + SOLID — separação estrita em camadas.

### Backendbackend/app/
│
├── api/v1/                  # Routers HTTP (SRP por domínio)
│   ├── auth.py              # Login, registro público e JWT
│   ├── usuarios.py          # CRUD de usuários
│   ├── combatentes.py       # CRUD de combatentes + upload de foto
│   ├── combate.py           # Lógica de combate (dano, cura, iniciativa)
│   └── condicoes.py         # Condições D&D 5e
│
├── core/                    # Infraestrutura e configurações
│   ├── config.py            # Settings via Pydantic + .env
│   ├── database.py          # Engine + sessão SQLAlchemy
│   ├── security.py          # JWT — geração e validação (lê SECRET_KEY do .env)
│   └── deps.py              # Dependências FastAPI (get_usuario_atual)
│
├── models/                  # ORM SQLAlchemy — mapeamento das tabelas
├── repositories/            # Acesso a dados — DIP (depende de abstração)
├── schemas/                 # Pydantic — validação de request/response
├── services/                # Regras de negócio — SRP por domínio
└── main.py                  # Entry point + CORS + seeds + rotas estáticas
### Frontendfrontend/
│
├── index.html               # Arena de combate
│
├── pages/
│   ├── login.html           # Tela de login + cadastro público
│   ├── dashboard.html       # Pós-login — cadastro de combatentes
│   └── usuarios.html        # Gestão de usuários (só Administrador)
│
└── js/
├── config/
│   └── api.config.js    # URLs dev/prod (único ponto de configuração)
│
├── controllers/         # Orquestração de telas (SRP por página)
│   ├── ArenaController.js
│   ├── ConfiguracaoController.js
│   ├── DashboardController.js
│   └── UsuarioController.js
│
├── services/            # Comunicação HTTP + sessão
│   ├── AuthService.js   # JWT, perfil, permissões, logout
│   ├── CombatenteService.js
│   ├── UsuarioService.js
│   ├── DanoCuraService.js
│   └── CondicaoService.js
│
├── ui/                  # Componentes visuais reutilizáveis
│   ├── Toast.js         # Notificações (global + ES module)
│   ├── ModalDanoCura.js
│   ├── ModalUsuario.js
│   └── CombatenteCard.js
│
├── models/              # Entidades do domínio no frontend
│   └── Combatente.js
│
└── main.js              # Entry point da arena

## 🛠️ Stack

### Backend
| Lib | Versão | Uso |
|---|---|---|
| Python | 3.11 | Runtime |
| FastAPI | 0.104 | Framework web |
| SQLAlchemy | 2.0 | ORM |
| Pydantic | 2.x | Validação e schemas |
| python-jose | latest | JWT |
| passlib + bcrypt | 1.7.4 / 4.0.1 | Hash de senhas |
| SQLite | — | Dev local |
| PostgreSQL | — | Produção (Railway) |

### Frontend
- HTML5 + CSS3 + JavaScript ES6 (Vanilla)
- Arquitetura modular: ES Modules + Scripts globais
- Sem frameworks — zero dependências de terceiros no front

### Infraestrutura
- **Railway** — backend + PostgreSQL
- **Cloudflare** — DNS + CDN
- **Registro.br** — domínio

---

## 🏛️ Arquitetura

Clean Architecture + SOLID — separação estrita em camadas.

### Backend

backend/app/
│
├── api/v1/                  # Routers HTTP (SRP por domínio)
│   ├── auth.py              # Login e geração de JWT
│   ├── usuarios.py          # CRUD de usuários
│   ├── combatentes.py       # CRUD de combatentes + upload de foto
│   ├── combate.py           # Lógica de combate (dano, cura, iniciativa)
│   └── condicoes.py         # Condições D&D 5e
│
├── core/                    # Infraestrutura e configurações
│   ├── config.py            # Settings via Pydantic + .env
│   ├── database.py          # Engine + sessão SQLAlchemy
│   ├── security.py          # JWT — geração e validação
│   └── deps.py              # Dependências FastAPI (get_usuario_atual)
│
├── models/                  # ORM SQLAlchemy (mapeamento das tabelas)
├── repositories/            # Acesso a dados — DIP (depende de abstração)
├── schemas/                 # Pydantic — validação de request/response
├── services/                # Regras de negócio — SRP por domínio
└── main.py                  # Entry point + CORS + seeds + rotas estáticas
### Frontendfrontend/
│
├── index.html               # Arena de combate
│
├── pages/
│   ├── login.html           # Tela de login (sempre exibida na entrada)
│   ├── dashboard.html       # Pós-login — cadastro de combatentes
│   └── usuarios.html        # Gestão de usuários (só Administrador)
│
└── js/
├── config/
│   └── api.config.js    # URLs dev/prod (único ponto de configuração)
│
├── controllers/         # Orquestração de telas (SRP por página)
│   ├── ArenaController.js
│   ├── ConfiguracaoController.js
│   ├── DashboardController.js
│   └── UsuarioController.js
│
├── services/            # Comunicação HTTP + sessão
│   ├── AuthService.js   # JWT, perfil, permissões, logout
│   ├── CombatenteService.js
│   ├── UsuarioService.js
│   ├── DanoCuraService.js
│   └── CondicaoService.js
│
├── ui/                  # Componentes visuais reutilizáveis
│   ├── Toast.js         # Notificações (global + ES module)
│   ├── ModalDanoCura.js
│   ├── ModalUsuario.js
│   └── CombatenteCard.js
│
├── models/              # Entidades e regras do domínio no frontend
│   └── Combatente.js
│
└── main.js              # Entry point da arena

### Princípios aplicados

| Princípio | Aplicação |
|-----------|-----------|
| **SRP** — Single Responsibility | Cada classe/arquivo tem uma única responsabilidade (ex: `AuthService` só gerencia sessão, `security.py` só gera/valida JWT) |
| **OCP** — Open/Closed | Novos tipos de combatente ou perfil de usuário sem alterar código existente |
| **DIP** — Dependency Inversion | Services dependem de Repositories via injeção — nunca instanciam diretamente |
| **ISP** — Interface Segregation | Schemas Pydantic separados por operação (`UsuarioCreate`, `UsuarioUpdate`, `UsuarioResponse`) |

## 🚀 Como executar localmente
```bash
# 1. Clone
git clone https://github.com/LuizBacaro/projetoRPG.git
cd projetoRPG
git checkout feature/fase_2

# 2. Backend
cd backend
python -m venv .venv
source .venv/bin/activate       # Linux/Mac
pip install -r requirements.txt

# 3. Variáveis de ambiente
cp .env.example .env
# Edite .env — mínimo necessário:
# DATABASE_URL=sqlite:///./rpg_arena.db
# SECRET_KEY=sua-chave-secreta-aqui

# 4. Inicia o servidor
uvicorn app.main:app --reload --port 8000

# 5. Acessa
# http://127.0.0.1:8000  →  tela de login

📡 Endpoints principais

## 📡 Endpoints principais

| Método | Rota | Auth | Descrição |
|--------|------|------|-----------|
| `POST` | `/api/auth/login` | ❌ Público | Login — retorna JWT |
| `GET` | `/api/usuarios` | ✅ Admin | Lista usuários |
| `POST` | `/api/usuarios` | ✅ Admin | Cria usuário |
| `PUT` | `/api/usuarios/{id}` | ✅ Admin | Atualiza usuário |
| `DELETE` | `/api/usuarios/{id}` | ✅ Admin | Inativa usuário |
| `GET` | `/api/combatentes` | ✅ Logado | Lista combatentes |
| `POST` | `/api/combatentes` | ✅ Logado | Cria combatente |
| `PUT` | `/api/combatentes/{id}` | ✅ Logado | Edita combatente |
| `DELETE` | `/api/combatentes/{id}` | ✅ Logado | Remove combatente |
| `POST` | `/api/combatentes/{id}/dano` | ✅ Logado | Aplica dano |
| `POST` | `/api/combatentes/{id}/cura` | ✅ Logado | Aplica cura |
| `GET` | `/api/condicoes` | ✅ Logado | Lista condições D&D |

> 💡 Todos os endpoints protegidos exigem header `Authorization: Bearer <token>`
> obtido no `POST /api/auth/login`.

🗄️ Modelo de dados

Usuario
├── id, perfil (administrador/mestre/jogador)
├── nome, email (único), senha_hash
├── ativo (exclusão lógica)
├── usuario_responsavel, data_acao (auditoria)

Combatente
├── id, nome, tipo (jogador/monstro/npc)
├── classe, nivel, pontos
├── hp_maximo, hp_atual, iniciativa
├── forca, destreza, constituicao
├── inteligencia, sabedoria, carisma
├── ca, toque, surpresa (defesa)
├── fortitude, reflexos, vontade (resistências)
├── foto_url
└── condicoes → N:N → Condicao

Condicao
└── id, nome, descricao, icone

🌐 Deploy em Produção
URLs
Aplicação:  https://arena-de-combate-rpg.com.br
API Docs:   https://arena-de-combate-rpg.com.br/docs
Infraestrutura
O fluxo de deploy em produção é configurado da seguinte forma: Registro.br (gerenciamento de domínio) → Cloudflare (DNS e CDN para performance e segurança) → Railway (hospedagem do backend FastAPI e do banco de dados PostgreSQL).

Railway
O deploy é automático a cada push na branch feature/salva. O Railway detecta as mudanças e reconstrói/redesplanta a aplicação.

Variáveis de ambiente configuradas no Railway:

DATABASE_URL      → URL de conexão com o PostgreSQL (gerada automaticamente pelo Railway)
PROJECT_NAME      → Arena de Combate TTRPG
ALLOWED_ORIGINS   → ["https://arena-de-combate-rpg.com.br"]

👤 Autor
Luiz Salvador GitHub: @LuizBacaro
