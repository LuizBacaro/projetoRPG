# `backend/app/games/tormenta/` — Tormenta 20

Stack vertical da ficha **Tormenta 20 Edição Jogo do Ano v1.3** (cadastro digital, CRUD).
O Módulo Básico (MB) permanece só como legado de compatibilidade em alguns JSON/`regra_versao=mb`.

**Fonte canónica de magias e poderes:** `livros/Tormenta20-Edicao-Jogo-do-Ano-v1.3.pdf`
(metadados em `data/magias_mb_catalogo.json` e `data/talentos_mb_catalogo.json`).
Ver `data/README.md`. Pipelines: `backend/scripts/build_magias_t20_v13_from_pdf.py`,
`backend/scripts/build_poderes_t20_v13_overlay.py`.

## Regras de atributos (T20)

- **Modificadores** (faixas), **compra por pontos** (8–18, 20 pts) e **rolagem 4d6** (reroll MB): `app.games.tormenta.rules.atributos_t20` + dados `app/games/tormenta/data/atributos_compra_pontos.json`; `ficha_json.metodo_geracao_atributos` (`compra_pontos` | `4d6`).
- API: `GET /tormenta/regras/atributos`, `POST /tormenta/regras/gerar-atributos`.
- Testes: `tests/test_tormenta_atributos_t20.py`.
- A ficha web espelha a mesma lógica em JS (`t20-atributos-geracao.js` + dashboard/ficha) — alterações na tabela devem atualizar **JSON + Python + JS**.

## API

- `GET/POST /api/v1/tormenta/personagens`
- `GET/PATCH/DELETE /api/v1/tormenta/personagens/{id}` — o `GET` por id inclui `talentos` (tabelas SQL, paridade com D&D 3.5).
- Talentos do personagem (catálogo `tormenta_talentos` + vínculo `tormenta_talentos_personagem`):
  - `GET /api/v1/tormenta/personagens/{id}/talentos`
  - `POST /api/v1/tormenta/personagens/{id}/talentos` — corpo `{ "talento_id": n }` **ou** `{ "nome": "..." }` (cria entrada de catálogo se não existir, `origem_catalogo_mb=false`).
  - `DELETE /api/v1/tormenta/personagens/{id}/talentos/{vinculo_id}`
- **Magias (grimório / conhecidas / preparadas)** — vínculos por `magia_slug` do catálogo `magias_mb_catalogo.json`; tabela `tormenta_magias_personagem`:
  - `GET /api/v1/tormenta/personagens/{id}/magias`
  - `POST /api/v1/tormenta/personagens/{id}/magias` — corpo `{ "magia_slug": "...", "papel": "grimorio" | "conhecida" | "preparada", "notas"?: "..." }`
  - `DELETE /api/v1/tormenta/personagens/{id}/magias/{vinculo_id}`
  - O `GET` por id do personagem inclui `magias` com metadados enriquecidos (nome, círculo, tipo, escola) quando o slug existe no catálogo.
  - `POST /api/v1/tormenta/personagens/{id}/talentos/migrar-do-json` — importa `ficha_json.talentos_mb_lista` para as tabelas (idempotente para duplicados).
- `GET /api/v1/tormenta/regras/racas` — raças MB com `ajustes`, `escolhe_duas_mais2`, `mod_car_fixo` (Lefou), `tracos_resumo`, `idioma_racial_mb`; inclui `idiomas_geral_mb` e `idiomas_tabela_mb` (Cap. 2 MB).
- `GET /api/v1/tormenta/regras/identidade-mb` — tendências (alinhamento, MB p.116–119) e divindades com **`slug` + `rotulo`** (Os Vinte, MB p.120–126); o personagem guarda só o `rotulo` em `divindade` (`tendencias_divindades_mb.json`).
- `GET /api/v1/tormenta/regras/magias` — catálogo **v1.3** (**metadados**: `slug`, `circulo` 1–5, `tipo` arcana/divina, `escola`, etc.); dados em `data/magias_mb_catalogo.json` (legado MB em `magias_mb_catalogo.legacy_mb.json`).
- `GET /api/v1/tormenta/regras/conjuracao-mb?regra_versao=v13` — **habilidade-chave** e **PM**; custo por círculo **Tabela 4-1** (1/3/6/10/15); motor em `rules/conjuracao_t20.py`.
- `GET /api/v1/tormenta/regras/tracos-raciais-preview?slug=` — bônus mecânicos raciais (`tracos_mecanicos_mb.json`).
- `GET /api/v1/tormenta/regras/pericias` — DCs padrão; `POST .../pericias/calcular-bonus` e `POST .../pericias/rolar`.
- `POST /api/v1/tormenta/personagens/{id}/magias/lancar` — debita PM (`pa_atual`) ao lançar magia MB; regista concentração em `ficha_json.tormenta_grimorio_sessao_mb` quando a duração MB exige.
- `POST /api/v1/tormenta/personagens/{id}/magias/migrar-do-json` — sincroniza lista de magias em texto (`magias_texto`) para vínculos SQL (chamado automaticamente ao abrir o grimório).
- `POST /api/v1/tormenta/personagens/{id}/magias/encerrar-concentracao` — remove concentração ativa da sessão.
- `POST /api/v1/tormenta/combate/rolar-iniciativa|rolar-ataque|rolar-dano` — rolagens na arena (mestre/admin); dano aplicado dispara teste de concentração (CD 10 + dano).
- `POST /api/v1/tormenta/combate/testar-resistencia-magia` — teste automático Fort/Ref/Von vs CD (10 + círculo + mod. chave) com bônus RM +4/+8.

**Catálogos SQL (RF-T20–T23):** mantidos em JSON versionado + API `/regras/*`; migração para tabelas SQL só se houver CRUD administrativo ou consultas pesadas (decisão documentada no skill Tormenta).

Guard: `requer_game_tormenta` (JWT `game_slug=tormenta` em modo estrito).

## Colunas principais

- Atributos na compra por pontos: fichas **tipo jogador** usam `ficha_json.atributos_compra` quando presente (valores-base 8–18); senão os seis atributos do modelo. O custo total na tabela MB deve ser **exatamente 20** pontos (nem menos nem mais). Monstro/NPC sem essa regra.
- `foto_url`: URL do retrato (opcional). Contrato e evolução: [docs/tormenta/05-contrato-dados-ficha-json-e-api.md](../../../../docs/tormenta/05-contrato-dados-ficha-json-e-api.md).

## `ficha_json` (extensível)

Campos usados pelo frontend atual (podem crescer sem migration):

- `pericias`: `[{ nome, graduacao, outros, somente_treinado, penalidade_armadura }]`
- `talentos_mb_lista`: `[{ nome }]` (ficha web); espelho canónico em SQL via rotas de talentos acima + migração.
- `talentos_texto`, `magias_texto`, `equipamento_texto`, `notas`
- `dinheiro`: `{ ts, tp, to }`, `pm_max`, `pm_atual`, `idiomas`
- `campanha`, `mestre`, `outros_jogadores`, `xp_atual`, `xp_proximo`
- `historia`, `personalidade`, `aparencia`
- `ameaca`: metadados de NPC/monstro (ND, papel, bloco override) — ver RF-13 e `rules/ameaca_bloco_t20.py`; endpoints `GET .../bloco-ameaca` e `POST .../converter-ameaca`

Levantamento de requisitos do jogo: [docs/tormenta/README.md](../../../../docs/tormenta/README.md).

## Frontend

`frontend/games/tormenta/pages/` — `dashboard.html`, `ficha-personagem.html` (compra MB **20 pontos exatos** para tipo **jogador** na API e na UI; **Exportar / Importar JSON** da ficha para backup local).

## Catálogos e regras MB (fonte única)

- **Tabelas de regra e listagens de catálogo** (raças, classes, equipamentos MB, talentos MB enriquecidos, **tendências e divindades** (`tendencias_divindades_mb.json`), perícias, custos de atributos, etc.) vivem em `app/games/tormenta/data/*.json` e são expostas por **`GET /api/v1/tormenta/regras/*`**.
- **Não duplicar** esses JSON em `frontend/games/tormenta/data/`: a ficha autenticada consome a API (`TormentaRegrasService`); uma fonte evita divergência e dispensa migração por linha de livro.
- **Dados por personagem** (ficha, vínculos a talentos/equipamentos/consumíveis) continuam no **Postgres** — ver rotas em secção API acima.
- Guia para agentes e manutenção: [`.cursor/skills/tormenta-20-arena-arquitetura-e-regras/SKILL.md`](../../../../.cursor/skills/tormenta-20-arena-arquitetura-e-regras/SKILL.md).
