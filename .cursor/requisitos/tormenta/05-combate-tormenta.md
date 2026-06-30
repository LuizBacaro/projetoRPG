# FEATURE: Combate Tormenta 20 (Edição Jogo do Ano v1.3) — Arena

> **Fonte:** `Tormenta20-Edicao-Jogo-do-Ano-v1.3.pdf` — Cap. 5 «Jogando» p.212+; **Combate p.230**; Lista de Condições **p.394**.  
> **Escopo Arena:** tracker de mesa + rolagens assistidas; economia de ações completa = backlog P3.

## Descrição

Rodadas, iniciativa, turnos, ataques, dano/cura PV, condições e testes de resistência — integrados ao dashboard Arena.

## Regras de negócio (v1.3)

- **Teste base:** 1d20 + modificadores vs CD (Cap. 5 p.220+).
- **Combate:** iniciativa, ações por turno, ataques, dano, movimento — p.230+.
- **PV em 0:** personagem começa a morrer (p.11); regras detalhadas de morte no combate p.230+.
- **Condições:** lista fechada p.394; modificadores automáticos quando aplicável.
- **PM em combate:** gasto de habilidades/poderes debita PM.

## API (existente)

- `POST /tormenta/combate/iniciar`, `/avancar-turno`, `/finalizar`
- `POST /tormenta/combate/condicoes-mb`
- `POST /tormenta/combate/rolar-iniciativa` — 1d20 + DES
- `POST /tormenta/combate/rolar-ataque` — 1d20 + BBA + mod vs CA
- `POST /tormenta/combate/rolar-dano` — fórmula NdM + mod
- `POST /tormenta/combate/testar-resistencia-magia` — RM +4/+8

## Requisitos funcionais

| ID | Requisito | Prioridade |
|----|-----------|------------|
| RF-T05a | Iniciativa ordenada + rolagem 1d20+DES | P0 |
| RF-T05b | Rolagem ataque/dano (MVP) | P0 |
| RF-T05c | Modificadores automáticos de condições (ataque/CA) | P1 |
| RF-T05d | Lista condições alinhada p.394 v1.3 | P1 |
| RF-T05e | Regras PV ≤ 0 / estabilização / morte | P2 |
| RF-T05f | Economia de ações, surpresa, ataque de oportunidade | P3 |
| RF-T05g | Parceiros (animais/montarias) p.260+ | P3 |

## Estado de implementação

| Item | Estado |
|------|--------|
| Iniciativa + rolagens ataque/dano | **Feito** |
| Modificadores condições (parcial) | **Feito** |
| Concentração + resistência magia | **Feito** |
| Condições vs lista p.394 v1.3 | **Feito** | Catálogo + motor ataque/CA; modal arena v1.3 |
| Morte / 0 PV | **Não feito** |
| Economia de ações completa | **Não feito** |

## Gap código

- Endpoints e módulos ainda sufixo `_mb`; revisar `combate_t20.py` contra p.230 v1.3.
- Renomear referências «Cap. 9 MB» → «Cap. 5 p.230 v1.3».

## Critérios de aceite

- Rolagem de iniciativa usa DES (não INT).
- Condição aplicada altera ataque/CA conforme tabela p.394 (casos cobertos pelo motor).
- Documentação RF cita páginas v1.3, não MB Cap. 9.

## Referência

- Livro: Cap. 5 p.230 (combate); p.394 (condições).
- Backlog: `docs/tormenta/03-requisitos-funcionais-backlog.md` (RF-T30–T31).
