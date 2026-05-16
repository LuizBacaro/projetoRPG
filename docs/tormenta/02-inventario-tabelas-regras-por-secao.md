# Inventário de tabelas e regras (por secção)

Legenda de **Tipo**:

- `formula` — expressão fixa no código (não reproduz texto do livro).
- `lookup_json` — tabela chave→valor em `docs/tormenta/tabelas/*.json` (preenchimento manual a partir do livro).
- `catalogo_db` — tabelas SQL + API de listagem (roadmap).
- `texto_livre` — jogador/mestre preenche na ficha.
- `regra_motor` — serviço backend que aplica regra complexa (futuro).

**Página:** preencher com o teu livro; “(pedido)” = referência que enviaste neste chat.

| ID | Nome (como no livro ou sumário) | Página (confirmar) | Tipo | Artefacto alvo | Estado |
|----|----------------------------------|--------------------|------|------------------|--------|
| T01 | Modificadores de Habilidade | **6 (pedido)** | `formula` / **faixas T20** | `modificador_atributo_t20` em `backend/app/games/tormenta/rules/atributos_t20.py` + ficha | **Feito** (substituiu d20) |
| T02 | Custo de Valores de Habilidade | **7 (pedido)** | `lookup_json` | `backend/app/games/tormenta/data/atributos_compra_pontos.json` + UI “pontos gastos” | **Feito** (JSON + soma na ficha) |
| T03 | Atributos — valor mínimo/máximo na criação | *livro* | `regra_motor` | Validação create/patch | Pendente |
| T04 | Perícias — lista, atributo-chave, somente treinada e penalidade de armadura | *livro* | `lookup_json` + `GET /tormenta/regras/atributos` | `pericias_atributo_chave.json` + ficha | **Feito** (API + tabela; mods; ✱ e Arm. pré-marcados) |
| T05 | Perícias — CD base / situações | *livro* | `lookup_json` ou `regra_motor` | Ajuda / calculadora | Pendente |
| T06 | Origens — lista e poderes | *livro* | `catalogo_db` | `tormenta_origens` (futuro) | Texto livre |
| T07 | Raças — traços e poderes | *livro* | `catalogo_db` | `tormenta_racas` (futuro) | Texto livre |
| T08 | Classes — PV/PM iniciais, perícias e proficiências | *livro* | `catalogo_db` + `lookup_json` | Tabelas de classe | Parcial |
| T09 | Progressão por nível (classe) | *livro* | `catalogo_db` | `tormenta_progressao_classe` (futuro) | Pendente |
| T10 | Poderes (talentos) — gerais e de classe | *livro* | `catalogo_db` | Espelhar padrão D&D `talentos` | Texto / roadmap |
| T11 | Magias — lista por círculo e aprendizagem | *livro* | `catalogo_db` | Espelhar padrão `magias` | Texto / roadmap |
| T12 | Equipamento — armas, armaduras, itens | *livro* | `catalogo_db` | Espelhar `equipamentos` | Parcial na ficha |
| T13 | Carga e limites | *livro* | `formula` + `lookup_json` | `ficha_json.carga` | Campos existentes |
| T14 | Defesa / CA — composição | *livro* | `texto_livre` + `formula` | `ficha_json.defesa_detalhe` | Parcial |
| T15 | Ataques — bônus, dano, crítico | *livro* | `texto_livre` | `ficha_json.ataques` | Parcial |
| T16 | Resistências (Fort/Ref/Von) | *livro* | `formula` + colunas SQL | `fort_total`, … | Manual na ficha |
| T17 | Iniciativa | *livro* | `formula` | Coluna `iniciativa` | Manual |
| T18 | Pontos de vida e mana | *livro* | `regra_motor` | `pv_*`, `pa_*` | Parcial |
| T19 | Condições | *livro* | `catalogo_db` | Futuro combate | Não iniciado |
| T20 | Níveis de desafio / encontros | *livro* | `catalogo_db` | Mestre / futuro | Não iniciado |
| T21 | Divindades e obrigações | *livro* p.120–126 | `lookup_json` + coluna SQL | `GET /tormenta/regras/identidade-mb` → `divindades[].slug` + `rotulo`; combo grava `rotulo` em `divindade` | Combo MB (Os Vinte + slug) |
| T22 | Idiomas | *livro* | `catalogo_db` | `ficha_json.idiomas` | Texto |
| T23 | Alinhamento / tendência | *livro* p.116–119 | `lookup_json` + coluna SQL | `GET /tormenta/regras/identidade-mb` → combo `tendencia`; valor em `tendencia` | Combo MB (9 alinhamentos) |
| T24 | Moedas (T$, etc.) | *livro* | `texto_livre` | `ficha_json.dinheiro` | Existe |
| T25 | XP e níveis | *livro* | `lookup_json` | Tabela XP por nível | Campos texto XP |
| T26 | Planilha oficial (papel) | 304–305 (comentário no model) | `referência` | UI `ficha-personagem.html` | Contínuo |

## Anexo — blocos típicos do livro para classificar

Ao folhear, associe cada bloco a um novo **ID** (T27+) na tabela principal ou marque aqui até migrar.

| Bloco (nome aproximado no sumário) | Notas |
|-----------------------------------|--------|
| Tamanhos e alcances | Afeta `tamanho`, armas, magias |
| Tipos de dano | Ataques, resistências |
| Ações na rodada | Combate futuro |
| Morrer / estabilizar / cura | PV |
| Ambiente, clima, visão | Mesa |
| Doenças, venenos | Condições / saves |
| Itens mágicos (raridade) | Catálogo futuro |
| Criaturas / ND | Monstros NPC |

## Como estender este inventário

1. Percorrer o **sumário** do livro capítulo a capítulo.
2. Para cada **tabela** ou **bloco de regra** numerada, acrescentar uma linha (novo ID).
3. Marcar **Estado** e abrir issue/RF em `03-requisitos-funcionais-backlog.md` quando for para implementação.
