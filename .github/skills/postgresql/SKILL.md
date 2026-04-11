---
name: creating-oracle-to-postgres-master-migration-plan
description: 'Descobre todos os projetos em uma solucao .NET, classifica cada um quanto a elegibilidade de migracao Oracle-para-PostgreSQL e gera um plano mestre de migracao persistente. Use ao iniciar uma migracao Oracle-para-PostgreSQL com varios projetos, criar um inventario de migracao ou avaliar quais projetos .NET possuem dependencias Oracle.'
---

# Criacao de um Plano Mestre de Migracao Oracle-para-PostgreSQL

Analise uma solucao .NET, classifique cada projeto quanto a elegibilidade para migracao Oracle→PostgreSQL e escreva um plano estruturado que agentes e skills subsequentes consigam interpretar.

## Fluxo de Trabalho

```
Progress:
- [ ] Etapa 1: Descobrir projetos na solucao
- [ ] Etapa 2: Classificar cada projeto
- [ ] Etapa 3: Confirmar com o usuario
- [ ] Etapa 4: Escrever o arquivo de plano
```

**Etapa 1: Descobrir projetos**

Encontre o arquivo de solucao (extensao `.sln` ou `.slnx`) na raiz do workspace (pergunte ao usuario caso exista mais de um). Faça o parse para extrair todas as referencias de projeto `.csproj`. Para cada projeto, registre nome, caminho e tipo (class library, web API, console, teste etc.).

**Etapa 2: Classificar cada projeto**

Varra cada projeto que nao seja de teste em busca de indicadores Oracle:

- Referencias NuGet: `Oracle.ManagedDataAccess`, `Oracle.EntityFrameworkCore` (verificar `.csproj` e `packages.config`)
- Entradas de configuracao: connection strings Oracle em `appsettings.json`, `web.config`, `app.config`
- Uso no codigo: `OracleConnection`, `OracleCommand`, `OracleDataReader`
- Referencias cruzadas de DDL em `.github/oracle-to-postgres-migration/DDL/Oracle/` (se existir)

Atribua uma classificacao por projeto:

| Classification | Meaning |
|---|---|
| **MIGRATE** | Possui interacoes Oracle que exigem conversao |
| **SKIP** | Sem indicadores Oracle (somente UI, utilitario compartilhado etc.) |
| **ALREADY_MIGRATED** | Existe um duplicado `-postgres` ou `.Postgres` e aparenta ja estar migrado |
| **TEST_PROJECT** | Projeto de teste; tratado pelo fluxo de testes |

**Etapa 3: Confirmar com o usuario**

Apresente a lista classificada. Permita ao usuario ajustar classificacoes ou ordem de migracao antes da finalizacao.

**Etapa 4: Escrever o arquivo de plano**

Salvar em: `.github/oracle-to-postgres-migration/Reports/Master Migration Plan.md`

Use este template exato — consumidores posteriores dependem dessa estrutura:

````markdown
# Master Migration Plan

**Solution:** {solution file name}
**Solution Root:** {REPOSITORY_ROOT}
**Created:** {timestamp}
**Last Updated:** {timestamp}

## Solution Summary

| Metric | Count |
|--------|-------|
| Total projects in solution | {n} |
| Projects requiring migration | {n} |
| Projects already migrated | {n} |
| Projects skipped (no Oracle usage) | {n} |
| Test projects (handled separately) | {n} |

## Project Inventory

| # | Project Name | Path | Classification | Notes |
|---|---|---|---|---|
| 1 | {name} | {relative path} | MIGRATE | {notes} |
| 2 | {name} | {relative path} | SKIP | No Oracle dependencies |

## Migration Order

1. **{ProjectName}** — {rationale, e.g., "Core data access library; other projects depend on it."}
2. **{ProjectName}** — {rationale}
````

Ordene os projetos para que bibliotecas compartilhadas/fundacionais sejam migradas antes dos projetos dependentes.