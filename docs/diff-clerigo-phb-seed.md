# Diff PHB × Seed — Magias de Clérigo (D&D 3.5)

Comparação entre a lista do **Livro do Jogador** (apêndice “Magias de Clérigo”, cap. 11) e `backend/scripts/seed_magias.py` (`MAGIAS_CLÉRIGO`).

## Como reproduzir

```bash
cd backend
python3 scripts/diff_clerigo_phb_seed.py
python3 scripts/diff_clerigo_phb_seed.py --json ../docs/diff-clerigo-phb-seed.json
```

Para aplicar correções no seed (níveis 0–1, renomeações PHB):

```bash
python3 scripts/patch_clerigo_phb_seed.py
```

Para sincronizar o banco após alterar o seed:

```bash
python3 scripts/seed_magias.py --classes CLERIGO
```

(Ajuste flags conforme o script; use `--help`.)

## Resumo (após patch de maio/2026)

| Nível | PHB | Seed | Observação |
|------:|----:|-----:|------------|
| 0 | 12 | 12 | Alinhado |
| 1 | 28 | 30 | 2 extras no seed (não listadas no PHB) |
| 2–5 | ✓ | ✓ | Alinhado |
| 6–9 | ✓ | ✓ | Alinhado (parser ignora artefatos de OCR) |

### Extras no seed (presentes no jogo, ausentes na lista PHB)

- **Nível 1:** Emaranhar, Proibição de Ação  
- **Nível 1:** Bane, Desespero, Favor Divino (variantes ou magias relacionadas; PHB usa Maldição Menor e Auxílio Divino — ambas foram adicionadas)

### Renomeações aplicadas (mesma magia, nome PHB)

| Antes (seed) | Depois (PHB) |
|--------------|--------------|
| Mending | Consertar |
| Guia | Orientação |
| Detectar Veneno | Detectar Venenos |
| Névoa Obscurecente | Névoa Obscurescente |
| Resistir Elementos | Suportar Elementos |

### Magias adicionadas ao seed (estavam no PHB e faltavam)

**Nível 0:** Criar Água, Infligir Ferimentos Mínimos  

**Nível 1:** Abençoar Água, Amaldiçoar Água, Auxílio Divino, Causar Medo, Divisibilidade Contra Mortos-Vivos, Infligir Ferimentos Leves, Proteção Contra o Caos / Mal / Bem / Ordem, Visão da Morte

## Níveis 8 e 9

Lista completa e idêntica ao PHB (17 magias de 8º, 11 de 9º). Problemas de exibição no grimório eram de `nivel` legado na API/UI, não de dados faltando.
