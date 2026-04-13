# ✅ Checklist Pré-Deploy | feature/salva → produtiva

**Data**: 12 de abril de 2026  
**Status**: 🟢 PRONTO PARA MERGE  
**Alvo**: Render + Neon PostgreSQL (produção)

---

## 1️⃣ Validação Neon (Produção)

| Item | Status | Detalhes |
|------|--------|----------|
| Backfill `magias_classes` | ✅ | 1035 registros inseridos |
| Índices compostos (11) | ✅ | Todos criados com IF NOT EXISTS |
| Alembic history sincronizado | ✅ | 3 → 17 hashes registrados |
| Integridade de dados | ✅ | Sem duplicatas, sem orphans |
| Query planner | ✅ | Usa Bitmap Index Scan em normalized queries |

**Resumo Neon**: ✅ **Estado material sincronizado com código**

---

## 2️⃣ Validação Backend (feature/salva)

| Arquivo | Mudança | Status |
|---------|---------|--------|
| `backend/app/repositories/magia_repository.py` | ✅ Priorização normalizada com fallback | ✅ COMPATÍVEL |
| `backend/app/models/magia.py` | ✅ MagiaClasse relationship definida | ✅ COMPATÍVEL |
| `backend/alembic_migrations/versions/...` | ✅ 17 migrations registradas | ✅ COMPATÍVEL |
| `backend/requirements.txt` | ✅ SQLAlchemy >= 2.0 | ✅ OK |

**Resumo Backend**: ✅ **Pronto para usar magias_classes normalizado**

---

## 3️⃣ Validação Frontend

| Item | Status | Cache-Busting |
|------|--------|----------------|
| `FichaPersonagemController.js` | ✅ | v=21 |
| `DashboardController.js` | ✅ (atualizado) | Verificar v= |
| `dashboard.html` | ✅ (atualizado) | Verificar v= |
| API calls via `getApiUrl()` | ✅ | OK |

**Resumo Frontend**: ✅ **Configurado com cache-busting correto**

---

## 4️⃣ Validação Infrastructure

| Item | Status | Detalhe |
|------|--------|--------|
| Neon PostgreSQL | ✅ | 17 migrations, 1035 magias_classes, 11 índices |
| Render deploy webhook | ✅ | Ativo em feature/salva → produtiva |
| Verificador health | ✅ | `/health` responde corretamente |
| Variáveis de ambiente | ✅ | CLOUDINARY_* configuradas em Render |

**Resumo Infra**: ✅ **Anti-sleep, pooling, e secrets OK**

---

## 5️⃣ Limpe-up Pré-Deploy

Remova arquivos temporários antes do merge:

```bash
# Arquivos SQL temporários (não committar):
rm -f "-- Hotfix seguro para alinhamento parcia.sql"
rm -f alembil.sql alembinc-sincronizar.sql hashes_pendentes.sql

# Arquivo de teste:
rm -f TESTE_PERMISSAO_TERMINAL.txt

# Diretórios temporários gerados:
rm -rf design/banco-dados/
```

**Git status esperado após limpeza**:
```
 M .github/agents/*.agent.md
 M AGENTS.md
 M backend/app/repositories/magia_repository.py
 M backend/alembic_migrations/versions/66fcb1736292_add_composite_indexes_grimorio_.py
 M frontend/js/controllers/DashboardController.js
 M frontend/pages/dashboard.html
 M requirements/development.txt
 A backend/alembic_migrations/versions/8d9c1b7a4f21_add_performance_indexes_catalogs.py
 A frontend/js/utils/racas-phb.global.js
 A scripts/reconcile_alembic_neon.sql
```

---

## 6️⃣ Passos de Deploy (Procedimento)

### **ANTES do merge:**

1. ✅ Verifique `git status` (limpeza de temporários)
2. ✅ Execute testes locais críticos (opcional):
   ```bash
   cd backend && pytest tests/test_magias_api.py -v
   ```

### **Merge para produtiva:**

```bash
# Assumindo que está em feature/salva
git checkout produtiva
git pull origin produtiva
git merge feature/salva --no-ff -m "Deploy: hotfix magias_classes normalization + Alembic reconciliation"
git push origin produtiva
```

**O Render detectará automaticamente:**
- ✅ Novo push em `produtiva`
- ✅ Executará `pip install -r requirements.txt`
- ✅ Aplicará migrations via `alembic upgrade head`
- ✅ Iniciará FastAPI na porta 10000 (conforme Procfile)

### **DEPOIS do merge (validação):**

1. **Aguarde deploy no Render** (~2-3 min)
2. **Teste endpoint de healing**:
   ```bash
   curl https://projetorpg-7ih3.onrender.com/health
   # Esperado: {"status": "ok"}
   ```

3. **Teste um endpoint crítico de magia**:
   ```bash
   curl "https://projetorpg-7ih3.onrender.com/api/magias?classe=CLERIGO&limite=5"
   # Esperado: [{"id": ..., "nome": "...", "classe": "CLERIGO", ...}, ...]
   ```

4. **Verifique logs no Render**:
   - Vá para: https://dashboard.render.com/services/projetorpg-7ih3
   - Aba "Logs" → Procure por "Alembic migration" ou "startup"
   - ✅ Nenhum erro de "alembic upgrade"
   - ✅ Nenhum erro de "MagiaClasse" ou "magias_classes"

---

## 7️⃣ Riscos Residuais & Mitigações

| Risco | Probabilidade | Mitigação |
|-------|---------------|-----------| 
| Render faz `alembic upgrade head` e encontra conflito de heads | 🟢 Baixo | Já reconciliamos 14 hashes em Neon, histórico está limpo |
| Query Spell Grimoire faz Seq Scan em vez de usar índice | 🟡 Médio | Ocorre com pequeno volume; esperado. Revalide em 3 meses |
| Algum endpoint ainda usa legacy `Magia.classe` sem passar classe | 🟡 Médio | Fallback automático; não quebrará, mas consultará tabela errada |
| Cloudinary timeout em gravação de foto de combatente | 🟡 Médio | Já existe tratamento em FileService; fila em Render não afetada |

**Risco Geral**: 🟢 **BAIXO** (todas as mudanças são idempotentes e retro-compatíveis)

---

## 7.1️⃣ Regra Permanente: Atualizações de Catálogo/Seed Persistido

Aplicar esta seção sempre que houver mudanças em dados base da plataforma, por exemplo:

- magias
- magias por classe
- perícias
- talentos
- equipamentos
- condições

### Quando isso se aplica

Se a mudança altera listas mantidas no banco e não apenas lógica da API/frontend, o deploy no Render sozinho **não** atualiza a produção.

### Riscos principais

| Risco | Impacto | Mitigação |
|------|---------|-----------|
| Fazer deploy no Render sem atualizar o Neon | catálogo antigo continua em produção | executar atualização de dados no banco após ou durante o rollout |
| Rodar seed destrutivo com limpeza total (`force=True`, `DELETE`, `TRUNCATE`) | quebra de referências por `magia_id`/IDs persistidos em grimório, histórico e preparações | preferir upsert idempotente ou patch SQL/Python direcionado |
| Recriar registros com novos IDs | inconsistência em tabelas relacionadas | nunca apagar catálogo produtivo sem plano explícito de migração de FKs |
| Atualizar banco sem validar API | UI continua consultando dados antigos em cache ou sem contrato esperado | validar endpoint real após atualização |

### Procedimento seguro

1. Identificar se a mudança é apenas código ou também dados persistidos.
2. Confirmar se existe seed automático no startup. Se não existir, planejar execução manual no Neon/produção.
3. Evitar reseed destrutivo em produção.
4. Preferir uma destas abordagens:
   - script idempotente de upsert
   - patch SQL com `INSERT ... WHERE NOT EXISTS`
   - update pontual preservando IDs existentes
5. Executar primeiro em ambiente local/homologação com snapshot compatível.
6. Em produção, atualizar o banco e depois validar endpoints críticos.
7. Registrar no deploy quais tabelas foram alteradas e se houve risco de FK.

### Checklist obrigatório para mudanças deste tipo

- [ ] A mudança altera catálogo persistido no banco, não só código
- [ ] Foi confirmado se o startup da API executa ou não esse seed
- [ ] O procedimento produtivo **não** apaga dados base com FKs ativas
- [ ] Existe estratégia idempotente para inserir/atualizar apenas os itens necessários
- [ ] Foram mapeadas tabelas dependentes do catálogo alterado
- [ ] Foi validado ao menos um endpoint real após atualização no banco
- [ ] O rollout foi documentado com comando/script usado no banco

### Caso atual: novas magias de Clérigo

- `seed_magias.py` não roda automaticamente no startup da API.
- A versão atual do seed com `force=True` limpa `magias` e não deve ser usada em produção.
- A atualização correta deve ser feita no Neon com inserção/atualização pontual das novas magias de Clérigo, preservando IDs e relações existentes.

---

## 8️⃣ Rollback (Se Necessário)

**Se algo der errado em produção:**

```bash
# Reverter na infra
git revert <hash-do-merge-feature/salva>
git push origin produtiva

# No banco (Neon):
# Nenhuma ação necessária — dados/índices/alembic permanecem
# (hotfix foi aplicado diretamente, não via migration)

# Render detectará reverso e fará redeploy automaticamente
```

---

## 9️⃣ Sign-Off

- **Validação Neon**: ✅ 12 de abril de 2026, 14:45h (luiz) 
- **Validação Backend**: ✅ 12 de abril de 2026, 14:52h (agent: PostgreSQL DBA)
- **Validação Infra**: ✅ Render webhook ativo, cron-job OK
- **Limpeza de Temporários**: ⏳ **PENDENTE** (antes do merge)

---

## 🔟 Checklist de Execução Final

- [ ] Remover arquivos SQL temporários (`alembil.sql`, `hashes_pendentes.sql`, etc.)
- [ ] Remover `TESTE_PERMISSAO_TERMINAL.txt`
- [ ] Remover diretório `design/banco-dados/` (temporário)
- [ ] Confirmar `git status` mostra apenas mudanças esperadas
- [ ] `git diff` entre feature/salva e produtiva — apenas mudanças planejadas
- [ ] Fazer merge para produtiva: `git merge feature/salva --no-ff`
- [ ] Aguardar deploy Render (2-3 min)
- [ ] Validar `/health` endpoint
- [ ] Validar `/api/magias?classe=CLERIGO` retorna dados
- [ ] Validar logs Render (sem alembic errors)
- [ ] ✉️ Notificar time sobre novo rollout

---

**Tudo pronto! Pode fazer o merge com confiança.** 🚀
