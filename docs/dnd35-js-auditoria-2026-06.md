# Auditoria JavaScript — `frontend/games/dnd35/js` (2026-06)

Escopo: **69 ficheiros**, ~22 800 linhas. Método: revisão estática + `scripts/audit-dnd35-js.sh`.

---

## Resumo executivo

| Área | Avaliação |
|------|-----------|
| API / produção | **Boa** — serviços usam `getApiUrl` de `api.config.js`; fetch com retry 503 |
| Segurança XSS | **Média** — `escapeHtml` existe; Grimório/MagiasAdmin ok; Ficha/Equipamentos com gaps |
| Manutenção | **Atenção** — 4 controllers >1 500 linhas (ficha, grimório, dashboard, arena) |
| Testes FE | **Fraca** — 1 script manual (`test-ficha-perfil-simples.js`); E2E Playwright no backend |
| Legado | `config.js` removido (duplicava URL localhost sem Render) |

---

## Achados por severidade

### Alta (confirmados)

| ID | Achado | Onde | Ação |
|----|--------|------|------|
| A1 | Controllers muito grandes (difícil testar/rever) | `FichaPersonagemController.js` (~3626), `GrimorioController.js` (~3323), `DashboardController.js` (~2000), `ArenaController.js` (~1783) | Fase 2: extrair módulos por domínio (equipamento, grimório UI, dashboard tabela) |
| A2 | `innerHTML` com dados de API/usuário sem `escapeHtml` em vários blocos | `FichaPersonagemController.js` (equipamentos, ataques, mensagens de erro), partes de `DashboardController` | Fase 1: escapar nomes em templates; mensagens de erro já corrigidas onde possível |
| A3 | Cobertura de testes automatizados FE quase inexistente | `frontend/games/dnd35/` | E2E Playwright + testes unitários Vitest por módulo crítico (fase 3) |

### Média (confirmados)

| ID | Achado | Onde | Ação |
|----|--------|------|------|
| M1 | Duplicação `combat-rules.js` + `combat-rules.global.js` | `utils/` | Manter global para HTML legado; documentar única fonte em `combat-rules.js` |
| M2 | Mistura ES modules + scripts globais (`window.AuthService`) | Vários HTML | Padrão aceite no projeto; novos ficheiros só ESM |
| M3 | `MagiasAdminController.js` ~1266 linhas | Admin magias | Aceitável para ferramenta interna; extrair importação/histórico depois |
| M4 | Cache-busting `?v=` heterogéneo | HTML imports | Ao alterar JS, incrementar `?v=` no HTML afetado (AGENTS.md) |

### Baixa / hipóteses

| ID | Achado | Notas |
|----|--------|-------|
| B1 | BroadcastChannel sem fallback em browsers antigos | Já há degradação graciosa em partes da ficha |
| B2 | Circuit breaker no fetch pode confundir utilizador | Toast/evento `api:circuit-open` — documentar em suporte |

---

## O que está bem

- **Sem** `fetch` hardcoded para `localhost:8000` nos serviços (após remoção de `config.js`).
- **AuthService**: refresh em 401 + integração multi-jogo.
- **GrimorioController** / **MagiasAdminController**: uso consistente de `escapeHtml` em listagens.
- **graceful-degradation.js**: bootstrap seguro na ficha.
- **validators.js**, **formatters.escapeHtml** exportado globalmente.

---

## Plano de melhorias

### Fase 1 — Quick wins (1–2 dias)

- [x] Remover `config.js` legado
- [x] Script `scripts/audit-dnd35-js.sh` no CI local / pré-push
- [ ] Escapar `nome`/`descricao` em templates de equipamento/ataque na ficha (PR dedicado)
- [ ] Extrair constantes de seletores DOM repetidos na ficha

### Fase 2 — Estrutural (incremental)

- Dividir `FichaPersonagemController` em: `FichaAtributos`, `FichaEquipamentos`, `FichaMagias`, `FichaPerfilMagico`
- Dividir `GrimorioController`: filtros vs lista vs preparação
- Reduzir `DashboardController`: tabela vs modais

### Fase 3 — Testes

- E2E: login, dashboard, ficha, grimório (já em `backend/tests/e2e/`)
- Vitest para `combat-rules.js`, `escapeHtml`, parsers de slots

---

## Métricas de sucesso

| Fase | Métrica |
|------|---------|
| 1 | `audit-dnd35-js.sh` exit 0; zero URLs localhost em `js/` |
| 2 | Nenhum ficheiro >2000 linhas em `controllers/` |
| 3 | E2E smoke verde no CI; ≥3 testes Vitest em `utils/` |

---

## Comandos

```bash
# Auditoria rápida
./scripts/audit-dnd35-js.sh

# E2E (API + frontend no mesmo origin)
cd backend && pytest tests/e2e/ -v

# ESLint (CI)
cd frontend && npx eslint games/dnd35/js/ --ext .js
```

---

## Referências

- Agente: [.github/agents/javascript-project-auditor.agent.md](../.github/agents/javascript-project-auditor.agent.md)
- [docs/e2e-playwright-arena.md](e2e-playwright-arena.md)
