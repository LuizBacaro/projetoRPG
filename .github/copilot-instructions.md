# Copilot Instructions

Este workspace usa instrucoes granulares por dominio em `.github/instructions`.

## Escopo Geral

- Projeto fullstack TTRPG com backend FastAPI/SQLAlchemy e frontend HTML/CSS/JavaScript vanilla.
- Priorize mudancas pequenas e de causa raiz; evite reformatacao ampla sem necessidade.
- Nao reverta mudancas existentes do usuario sem solicitacao explicita.

## Onde Estao as Regras Especificas

- Backend Python: `.github/instructions/backend.instructions.md`
- Frontend Web: `.github/instructions/frontend.instructions.md`
- Migrations Alembic: `.github/instructions/migrations.instructions.md`

## Convencoes Transversais

- Preserve autenticacao real e autorizacao por perfil; nao introduza atalhos permissivos.
- Ao mexer em fluxos criticos (auth, cache, listagens, migrations), valide o impacto e informe risco residual quando nao houver teste automatizado.
- Para textos de interface, prefira portugues consistente com o restante do produto.