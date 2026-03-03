markdown
# 🏟️ Arena de Combate TTRPG

[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![JavaScript ES6](https://img.shields.io/badge/JavaScript-ES6-F7DF1E?style=for-the-badge&logo=javascript)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![Railway](https://img.shields.io/badge/Railway-Deploy-0B0D0E?style=for-the-badge&logo=railway)](https://railway.app/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

---

## 📖 Sobre o Projeto

Plataforma web fullstack para gerenciamento de combates de TTRPG (Tabletop RPG), como Dungeons & Dragons. Permite cadastrar combatentes (jogadores, monstros e NPCs), gerenciar pontos de vida, aplicar dano e cura em massa, controlar ordem de iniciativa, aplicar condições D&D 5e, e acompanhar o estado da arena em tempo real.

---

## ✨ Funcionalidades

-   **Cadastro de combatentes**: Jogadores, Monstros e NPCs com ficha completa (atributos, HP, iniciativa, classe, nível, pontos)
-   **Gerenciamento de HP**: Aplicar dano e cura em combatentes individuais ou em massa
-   **Ordem de Iniciativa**: Controle automático da ordem de turnos
-   **25 Condições D&D**: Agraciado, Assustado, Atordoado, Cego, Encantado, Envenenado, Imobilizado, Inconsciente, Invisível, Paralisado, Petrificado, Prone, Surdo, etc.
-   **Arena de Combate**: Visualização em tempo real do estado da batalha
-   **Seed automático**: Banco populado com combatentes e condições D&D na inicialização
-   **Upload de imagem**: Foto do combatente

---

## 🛠️ Stack Tecnológica

### Backend
-   **Python**: 3.11
-   **FastAPI**: 0.104.1
-   **SQLAlchemy**: 2.0.36
-   **Banco de Dados**: PostgreSQL (produção) / SQLite (desenvolvimento)
-   **Uvicorn**: 0.24.0
-   **Pydantic Settings**: 2.1.0
-   **Psycopg2-binary**: 2.9.9
-   **Aiofiles**: 23.2.1

### Frontend
-   **HTML5**, **CSS3**, **JavaScript ES6** (vanilla)
-   Arquitetura modular com ES Modules + Scripts globais
-   Design temático medieval RPG
-   Responsivo (mobile-first)

### Infraestrutura
-   **Railway**: Hospedagem do backend e banco de dados PostgreSQL
-   **Cloudflare**: Gerenciamento de DNS e CDN
-   **Registro.br**: Registro de domínio
-   **GitHub**: Versionamento de código

---

## 🏛️ Arquitetura

O projeto segue Clean Architecture com separação clara de responsabilidades e princípios SOLID.

### Backend — Camadas

backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── combatentes.py     # Endpoints REST de combatentes
│   │       ├── combate.py         # Endpoints de controle de combate
│   │       └── condicoes.py       # Endpoints de condições D&D
│   ├── core/
│   │   ├── config.py              # Configurações via Pydantic Settings
│   │   └── database.py            # Engine SQLAlchemy e sessão
│   ├── models/
│   │   ├── combatente.py          # Model ORM de combatente
│   │   ├── combate.py             # Model ORM de combate
│   │   ├── condicao.py            # Model ORM de condição
│   │   └── combatente_condicao.py # Tabela pivot (N:N)
│   ├── repositories/
│   │   ├── combatente_repository.py
│   │   ├── combate_repository.py
│   │   └── condicao_repository.py
│   ├── schemas/
│   │   ├── combatente.py          # Schemas Pydantic (request/response)
│   │   ├── combate.py
│   │   └── condicao.py
│   ├── services/
│   │   ├── combatente_service.py  # Regras de negócio de combatente
│   │   ├── combate_service.py     # Regras de negócio de combate
│   │   └── condicao_service.py    # Regras de negócio + seed D&D
│   ├── exceptions/                # Exceções customizadas
│   └── main.py                    # Entry point FastAPI
├── migrations/                    # Migrações Alembic
├── tests/                         # Testes unitários e integração
├── Procfile                       # Comando de start Railway
└── requirements.txt               # Dependências de produção
```

### Frontend — Camadas

```
frontend/
├── css/
│   ├── variables.css              # Variáveis CSS (cores, fontes)
│   ├── layout.css                 # Layout principal
│   ├── botoes.css                 # Estilos de botões
│   ├── combatentes.css            # Cards de combatentes
│   ├── modais.css                 # Modais genéricos
│   ├── modal-condicao.css         # Modal de condições
│   ├── arena.css                  # Tela de arena
│   ├── formularios.css            # Formulários de cadastro
│   └── responsivo.css             # Media queries
├── js/
│   ├── config/
│   │   └── api.config.js          # Configuração centralizada de URLs (dev/prod)
│   ├── controllers/
│   │   ├── ConfiguracaoController.js  # Gerencia tela de configuração
│   │   ├── ArenaController.js         # Gerencia tela de arena
│   │   └── CondicaoController.js      # Gerencia condições
│   ├── services/
│   │   ├── CombatenteService.js   # Chamadas HTTP de combatente
│   │   ├── DanoCuraService.js     # Chamadas HTTP de dano/cura
│   │   └── CondicaoService.js     # Chamadas HTTP de condições
│   ├── ui/
│   │   ├── ModalCadastro.js       # Modal de cadastro de combatente
│   │   ├── ModalEdicao.js         # Modal de edição de combatente
│   │   ├── ModalDanoCura.js       # Modal de aplicação de dano/cura
│   │   ├── CondicaoUI.js          # Interface de condições
│   │   ├── CombatenteCard.js      # Card visual de combatente
│   │   ├── TipoSelector.js        # Seletor de tipo (jogador/monstro/NPC)
│   │   └── Toast.js               # Notificações toast
│   ├── models/
│   │   └── Combatente.js          # Model de combatente no frontend
│   └── main.js                    # Entry point frontend (ES module)
└── index.html                     # SPA principal
```

---

## 🎯 Princípios SOLID Aplicados

-   **S** — **Single Responsibility Principle (SRP)**: Cada classe e módulo possui uma única responsabilidade bem definida. Por exemplo, `CombatenteService` é responsável exclusivamente pelas operações HTTP relacionadas a combatentes, enquanto `CombatenteRepository` lida apenas com a persistência de dados de combatentes.
-   **O** — **Open/Closed Principle (OCP)**: O sistema é projetado para ser aberto à extensão, mas fechado para modificação. O `api.config.js` é um exemplo, permitindo a adição de novos ambientes (desenvolvimento, produção, testes) sem a necessidade de alterar o código dos serviços que o consomem.
-   **L** — **Liskov Substitution Principle (LSP)**: Objetos de um supertipo podem ser substituídos por objetos de um subtipo sem quebrar a aplicação. No backend, os `Repositories` são intercambiáveis, permitindo o uso de SQLite em desenvolvimento e PostgreSQL em produção sem impactar a lógica de negócio.
-   **I** — **Interface Segregation Principle (ISP)**: Interfaces são pequenas e específicas para cada cliente. No frontend, os `Services` são separados por domínio (`CombatenteService`, `CombateService`, `CondicaoService`), garantindo que os componentes consumam apenas as funcionalidades de que realmente precisam.
-   **D** — **Dependency Inversion Principle (DIP)**: Módulos de alto nível não dependem de módulos de baixo nível. Ambos dependem de abstrações. No backend, os `Controllers` dependem de abstrações (interfaces de `Services`), não de implementações concretas, facilitando a troca de implementações e a testabilidade.

---

## 🚀 Como Executar Localmente

### Pré-requisitos
-   Python 3.11+
-   Git

### 1. Clone o repositório
```bash
git clone https://github.com/LuizBacaro/projetoRPG.git
cd projetoRPG
git checkout feature/salva
```

### 2. Configure o ambiente backend
```bash
cd backend
cp .env.example .env
# Edite .env com suas configurações (ex: DATABASE_URL para SQLite)

python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate     # Windows

pip install -r requirements.txt
```

### 3. Configure variáveis de ambiente
Crie ou edite o arquivo `.env` na pasta `backend` com as seguintes variáveis:
```env
DATABASE_URL=sqlite:///./arena_rpg.db
PROJECT_NAME=Arena de Combate TTRPG
VERSION=1.0.0
API_V1_PREFIX=/api
ALLOWED_ORIGINS=["http://localhost:3000","http://127.0.0.1:5500"]
```

### 4. Execute o backend
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Acesse o frontend
Abra o `frontend/index.html` com Live Server (extensão do VSCode) ou qualquer servidor HTTP local. Certifique-se de que o servidor esteja rodando na porta 5500 para compatibilidade com `ALLOWED_ORIGINS`.

```
Backend: http://localhost:8000
API Docs: http://localhost:8000/docs
Frontend: http://127.0.0.1:5500
```

---

## 🌐 Deploy em Produção

### URLs
```
Aplicação:  https://arena-de-combate-rpg.com.br
API Docs:   https://arena-de-combate-rpg.com.br/docs
```

### Infraestrutura
O fluxo de deploy em produção é configurado da seguinte forma:
`Registro.br` (gerenciamento de domínio) → `Cloudflare` (DNS e CDN para performance e segurança) → `Railway` (hospedagem do backend FastAPI e do banco de dados PostgreSQL).

### Railway
O deploy é automático a cada push na branch `feature/salva`. O Railway detecta as mudanças e reconstrói/redesplanta a aplicação.

Variáveis de ambiente configuradas no Railway:
```
DATABASE_URL      → URL de conexão com o PostgreSQL (gerada automaticamente pelo Railway)
PROJECT_NAME      → Arena de Combate TTRPG
ALLOWED_ORIGINS   → ["https://arena-de-combate-rpg.com.br"]
```

---

## 📡 Endpoints da API

### Combatentes
| `GET`    | `/api/combatentes?tipo=jogador` | Filtra combatentes por tipo |
| `POST`   | `/api/combatentes` | Cria um novo combatente |
| `DELETE` | `/api/combatentes/{id}` | Remove um combatente por ID |
| `POST`   | `/api/combatentes/{id}/cura` | Aplica cura a um combatente |
| `PATCH`  | `/api/combatentes/{id}/iniciativa` | Atualiza a iniciativa de um combatente |

### Condições
| `GET`    | `/api/condicoes/combatente/{id}` | Lista as condições aplicadas a um combatente |
| `DELETE` | `/api/condicoes/combatente/{id}/{condicao_id}` | Remove uma condição específica de um combatente |

### Combate
| `GET`    | `/api/combate/estado` | Retorna o estado atual do combate (ordem de iniciativa, turno ativo) |

---

## 🗄️ Modelo de Dados

```
Combatente
├── id (PK), nome, tipo (jogador/monstro/npc)
├── classe, nivel, pontos
├── hp_maximo, hp_atual
├── iniciativa
├── forca, destreza, constituicao
├── inteligencia, sabedoria, carisma
├── foto (URL para upload)
└── condicoes → (N:N) Condicao (via CombatenteCondicao)

Condicao
├── id (PK), nome, descricao
└── icone (URL para ícone da condição)

CombatenteCondicao (Tabela pivot para relacionamento N:N)
├── combatente_id (FK para Combatente)
└── condicao_id (FK para Condicao)
```

---

## 🧪 Testes

Para executar os testes do backend:

```bash
cd backend
# Ative seu ambiente virtual se ainda não estiver ativo
source .venv/bin/activate # Linux/Mac ou .venv\Scripts\activate para Windows

# Executar todos os testes com verbosidade
pytest tests/ -v

# Executar testes e gerar relatório de cobertura de código (HTML)
pytest tests/ --cov=app --cov-report=html
```

---

## 🗂️ Branches

| `feature/hospedar` | Branch para experimentos e testes de diferentes configurações de hospedagem. | Em Desenvolvimento |

---

## 👤 Autor

**Luiz Salvador**
GitHub: [@LuizBacaro](https://github.com/LuizBacaro)

---

## 📄 Licença

Este projeto está licenciado sob a [Licença MIT](https://opensource.org/licenses/MIT).
```