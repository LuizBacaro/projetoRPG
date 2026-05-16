# Visão e fontes legais

## Objetivo do levantamento

- Mapear **tudo o que o sistema precisa** para suportar Tormenta 20 (criação de personagem, ficha, combate futuro, listas) de forma **rastreável** (livro → requisito → código → teste).
- Servir de guia para **catálogos dinâmicos** (talentos, magias, equipamentos, poderes) sem duplicar o livro inteiro no repositório.

## Direitos autorais (Jambo Editora / Tormenta 20)

- **Não** reproduzir no repositório texto longo nem tabelas completas do livro (valores, descrições extensas de poderes, etc.).
- O que **pode** ficar no repo:
  - **Estrutura** de dados (chaves JSON, nomes de campos, fórmulas genéricas do tipo d20 “modificador = ⌊(valor−10)/2⌋” quando for regra matemática trivial e universal).
  - **Referência de página** e nome da tabela (“Modificadores de Habilidade”, p. X).
  - **Critérios de aceite** e pseudocódigo que não copiem redação do livro.
- Valores tabulares (custos por pontuação, CD, preços) devem ser **introduzidos por quem tem licença de uso** (tu, no teu ambiente), preferencialmente em ficheiros em `docs/tormenta/tabelas/` ou seeds privados, conforme política do projeto.

## “Regra da fonte” vs “produto Arena”

Para cada mecanismo, o inventário em `02-inventario-tabelas-regras-por-secao.md` distingue:

1. **O que o livro exige** (resumo, sem copiar).
2. **O que a Arena implementa na v1** (MVP: ficha digital, cálculos auxiliares, listas estáticas ou dinâmicas).
3. **O que fica para depois** (automação total de multiclasse, validação de pré-requisitos de todos os poderes, etc.).
