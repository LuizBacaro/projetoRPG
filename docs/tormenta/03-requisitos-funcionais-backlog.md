# Requisitos funcionais — backlog Tormenta (Arena)

Prioridade: **P0** crítico para ficha utilizável; **P1** conforto; **P2** paridade com livro; **P3** arena/combate.

## P0 — Ficha e persistência

| ID | Requisito | Critérios de aceite |
|----|-----------|---------------------|
| RF-T00 | Personagem CRUD autenticado com `game_slug=tormenta` | Já coberto por testes API |
| RF-T01 | Atributos com modificador d20 coerente | Alterar valor atualiza modificador na UI |
| RF-T02 | `ficha_json` guarda perícias, ataques, equipamento, metadados de mesa | PATCH preserva chaves desconhecidas futuras |
| RF-T03 | Retrato do personagem (URL) persistido | `foto_url` preenchida na API e exibida na ficha quando HTTPS/relativo válido |

## P1 — Dados de apoio sem catálogo completo

| ID | Requisito | Critérios de aceite |
|----|-----------|---------------------|
| RF-T10 | Editor de pontos de atributo com validação por **tabela de custos** (livro) | Ficha mostra soma 8–18; **jogador**: salvar bloqueado se soma ≠ 20 ou valor fora de 8–18 (API + UI); monstro/NPC sem essa regra |
| RF-T11 | Exportar/importar JSON da ficha (backup) | Opcional; útil para mesa |

## P2 — Catálogos dinâmicos (paridade livro)

| ID | Requisito | Critérios de aceite |
|----|-----------|---------------------|
| RF-T20 | API + tabela `tormenta_pericias` (ou prefixo comum) | Listagem paginada; `pagina_referencia` opcional |
| RF-T21 | API + tabela `tormenta_poderes` (talentos T20) | Nome, tipo, pré-requisitos, texto; seed incremental |
| RF-T22 | API + tabela `tormenta_magias` | Círculo, escola/resistência, referência |
| RF-T23 | API + tabela `tormenta_equipamentos` | Slots, carga, preço em cobre |
| RF-T24 | Ligação personagem ↔ poder escolhido (N:N) | Similar `TalentoJogador` D&D |

## P3 — Combate e mestre

| ID | Requisito | Notas |
|----|-----------|--------|
| RF-T30 | Importar personagem Tormenta para arena | Depende modelo de combate T20 |
| RF-T31 | Condições e efeitos automáticos | Catálogo + motor |

## Decisões de produto em aberto

- **PM vs PA:** no modelo SQL usa-se `pa_max` / `pa_atual` para Pontos de Mana; na UI “PM”. Manter nome interno estável ou renomear coluna (migration) — documentar em ADR se mudar.
- **Multiclasse:** texto em `classe_nivel` vs tabela de classes — MVP texto.
