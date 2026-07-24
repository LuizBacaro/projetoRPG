# FEATURE: Sistema de Vantagens e Desvantagens GURPS 4E

## Descrição Breve
Catálogo completo de vantagens e desvantagens da 4ª edição do GURPS,
extraído das **tabelas de referência rápida do Módulo Básico – Personagens**
(páginas 298–299 vantagens, 300–301 desvantagens), com contrato de custo
enriquecido consumido pela ficha e pela API.

## Fonte de Verdade
- Livro: `livros/GURPS 4E - Módulo Básico - Personagens.pdf`, tabelas
  rápidas das páginas 298–301.
- Corpo do livro para variantes explícitas (ex.: Pacifismo p.151,
  Indulgente p.146, Aparência p.20).
- Arquivo canônico gerado no repositório:
  `backend/app/games/gurps/catalogs/gurps_personagens_sumario_catalogo.json`.
- Fusão Lite + sumário em
  `backend/app/games/gurps/catalogs/lite_catalog.py`.
- Regenerador determinístico (para curadoria / re-execução):
  `scripts/gurps_gerar_sumario_enriquecido.py` seguido de
  `scripts/gurps_reacentuar_sumario.py`.

## Contrato do item (JSON e resposta da API)

Cada item de `vantagens` / `desvantagens` retornado por
`GET /api/v1/gurps/personagens/catalogo/lite-ficha` respeita o formato:

| Campo             | Tipo          | Obrigatório | Observações                                          |
|-------------------|---------------|-------------|-----------------------------------------------------|
| `nome`            | string        | sim         | Nome canônico com acentuação portuguesa.            |
| `custo_texto`     | string        | sim         | Texto do livro (ex.: `"-15*"`, `"5/nível"`).        |
| `custo`           | int \| null   | sim         | Valor único quando aplicável; `null` para variável. |
| `cost_model`      | enum          | sim         | Ver enum abaixo.                                    |
| `custo_por_nivel` | int           | não         | Presente em `por_nivel` e `fixo_mais_por_nivel`.    |
| `custo_base`      | int           | não         | Presente em `fixo_mais_por_nivel`.                  |
| `custo_min`/`custo_max` | int     | não         | Presente em `faixa`.                                |
| `opcoes_custo`    | array         | não         | Presente em `opcoes_discretas`.                     |
| `autocontrole`    | bool          | não         | `true` para desvantagens com `*` no livro.          |
| `unidade_nivel`   | string        | não         | Ex.: `"boca"`, `"apetrecho"`, `"cultura"`.          |
| `tipo_mfsoc`      | `M`/`F`/`Soc`/`M/F` | não   | Tipo M/F/Soc da tabela do livro.                    |
| `exotica_sob`     | `X`/`Sob`     | não         | Coluna X/Sob da tabela.                             |
| `paginas`         | int[]         | não         | Página de referência.                               |

### Valores válidos para `cost_model`
- `fixo` — um valor único (`custo`).
- `por_nivel` — `custo_total = nivel × custo_por_nivel`.
- `fixo_mais_por_nivel` — `custo_total = custo_base + nivel × custo_por_nivel`.
- `opcoes_discretas` — usuário escolhe uma opção de `opcoes_custo:[{rotulo?, custo}]`.
- `faixa` — usuário escolhe qualquer valor entre `custo_min` e `custo_max`.
- `variavel` — sem regra rígida; usuário edita livremente; `custo_texto` é a dica.

### Autocontrole
- Nesta fase o campo `autocontrole=true` apenas sinaliza a origem do valor
  padrão de autocontrole 12 (custo do livro). O seletor de valor de
  autocontrole (×0,5 / ×1 / ×1,5 / ×2) fica como fase 2.

## Persistência e API

- JSON é a fonte primária. Se as tabelas
  `gurps_catalogo_ficha_vantagens` / `gurps_catalogo_ficha_desvantagens` /
  `gurps_catalogo_ficha_pericias` estiverem populadas, a API lê do Postgres
  (`meta.catalogo_listas_origem = "postgres"`).
- Migração `q2r3s4t5u6v7_gurps_catalogo_ficha_meta_custo.py` adiciona uma
  coluna JSON (`JSONB` no Postgres) `meta_custo` nas tabelas de vantagens
  e desvantagens para persistir o contrato enriquecido.
- Round-trip garantido pelo repositório
  `backend/app/games/gurps/repositories/catalogo_ficha_repository.py`
  (`_extrair_meta_custo` no seed; `_linha_para_resposta_api` na leitura).

## UI da ficha

`frontend/games/gurps/js/pages/ficha-gurps.js` renderiza um slot de
controle entre o nome do traço e o custo (`.fg-vant-controle` /
`.fg-desv-controle`) conforme o `cost_model`:

- `fixo`: apenas hint de autocontrole `*` quando aplicável.
- `por_nivel` / `fixo_mais_por_nivel`: botões `−` / `+` (44px+) com input
  numérico de nível; o custo é derivado automaticamente. Botões custom
  visíveis em qualquer navegador — não dependem do spinner nativo do
  `input[type=number]`.
- `opcoes_discretas`: `<select>` com todas as variantes do livro
  (ex.: Pacifismo lista Assassino Relutante −5 / Incapaz de Ferir
  Inocentes −10 / Incapaz de Matar −15 / Legítima Defesa −15 /
  Não-Violência Total −30).
- `faixa`: hint `min…max` + input numérico com atributos `min`/`max`.
- `variavel`: hint com texto do livro; usuário edita o custo.

CSS em `frontend/games/gurps/css/ficha-gurps.css` reflow para 3 linhas em
telas ≤ 640px (nome + custo + remover na 1ª linha; controle em linha
cheia na 2ª). `?v=` bump obrigatório no `<link>`/`<script>` de
`ficha-personagem.html` a cada mudança.

## Escopo desta entrega (2026-07-24)

- ✅ Catálogo completo pelas tabelas rápidas 298–301 (com Indulgente,
  Pacifismo, Honestidade, Covardia, Impulsividade, Aliados, Destemor, e
  demais faltantes anteriores).
- ✅ `cost_model` + campos derivados no JSON, na API e persistidos em
  `meta_custo` no Postgres.
- ✅ UI da ficha com steppers e selects de opções discretas — funciona
  em desktop e mobile, sem depender do spinner nativo.
- ✅ Cache-bust nos assets da ficha (`?v=20260724cm`).

## Fora do escopo (fase 2)

- Modificadores percentuais (ampliações/limitações) das vantagens.
- Pré-requisitos declarativos por traço (validação atualmente é textual).
- Seletor de valor de autocontrole (`×0,5` / `×1` / `×1,5` / `×2`).
- Limite `-75` / `-50` do RF genérico anterior (superseded pelo sumário
  do Módulo Personagens; deve ser reintroduzido só quando validado no
  livro Campanhas ou nas regras de mesa).

## Runbook de produção

1. `alembic upgrade head` (aplica `q2r3s4t5u6v7`).
2. Consulte `GET /api/v1/gurps/personagens/catalogo/lite-ficha` autenticado:
   verifique `meta.catalogo_listas_origem` e presença de `Indulgente` /
   `Pacifismo`.
3. Se `origem === "postgres"`, execute
   `python3 scripts/seed_gurps_catalogo_ficha.py` no ambiente para
   repopular o catálogo com o novo contrato (não altera personagens).
4. Hard refresh da ficha na Vercel e validar UI em desktop e mobile.

## Testes automatizados

- `backend/tests/test_gurps_personagens_api.py`:
  - `test_catalogo_lite_ficha_contem_indulgente_e_pacifismo`
  - `test_catalogo_lite_ficha_cost_model_por_nivel`
  - `test_catalogo_lite_ficha_preserva_meta_custo_no_banco`
  - Testes legados de contagens (`pericias >= 50`, `vantagens >= 50`,
    `desvantagens >= 50`) permanecem verdes.

## Referência do Livro
Capítulo 2 (Vantagens, pp. 34–101) e Capítulo 3 (Desvantagens, pp. 122–165);
tabelas de referência rápida nas páginas 298–301.
