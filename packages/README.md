# `packages/` — código partilhado (opcional)

Reservado para **bibliotecas internas** usadas por mais do que um app, quando
a separação em `apps/` acontecer. Sugestões do plano de arquitetura multi-jogo:

| Pacote (futuro) | Conteúdo típico |
|-----------------|-----------------|
| **common-ui** | Tema, header com “trocar jogo”, componentes de auth (se o shell e os jogos deixarem de duplicar HTML/CSS). |
| **common-infra** | Cliente HTTP com tratamento de `409`/`X-Game-Slug-Required`, tipos de erro, helpers de telemetria. |

**Hoje:** o frontend usa `frontend/js/shared/` e serviços por página; o
backend não tem pacote Python partilhado fora de `backend/app/shared/constants.py`.
Nada nesta pasta é exigido para build ou testes até existir um segundo cliente
que importe o mesmo código.
