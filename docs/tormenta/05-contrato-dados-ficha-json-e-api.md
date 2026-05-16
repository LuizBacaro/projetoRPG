# Contrato de dados — `ficha_json`, API e retrato

## Colunas SQL (`tormenta_personagens`)

| Coluna | Uso |
|--------|-----|
| Atributos `*_valor` | FOR, DES, CON, INT, SAB, CAR |
| `pv_max`, `pv_atual` | Pontos de vida |
| `pa_max`, `pa_atual` | Pontos de Magia (PM na UI; colunas `pa_*` no banco) |
| `ca`, `rd`, `nivel`, `iniciativa`, `deslocamento`, `tamanho` | Combate / exploracao |
| `fort_total`, `ref_total`, `von_total` | Resistências totais na ficha |
| `ficha_json` | Ver secção abaixo |
| `foto_url` | URL HTTPS do retrato (Cloudinary em produção, relativo `/uploads/...` em dev) — **nullable** |

## `ficha_json` — chaves usadas pelo frontend atual

Documentado também em `backend/app/games/tormenta/README.md`. Resumo:

- `origem`, `pericias[]`, `ataques[]`, `equipamentos[]`
- `defesa_detalhe`, `armadura_escudo_tabela`
- `talentos_texto`, `magias_texto`, `raca_origem_texto`
- `raca_tormenta_slug`, `raca_tormenta_mais2a`, `raca_tormenta_mais2b`, `raca_tormenta_livre` (raça MB + escolhas Humano/Lefou ou texto livre)
- `atributos_compra` — mapa `{ for, des, con, int, sab, car }` com valores-base 8–18 (compra por pontos; soma dos custos na tabela MB = **20**)
- `dinheiro`, `carga`, `idiomas`, `campanha`, `mestre`, `outros_jogadores`, `xp_atual`, `xp_proximo`
- `historia`, `personalidade`, `aparencia`, `notas`
- **Grimório / conjuração MB:** `tormenta_classe_mb_slug`, `tormenta_conjuracao_manual_mb`, `tormenta_nivel_conjurador_mb` (opcional), `tormenta_niveis_classe_mb` (opcional, lista `{slug, nivel}` — editável na ficha em «Multiclasse — classes conjuradoras» ou no JSON), `tormenta_grimorio_sessao_mb` (`pm_gastos_sessao`, `preparadas_anotacao` — lembretes de sessão)

Novas chaves devem ser **aditivas** (nunca remover silenciosamente) para compatibilidade com fichas já salvas.

**Compra por pontos (jogador):** ao criar ou atualizar via API, a soma dos custos dos seis atributos (8–18) deve ser **exatamente 20** pontos (MB). Monstro/NPC: sem essa regra.

### Evolução recomendada

1. **IDs de catálogo** em arrays paralelos (`poder_ids: number[]`) quando catálogos SQL existirem.
2. **Versão de schema** opcional: `ficha_json._schema_version: 1` para migrações automáticas futuras.

## API

- `POST/PATCH` aceitam `foto_url` como string opcional (comprimento máximo definido no schema Pydantic).
- Validação de URL pode ser fase posterior (formato básico ou allowlist de domínio).
- `GET /api/v1/tormenta/regras/atributos` — resposta `{ pontos_compra_iniciais, custos[], pericias[] }` (`pericias[].nome`, `atributo`, `somente_treinado`, `penalidade_armadura`). Espelha `data/atributos_compra_pontos.json` + `data/pericias_atributo_chave.json`. Fallback estático na ficha: `/games/tormenta/data/regras-atributos.json`.
- `GET /api/v1/tormenta/regras/racas` — raças MB (`slug`, `nome`, `ajustes`, `escolhe_duas_mais2`, `mod_car_fixo`, `tracos_resumo`, `idioma_racial_mb`), mais `idiomas_geral_mb` e `idiomas_tabela_mb` (tabela do livro). Fallback estático: `/games/tormenta/data/racas-mb.json`.
- `GET /api/v1/tormenta/regras/magias` — catálogo MB de magias (`q`, `circulo`, `tipo`, `escola`, paginação). Com `catalogo_por_classe_mb=true`, `classe_mb_slug` e `nivel_mb`, restringe ao **tipo de lista** (arcana/divina) e ao **círculo máximo** lançável naquele nível (MB; ver `magias_progressao_mb_t20.py`). Use `conjuracao_manual_mb=true` para ignorar essa restrição (multiclasse / mesa). Ver `docs/tormenta/grimorio-mb-mesa.md`.
- `GET /api/v1/tormenta/regras/conjuracao-preview` — CD base (10+mod), modificador da chave e PM máx. de conjuração MB (`classe_slug`, `nivel`, opcional `nivel_conjurador`, `for_valor`…`car_valor`). Inclui `magias_lista_tipo` e `magias_circulo_max` para alinhar o catálogo ao nível da classe.
- **Upload de ficheiro** (em vez de URL): reutilizar o padrão do hub D&D (`FileService` + Cloudinary) num endpoint dedicado Tormenta é trabalho futuro; até lá, URL absoluta ou caminho `/uploads/...` em dev.
