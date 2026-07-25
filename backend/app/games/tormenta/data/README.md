# Dados Tormenta — fonte canónica v1.3

Estes JSON alimentam a ficha, o motor de regras e a API `/tormenta/regras/*`.
Desde julho de 2026 a **fonte canónica** de magias e poderes é
`livros/Tormenta20-Edicao-Jogo-do-Ano-v1.3.pdf`. As tabelas do Módulo Básico
(MB, pp.307–317 magias e Cap. 5 talentos) estão **depreciadas** e ficam
preservadas apenas como legado para depuração e migração histórica.

## Catálogos v1.3

- `magias_mb_catalogo.json`
  - Total: **227** entradas — magias arcanas (124) e divinas (103).
  - Círculos: **1–5** (v1.3 removeu truques 0 e 6º–9º do MB antigo).
  - Fonte: listas p.174–177 do PDF v1.3; textos longos ficam no livro.
  - Metadados por item: `slug`, `nome`, `circulo`, `tipo` (arcana/divina),
    `escola`, `descricao_curta`, `pagina_referencia`.
  - Magias nas **duas** listas (mesmo nome) usam slug único com sufixo
    `_arc` / `_div` (ex.: `luz_arc`, `luz_div`). O check CI
    (`scripts/check_magias_mb_catalogo.py`) exige slugs únicos e círculos 1–5.
- `talentos_mb_catalogo.json`
  - Total: **162** poderes — combate (40), destino (20), magia (8),
    concedidos (72), tormenta (22).
  - Fonte: Cap. 2, tabelas p.126–128 + descrições p.124–136 do PDF v1.3.
  - Nomenclatura: v1.3 chama de «poderes»; nome do ficheiro mantido por
    compatibilidade com o resto do código.
  - Metadados por item: `slug`, `nome`, `categoria_v13`, `prerequisitos`,
    `descricao_resumo` (curta), `pagina_referencia`, `fonte_catalogo`.

## Alias MB → v1.3

- `magias_mb_v13_slug_aliases.json`
  - Mapeia slugs MB antigos (`resistencia_a_energia_div`, `luz_div`, etc.)
    para o slug v1.3 correspondente.
  - Usado pelo backend em `resolver_slug_mb_para_v13(slug)` para preservar
    vínculos em `tormenta_magias_personagem` gravados antes da migração.
  - Vínculos MB sem equivalente v1.3 (círculo 0 e 6–9 do MB, magias não
    portadas) permanecem **órfãos** e devem aparecer com aviso na UI. Não
    apagar em massa.

## Legado (MB)

- `magias_mb_catalogo.legacy_mb.json` — snapshot do catálogo antigo com
  ~707 entradas em círculos 0–9 (Módulo Básico pp.307–317). Preservado só
  para auditoria; **não é lido pelo código de produção**.
- `talentos_mb_catalogo.legacy_mb.json` — snapshot MB Cap. 5 (~27 entradas,
  muitas eram proficiências de classe embutidas). Preservado para
  referência.
- `magias_mb_nome_aliases.json` — aliases de nomes usados pelo pipeline
  histórico `backend/scripts/enrich_magias_mb_catalogo.py`. Legado.

## Regras associadas

- Custo em PM por círculo (v1.3, Tabela 4-1): 1º=1, 2º=3, 3º=6, 4º=10,
  5º=15. Implementado em `rules/conjuracao_t20.py`
  (`custo_pm_preparar_ou_lancar_magia`).
- Fonte legal: `docs/tormenta/00-visao-e-fontes-legais.md` — apenas
  metadados curtos + página de referência; textos longos ficam no livro.
