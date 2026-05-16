# Tabelas de dados (JSON) — Tormenta

Ficheiros nesta pasta guardam **estrutura** e, quando permitido, **valores** digitados a partir do livro licenciado.

## Convenções

- Um ficheiro = uma tabela lógica do livro (ex.: custo de atributos).
- Chaves em **snake_case** ou **camelCase** estáveis; não renomear sem migração.
- Incluir no topo do JSON (comentário **não** é JSON válido — usar campo `_meta`):

```json
{
  "_meta": {
    "titulo_livro": "Tormenta 20 — Módulo Básico",
    "tabela": "Custo de Valores de Habilidade",
    "pagina_livro": null,
    "versao_schema": 1
  },
  "custos": []
}
```

## Ficheiros

| Ficheiro | Descrição |
|----------|------------|
| `custo-atributos.schema.json` | JSON Schema genérico |
| `custo-atributos.exemplo.json` | Exemplo mínimo de formato |

## Dados canónicos no backend

A tabela de **custos 8–18** e os **20 pontos** iniciais estão em:

`backend/app/games/tormenta/data/atributos_compra_pontos.json`

Altere esse ficheiro quando o livro ou errata mudarem os números e **atualize o espelho em JS** na ficha (`CUSTO_COMPRA_ATRIBUTO` em `ficha-personagem.html`), conforme `backend/app/games/tormenta/README.md`.
