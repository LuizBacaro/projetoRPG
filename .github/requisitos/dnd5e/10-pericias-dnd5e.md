# FEATURE: Sistema de Perícias D&D 5E

## Descrição breve

Implementar as **dezoito perícias fixas** do PHB (Cap. 7, pp. 174–175). Perícias **não** usam pontos, ranks ou nível por perícia — apenas **proficiência** (sim/não) e o **modificador de habilidade** associado.

**Referência:** Livro do Jogador 5e, Cap. 7 (Perícias); talento *Skilled* (Habilidoso), p. 170.

---

## Divergência crítica: 5e ≠ 3.5

| | **D&D 3.5** (`dnd35`) | **D&D 5e** (este RF) |
|---|------------------------|----------------------|
| Quantidade | ~36 perícias | **18 perícias fixas** |
| Progressão | Pontos de perícia por nível; ranks 0…nível+3 | **Sem pontos por nível** |
| Bônus de treino | +3 classe + ranks | **+ bônus de proficiência** (se proficiente) |
| Melhorar uma perícia | Gastar pontos em ranks | **Ganhar proficiência** (classe, antecedente, talento, etc.) |
| Foco extremo | Muitos ranks na mesma perícia | **Especialização (Expertise)** — dobra bônus de proficiência (ladino/bardo) |

**Proibido no módulo `dnd5e`:** campos `graduacoes`, `pontos_pericia`, compra de ranks ao subir de nível, ou UI estilo 3.5. Ver [06-pericias-dnd35.md](../dnd35/06-pericias-dnd35.md) apenas para o jogo 3.5.

---

## Regra principal

**Teste de perícia (PHB):**

`1d20 + modificador da habilidade da perícia + bônus de proficiência (se proficiente)`

- Sem proficiência: apenas o modificador de habilidade entra no bônus total exibido na ficha.
- Com proficiência: modificador + bônus de proficiência do **nível total do personagem**.
- Não existe “nível de perícia” nem investimento de pontos ao passar de nível.

---

## As 18 perícias (catálogo fechado)

Todas as situações de jogo envolvendo perícias usam **somente** esta lista. Exceções oficiais fora dela: **combate** (ataque/dano) e **ferramentas** (proficiência de ferramenta separada).

| Slug (API) | Nome PT | Habilidade |
|------------|---------|------------|
| acrobacia | Acrobacia | DES |
| adestrar_animais | Adestrar Animais | SAB |
| arcanismo | Arcanismo | INT |
| atletismo | Atletismo | FOR |
| atuacao | Atuação | CAR |
| enganacao | Enganação | CAR |
| furtividade | Furtividade | DES |
| historia | História | INT |
| intimidacao | Intimidação | CAR |
| intuicao | Intuição | SAB |
| investigacao | Investigação | INT |
| medicina | Medicina | SAB |
| natureza | Natureza | INT |
| percepcao | Percepção | SAB |
| persuasao | Persuasão | CAR |
| prestidigitacao | Prestidigitação | DES |
| religiao | Religião | INT |
| sobrevivencia | Sobrevivência | SAB |

Fonte de dados: `backend/app/games/dnd5e/data/pericias_catalogo.py` · API `GET /api/v1/dnd5e/regras/pericias`.

---

## 1. Evolução automática — bônus de proficiência

Ao subir de nível **não se distribuem pontos em perícias**. O que evolui automaticamente é o **bônus de proficiência**, aplicado a **todas** as perícias em que o personagem é proficiente:

| Nível do personagem | Bônus de proficiência |
|---------------------|------------------------|
| 1–4 | +2 |
| 5–8 | +3 |
| 9–12 | +4 |
| 13–16 | +5 |
| 17–20 | +6 |

Implementação: `calcular_bonus_proficiencia()` em `backend/app/games/dnd5e/rules/habilidades.py` · exposto em `GET /regras/atributos` e no preview da ficha (`bonus_proficiencia`).

---

## 2. Evolução automática — incremento de atributos (ASI)

Nos níveis **4, 8, 12, 16 e 19** (marco `tipo: asi`), o jogador pode aumentar atributos (+2 em um ou +1 em dois). **Imediatamente**, todas as perícias ligadas aos atributos alterados passam a usar o **novo modificador** (via `scores_efetivos` + `bonus_atributo_feat` no preview).

Não há passo separado de “atualizar perícias” — o recálculo da grade é automático ao salvar o marco ou rodar `POST /regras/calcular-atributos`.

---

## 3. Como ganhar novas proficiências (PHB)

Não existe compra de ranks. Novas proficiências vêm de:

| Fonte | PHB | Arena (estado) |
|-------|-----|----------------|
| **Classe** | Lista fixa + escolha N da lista da classe | ✅ `pericias_classe_escolhidas` |
| **Antecedente** | 2 perícias | ✅ `antecedente_slug` |
| **Raça** | Ex.: meio-elfo +1 perícia | ✅ `pericia_racial_extra` |
| **Talento Habilidoso (Skilled)** | +3 proficiências à escolha | ✅ `feat_escolhas.skilled_pericias` (3 slugs distintos) |
| **Talento Especialista (Skill Expert)** | +1 proficiência + Expertise em outra | ✅ `feat_escolhas.skill_expert_nova` / `skill_expert_expertise` |
| **Multiclasse** | Proficiências da nova classe | ⏳ Parcial: `ficha_json.pericias_override` (ajuste manual / mesa) |
| **Subclasse** | Algumas concedem perícias (nív. 3+) | ⏳ Não implementado |
| **Tempo livre (Xanathar)** | Treinar idioma/ferramenta com ouro | ⏳ Fora de escopo MVP |

---

## 4. Especialização (Expertise)

Ladino e Bardo (e alguns talentos/subclasses) **dobram o bônus de proficiência** em perícias escolhidas — **não** aumentam ranks.

Fórmula com Expertise: `mod. habilidade + (2 × bônus de proficiência)`.

**Estado Arena:** ✅ Ladino/Bardo via `expertise_pericias`; talento Especialista via `feat_escolhas`.

| Classe | Marcos PHB | Slots totais |
|--------|------------|--------------|
| Ladino | 1, 6 | 2 + 2 (máx. 4) |
| Bardo | 3, 10 | 2 + 2 (máx. 4) |

Persistência classe: `ficha_json.expertise_pericias` · API `POST /personagens/{id}/progressao/expertise-pericias` · UI abaixo da grade de perícias.

---

## 5. Proficiência na ficha (modelo de dados)

### Proficiência automática

Calculada por `montar_proficiencias_automaticas()`:

- Classe + antecedente + raça + talento **Habilidoso**
- Resultado exposto no preview como `pericias_automaticas` (antes de overrides)

### Override manual (`pericias_override`)

Para mesa, multiclasse parcial ou correções:

```json
"pericias_override": {
  "furtividade": true,
  "atletismo": false
}
```

- `true` — força proficiente mesmo sem fonte automática  
- `false` — remove proficiência que viria de classe/raça/antecedente  
- Ausente — usa cálculo automático  

Persistência: `ficha_json.pericias_override` · API `POST /personagens/{id}/progressao/pericias-override` · UI “Editar” na grade de perícias.

**Não** representa pontos gastos por nível — apenas desvio documentado em relação às fontes automáticas.

### Grade exibida

Cada item em `pericias[]` do preview:

- `slug`, `nome`, `habilidade`
- `proficiente`: bool (resultado final)
- `bonus`: mod. habilidade + proficiência (se aplicável)

---

## 6. Talentos relacionados

| Feat | Slug API | Efeito em perícias |
|------|----------|-------------------|
| Habilidoso | `skilled` | +3 proficiências (`feat_escolhas.skilled_pericias`) |
| Especialista | `skill-expert` | +1 proficiência + expertise (`skill_expert_nova`, `skill_expert_expertise`) |
| Observador | `observant` | +5 passiva Percepção/Investigação (não é proficiência extra) |
| Resiliente | `resilient` | Proficiência em **salvaguarda**, não perícia |

Escolhas de talento: `feat_escolhas` em `ficha_json` · pendências `feat_escolha_skilled`, etc.

---

## 7. Validações

- Slug de perícia deve estar nas 18 do catálogo.
- Escolhas de classe: quantidade e pool conforme `classes_catalogo` / `proficiencias_classe`.
- Habilidoso: exatamente **3** perícias **distintas** em `skilled_pericias`.
- Override: slugs válidos; valores booleanos.
- **Nunca** validar ou persistir `graduacoes` / pontos de perícia por nível.

---

## 8. Cálculos (resumo)

```
mod_habilidade = (score_efetivo - 10) // 2
bonus_prof = tabela_por_nivel(nivel_total)
bonus_pericia = mod_habilidade + (bonus_prof se proficiente else 0)
```

Com Expertise (futuro): `+ bonus_prof` adicional nas perícias marcadas.

---

## 9. Estado de implementação Arena

| Item | Módulo / rota |
|------|----------------|
| 18 perícias + bônus | `rules/pericias.py`, `rules/ficha.py` |
| Bônus de proficiência por nível | `rules/habilidades.py` |
| Proficiências classe/raça/antecedente | `montar_proficiencias_pericias` |
| Skilled (+3) | `proficiencias_feat_skilled`, UI progressão |
| Override manual | `pericias_override`, UI Editar perícias |
| ASI → mod. de perícias | `bonus_atributo_feat` + preview |
| Expertise | ✅ `expertise_pericias`, cálculo 2× prof |
| Skill Expert feat | ✅ `feat_escolhas` + UI progressão |
| Multiclasse completa | Pendente (D5E-080+) |

Testes: `backend/tests/test_dnd5e_pericias.py`, `test_dnd5e_progressao.py` (Skilled).

---

## Referência do livro

- Cap. 1: Habilidades e bônus de proficiência  
- Cap. 7: Perícias (pp. 174–175)  
- Cap. 6: Talento *Skilled* (p. 170)  
- Opcional: Guia de Xanathar (tempo livre); Expertise — Ladino/Bardo
