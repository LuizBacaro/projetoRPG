# `backend/app/games/tormenta/` — Tormenta 20

Stack vertical da ficha do **Módulo Básico** (cadastro digital, CRUD).

## Regras de atributos (T20)

- **Modificadores** (faixas) e **custos de compra por pontos** (8–18): `app.games.tormenta.rules.atributos_t20` + dados `app/games/tormenta/data/atributos_compra_pontos.json`.
- Testes: `tests/test_tormenta_atributos_t20.py`.
- A ficha web espelha a mesma lógica em JS — alterações na tabela devem atualizar **JSON + Python + `ficha-personagem.html` (CUSTO_COMPRA_ATRIBUTO / modificadorAtributoT20)**.

## API

- `GET/POST /api/v1/tormenta/personagens`
- `GET/PATCH/DELETE /api/v1/tormenta/personagens/{id}`
- `GET /api/v1/tormenta/regras/racas` — raças MB com `ajustes`, `escolhe_duas_mais2`, `mod_car_fixo` (Lefou), `tracos_resumo`, `idioma_racial_mb`; inclui `idiomas_geral_mb` e `idiomas_tabela_mb` (Cap. 2 MB)

Guard: `requer_game_tormenta` (JWT `game_slug=tormenta` em modo estrito).

## Colunas principais

- Atributos na compra por pontos: fichas **tipo jogador** usam `ficha_json.atributos_compra` quando presente (valores-base 8–18); senão os seis atributos do modelo. O custo total **não pode ultrapassar 20**; gastar menos é permitido (rascunho). Monstro/NPC sem essa regra.
- `foto_url`: URL do retrato (opcional). Contrato e evolução: [docs/tormenta/05-contrato-dados-ficha-json-e-api.md](../../../../docs/tormenta/05-contrato-dados-ficha-json-e-api.md).

## `ficha_json` (extensível)

Campos usados pelo frontend atual (podem crescer sem migration):

- `pericias`: `[{ nome, graduacao, outros, somente_treinado, penalidade_armadura }]`
- `talentos_texto`, `magias_texto`, `equipamento_texto`, `notas`
- `dinheiro`: `{ ts, tp, to }`, `pm_max`, `pm_atual`, `idiomas`
- `campanha`, `mestre`, `outros_jogadores`, `xp_atual`, `xp_proximo`
- `historia`, `personalidade`, `aparencia`

Levantamento de requisitos do jogo: [docs/tormenta/README.md](../../../../docs/tormenta/README.md).

## Frontend

`frontend/games/tormenta/pages/` — `dashboard.html`, `ficha-personagem.html`.
