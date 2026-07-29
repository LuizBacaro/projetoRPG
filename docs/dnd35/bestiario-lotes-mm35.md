# Bestiário MM 3.5 — backlog de lotes (RF-M09)

**Fonte:** `livros/dd-3e-livro-dos-monstros-3-5.pdf`  
**Artefacto:** `backend/app/games/dnd35/data/bestiario_mm35.json`  
**RF:** [`.cursor/requisitos/dnd35/11-monstros-dnd35.md`](../../.cursor/requisitos/dnd35/11-monstros-dnd35.md)  
**Runbook:** [livros-para-dados.md](../livros-para-dados.md)

**Legal:** só stats estruturados + `pagina_referencia`. Não copiar prosa longa de Combate.

---

## Estado atual

| Item | Valor |
|------|--------|
| Lote 0 (pipeline / curado) | ✅ ~51 entradas |
| Lote 1 (Cap. A–Z frequentes) | ✅ +53 (total ~104) |
| Lote 2 (Animais) | ✅ +55 (~61 animais; total ~159) |
| Lote 3 (Insetos / vermin) | ✅ +32 (~34 insetos; total ~191) |
| Lote 4 (Dragões) | ✅ 10 espécies × 12 idades + pais (120 idades; catálogo ~317) |
| API / import / UI / bloco | ✅ v1 |
| Contagem mínima nos testes | `>= 300` em `tests/test_dnd35_bestiario.py` |

Validação local:

```bash
python3 scripts/extrair_bestiario_mm35.py --validate
cd backend && python3 -m pytest tests/test_dnd35_bestiario.py -q
```

---

## Ordem dos lotes

Cada lote = 1 PR (ou conjunto pequeno de PRs): JSON revisado + bump de contagem mínima no teste + smoke API.

### Lote 1 — Capítulos A–Z (resto do MM principal)

Completar entradas **ainda ausentes** do corpo alfabético (humanoides, monstros, mortos-vivos, construtos, fadas, etc.), **exceto** o que for deferido aos lotes 2–4.

- Preferir criaturas de mesa frequente (ND baixo/médio) antes de ND 15+.
- Manter `slug` estável; usar `aliases` para nomes alternativos / inglês.
- Não duplicar linhas já no lote 0 (ver slugs atuais no JSON).

**Aceite:** +≥40 novas entradas; teste `total >= 90`. ✅ cumprido (~53 novas; total ~104).

Restante do Cap. A–Z (ND alto / raros / templates) pode entrar em PRs incrementais ainda rotulados como “lote 1b” se necessário; a prioridade seguinte do backlog oficial é o **lote 2**.

### Lote 2 — Animais (apêndice)

Entradas tipadas `tipo_criatura: "Animal"` do apêndice de animais (lobos, ursos, cavalos, felinos, etc. restantes).

- Distinguir de companheiro animal / familiar (RFs 09/10): aqui é **monstro de bestiário** para import na arena.
- Já existem alguns animais no lote 0 — completar o restante.

**Aceite:** cobertura do apêndice de animais do MM (ou subset documentado). ✅ ~61 animais (comuns + atrozes + aquáticos/montaria).

### Lote 3 — Insetos / vermin

Entradas `Inseto` (e vermin equivalentes no MM): aranhas, centopéias, etc. restantes além de `giant-spider` / `giant-centipede`.

**Aceite:** apêndice de insetos/vermin. ✅ ~34 insetos (tamanhos de aranha/centopéia/escorpião + formigas/besouros/enxames).

### Lote 4 — Dragões (todas as espécies × idades)

Modelo já em uso:

- Espécie-pai: `especie_pai: null`, `nd: null`, `categoria_idade: null` (ex.: `dragao-azul`) — **não importável**.
- Filhas: `especie_pai`, `categoria_idade`, slug `dragao-<cor>-<idade>`.

Categorias de idade 3.5 (usar rótulos estáveis em `categoria_idade`):

`filhote` · `muito-jovem` · `jovem` · `adulto-jovem` · `adulto` · `maduro` · `velho` · `muito-velho` · `anciao` · `anciao-grande` · `anciao-wyrm` · `grande-wyrm`  
(ajustar ortografia aos rótulos já usados no JSON; manter consistência.)

Espécies cromáticas + metálicas do MM (além do azul já parcial): branco, negro, verde, vermelho, cobre, bronze, latão, prata, ouro (+ outros se o MM da edição incluir).

**Aceite:** ≥1 espécie completa além do azul; idealmente fechar cromáticos + metálicos. ✅ 10 espécies (azul, vermelho, verde, negro, branco, latão, bronze, cobre, prata, ouro) × 12 idades + pais. `categoria_idade` normalizada com hífen (`muito-jovem`, etc.).

---

## Checklist por PR de lote

1. Extrair rascunho (`scripts/extrair_bestiario_mm35.py --draft` se útil) **ou** editar JSON à mão a partir do PDF.
2. Revisar stats: CA / toque / surpresa, HP, saves, attrs, ≥1 ataque quando o livro tiver.
3. `pagina_referencia` no formato `Livro dos Monstros p.NNN`.
4. `python3 scripts/extrair_bestiario_mm35.py --validate` (slugs únicos, campos obrigatórios).
5. Subir `assert len(rows) >= N` (e smoke GET/import se novos slugs de referência).
6. Atualizar a tabela “Estado” neste doc e a linha do RF-M09 se o lote fechar.

---

## Fora de escopo (por agora)

| Item | Nota |
|------|------|
| RF-M08 Tesouro automático | Só remissão; não gerar loot |
| Templates / classes de nível em monstros | Fora do v1 do catálogo |
| Prosa de Combate do livro | Proibida no repo |
| Misturar com bestiário Tormenta | Pacote só `dnd35` |
