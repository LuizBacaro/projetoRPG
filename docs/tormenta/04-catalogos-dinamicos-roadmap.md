# Roadmap — catálogos dinâmicos (talentos, habilidades, magias, equipamento)

Objetivo: repetir o padrão **maduro do D&D 3.5** no monorepo (`Magia`, `Talento`, `Equipamento`, `Pericia` + APIs + seeds), mas isolado no namespace `tormenta`.

## Fases sugeridas

### Fase A — Contratos e dados estáticos licenciados

1. Definir schemas JSON em `docs/tormenta/tabelas/` (só estrutura no repo público).
2. Carregar seeds a partir de processo **privado** ou manual (respeitar licença).
3. Testes de importação: validação de schema, não conteúdo protegido no CI se política exigir.

### Fase B — Tabelas SQL Tormenta

Nomes sugeridos (prefixo evita colisão com D&D):

- `tormenta_catalogo_pericia`
- `tormenta_catalogo_poder` (ou `tormenta_poder`)
- `tormenta_catalogo_magia`
- `tormenta_catalogo_item` (equipamento)

Campos mínimos comuns:

- `id`, `nome`, `slug` (opcional), `descricao_curta`, `pagina_referencia`, `ativo`, `metadata_json`

### Fase C — APIs somente leitura

- `GET /api/v1/tormenta/catalogo/pericias?skip&limit`
- Idem poderes, magias, itens — com filtros por nível/círculo/tipo quando fizer sentido.

### Fase D — Ligação à ficha

- Tabelas N:N `tormenta_personagem_poder`, etc., ou evolução de `ficha_json` para IDs estáveis.
- UI: autocompletar a partir do catálogo em vez de só textarea.

## Habilidades vs poderes

No T20, “poderes” cobrem muito do que em outros sistemas são talentos ou habilidades de classe. **Uma única entidade `poder`** com campo `categoria` (geral, origem, raça, classe, etc.) simplifica consultas.

## Equipamento e carga

- Item com peso e tipo → soma na `ficha_json.carga` pode ser calculada no cliente ou servidor.
- Regra exata de carga: `lookup_json` + motor conforme livro.

## Magias e grimório (MB p.144–209)

- **Âmbito editorial:** lista de magias MB (≈ p.150–209) alimenta o catálogo; **instância por personagem** (conhecidas, preparadas, gasto de PM) fica em Postgres + API Tormenta.
- **Documento de RFs e fases:** [07-requisitos-grimorio-mb-144-209.md](07-requisitos-grimorio-mb-144-209.md).
- **Paridade UX:** fluxo D&D 3.5 em `frontend/games/dnd35/js/controllers/GrimorioController.js` + `GrimorioService.js` (adaptar a `personagem_id` e prefixo `/tormenta/`).
