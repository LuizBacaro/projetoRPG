# ADR 0002 — Tormenta: colunas SQL + `ficha_json` extensível

**Status:** aceite (em evolução)  
**Data:** 2026-06  
**Contexto:** [05-contrato-dados-ficha-json-e-api.md](../tormenta/05-contrato-dados-ficha-json-e-api.md)

## Contexto

A ficha Tormenta MB mistura atributos estáveis (PV, PM, CA), listas dinâmicas (perícias, ataques) e catálogos que migram para SQL (talentos, magias por `magia_slug`).

## Decisão

1. **Colunas SQL** para campos de combate/ficha usados em queries e arena (`pv_*`, `pa_*` como PM, atributos, `foto_url`).
2. **`ficha_json`** para estruturas flexíveis e legado (`pericias[]`, `equipamentos[]`, flags de conjuração MB, anotações de mesa).
3. **Catálogos MB** em `backend/app/games/tormenta/data/*.json` + `GET /tormenta/regras/*` — sem texto longo do livro no repo público.
4. **Vínculos canónicos** em tabelas SQL quando há catálogo: `tormenta_talentos_personagem`, `tormenta_magias_personagem` (papel: grimorio | conhecida | preparada).
5. Chaves novas em `ficha_json` são **aditivas**; migração pontual via endpoints `migrar-do-json` quando existir paridade SQL.

**PM vs `pa_*`:** manter nomes de coluna `pa_max`/`pa_atual` no banco; UI e docs usam “PM”. Renomear coluna só com migration + ADR novo.

## Consequências

- PATCH de personagem deve preservar chaves desconhecidas em `ficha_json`.
- Grimório G0–G3 (regras + API magias) não exige duplicar catálogo no frontend.
- Próximo passo de produto: reduzir dependência de `magias_texto` livre após adoção total do modal grimório (G4/G5).

## Alternativas consideradas

| Alternativa | Motivo de rejeição |
|-------------|-------------------|
| Tudo em JSON | Dificulta grimório, talentos e relatórios SQL |
| Tudo normalizado cedo | Custo alto antes do MB estar estável na UI |
