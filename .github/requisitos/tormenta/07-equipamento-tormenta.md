# FEATURE: Equipamento Tormenta 20 (Edição Jogo do Ano v1.3)

> **Fonte:** `Tormenta20-Edicao-Jogo-do-Ano-v1.3.pdf` — Cap. 3 **Equipamento p.138–164**; equipamento inicial p.140; Defesa p.106.

## Descrição

Catálogo de armas, armaduras, escudos, munições, itens gerais, itens superiores e serviços; integração com ficha (inventário, Defesa, penalidade de armadura, carga). Moeda padrão: **T$** (Tibar).

## Moeda (p.140)

| Moeda | Valor |
|-------|-------|
| **T$** (Tibar de prata) | Padrão — preços das tabelas |
| **TC** (Tibar de cobre) | 1 TC = T$ 0,1 |
| **TO** (Tibar de ouro) | 1 TO = T$ 10 |

Compra/venda: preço de tabela para comprar; vender pela **metade**. Barganha via Diplomacia (Mesa pode variar preço/disponibilidade).

## Equipamento inicial (p.140)

Personagens de **1º nível** recebem, além dos itens da **origem**:

| Item | Regra |
|------|-------|
| Mochila, saco de dormir, traje de viajante | Grátis (mochila não ocupa espaço) |
| Arma simples | À escolha |
| Arma marcial | Se proficiente em armas marciais |
| Armadura | Couro, couro batido ou gibão de peles; **brunea** se proficiente em armaduras pesadas |
| Escudo leve | Se proficiente em escudos |
| Exceção | **Arcanistas** começam **sem armadura** |
| Dinheiro | **T$ 4d6** |

Personagens acima do 1º nível: **Tabela 3-1** (dinheiro inicial por nível).

## Limites de uso (p.141)

| Tipo | Limite |
|------|--------|
| **Empunhados** | Máx. 2 (uma mão cada) — armas, escudos, tochas, varinhas, etc. |
| **Vestidos** | Máx. **4** itens com benefício mecânico simultâneo; 5º não aplica bônus até remover outro |
| Roupa cosmética | Traje de viajante etc. não conta no limite |

Vestir/despir = ação de movimento; guardar = ação de movimento; largar = ação livre.

## Carga — espaços (p.141)

| Regra | Valor |
|-------|-------|
| Limite base | **10 + 2 × FOR** (FOR negativa: −1 espaço por ponto) |
| Sobrecarga | Acima do limite: penalidade de armadura **−5**, deslocamento **−3 m** |
| Máximo absoluto | **2×** o limite (ex.: FOR 2 → 14 normal, até 28 sobrecarregado, não passa de 28) |

### Ocupação por item

| Categoria | Espaços |
|-----------|---------|
| Padrão | 1 |
| Leve/pequeno (poções, pergaminhos, alquímicos) | ½ (dois = 1) |
| Duas mãos, armadura leve, escudo pesado, criatura Minúscula | 2 |
| Armadura pesada, criatura Pequena, barril/baú | 5 |
| Criatura Média, item extremamente pesado | 10 |
| Moedas | 1 espaço por **1.000** moedas (qualquer tipo) |

Recipientes que só carregam outros itens (bainha da espada) não ocupam espaço; bandoleira de poções **ocupa**.

## Armas (p.142–151)

### Classificação

| Eixo | Valores |
|------|---------|
| Proficiência | Simples (todos), marciais, exóticas, de fogo |
| Propósito | Corpo a corpo (Luta + FOR no dano) ou à distância (Pontaria) |
| Empunhadura | Leve, uma mão, duas mãos |
| Distância | Arremesso (FOR no dano) ou disparo (sem atributo no dano; arco longo e funda somam FOR) |

**Não proficiente:** −5 no ataque. Todos proficientes em desarmado e armas naturais.

### Crítico e alcance

- **20 natural** = crítico: dados de dano ×2 (bônus fixos e dados extras não multiplicam).
- Margens 19/18 e multiplicadores ×3/×4 conforme arma (Tabela 3-3).
- Alcance curto/médio/longo: sem penalidade no alcance; até **2×** alcance com **−5** no ataque.

### Tamanho (cross-ref p.106 / Tabela 3-2)

Armas para criaturas Minúsculas/Grandes/Colossais alteram passo de dano; usar arma ±1 categoria de tamanho: **−5** ataque e ±1 espaço.

### Habilidades de arma (metadados no catálogo)

Adaptável, Ágil, Alongada, Desbalanceada, Dupla, Versátil — efeitos mecânicos no livro p.143; persistir flags no JSON, não texto longo.

## Armaduras e escudos (p.152–153, Tabela 3-5)

**Defesa = 10 + DES + bônus armadura + bônus escudo** (armadura pesada: **não** aplica DES; desloc. **−3 m**; vestir/remover 5 min; dormir de armadura pesada = fatigado).

| Tipo | Exemplos (bônus Defesa / penalidade / espaços) |
|------|------------------------------------------------|
| Leves | Acolchoada +1/0/2 … Couraça +5/−4/2 |
| Pesadas | Brunea +5/−2/5 … Completa +10/−5/5 |
| Escudos | Leve +1/−1/1; Pesado +2/−2/2 |

Penalidade de armadura aplica em **Acrobacia, Furtividade, Ladinagem** e natação (Atletismo); armadura + escudo **acumulam**. Não proficiente: penalidade em **todas** perícias For/Des.

Ataque com escudo (prof. armas marciais): dano 1d4 (leve) ou 1d6 (pesado); perde bônus de Defesa até o próximo turno.

## Itens superiores (p.164+, Tabelas 3-7 e 3-8)

- **1 a 4 melhorias** por item (armas, armaduras, escudos, ferramentas, vestuário, esotéricos).
- Cada melhoria: +T$ 300 / +3.000 / +9.000 / +18.000 (Tabela 3-7); mesma melhoria **1×** por item.
- Exemplos: Ajustada (−1 penalidade armadura), Certeira (+1 ataque), Delicada, Canalizador (+1 PM máx. em magia), etc. — lista completa na Tabela 3-8.

Inventor e classes com itens superiores: cross-ref `03-classes-tormenta.md`.

## Tabelas do livro (referência — não replicar no repo)

| Tabela | Conteúdo | p. |
|--------|----------|-----|
| 3-1 | Dinheiro inicial por nível | 140 |
| 3-2 | Dano de armas por tamanho | 143 |
| 3-3 | Armas (preço, dano, crítico, alcance, tipo, espaços) | 143–145 |
| 3-4 | Munições | 151 |
| 3-5 | Armaduras e escudos | 152 |
| 3-6 | Itens gerais / serviços | 155+ |
| 3-7 | Preço de melhorias | 164 |
| 3-8 | Lista de melhorias | 164+ |

## Requisitos funcionais

| ID | Requisito | Prioridade |
|----|-----------|------------|
| RF-T07a | Catálogo `equipamentos_mb_catalogo.json` alinhado v1.3 Tabelas 3-3 e 3-5 | **Parcial** | Overlay armas + nomes sincronizados no catálogo de equipamentos |
| RF-T07b | API `GET /tormenta/regras/equipamentos` | P0 |
| RF-T07c | Modal equipamentos na ficha + vínculo SQL | P0 |
| RF-T07d | **Defesa** = 10 + DES + armadura + escudo; armadura pesada sem DES e −3 m | P0 |
| RF-T07e | Penalidade de armadura em perícias For/Des conforme item equipado | P1 |
| RF-T07f | Carga: limite 10+2×FOR, sobrecarga, ocupação por espaços | P2 |
| RF-T07g | Equipamento inicial na criação (passo 7 wizard / p.140) + itens de origem | P1 |
| RF-T07h | Metadados de arma: proficiência, dano, crítico, alcance, habilidades | **Parcial** | Modal Ataques + overlay; flags Adaptável/Ágil… ainda P1 |
| RF-T07i | Itens superiores / melhorias (metadados + remissão Tabela 3-8) | **Parcial** | JSON + `GET /itens-superiores` + UI no modal de ataques (MVP mods explícitos) |

## Estado de implementação

| Item | Estado | Notas |
|------|--------|-------|
| Catálogo + API equipamentos | **Feito** | Base MB; revisão stats v1.3 pendente |
| UI modal equipamentos na ficha | **Feito** | Vínculo SQL `tormenta_personagem_equipamentos` |
| **Itens de origem na criação v1.3** | **Feito** | `origens_itens_v13.json` + sync SQL na criação |
| **Kit inicial wizard (p.140)** | **Feito** | Passo 7 do wizard; pulado se nível > 1 |
| Sync automático origem + kit → SQL | **Feito** | `equipamentos_ficha_v13_t20.py`; notas `auto:v13:origem:*` / `auto:v13:kit:*` |
| API opções do kit | **Feito** | `GET /tormenta/regras/kit-inicial?tormenta_classe_mb_slug=` |
| Arcanista sem armadura no kit | **Feito** | `sem_armadura` em `kit_inicial_v13_t20.py` |
| T$ 4d6 no wizard | **Feito** | Botão «Rolar T$ 4d6»; persiste em `ficha_json.dinheiro` |
| Defesa v1.3 (valor DES, armadura pesada sem DES) | **Feito** | `defesa_t20.py` (`defesa_total_v13`); ficha `t20CalcularCaTotal()` |
| Penalidade armadura por perícia | **Feito** | `penalidade_armadura_t20.py`; ficha + rolador v1.3; proficiência For/Des (RF-T07e-1) |
| Carga / espaços | **Feito** | `carga_t20.py`, API `carga-preview`, ficha v1.3 |
| Revisão preços/stats catálogo v1.3 | **Feito** | Tabela 3-3 core (~56 itens); legacy MB documentado (Cajado, Estilingue, Wakizashi, mangual, martelo leve, arco composto) |
| Modal Ataques (catálogo + inventário) | **Feito** | `modalAtaquesTormenta` + `t20-ataques-modal.js` |
| Itens superiores / materiais (RF-T07i MVP) | **Feito** | `itens_superiores_v13.json` + `GET /tormenta/regras/itens-superiores` |

## Implementação — criação v1.3 (dashboard)

Wizard de 8 passos (`t20-dashboard-wizard-v13.js`):

| Passo | Conteúdo equipamento |
|-------|----------------------|
| 4 | Origem — itens fixos da origem (catálogo) + escolhas (`origem_itens_escolha`) |
| 7 | Kit inicial — arma simples*, marcial/armadura/escudo conforme classe; T$ 4d6 |
| 8 | Revisão — checklist inclui kit quando nível = 1 |

\* Obrigatório no 1º nível. Se **nível > 1**, o passo 7 é **pulado** (sem kit automático).

### Payload na criação (`ficha_json`)

| Campo | Uso |
|-------|-----|
| `origem_slug` | Resolve itens via `resolver_itens_origem_v13()` |
| `origem_itens_escolha` | Escolhas de itens variantes (ex.: tipo de traje) |
| `kit_inicial_v13` | `{ arma_simples, arma_marcial?, armadura?, escudo, dinheiro_pp? }` |
| `dinheiro` | `{ pc, pp, po, pl }` — preenchido com T$ rolado no wizard |

### Backend (sync na criação)

1. `PersonagemService.criar()` → `_sincronizar_equipamentos_v13()`
2. `listar_equipamentos_sync_v13()` monta lista: itens origem + itens kit
3. `TormentaPersonagemEquipamentosService.sincronizar_equipamentos_automaticos_v13()` upsert/remove por nota `auto:v13:*`

Itens fixos do kit (sempre adicionados quando há `kit_inicial_v13`): **Mochila**, **Saco de dormir**, **Roupas de viajante**.

### Testes

- Testes: `backend/tests/test_tormenta_equipamentos_v13.py` — origem, kit, sync SQL, opções por classe
- Testes: `backend/tests/test_tormenta_carga_v13.py` — limite FOR, ocupação, sobrecarga
- Carga: `backend/app/games/tormenta/rules/carga_t20.py`, `frontend/games/tormenta/js/t20-carga-v13.js`
- API carga: `POST /api/v1/tormenta/regras/carga-preview`

## Gap código

- Backend pode usar nomenclatura ou valores do **MB** no catálogo geral; revisão Tabelas 3-3 e 3-5 v1.3 — **Feito** para armas core + legacy MB documentado (**RF-T07a-1**).
- ~~Defesa na ficha (valor DES; pesada sem DES)~~ — **Feito** (`defesa_t20.py`, `t20-regra-versao.js`, ficha).
- Penalidade de armadura em perícias For/Des: integração completa com item equipado — **Feito** (RF-T07e / RF-T04d); proficiência armadura em **todas** For/Des — **Feito** (RF-T07e-1).
- Carga v1.3: motor em `rules/carga_t20.py` — **Feito** (RF-T07f).
- Personagens **acima do 1º nível**: Tabela 3-1 (dinheiro por nível) — **Feito** (RF-T07g-1).
- Modal equipamentos: exibir espaços/proficiência v1.3 — **Feito** (RF-T07a-2).
- Limite 4 vestidos / 2 empunhados (p.141) — **Feito** (RF-T07h-1; escudos + armas ⚔️ marcadas em Ataques).
- Arena: CA com armaduras equipadas — **Feito** (RF-T07d-1: `ca_efetiva_personagem`, combate Tormenta).

Backlog central: `docs/tormenta/03-requisitos-funcionais-backlog.md` (secção **Backlog v1.3**).

## Critérios de aceite

- Item equipado altera Defesa e penalidade conforme metadados v1.3.
- Arma não proficiente reflete −5 (quando combate implementar ataque).
- Catálogo `_meta.fonte` aponta v1.3 p.142–164.
- Sem tabelas completas de preço/dano no repositório.
- **Criação v1.3:** personagem nv 1 criado pelo wizard sai com itens de origem + kit p.140 em SQL (notas `auto:v13:*`), salvo escolhas explícitas no passo 7.
- **Arcanista nv 1:** kit sem armadura; demais opções conforme proficiências da classe.

## Referência

- Catálogo geral: `backend/app/games/tormenta/data/equipamentos_mb_catalogo.json`
- Itens por origem: `backend/app/games/tormenta/data/origens_itens_v13.json`
- Kit p.140: `backend/app/games/tormenta/rules/kit_inicial_v13_t20.py`
- Sync ficha → SQL: `backend/app/games/tormenta/rules/equipamentos_ficha_v13_t20.py`
- Serviço: `backend/app/games/tormenta/services/personagem_equipamentos_service.py`
- Penalidade armadura: `backend/app/games/tormenta/rules/penalidade_armadura_t20.py`, `proficiencia_armadura_t20.py`, `frontend/games/tormenta/js/t20-penalidade-armadura.js`
- Limites vestido/empunhado: `limites_equipamento_v13_t20.py`, `t20-limites-equipamento-v13.js`
- API kit: `GET /api/v1/tormenta/regras/kit-inicial`
- Skill: `tormenta-20-arena-arquitetura-e-regras`
- Cross-ref origens: `09-origens-divindades-tormenta.md`
