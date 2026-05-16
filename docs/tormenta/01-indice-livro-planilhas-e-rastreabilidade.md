# Índice: livro ↔ planilhas ↔ código

## Planilhas no repositório (referência visual)

| Ficheiro | Uso |
|----------|-----|
| `planilha-tormenta.png` | Layout geral, identidade, blocos |
| `planilha-tormenta2.png` | Refinamentos de layout |
| `planilha-tormenta3.png` | Escudos de atributos, faixas vermelhas, molduras |

**Rastreabilidade:** alterações de UI na ficha web devem citar qual planilha guiou o bloco (comentário curto no CSS/HTML ou neste doc).

## Estrutura lógica do *Tormenta 20* (Módulo Básico)

O livro completo tem dezenas de secções; abaixo está um **esqueleto** típico para amarrar requisitos. **Os números de página devem ser confirmados na tua edição** (impressão e PDF podem diferir).

| Secção lógica (livro) | Conteúdo relevante para a plataforma | Onde no código hoje |
|----------------------|----------------------------------------|---------------------|
| Introdução / como jogar | Dados, rolagens, CD — conceitos | Futuro: ajuda contextual |
| Criação de personagem | Atributos, custos, perícias, origem, raça, classe, equipamento inicial | `ficha-personagem.html`, `TormentaPersonagem`, `ficha_json` |
| Atributos e modificadores | Tabela modificadores; custo de valores | Motor: `mod = ⌊(v−10)/2⌋` já na ficha; custo: **JSON** em `tabelas/` |
| Raças | Traços, poderes raciais | Texto livre + futuro catálogo |
| Origens | Poderes de origem | `ficha_json` / textarea |
| Classes | PV, PM, perícias, proficiências, progressão | Colunas parciais + `classe_nivel` texto |
| Perícias | Lista, treinamento, CD | `ficha_json.pericias` + futuro catálogo |
| Poderes / talentos | Lista extensa, pré-requisitos | Texto + roadmap catálogo |
| Magias | Círculos, aprendizagem, lista | Texto + roadmap catálogo |
| Equipamento | Armas, armaduras, itens, carga | `ficha_json` + roadmap catálogo |
| Combate | Ataque, defesa, dano, condições | Parcial (CA, ataques); arena futura |
| Mestre / ambientação | Opcional para VTT | Fora do MVP ficha |

## Âncoras que referiste (confirmar na tua edição)

| Tema | Página (referência do pedido) | Nota |
|------|-------------------------------|------|
| Modificadores de Habilidade | **p. 6** | Alinhar com fórmula d20 e UI dos escudos |
| Custo de Valores de Habilidade | **p. 7** | Implementar via tabela em `tabelas/custo-atributos.json` (estrutura vazia + preenchimento manual) |

Se a tua edição tiver **paginação diferente**, atualiza a coluna “Página” no ficheiro `02-inventario-tabelas-regras-por-secao.md` — não há conflito com o código.
