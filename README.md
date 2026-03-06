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

/                    → redireciona para login
/pages/login.html    → autenticação JWT
↓ login OK
/dashboard           → cadastro de combatentes (todos os perfis)
├── Aba Combatentes → CRUD jogador / monstro / NPC
├── Aba Arena       → link para /arena
└── Header         → nome, perfil, link Usuários (admin), Sair/arena               → seleção e combate (sem cadastro)
/pages/usuarios.html → gestão de usuários (só Administrador)
**Credencial padrão** (criada no primeiro startup):E-mail: admin@rpg.com
Senha:  admin123
---

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

Clean Architecture + SOLID. Separação em camadas:backend/app/
├── api/v1/         # Routers HTTP (SRP por domínio)
│   ├── auth.py
│   ├── usuarios.py
│   ├── combatentes.py
│   ├── combate.py
│   └── condicoes.py
├── core/
│   ├── config.py   # Configurações via Pydantic Settings
│   ├── database.py # Engine + sessão SQLAlchemy
│   ├── security.py # JWT — geração e validação
│   └── deps.py     # Dependências FastAPI (get_usuario_atual)
├── models/         # ORM SQLAlchemy
├── repositories/   # Acesso a dados (DIP)
├── schemas/        # Pydantic request/response
├── services/       # Regras de negócio (SRP)
└── main.py         # Entry point + seedsfrontend/
├── pages/
│   ├── login.html
│   ├── dashboard.html
│   └── usuarios.html
├── js/
│   ├── config/api.config.js    # URLs dev/prod
│   ├── controllers/            # Orquestração de telas
│   ├── services/               # HTTP + AuthService
│   ├── ui/                     # Componentes visuais
│   ├── models/                 # Entidades frontend
│   └── main.js                 # Entry point arena
└── index.html                  # Arena de combate
---

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

MétodoRotaAuthDescriçãoPOST/api/auth/login❌Login — retorna JWTGET/api/usuarios✅ AdminLista usuáriosPOST/api/usuarios✅ AdminCria usuárioPUT/api/usuarios/{id}✅ AdminAtualiza usuárioDELETE/api/usuarios/{id}✅ AdminInativa usuárioGET/api/combatentes✅Lista combatentesPOST/api/combatentes✅Cria combatentePUT/api/combatentes/{id}✅Edita combatenteDELETE/api/combatentes/{id}✅Remove combatentePOST/api/combatentes/{id}/dano✅Aplica danoPOST/api/combatentes/{id}/cura✅Aplica curaGET/api/condicoes✅Lista condições D&D

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

