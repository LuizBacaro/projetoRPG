# FEATURE: Suplementos opcionais (Heróis, Deuses, Atlas)

> **Escopo:** conteúdo **fora do core v1.3** ou **regras opcionais** — implementar só quando pedido; não misturar no MVP da ficha core.

## Fontes

| PDF | Conteúdo | Uso na Arena |
|-----|----------|--------------|
| `T20-Herois-de-Arton-v1-1.pdf` | Raças/classe variantes, distinções, arsenal, regras opcionais | P2–P3 |
| `T20-Deuses-de-Arton-v1-1.pdf` | Panteão expandido, Frade, distinções divinas | Ver [09-origens-divindades-tormenta.md](09-origens-divindades-tormenta.md) |
| `Atlas-de-Arton-v1.0-17-11-2023.pdf` | Geografia, organizações, vida em Arton | Ambientação; origens regionais p.470 |

---

## Heróis de Arton v1.1

### Sumário

| Capítulo | p. | Escopo |
|----------|-----|--------|
| Campeões de Arton | 6 | Novas raças, Treinador, variantes de classe |
| Distinções | 102 | ~40 distinções (prestígio) |
| Arsenal dos Heróis | 214 | Equipamento, magias, itens mágicos |
| Regras Opcionais | 278 | Combate avançado, lesões, domínios, etc. |

### Novas raças (suplemento — **não** core v1.3)

Duende, Eiradaan, Galokk, Meio-Elfo, Sátiro (p.8–15).

### Nova classe

**Treinador** p.16 — backlog separado se implementar.

### Classes variantes (14)

p.22–44 — substituem/blocam variantes de classes core; flag `fonte: herois_arton` no catálogo.

### Requisitos funcionais (opcionais)

| ID | Requisito | Prioridade |
|----|-----------|------------|
| RF-T10a | Flag `regras_opcionais` na campanha/mesa | P3 |
| RF-T10b | Catálogo raças/classes suplemento (isolado do core) | P3 |
| RF-T10c | Distinções como vínculo personagem | P3 |
| RF-T10d | Regras opcionais combate/lesões | P3 |

---

## Atlas de Arton v1.0

### Sumário

| Capítulo | p. |
|----------|-----|
| O Reinado | 44 |
| Além do Reinado | 170 |
| Além de Arton | 322 |
| Organizações | 422 |
| Vida em Arton | 446 |
| Apêndice: Origens Regionais | 470 |

### Requisitos funcionais (ambientação)

| ID | Requisito | Prioridade |
|----|-----------|------------|
| RF-T10e | Origens regionais ligadas a região do Atlas | P3 |
| RF-T10f | Sem catálogo mecânico obrigatório (lore only) | — |

---

## Decisão de produto

- **Core Arena:** apenas `Tormenta20-Edicao-Jogo-do-Ano-v1.3.pdf` (RFs 01–09).
- **Suplementos:** feature flags ou `game_slug` futuro **não necessário** — usar campo `fonte_catalogo: core | herois | deuses` nos JSON.
- **Não criar** pasta `.cursor/requisitos/tormenta-ve/` — mesma edição T20, versionada no README e `_meta.fonte` dos JSON.

## Estado de implementação

| Item | Estado |
|------|--------|
| Conteúdo Heróis/Atlas no repo | **Não feito** |
| Meio-elfo no backend (MB) | **Legado** — mover para suplemento Heróis se mantido |

## Referência

- Índice master: [README.md](README.md)
