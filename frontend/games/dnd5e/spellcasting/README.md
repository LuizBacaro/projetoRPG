# D&D 5e — módulo spellcasting (TypeScript)

Compila fontes TS desta pasta para `../js/spellcasting/` (consumido pela ficha 5e).

## Pré-requisitos

- Node.js 20+ (CI usa 22)

## Instalação e build (local)

```bash
cd frontend/games/dnd5e/spellcasting
npm ci
npm run build
npm test
```

## O que não commitar

- `node_modules/` — listado no `.gitignore` da raiz do repositório
- Artefatos gerados em `../js/spellcasting/` só entram no Git se forem o bundle estável da ficha; após `npm run build`, revise o diff antes do PR

## CI

O pipeline principal **não** instala este pacote por padrão. Se alterar `.ts` aqui, rode `npm ci && npm test` localmente antes do push.
