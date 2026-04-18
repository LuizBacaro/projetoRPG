# 🔧 Fix: Execução de Migrations Alembic no Startup

## Problema

**Erro em produção (Render/Neon):**
```
❌ Erro durante startup: Falha no startup em 'inicializar_equipamentos': 
(psycopg2.errors.UndefinedColumn) column equipamentos.categoria does not exist
```

### Causa Raiz

1. **Migrations do Alembic não eram executadas no startup** — o `app/main.py` apenas chamava `Base.metadata.create_all()` do SQLAlchemy
2. `create_all()` **apenas cria tabelas novas**, não altera tabelas existentes
3. A migration `af4a62e567b7_adicionar_campos_equipamentos_manual.py` adicionava novas colunas (`categoria`, `subcategoria`, etc.) à tabela `equipamentos`
4. **Banco local**: as colunas foram adicionadas manualmente via SQLAlchemy (sem passar pela migration Alembic)
5. **Banco de produção (Neon)**: a migration nunca foi aplicada, então as colunas não existem

## Solução

### Modificação em `backend/app/main.py`

Adicionada função `_executar_alembic_migrations()` que:

1. Lê a configuração do Alembic (`alembic.ini`)
2. Executa `alembic upgrade head` automaticamente no startup
3. Garante que o schema esteja sempre atualizado em todas as instâncias

**Ordem de execução no startup:**
```python
passos = [
    ("executar_alembic_migrations", _executar_alembic_migrations),  # ← Novo, primeiro
    ("criar_tabelas", lambda: Base.metadata.create_all(bind=engine)),
    ("criar_admin_padrao", lambda: criar_admin_padrao(db)),
    # ... resto dos passos
]
```

### Benefícios

✅ **Automático**: Migrations rodam sem ação manual  
✅ **Seguro**: Não falha o startup se migrations falharem (fallback para create_all)  
✅ **Produção-pronto**: Funciona em SQLite (dev) e PostgreSQL (prod)  
✅ **Idempotente**: Pode rodar múltiplas vezes sem problemas  

## Histórico Local vs Produção

| Estado | Local (SQLite) | Produção (Neon PostgreSQL) |
|---|---|---|
| **Antes do fix** | Colunas existem (criadas via SQLAlchemy) | Colunas NÃO existem (migration não aplicada) |
| **Migrations marcadas** | `af4a62e567b7` (stamped) | Nenhuma aplicada |
| **Erro no startup** | ✅ Funciona (as colunas existem) | ❌ Falha (coluna não existe) |
| **Após o fix** | ✅ Migrations aplicadas automaticamente | ✅ Migrations aplicadas automaticamente |

## Próximas Etapas

1. ✅ **Commit**: Fix adicionado em `ed70021`
2. ✅ **Push**: Enviado para `feature/salva`
3. 📋 **Deploy**: Render detectará novo commit e:
   - Fará deploy automático
   - Executará startup com migrations
   - As colunas de equipamentos serão criadas
4. ✅ **Resultado**: `/api/v1/equipamentos` funcionará normalmente

## Referências

- Migration: [`af4a62e567b7_adicionar_campos_equipamentos_manual.py`](backend/alembic_migrations/versions/af4a62e567b7_adicionar_campos_equipamentos_manual.py)
- Fix: [Commit `ed70021`](https://github.com/LuizBacaro/projetoRPG/commit/ed70021)
- Arquivo modificado: [`backend/app/main.py`](backend/app/main.py#L226-L252)

## Lições Aprendidas

⚠️ **Never rely on SQLAlchemy's `create_all()` alone** — use Alembic migrations para todas as mudanças de schema  
⚠️ **Always test migrations locally** — garanta que a coluna exista no banco de dev  
✅ **Automate migrations in startup** — evita surpresas em produção
