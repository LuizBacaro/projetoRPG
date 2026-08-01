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
  - **Não** inclui proficiências de classe (`talentos_adicionais` em
    `classes_mb.json`) — essas strings ficam só na ficha de classe.
- `poderes_herois_arton.json`
  - Catálogo completo Heróis de Arton v1.1: Treinador + poderes de classe
    (p.54–77), gerais (p.78–83), raça (p.84–91), grupo (p.92–97).
  - Build: `scripts/build_poderes_herois_arton_catalogo.py` a partir de
    `_ha_poderes_extract_raw.json` (extração local do PDF).
  - API: `GET /tormenta/regras/poderes?suplemento=herois_arton`.
- `itens_superiores_v13.json`
  - Tabelas 3-7 / 3-8 / 3-9 (melhorias + materiais especiais).
  - API: `GET /tormenta/regras/itens-superiores`.
- `bestiario_v13.json`
  - ~80 criaturas da Tabela 7-1 (v1.3 p.284–316): stats mecânicos +
    `descricao_curta` + `pagina_referencia` (sem prosa longa do livro).
  - ND numérico (`0.25`, `0.5`, …) + `nd_rotulo` (`1/4`, `1/2`); aliases
    de stubs (`goblin` → `goblin-salteador`).
  - API: `GET /tormenta/regras/bestiario` (`q`, `skip`, `limit`, `tipo`,
    `nd_min`, `nd_max`) e detalhe por slug; import via
    `POST /tormenta/personagens/importar-bestiario`.
  - Extração local: `scripts/extrair_bestiario_t20_v13.py` (PDF em `livros/`,
    não versionado).
- `bestiario_dda_v11.json`
  - ~56 criaturas do Cap. 4 *Deuses de Arton* v1.1 (pp. impressas 252–315):
    Abissais, Aspectos, Celestiais, Fadas, Gênios, Gigantes.
  - Mesmo shape mecânico; `fonte: dda_v11`; ND especiais `S`/`S+`/`?` via
    `nd_rotulo` (sem `nd` numérico).
  - Merge automático em `catalogo_t20._carregar_bestiario_mb`.
  - Extração: `scripts/extrair_bestiario_dda_v11.py` (PDF DdA em `livros/`).
- `armas_v13_overlay.json` + `equipamentos_mb_catalogo.json`
  - Stats de combate (Tabela 3-3) e autocomplete de inventário.

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
