# FEATURE: Catálogo de bônus/penalidades de perícias (fontes do livro)

> **Fonte:** Tormenta20 Edição Jogo do Ano v1.3 — Cap. 1 (raças/origens/classes), Cap. 2 (poderes), Cap. 3 (equipamento/melhorias), Cap. 8 (itens mágicos).  
> **Dados:** [`backend/app/games/tormenta/data/bonus_pericias_fontes_v13.json`](../../../backend/app/games/tormenta/data/bonus_pericias_fontes_v13.json)  
> **Extrator:** [`scripts/extrair_bonus_pericias_t20_v13.py`](../../../scripts/extrair_bonus_pericias_t20_v13.py)  
> **Relacionado:** [04-pericias-tormenta.md](04-pericias-tormenta.md) (RF-T04i usos / `bonus_uso`).

## Descrição

Inventariar no Arena **quais fontes do livro** concedem bônus ou penalidade em perícias (e, raramente, em **usos**), com remissão de página e cruzamento com o que o motor já aplica.

**Esta fase entrega o catálogo e o MVP de auto-apply de melhorias TS em ataques.** Vestuário Cap. 3, encantamentos Cap. 8 e poderes estruturados ficam para iterações seguintes.

## Como regenerar

```bash
python3 scripts/extrair_bonus_pericias_t20_v13.py \
  --pdf livros/Tormenta20-Edicao-Jogo-do-Ano-v1.3.pdf \
  --out backend/app/games/tormenta/data/bonus_pericias_fontes_v13.json
```

Offset neste PDF: `pagina_pdf ≈ pagina_impressa + 6`.

## Forma do registro

| Campo | Significado |
|-------|-------------|
| `fonte_tipo` | `raca` \| `origem` \| `classe_poder` \| `poder_geral` \| `equipamento` \| `item_magico` |
| `pericia_slug` | slug canônico Cap. 2 |
| `uso_id` | id RF-T04i ou `null` (perícia inteira) |
| `valor` | inteiro com sinal (+2 / −5) |
| `escopo` | `pericia` \| `uso` \| `contexto_prosa` |
| `ja_no_codigo` | `true` \| `parcial` \| `false` |
| `confianca` | `alta` \| `media` \| `baixa` |
| `pagina` | impressa |

## Achados (extração atual)

Ver `_meta` no JSON (totais mudam se o script for reexecutado). Ordem de grandeza:

| Fonte | Entradas (ordem) | Nota |
|-------|------------------|------|
| Equipamento / melhorias | ~30 | Vestuário + Tabela melhorias; vários ainda `false` |
| Poder geral | ~18 | `+N em testes de X`; sem `mods` no catálogo de poderes |
| Classe / poder | ~14 | Sample Cap. 1; revisar falsos positivos |
| Item mágico | ~9 | Ex.: Acrobático +5, Sombrio +5 |
| Origem / raça | ~5–6 cada | Raça em grande parte já em `tracos_mecanicos_v13` |

**Usos (subperícias):** minoria. Exemplos no catálogo:

- Melhoria **Discreto** → Ladinagem / uso `ocultar` +5 (`ja_no_codigo: true` via `itens_superiores_v13`)
- Sem gazua → Ladinagem / `abrir_fechadura` −5
- Sem estojo → Enganação / `disfarce` −5
- Coleção de livros → Percepção / `observar` +5 (contexto)

Quase todo o resto é **perícia inteira**.

## Já automático no Arena

- Racial `pericias_bonus` (+ escolhas Lefou/Kliren no preview)
- Pen. armadura / natação / sobrecarga
- Treino, ½ nível, atributo
- **Melhorias TS em ataques** (`ficha_json.ataques[].melhorias`): Banhado a ouro, Cravejado, Macabro, Discreto→`ocultar`, etc. — agregador `bonus_pericias_itens_t20.py` via `itens_com_melhorias` no `calcular-bonus` (RF-T14 fase auto-apply MVP)
- Manual: coluna Outros + `pericias_usos_bonus` (somam **além** dos itens)

## Gaps prioritários (ainda manuais / sem slot)

1. **Vestuário Cap. 3** (Andrajos, Enfeite de Elmo…) — sem `melhorias[]` / slug de vestuário na ficha.
2. **Encantamentos Cap. 8** Acrobático / Sombrio — ainda não modelados como melhoria/encantamento no inventário.
3. **Aprimorado** (+1 perícia) — só se o item enviar `pericia_slug`.
4. **Poderes** com +N em perícia — sem `efeitos` estruturados.
5. Armaduras com melhorias TS — suportadas se `armaduras_protecao[].melhorias` existir (UI ainda não grava).

## Critérios de aceite (catálogo)

1. Script documentado e JSON versionado com `_meta` + `entradas[]`.
2. Entradas distinguem perícia vs uso vs contexto.
3. Cruzamento `ja_no_codigo` com `tracos_mecanicos_v13` e `itens_superiores_v13`.
4. RF indexado no README Tormenta; ponteiro em RF-T04.

## Critérios de aceite (auto-apply MVP)

1. Ataque com `melhorias: ["banhado_a_ouro"]` → Diplomacia Σ / rolagem inclui +2 sem digitar Outros.
2. `discreto` + uso Ocultar → `bonus_uso` +5; outros usos de Ladinagem sem esse +5.
3. Macabro → Intimidação +2 e Diplomacia −2.
4. Coluna Outros manual **não** é sobrescrita; soma com itens.
5. Response `bonus_itens` + `itens_fontes` para auditoria/breakdown.

## Fora de escopo

- Auto-preencher ficha a partir do inventário
- Parser total de poderes sem estrutura
- Condições de combate (endpoint próprio)
- Texto longo do livro no repositório (só snippet curto + página)
