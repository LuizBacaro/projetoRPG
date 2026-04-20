# Contrato do Catálogo de Tabelas de Classes

Este documento define o contrato alvo entre:
- extração de planilhas (`tabelas_classes_excel/`);
- normalização (`processar_tabelas_classes_excel.py`);
- consumo futuro no backend (opt-in por feature flag).

## Objetivo

Preservar compatibilidade e evitar breaking change durante a evolução do catálogo
de tabelas 3-3..3-18 do Livro do Jogador (D&D 3.5).

## Artefato canônico

- Arquivo: `docs/dados/tabelas_classes_catalogo.json`
- Estrutura raiz:
  - `schema_version: number`
  - `generated_from: string`
  - `tables: ClassTable[]`

## Contrato de `ClassTable`

- `table_number: number` (intervalo esperado: 3..18)
- `title: string`
- `source_file: string` (nome da planilha de origem)
- `metadata: object<string,string>`
- `header: string[]` (cabeçalhos inferidos ou `col_n`)
- `rows: object<string,string>[]` (linhas normalizadas)

## Regras de validação

- O catálogo deve conter todas as tabelas `3-3` até `3-18`.
- Cada tabela deve respeitar quantidade mínima de linhas (validação conservadora).
- Tabelas baseadas em nível de classe devem conter marcadores de nível (`1°`, `20°`).
- A tabela `3-18` deve conter termos de domínio (`Aberração`, `Morto-vivo`).

## Evolução compatível

- Mudanças de contrato devem incrementar `schema_version`.
- Consumidores novos devem ser protegidos por feature flag:
  - `CLASSES_TABLES_CATALOG_ENABLED=false` por padrão.
- Não remover campos existentes sem etapa de migração compatível.
