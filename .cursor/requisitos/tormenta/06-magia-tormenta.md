# FEATURE: Magia Tormenta 20 (Edição Jogo do Ano v1.3)

> **Fonte:** `Tormenta20-Edicao-Jogo-do-Ano-v1.3.pdf` — Cap. 4 p.168–178; Arcanista p.36–39; PM/habilidades p.224+.  
> **Não usar** slots 0–9 do d20. Recurso = **PM (Pontos de Mana)**.

## Descrição

Magias arcanas ou divinas, círculos 1º–5º, lançamento gasta **PM** conforme Tabela 4-1. Conjuradores: **Arcanista**, **Bardo**, **Clérigo**, **Druida** (+ **Paladino** / **Caçador** conforme classe). Grimório SQL + catálogo JSON.

## PM e custo de magias

| Recurso | Regra |
|---------|--------|
| Nome no livro | **Pontos de Mana (PM)** — mesmo pool de poderes/habilidades |
| Campos legado Arena | `pa_atual` / `pa_max` (= PM) |

**Tabela 4-1 — Custo de magias (p.170):**

| Círculo | PM |
|---------|-----|
| 1º | **1** |
| 2º | **3** |
| 3º | **6** |
| 4º | **10** |
| 5º | **15** |

> **Não** usar regra MB «círculo C = C PM». Backend `custo_pm_preparar_ou_lancar_magia(circulo)` retorna `circulo` — **incorreto para v1.3**.

**Truque (p.170):** aprimoramento que reduz custo da magia a **0 PM** (não é círculo 0 separado).

## Atributo-chave e CD (p.170)

| Tipo / classe | Atributo-chave |
|---------------|----------------|
| Bruxo, Mago (arcanista) | **Inteligência** |
| Feiticeiro, Bardo | **Carisma** |
| Clérigo, Druida | **Sabedoria** |

**CD resistência** = **10 + ⌊nível/2⌋ + atributo-chave**  
(ex.: feiticeira 8º, CAR 5 → CD **19**).

## Arcanista — três caminhos (p.36–39)

Classe única que substitui Mago + Feiticeiro do MB.

| Caminho | Conjuração | Notas |
|---------|------------|--------|
| **Bruxo** | Via **foco**; Misticismo se sem foco | PM 6/nível (Tabela 1-3) |
| **Mago** | **Grimório**; memoriza metade das conhecidas | Preparação |
| **Feiticeiro** | **Espontâneo**; linhagens (p.39) | Conhecidas por nível |

Bardo: arcano espontâneo (CAR). Clérigo/Druida: divino (SAB), devoção.

## Regras de lançamento (p.170+)

| Regra | Resumo |
|-------|--------|
| Gestos e palavras | Mãos livres; amordaçado → não lança |
| Concentração | Teste **Vontade** se condição ruim/terrível (CD 15/20 + custo PM da magia) |
| Armadura + magia arcana | Teste **Misticismo** CD 20 + custo PM (+ penalidade armadura) |
| Aprimoramentos | Gasto extra de PM; limite p.224 |
| Listas | Arcanas p.174+; divinas p.176+; descrições p.178+ (sem texto longo no repo) |

## Modos por classe (v1.3)

| Padrão | Classes |
|--------|---------|
| Grimório / preparação | Arcanista (**Mago**), Clérigo, Druida |
| Espontâneo / conhecidas | Arcanista (**Feiticeiro**), Bardo |
| Foco | Arcanista (**Bruxo**) |
| Divino por devoção | Clérigo, Paladino (parcial) |

> Migrar `conjuracao_classe_mb.json`: sair mago/feiticeiro/ranger → **arcanista** (+ caminho), **caçador**.

## Dados e API

- `conjuracao_classe_mb.json` → classes v1.3 + caminho arcanista
- `magias_mb_catalogo.json`, `GET /tormenta/regras/magias`
- `tormenta_magias_personagem`, `/personagens/{id}/magias`, `/lancar`
- `grimorio_conjuracao_t20.py` — papéis grimório / conhecida / preparada / foco

## Requisitos funcionais

| ID | Requisito | Prioridade |
|----|-----------|------------|
| RF-T06a | Custo PM **1/3/6/10/15** por círculo (Tabela 4-1) | P0 |
| RF-T06b | CD = 10 + ⌊nível/2⌋ + atributo-chave | P0 |
| RF-T06c | Arcanista: caminho Bruxo / Mago / Feiticeiro | P0 |
| RF-T06d | Grimório SQL + modal; preparar vs espontâneo vs foco | P0 |
| RF-T06e | Débito PM ao lançar (+ aprimoramentos) | P0 |
| RF-T06f | Catálogo metadados p.174–178 | P0 |
| RF-T06g | Armadura + magia arcana → teste Misticismo | P1 |
| RF-T06h | Concentração (Vontade) + resistência à magia | P1 |
| RF-T06i | Truque via aprimoramento (0 PM) | P1 |
| RF-T06j | Linhagens feiticeiro + progressão conhecidas | P2 |

## Estado de implementação

| Item | Estado |
|------|--------|
| Grimório SQL + modal | **Feito** |
| Catálogo v1.3 (~227 metadados, círculos **1–5**) | **Feito** (`magias_mb_catalogo.json`; legado MB em `*.legacy_mb.json`) |
| Custo PM Tabela 4-1 (1/3/6/10/15) | **Feito** (`custo_pm_preparar_ou_lancar_magia(..., "v13")` + lançamento na ficha) |
| Aliases MB→v1.3 + aviso de órfãos na UI | **Feito** |
| Arcanista 3 caminhos | **Feito** |
| CD com atributo **valor** | **Feito** |
| Concentração + RM | **Feito** (revisar fórmula CD) |

## Gap código

| Módulo | Correção |
|--------|----------|
| Listas nomeadas por classe/nível (progressão magias) | Revalidar stubs `magias_*_mb.json` vs listas v1.3 (P1) |
| Preview CD magia | Revisar edge cases multiclasse |
| UI ficha | Polimento de rótulos «MB» remanescentes |

## Critérios de aceite

- Lançar magia 3º círculo debita **6 PM**, não 3.
- Arcanista Mago: só lança magias **memorizadas** (metade das conhecidas).
- Arcanista Feiticeiro: lança conhecidas sem preparação diária.
- CD de magia nível 8, SAB 4 → **16** (10 + 4 + 2).
- Repo sem `descricao_longa` de magias (RF-T46).

## Referência

- Livro: Cap. 4 p.168–178; Arcanista p.36–39; gasto PM p.224.
- Docs legado (atualizar páginas): `docs/tormenta/07-requisitos-grimorio-mb-144-209.md`.
