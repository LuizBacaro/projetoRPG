# ⚠️ Pendente antes do próximo push no Render

**Status:** 🔴 **NÃO FEITO** — alinhar `alembic_version` no Neon production  
**Criado em:** 2026-07-11  
**Pode apagar este arquivo** depois de concluir o stamp e validar o deploy.

---

## Por que fazer (mesmo com produção estável)

- `alembic_version` em prod: `a7b9d3e1c2f4` → head do repo: `p1q2r3s4t5u6`
- O `Procfile` roda `alembic upgrade head` em **cada deploy** — com versão desalinhada, o próximo push pode falhar ou tentar SQL perigoso.
- O stamp **não apaga dados** — só atualiza a tabela `alembic_version`.

---

## Checklist (5–10 min)

- [ ] Backup no Neon (PITR ou snapshot) — projeto **projetoRPG_Oreon**, branch **production**
- [ ] Copiar `DATABASE_URL` do Render (Oregon `us-west-2`, **não** Virginia)
- [ ] Pre-check (somente leitura):

```bash
export DATABASE_URL='postgresql://...'
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f scripts/neon-producao-alembic-precheck.sql
```

- [ ] Stamp (interativo):

```bash
./scripts/neon-producao-alinhar-alembic.sh
```

- [ ] Confirmar: `cd backend && alembic current` → `p1q2r3s4t5u6 (head)`
- [ ] Smoke: `curl -sS https://projetorpg-7ih3.onrender.com/health`
- [ ] **Só então** `git push` / deploy no Render
- [ ] Após deploy OK: marcar este arquivo como feito ou deletá-lo

---

## Documentação completa

- [docs/ANTES-DO-PUSH-RENDER.md](docs/ANTES-DO-PUSH-RENDER.md)
- [docs/runbook-neon-producao-alembic.md](docs/runbook-neon-producao-alembic.md)

---

## Pedir guia ao agente

No chat do Cursor, antes do push:

> "Vou fazer push no Render — me guie no stamp Neon"

O agente deve ler esta pendência e o runbook, e acompanhar passo a passo.
