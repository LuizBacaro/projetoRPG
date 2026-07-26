# FEATURE: Construção de Ameaça (NPC / Monstro) — Tormenta 20

> **Fonte:** Tormenta20 Edição Jogo do Ano v1.3 — bestiário / Reforma Monstrográfica (remissão ao capítulo de ameaças do livro; sem copiar texto longo).  
> **Escopo Arena:** CRUD de Ameaça reutilizando `tormenta_personagens` (`tipo` npc|monstro) + bloco de texto estilo livro gerado de forma **determinística**.  
> **Código:** `backend/app/games/tormenta/rules/ameaca_bloco_t20.py`, rotas em `api/v1/personagens.py`, UI em `frontend/games/tormenta/`.

## Descrição

Transformar a ficha detalhada de um personagem (ou dados de monstro/NPC) na estrutura simplificada de uma **Ameaça**: rápida de ler na mesa, com **valores finais** (sem breakdown de bônus) e ações de combate.

Ameaça no Arena **não** é tabela nova: é personagem com `tipo ∈ {npc, monstro}` e metadados em `ficha_json.ameaca`.

## Regras de negócio

1. **ND (Nível de Desafio):** base = nível do personagem; editável em `ameaca.nd`.
2. **Papel de combate:** `solo` (atua sozinho; PV tipicamente altos), `lacaio` (pouco PV, quantidade), `especial` (suporte/conjurador). Default: `especial` se `pa_max > 0`, senão `solo`.
3. **Consolidação:** só valores finais de ataque, dano, defesa, perícias e resistências.
4. **Ações:** habilidades e magias como blocos (padrão / movimento / livre / reação) com custo de PM quando houver.
5. **Identificar criatura:** CD de Investigação ou Misticismo = **15 + ND** (informação de mesa; não bloqueia o bloco).
6. **Atributos nulos:** construto/morto-vivo podem marcar atributos como `—` via `ameaca.atributos_nulos`.
7. **Perícias:** listar só as **fortes**; opcionalmente um bônus base de perícia fraca.

## Contrato `ficha_json.ameaca`

Ver também `docs/tormenta/05-contrato-dados-ficha-json-e-api.md`.

```json
{
  "ameaca": {
    "nd": 3,
    "papel_combate": "solo",
    "tipo_criatura": "Humanoide",
    "percepcao": 5,
    "sentidos": "visão na penumbra",
    "atributos_nulos": [],
    "pericias_fortes": [{"nome": "Furtividade", "bonus": 8}],
    "pericias_fracas_bonus": 0,
    "acoes": {
      "corpo_a_corpo": [{"nome": "Espada", "ataque": "+7", "dano": "1d8+3", "critico": "19-20"}],
      "distancia": [],
      "especiais": [{"nome": "...", "tipo_acao": "padrao", "custo_pm": 2, "texto": "..."}],
      "magias": [{"nome": "...", "cd": 15, "custo_pm": 3}]
    },
    "equipamento_tesouro": "",
    "texto_override": null
  }
}
```

- Import do bestiário pode gravar `nd` / `tipo_criatura` na raiz do JSON (legado); o motor lê ambos e normaliza para `ameaca` na conversão/save.
- `texto_override`: edição manual da caixa; **Regenerar** limpa e recalcula.

## Requisitos funcionais

| ID | Requisito | Prioridade |
|----|-----------|------------|
| RF-T13a | Persistir metadados de ameaça em `ficha_json.ameaca` (ND, papel, tipo criatura, sentidos, ações) | P0 | **Feito** |
| RF-T13b | Motor determinístico `montar_bloco_ameaca` (template do apêndice) | P0 | **Feito** |
| RF-T13c | `GET /tormenta/personagens/{id}/bloco-ameaca` (`texto` + `fonte: override\|gerado`) | P0 | **Feito** |
| RF-T13d | `POST /tormenta/personagens/{id}/converter-ameaca` — cópia npc/monstro sem alterar o original | P0 | **Feito** |
| RF-T13e | UI ficha: secção Ameaça (campos + textarea + Copiar / Regenerar / Salvar override) | P0 | **Feito** |
| RF-T13f | UI jogador: botão Converter em Ameaça | P1 | **Feito** |
| RF-T13g | Dashboard: criação npc/monstro com `ameaca` mínima; ND visível na arena compacta quando existir | P2 | **Feito** |

## Gap código (baseline)

| Item | Estado |
|------|--------|
| `tipo` jogador / npc / monstro + CRUD personagens | **Feito** |
| Import bestiário stub + arena NPC compacta | **Feito** |
| `ficha_json.ameaca` + bloco de texto | **Feito** |
| LLM / prompt Gemini na API | **Fora de escopo** (conversão determinística) |

## Critérios de aceite

- Mestre cria/edita/apaga personagem `npc` ou `monstro` com ND e papel persistidos.
- Bloco gerado segue o template do apêndice (valores finais, sem breakdown).
- Override manual persiste; Regenerar volta ao motor.
- Converter PJ gera cópia independente.
- Testes cobrem formatação e GET do bloco; sem chamada a LLM.
- Sem texto longo de livro no repositório.

## Referência

- Skill: `.cursor/skills/tormenta-20-arena-arquitetura-e-regras/SKILL.md`
- Contrato: `docs/tormenta/05-contrato-dados-ficha-json-e-api.md`
- Backlog: `docs/tormenta/03-requisitos-funcionais-backlog.md` (RF-T13)

## Apêndice A — Template do bloco (formatação)

```
[Nome] ND [X]
[Tipo e Tamanho] (ex.: Humanoide Médio)
Iniciativa, Percepção e Sentidos
Defesa, Resistências (Fort, Ref, Von) e RD
Pontos de Vida e Pontos de Mana
Deslocamento
Ações Corpo a Corpo: Ataque +X (Dano, Crítico)
Ações À Distância: Ataque +X (Dano, Crítico)
Habilidades Especiais
Magias (com CD quando conjurador)
Atributos: For X, Des X, Con X, Int X, Sab X, Car X (só bônus; ou —)
Perícias: bônus finais das principais
Equipamento e Tesouro
```

## Apêndice B — Referência histórica (prompt offline)

O texto abaixo foi o rascunho inicial (uso offline com LLM). **Não** é contrato de implementação da Arena; o motor canónico é `ameaca_bloco_t20.py`.

> Converter PJ → Ameaça: ND ≈ nível; papel Solo/Lacaio/Especial; só valores finais; ações com PM; estrutura do Apêndice A.
