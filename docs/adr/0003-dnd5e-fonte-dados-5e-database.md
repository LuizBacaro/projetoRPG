# ADR 0003 — D&D 5E: catálogos derivados (não clone integral do 5e-database)

**Status:** aceite  
**Data:** 2026-06  
**Contexto:** [.cursor/requisitos/dnd5e/README.md](../../.cursor/requisitos/dnd5e/README.md)

## Contexto

O 5e no Arena precisa de raças, classes, magias e equipamento alinhados ao SRD/OGL, em PT-BR na UI, sem misturar com D&D 3.5 (`dnd35`).

## Decisão

1. **Fonte de referência upstream:** [5e-bits/5e-database](https://github.com/5e-bits/5e-database) (OGL), com **tag fixada** em `backend/app/games/dnd5e/data/catalogo_metadata.py` (`DND5E_DATABASE_VERSION`).
2. **Dados no repo:** subconjuntos **curados** em Python/JSON (`*_catalogo.py`, `foundry_spells.py`, seeds), não o repositório upstream inteiro como submodule.
3. **Tradução:** camada `spell_i18n.py` e rótulos na UI; nomes em inglês no catálogo interno quando necessário.
4. **Isolamento:** zero import de `app.games.dnd35` a partir de `dnd5e`; rotas sob `/api/v1/dnd5e/...` e frontend `frontend/games/dnd5e/`.
5. **Import Excel** (`magia_import_service`) para magias fora do subconjunto embutido — fluxo de mesa, não substitui a pinagem de versão.

Regenerar catálogos a partir do upstream: script/documentar em [plano-ui-dashboard.md](../dnd5e/plano-ui-dashboard.md) (fase de tooling).

## Consequências

- Conteúdo de livros Wizards **não** licenciado no dataset público do repo.
- Paridade com 3.5 no seletor (`disponivel`) não implica mesmas mecânicas.
- Atualizar `DND5E_DATABASE_VERSION` + changelog no PR quando alterar seeds derivados do 5e-database.

## Alternativas consideradas

| Alternativa | Motivo de rejeição |
|-------------|-------------------|
| Submodule 5e-database no Git | Tamanho, ruído em CI, mistura EN/PT |
| Portar regras 5e para tabelas 3.5 | Viola fronteira multi-jogo |
