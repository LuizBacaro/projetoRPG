# Frontend D&D 3.5 (`frontend/games/dnd35/`)

Bundle estático do **Dungeons & Dragons 3.5**. Outros jogos (ex.: GURPS, D&D 5e)
devem ganhar pastas irmãs (`frontend/games/gurps/`, etc.) com a mesma ideia:
HTML + CSS + JS daquele sistema, sem misturar com o shell global da conta.

## O que fica aqui

| Pasta / arquivo | Conteúdo |
|-----------------|----------|
| `pages/`        | `dashboard.html`, `ficha-personagem.html`, `magias.html`, `pericias.html`, `pericias-ficha.html`, `usuarios.html`, `arena-combate.html` |
| `css/`          | Folhas de estilo do app 3.5 |
| `js/`           | Módulos, controllers, services, `config/` (`api.config.js`, …) |
| `arena.html`    | Arena de combate (fluxo principal) |

## Shell global (fora deste pacote)

- `frontend/pages/login.html` — login e cadastro (conta global).
- `frontend/pages/selecionar-jogo.html` — escolha de jogo pós-login.
- `frontend/pages/*.html` **stubs** — redirects 301 via HTML para URLs antigas
  (`/pages/dashboard.html` → `/games/dnd35/pages/dashboard.html`).

Estilos compartilhados só entre login e seletor continuam servidos a partir deste
bundle (`/games/dnd35/css/login.css`, `responsivo.css`, `selecionar-jogo.css`) para
não duplicar arquivos.

## URLs e deploy

- **Desenvolvimento (uvicorn):** o backend monta `StaticFiles` em `/games/dnd35`
  e mantém atalhos `/dashboard`, `/arena`, `/pericias` apontando para ficheiros
  dentro desta pasta (`backend/app/main.py`).
- **Vercel:** `vercel.json` na raiz do repositório define `rewrites` para os mesmos
  atalhos, com `outputDirectory: frontend`.

Referências internas usam prefixo **`/games/dnd35/`** (CSS, JS e links entre
páginas do 3.5). O `AuthService` continua a enviar o utilizador para
`/pages/login.html` e `/pages/selecionar-jogo.html` (hub).

## Próximo jogo (ex.: GURPS)

1. Criar `frontend/games/gurps/` com `pages/`, `css/`, `js/` (ou só `em-breve.html`
   até existir jogo completo).
2. Registrar slug no backend (`games_catalog`) e no seletor.
3. Não reutilizar paths `/games/dnd35/` no GURPS; cada slug é um pacote isolado.
