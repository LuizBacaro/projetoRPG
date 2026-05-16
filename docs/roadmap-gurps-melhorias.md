# Roadmap — GURPS e melhorias operacionais (Arena TTRPG)

> **Norma de codigo:** [AGENTS.md](../AGENTS.md) e [arquitetura-camadas-solid.md](arquitetura-camadas-solid.md). Este ficheiro e **volatil** (checklists, ondas, issues); atualize ao fechar itens.

---

## 7. GURPS 4E — checklist de implementacao (ficha + arena)

**Fonte de requisitos:** skill [.cursor/skills/gurps-4e-requisitos-ficha-arena/SKILL.md](../.cursor/skills/gurps-4e-requisitos-ficha-arena/SKILL.md) (derivada do *Modulo Basico Lite* + *Personagens*, sem copiar texto dos PDFs).

**Legenda:** criterio objetivo de aceite; **Onda** = ordem sugerida (menor numero primeiro).

### Onda 0 — Decisao de produto (bloqueante)

| ID | Item | Aceite |
|----|------|--------|
| **G0.1** | Ordem na arena | Documentar: ordem padrao = **Velocidade basica** (desempate DX, depois aleatorio). Campo `iniciativa` vira derivado, override opcional, ou deprecado. |
| **G0.2** | Escopo de regras | “Lite primeiro”: combate e ficha minimos alinhados ao Lite; livro *Personagens* so em tickets explicitos (catalogos grandes). |

### Onda 1 — Ficha: derivacoes canonicas (backend + UI)

| ID | RF | Item | Aceite |
|----|-----|------|--------|
| **G1.1** | RF-F05 | Dano thr/swing por ST | Tabela Lite ST→GDP/BAL codificada; ficha e API expoem par (ex. `1d` / `2d-1`); opcionalmente persistir ou so calcular. |
| **G1.2** | RF-F06 | Esquiva | Esquiva = VB + 3 (fracao de VB ignorada na esquiva, conforme Lite); recalcular ao mudar HT/DX se VB mudar. |
| **G1.3** | RF-F02 | PV / PF base | Defaults: PV max = ST, PF max = HT quando sem modificadores; UI mostra coerencia com colunas existentes. |
| **G1.4** | RF-F03 | Von / Per | Defaults IQ; edicao continua permitida; documentar no OpenAPI/help da ficha. |
| **G1.5** | RF-F04 | VB e deslocamento | VB = (HT+DX)/4 sem arredondar a toa; deslocamento exibido como na regra escolhida (Lite); tooltip ou doc “como calculamos”. |

### Onda 2 — Resolucao (motor de jogo reutilizavel)

| ID | RF | Item | Aceite |
|----|-----|------|--------|
| **G2.1** | RF-R01 | Rolagem 3d6 | Funcao unica (front ou `shared` TS + testes; opcional endpoint dev): total, sucesso/falha vs NH, margem, regras 3–4 / 17–18 do Lite. |
| **G2.2** | RF-R02 | Nivel efetivo | API ou helper: `nh_base + soma(modificadores)` como alvo do 3d6. |
| **G2.3** | RF-R03 | Dado de dano | Parser `Nd+M`, rolar e retornar total; hook para RD depois. |

### Onda 3 — Arena GURPS (fluxo de combate Lite)

| ID | RF | Item | Aceite |
|----|-----|------|--------|
| **G3.1** | RF-A01 | Iniciativa / ordem | Ao iniciar combate, ordenar por VB desc.; persistir ordem no estado do combate; desempate DX depois regra G0.1. |
| **G3.2** | RF-A02 | Manobra por turno | Estado guarda manobra atual por combatente; troca so no turno; efeito em defesas conforme manobra (minimo: Fazer Nada, Ataque, Defesa Total). |
| **G3.3** | RF-A03 | Ataque → defesa → dano | Fluxo minimo: escolher alvo, rolar ataque (G2.1), defesa ativa do alvo, se falhar aplicar dano (G2.3) em `pvs_atual`. |
| **G3.4** | RF-A04 | Multiplas defesas | Penalidade cumulativa configuravel ou fixa Lite; documentar constante. |
| **G3.5** | RF-A05 | Postura | Minimo: em pe / agachado / deitado com mods de ataque/defesa/alvo/mov do Lite (tabela resumida na UI). |

### Onda 4 — Conteudo e ficha rica

| ID | RF | Item | Aceite |
|----|-----|------|--------|
| **G4.1** | RF-F09 | Combate sem armas | Soco/chute com dano derivado e NH minimo (DX ou pericia quando existir). |
| **G4.2** | RF-F10 / F11 | Defesas + equipamento | Aparar/Bloqueio ligados a pericia/escudo estruturado; RD de armadura no fluxo de dano. |
| **G4.3** | RF-F07 / F08 | Catalogo | Subconjunto **Lite** de pericias; V/D como lista + validacao de pre-requisitos (fase posterior ao Lite). |
| **G4.4** | RF-F12 | extras_json | Mapa documentado (README curto ou comentario no schema): o que migra para coluna quando estavel. |

### Onda 5 — Condicionais avancadas

| ID | RF | Item | Aceite |
|----|-----|------|--------|
| **G5.1** | RF-A06 | Fadiga em combate | Regras de esforco/surtos conforme mesa (apos PV/dano estavel). |
| **G5.2** | RF-A07 | Lesao / atordoamento / morte | Estados e recuperacao HT alinhados ao Lite; integrar com manobra Fazer Nada. |

### Andamento de implementacao (execucao)

- Concluidos: **G0.1**, **G0.2**, **G1.1**, **G1.2**, **G1.3**, **G1.4**, **G1.5**, **G2.1**, **G2.2**, **G2.3**, **G3.1**, **G3.2**, **G3.3**, **G3.4**, **G3.5**, **G4.1**, **G4.2**, **G4.3**, **G4.4**, **G5.1**, **G5.2**.
- Proximo recomendado: mapear a **Ficha Aprimorada** (PDF) para colunas SQL vs `extras_json` (abaixo); abrir ou sincronizar issues do §7.1 no GitHub/Notion, se ainda nao existirem. Refinos visuais pontuais na ficha/arena sao opcionais pos-checklist.

### Cruzamento com a “Ficha Aprimorada” (PDF no repo)

- Abrir `GURPS 4E - Ficha de Personagem (Aprimorada 1).pdf` e marcar cada bloco: **coluna SQL** | **extras_json** | **ainda nao existe**.
- Priorizar mover para colunas o que entrar em **G1**–**G3** (calculo e combate).

### Prompt rapido para agente

> Implementa o proximo item do **§7 GURPS** em [roadmap-gurps-melhorias.md](roadmap-gurps-melhorias.md), na ordem das ondas. Obedece `.cursor/skills/gurps-4e-requisitos-ficha-arena/SKILL.md`. Nao copiar texto dos PDFs. Preserva contratos `GurpsPersonagem*` e testes; migrations so quando necessario.

---

### 7.1 Mapeamento para issues (GitHub / Notion)

**Objetivo:** cada linha abaixo vira **uma issue** com o mesmo **ID** (`G0.1` … `G5.2`) no titulo, para rastreio cruzado com esta checklist.

#### Convencao

| Campo | Valor sugerido |
|--------|----------------|
| **Titulo** | `[GURPS G1.1] Dano thr/swing por ST (RF-F05)` — sempre `GURPS` + ID + nome curto + `(RF-…)` |
| **Labels** | `gurps`, `onda-N` (0–5), e uma de area: `ficha` \| `arena` \| `motor` \| `produto` \| `conteudo` |
| **Epico (milestone ou pai Notion)** | `GURPS — Onda 0 (decisoes)` … `GURPS — Onda 5 (avancado)` |
| **Corpo minimo** | Colar o bloco *template* no fim desta secao; preencher **Aceite** copiando da tabela da onda correspondente. |

#### Lista de issues (titulo pronto)

| ID | Titulo da issue | Labels (exemplo) | Depende de |
|----|-------------------|------------------|------------|
| G0.1 | `[GURPS G0.1] Ordem na arena: VB + desempates (RF-A01)` | `gurps`, `onda-0`, `produto`, `arena` | — |
| G0.2 | `[GURPS G0.2] Escopo: Lite primeiro; Personagens em tickets` | `gurps`, `onda-0`, `produto` | — |
| G1.1 | `[GURPS G1.1] Tabela ST → dano thr/swing na ficha e API (RF-F05)` | `gurps`, `onda-1`, `ficha`, `backend` | G0.2 |
| G1.2 | `[GURPS G1.2] Esquiva = VB+3; recalcular com HT/DX (RF-F06)` | `gurps`, `onda-1`, `ficha`, `backend` | G1.5 |
| G1.3 | `[GURPS G1.3] PV/PF max default ST/HT sem mods (RF-F02)` | `gurps`, `onda-1`, `ficha` | — |
| G1.4 | `[GURPS G1.4] Von/Per default IQ + doc OpenAPI/UI (RF-F03)` | `gurps`, `onda-1`, `ficha` | — |
| G1.5 | `[GURPS G1.5] VB (HT+DX)/4 e deslocamento Lite na UI (RF-F04)` | `gurps`, `onda-1`, `ficha` | — |
| G2.1 | `[GURPS G2.1] Motor rolagem 3d6 + margem + criticos Lite (RF-R01)` | `gurps`, `onda-2`, `motor` | — |
| G2.2 | `[GURPS G2.2] Nivel efetivo NH + modificadores (RF-R02)` | `gurps`, `onda-2`, `motor` | G2.1 |
| G2.3 | `[GURPS G2.3] Parser/rolo Nd+M e total de dano (RF-R03)` | `gurps`, `onda-2`, `motor` | — |
| G3.1 | `[GURPS G3.1] Ordenar combatentes por VB + desempate (RF-A01)` | `gurps`, `onda-3`, `arena` | G0.1, G1.5 |
| G3.2 | `[GURPS G3.2] Estado de manobra por turno (minimo Lite) (RF-A02)` | `gurps`, `onda-3`, `arena` | G3.1 |
| G3.3 | `[GURPS G3.3] Fluxo ataque → defesa → dano em PV (RF-A03)` | `gurps`, `onda-3`, `arena` | G2.1, G2.3, G3.2 |
| G3.4 | `[GURPS G3.4] Penalidade multiplas defesas (RF-A04)` | `gurps`, `onda-3`, `arena` | G3.3 |
| G3.5 | `[GURPS G3.5] Postura em pe/agachado/deitado + mods (RF-A05)` | `gurps`, `onda-3`, `arena` | G3.3 |
| G4.1 | `[GURPS G4.1] Combate sem armas soco/chute (RF-F09)` | `gurps`, `onda-4`, `ficha`, `arena` | G1.1, G2.x |
| G4.2 | `[GURPS G4.2] Aparar/bloqueio + RD armadura no dano (RF-F10/F11)` | `gurps`, `onda-4`, `ficha`, `arena` | G3.3 |
| G4.3 | `[GURPS G4.3] Catalogo Lite pericias + V/D e pre-reqs (RF-F07/F08)` | `gurps`, `onda-4`, `conteudo` | G0.2 |
| G4.4 | `[GURPS G4.4] Documentar extras_json e migracao p/ colunas (RF-F12)` | `gurps`, `onda-4`, `ficha`, `docs` | — |
| G5.1 | `[GURPS G5.1] Fadiga em combate esforco/surtos (RF-A06)` | `gurps`, `onda-5`, `arena` | G3.3 |
| G5.2 | `[GURPS G5.2] Lesao/atordoamento/morte + Fazer Nada (RF-A07)` | `gurps`, `onda-5`, `arena` | G3.2, G3.3 |

#### Template de corpo (GitHub ou Notion)

```markdown
## Contexto
Arena TTRPG — GURPS 4E (Lite primeiro). Ver skill `.cursor/skills/gurps-4e-requisitos-ficha-arena/SKILL.md`.

## ID
<!-- ex.: G1.1 -->

## Criterios de aceite
<!-- copiar da tabela da onda em §7 -->

## Fora de escopo
Nao copiar texto dos PDFs; nao expandir para regras fora do Lite sem ticket.

## Verificacao
- [ ] Testes ou smoke manual indicados no PR
- [ ] Contrato API / migracao se aplicavel
```

#### Criar no GitHub (local)

Com [GitHub CLI](https://cli.github.com/) autenticado:

```bash
gh issue create --title "[GURPS G1.1] …" --label "gurps,onda-1,ficha" --body-file issue-body.md
```

#### Notion

Criar uma **database de tarefas** (ou usar a existente): propriedades **ID** (texto `G1.1`), **Onda** (numero), **RF** (texto), **Estado**, **Depende** (relacao). Duplicar uma linha por issue usando a coluna **Titulo da issue** acima.

---

## 8. Roadmap de melhoria continua (4 frentes)

Objetivo deste bloco: manter um plano unico e rastreavel para estabilizar producao, reduzir latencia, acelerar novos jogos e preparar monetizacao sem comprometer dados.

### 8.1 Estabilidade (0 a 4 semanas)

**Meta:** remover incidentes de producao (500/CORS mascarado), padronizar checagens pos-deploy e aumentar seguranca operacional de banco.

#### Escopo imediato

- Deploy do backend com meta de diagnostico no `catalogo/lite-ficha`.
- Checagem manual em producao via Network para validar origem e contagens do catalogo.
- Rotina de backup Neon antes de seed/migration grande.
- Smoke pos-deploy com endpoints de saude e catalogo autenticado.
- Revisao de modo estrito multi-jogo e fluxo de token em producao.

#### Checklist de execucao

- [ ] Deploy contendo `meta.catalogo_listas_origem`, `meta.catalogo_listas_counts` e fallback seguro.
- [ ] Validar `GET /api/v1/gurps/personagens/catalogo/lite-ficha` em producao com token GURPS.
- [ ] Registrar evidencia (sem token) do trecho `meta` da resposta.
- [ ] Confirmar `GET /health/live` (startup/deploy) e `GET /health` (operacao continua).
- [ ] Antes de mudanca de schema/seed relevante: criar branch de backup no Neon + `pg_dump`.
- [ ] Validar `DATABASE_URL` de producao no Render apontando para branch correta no Neon.
- [ ] Revisar `MULTI_GAME_STRICT_MODE` e tratamento de 409 no front para nao falhar silenciosamente.

#### Criterio de pronto

- 7 dias sem erro 500 recorrente no catalogo GURPS em producao.
- Evidencia de `meta.catalogo_listas_origem` conhecida (`postgres` ou `arquivos_json`) com contagens coerentes.
- Procedimento de backup pre-mudanca documentado e repetivel.

### 8.2 Velocidade (paralelo, apos diagnostico)

**Meta:** reduzir tempo percebido de carregamento e latencia p95 dos endpoints mais acessados.

#### Escopo

- Avaliar plano pago no Render para reduzir cold start.
- Medir p95 antes/depois da mudanca de infraestrutura.
- Otimizar consultas e indices nos endpoints criticos.
- Introduzir cache curto para leituras idempotentes (catalogos), com invalidacao explicita.

#### Checklist de execucao

- [ ] Baseline de latencia (p50/p95/p99) para: grimorio, listas e personagem.
- [ ] Comparar baseline com ambiente apos upgrade de plano no Render.
- [ ] Levantar queries lentas e planos de execucao no Postgres.
- [ ] Criar/ajustar indices com rollback plan para cada alteracao.
- [ ] Implementar cache TTL curto em catalogo (`lite-ficha`) com chave por versao/origem.
- [ ] Definir gatilho de invalidacao (deploy, seed, alteracao de catalogo).

#### Criterio de pronto

- p95 reduzido de forma mensuravel nos tres endpoints criticos.
- Cold start fora do caminho critico de uso diario.
- Cache com invalidacao previsivel e sem inconsistencia funcional.

### 8.3 Novo jogo (medio prazo)

**Meta:** transformar o padrao atual em um pipeline replicavel por `game_slug`.

#### Escopo

- Contrato minimo por jogo (rotas, seeds, front, autenticacao por `game_slug`).
- Staging dedicado com branch de banco e deploy automatizado.
- Testes minimos de contrato por jogo, seguindo padrao GURPS catalogo.

#### Checklist de execucao

- [ ] Criar documento de contrato por `game_slug` (API, payloads, permissoes, seeds).
- [ ] Definir template de modulo de jogo (`api`, `services`, `repositories`, `schemas`, `catalogs`).
- [ ] Provisionar staging isolado (Render + Neon branch).
- [ ] Pipeline de deploy automatico para staging a cada merge em branch de integracao.
- [ ] Suite minima de contrato por jogo (health, autenticacao, catalogo/listas essenciais).

#### Criterio de pronto

- Onboarding de novo jogo com checklist unica e sem decisoes ad hoc.
- Staging validando mudancas antes de producao.
- Contratos minimos automatizados para evitar regressoes cross-game.

### 8.4 Monetizacao (apos estabilizacao)

**Meta:** habilitar receita com baixo risco tecnico e governanca de uso.

#### Escopo

- Planos/assinatura (Stripe ou equivalente) com feature flags.
- Limites por plano (campanhas, uploads, recursos premium).
- Observabilidade de uso para precificacao e evolucao do produto.

#### Checklist de execucao

- [ ] Definir planos, beneficios e limites por recurso.
- [ ] Implementar camada de feature flags por tenant/usuario/plano.
- [ ] Integrar cobranca (checkout, webhook, cancelamento, estado de assinatura).
- [ ] Aplicar limites tecnicos por plano com mensagens claras no front.
- [ ] Instrumentar eventos: login, criacao de ficha, inicio de combate, uso de uploads.
- [ ] Painel de metricas de adocao e custo por recurso.

#### Criterio de pronto

- Fluxo de cobranca auditavel de ponta a ponta.
- Limites aplicados de forma consistente entre backend e frontend.
- Dados de uso suficientes para iteracao de pricing.

### 8.5 Dependencias e ordem sugerida

1. Estabilidade (8.1) inicia imediatamente e bloqueia mudancas sensiveis em producao.
2. Velocidade (8.2) roda em paralelo apos o diagnostico inicial de estabilidade.
3. Novo jogo (8.3) depende de estabilidade operacional e contrato consolidado.
4. Monetizacao (8.4) inicia quando estabilidade e observabilidade minima estiverem maduras.

### 8.6 Proximo passo pratico (execucao curta)

Apos o proximo deploy com correcoes de catalogo:

1. Executar `GET /api/v1/gurps/personagens/catalogo/lite-ficha` em producao com token GURPS.
2. Copiar apenas o objeto `meta` (sem token) e anexar no registro operacional.
3. Classificar a causa operacional:
   - `catalogo_listas_origem = postgres`: foco em qualidade/latencia de consulta.
   - `catalogo_listas_origem = arquivos_json`: foco em migracao/seed/estado do banco.
4. Abrir tarefas derivadas da causa encontrada antes de avancar para outras frentes.

### 8.7 Backlog operacional (issues prontas)

**Objetivo:** transformar as 4 frentes em tarefas rastreaveis com ordem de execucao, prioridade e tamanho.

#### Convencao

- **ID:** `RM-EST-*` (Estabilidade), `RM-VEL-*` (Velocidade), `RM-NJG-*` (Novo jogo), `RM-MON-*` (Monetizacao).
- **Prioridade:** `P0` (urgente), `P1` (alta), `P2` (media), `P3` (baixa).
- **Estimativa:** `S` (ate 1 dia), `M` (2 a 4 dias), `L` (5+ dias).
- **Status inicial sugerido:** `Todo`.

#### Lista de issues (titulo pronto + execucao)

| ID | Titulo da issue | Frente | Prioridade | Estimativa | Depende de |
|----|------------------|--------|------------|------------|------------|
| RM-EST-01 | `[RM-EST-01] Deploy backend com meta de diagnostico no catalogo Lite` | Estabilidade | P0 | S | — |
| RM-EST-02 | `[RM-EST-02] Validar em producao o meta de catalogo/lite-ficha (Network)` | Estabilidade | P0 | S | RM-EST-01 |
| RM-EST-03 | `[RM-EST-03] Padronizar smoke pos-deploy (/health/live e /catalogo/lite-ficha)` | Estabilidade | P0 | S | RM-EST-01 |
| RM-EST-04 | `[RM-EST-04] Formalizar backup Neon pre-migration (branch + pg_dump)` | Estabilidade | P0 | M | — |
| RM-EST-05 | `[RM-EST-05] Revisar MULTI_GAME_STRICT_MODE e tratamento de 409 no front` | Estabilidade | P1 | M | RM-EST-01 |
| RM-EST-06 | `[RM-EST-06] Validar DATABASE_URL de producao e branch Neon ativo` | Estabilidade | P0 | S | — |
| RM-VEL-01 | `[RM-VEL-01] Coletar baseline de latencia p50/p95/p99 (grimorio/listas/personagem)` | Velocidade | P1 | M | RM-EST-02 |
| RM-VEL-02 | `[RM-VEL-02] Comparar p95 antes/depois de upgrade Render` | Velocidade | P1 | M | RM-VEL-01 |
| RM-VEL-03 | `[RM-VEL-03] Levantar queries lentas e plano de indices no Postgres` | Velocidade | P1 | M | RM-VEL-01 |
| RM-VEL-04 | `[RM-VEL-04] Implementar otimizacoes de indice/query nos endpoints criticos` | Velocidade | P1 | L | RM-VEL-03 |
| RM-VEL-05 | `[RM-VEL-05] Implementar cache TTL curto para catalogos com invalidacao explicita` | Velocidade | P2 | M | RM-EST-02 |
| RM-NJG-01 | `[RM-NJG-01] Definir contrato padrao por game_slug (rotas, seeds, front, auth)` | Novo jogo | P1 | M | RM-EST-03 |
| RM-NJG-02 | `[RM-NJG-02] Criar template de modulo de jogo reutilizavel` | Novo jogo | P2 | L | RM-NJG-01 |
| RM-NJG-03 | `[RM-NJG-03] Provisionar staging isolado (Render + Neon branch)` | Novo jogo | P1 | M | RM-EST-04 |
| RM-NJG-04 | `[RM-NJG-04] Automatizar deploy para staging por branch de integracao` | Novo jogo | P2 | M | RM-NJG-03 |
| RM-NJG-05 | `[RM-NJG-05] Criar testes minimos de contrato por jogo` | Novo jogo | P1 | L | RM-NJG-01 |
| RM-MON-01 | `[RM-MON-01] Definir catalogo de planos e limites por recurso` | Monetizacao | P2 | M | RM-EST-03 |
| RM-MON-02 | `[RM-MON-02] Implementar feature flags por plano/tenant` | Monetizacao | P2 | L | RM-MON-01 |
| RM-MON-03 | `[RM-MON-03] Integrar cobranca (checkout + webhook + estado de assinatura)` | Monetizacao | P2 | L | RM-MON-01 |
| RM-MON-04 | `[RM-MON-04] Aplicar limites tecnicos por plano no backend/frontend` | Monetizacao | P2 | L | RM-MON-02 |
| RM-MON-05 | `[RM-MON-05] Instrumentar eventos de uso para precificacao` | Monetizacao | P1 | M | RM-EST-03 |
| RM-MON-06 | `[RM-MON-06] Criar painel de metricas de adocao e custo por recurso` | Monetizacao | P2 | M | RM-MON-05 |

#### Sequencia sugerida (primeiras 2 semanas)

1. **Semana 1 (estabilidade):** `RM-EST-01`, `RM-EST-02`, `RM-EST-03`, `RM-EST-06`.
2. **Semana 1 (governanca de dados):** `RM-EST-04`.
3. **Semana 2 (hardening):** `RM-EST-05` + inicio de `RM-VEL-01`.
4. **Semana 2 (performance):** `RM-VEL-03` e decisao sobre `RM-VEL-02`.

#### Template curto de issue

```markdown
## Contexto
Relacionado ao roadmap §8 em [roadmap-gurps-melhorias.md](roadmap-gurps-melhorias.md).

## Objetivo
<!-- Descrever o resultado esperado da tarefa -->

## Escopo
- [ ] Item 1
- [ ] Item 2

## Criterios de aceite
- [ ] Criterio funcional validado
- [ ] Smoke/teste executado
- [ ] Evidencia anexada (logs/prints/JSON sem dados sensiveis)

## Dependencias
<!-- IDs: ex. RM-EST-01 -->
```
