# ADR 0004 — Fase 5 (`apps/` separados): adiado

**Status:** Aceite (adiamento)  
**Data:** 2026-06

## Contexto

O [roteiro de melhorias de arquitetura](../roteiro-melhorias-arquitetura.md) prevê, na **Fase 5**, repositórios ou pacotes em `apps/` (um por jogo) com deploy independente, mantendo Auth Hub e Postgres partilhados.

Hoje o monólito FastAPI em `backend/app/games/{dnd35,dnd5e,tormenta,gurps}` + frontend em `frontend/games/*` já isola domínios por pasta e `game_slug`. O custo de split físico (CI/CD, CORS, versões de API, migrações coordenadas) é alto face ao ganho imediato.

## Decisão

**Não** iniciar split para `apps/` neste ciclo. Continuar:

- Monólito + Auth Hub (`ADR 0001`)
- Frontends estáticos por jogo sob `frontend/games/`
- Catálogo multi-jogo e enroll no startup

Reavaliar Fase 5 quando **pelo menos um** destes for verdadeiro:

1. Equipa ou release train separada por jogo com cadência diferente.
2. Necessidade legal/comercial de licenciar ou distribuir um jogo isoladamente.
3. Escala de deploy onde um jogo derruba os outros (SLO por `game_slug`).

## Consequências

- **Positivo:** Menos complexidade operacional (um serviço Render, uma migration chain).
- **Negativo:** Bundle e tempo de CI continuam acoplados; refactors grandes em `dnd35` ainda exigem disciplina manual.
- **Mitigação:** ADRs por jogo (`0002`, `0003`), matriz de requisitos, E2E smoke e auditoria JS (`docs/dnd35-js-auditoria-2026-06.md`).

## Referências

- [apps/README.md](../../apps/README.md) — esboço futuro
- [docs/arquitetura-multi-jogo.md](../arquitetura-multi-jogo.md)
