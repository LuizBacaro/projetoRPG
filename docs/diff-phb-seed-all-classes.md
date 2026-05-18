# Diff PHB × Seed — Todas as classes (D&D 3.5)

Comparação entre listas do **Livro do Jogador** (apêndice, cap. 11) e `backend/scripts/seed_magias.py`.

## Comandos

```bash
cd backend

# Relatório completo (terminal + JSON)
python3 scripts/diff_phb_seed_all_classes.py
python3 scripts/diff_phb_seed_all_classes.py --json ../docs/diff-phb-seed-all-classes.json

# Aplicar correções (ordem recomendada)
python3 scripts/patch_clerigo_phb_seed.py      # magias nv.0–1 do clérigo
python3 scripts/patch_phb_seed_all_classes.py  # limpeza geral + paladino/ranger
python3 scripts/patch_phb_bardo_mago.py        # bardo = PHB; renomes mago

# Sincronizar banco após alterar o seed
python3 scripts/seed_magias.py --sync --classes CLERIGO,BARDO,DRUIDA,PALADINO,RANGER,MAGO
```

Requer `pdftotext` (pacote `poppler-utils`) e o PDF em `livros/D&D3_5_livro_jogador.pdf`.

## Resumo (após pente fino maio/2026)

| Classe | PHB (único) | Seed | Faltando | Extras | Observação |
|--------|------------:|-----:|---------:|-------:|------------|
| **Ranger** | 46 | 46 | 0 | 0 | Alinhado com PHB |
| **Paladino** | 46 | 49 | 0 | 3 | +5 magias nv.4 do PHB; 3 extras (círculos nv.3) |
| **Clérigo** | 207 | 222 | 0* | 19 | Removidos Emaranhar, Proibição de Ação, Favor Divino; Bane→Maldição Menor |
| **Druida** | 162 | 169 | ~0 | 8 | Renomes PHB (Divisibilidade, Dominar Animais, etc.) |
| **Bardo** | 146 | 146 | 0 | 0 | Alinhado com PHB |
| **Mago** | 327 | 371 | 0 nomes* | ~111 | *Todas as magias PHB existem no seed; diff por nível é artefato do PDF |

\*Falsos “faltando” de Detectar Caos/Mal/Bem/Ordem no nv.5 foram corrigidos no parser (linha Dissipar…).

## Correções aplicadas no seed

- Duplicatas removidas no **Bardo** (nv. 0–1).
- Placeholders `NOME DA MAGIA` removidos (Bardo, Druida, Mago).
- **Clérigo:** removidos Emaranhar, Proibição de Ação, Favor Divino (duplicata de Auxílio Divino); Bane renomeado para Maldição Menor.
- **Paladino nv.4:** adicionados Presa Mágica, Resistência a Elementos, Retardar Envenenamento, Salto, Suportar Elementos (bloco PHB após quebra de página).
- **Ranger nv.1:** removidas 5 magias que pertencem ao paladino no apêndice PHB, não ao ranger.

## Limitações conhecidas

1. **PDF desordenado:** no apêndice, níveis de Ranger e trechos de Paladino aparecem fora de ordem; o script usa marcadores específicos (`NÍVEL DE RANGER`, etc.).
2. **Bardo / Mago:** o seed histórico é mais amplo que a lista PHB do bardo; remover os “extras” exigiria decidir se magias de outras listas devem sair só do bardo ou virar multiclase explícita.
3. **Mago:** nomes truncados pelo `pdftotext` geram diffs até mapear aliases; use o JSON para priorizar lacunas reais.

## Arquivos

- `backend/scripts/diff_phb_seed_all_classes.py`
- `backend/scripts/patch_phb_seed_all_classes.py`
- `docs/diff-phb-seed-all-classes.json` (gerado)
- `docs/diff-clerigo-phb-seed.md` (relatório anterior só clérigo)
