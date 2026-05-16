# Grimório MB na mesa (ficha web)

Este documento resume o que o aplicativo cobre hoje para **magias do Módulo Básico (MB)** e como a mesa pode contornar lacunas.

## O que o catálogo cobre

- A listagem principal segue a **tabela de magias MB pp.307–317** (nomes e resumos curtos). O texto integral das magias **não** é distribuído no catálogo por restrição de licença; use o livro oficial na mesa.
- Entradas marcadas como **stub** ou fora dessa faixa de páginas podem existir para testes ou rascunhos — não confunda com a lista oficial do livro.
- **Magias de outras fontes** (suplementos, aventuras, conteúdo além do MB) não são garantidas no JSON; o mestre pode registrar efeitos em **notas** ou marcar **conjuração manual** (ver abaixo).

## Elegibilidade ao grimório

- O botão do grimório e os `POST` de magias exigem **classe conjuradora MB** com **nível** suficiente (ex.: paladino/ranger a partir do 5º, conforme `conjuracao_classe_mb.json`).
- **`tormenta_conjuracao_manual_mb: true`** em `ficha_json` libera o grimório para multiclasse, talentos, inventor, homebrew etc., conforme decisão da mesa.
- **`tormenta_nivel_conjurador_mb`** (número 1–40): nível usado **só** para essa checagem e para o cálculo de PM máx. de conjuração na pré-visualização, quando o nível total do personagem não reflete os níveis de conjurador (multiclasse).
- **`tormenta_niveis_classe_mb`** (opcional): na ficha, bloco **«Multiclasse — níveis em classes conjuradoras MB»** (linhas com classe + nível); quando «nível de conjuração MB» está vazio, o app soma esses níveis para o grimório. Pode continuar a editar no JSON se preferires.

## UI da ficha

- **Editar ficha**: campos opcionais «Nível de conjuração MB», «PM gastos na sessão» e «Preparadas / anotação de sessão» gravam as chaves acima e `tormenta_grimorio_sessao_mb` (`pm_gastos_sessao`, `preparadas_anotacao`). São lembretes de mesa; o app não impõe limite de PM gasto automaticamente.
- **Modal Grimório**: busca, filtros por **círculo** e **tipo**, opção **«Só magias MB da classe (tipo + círculos por nível)»** (ligada por defeito quando não está em conjuração manual): o servidor aplica `catalogo_por_classe_mb` + `classe_mb_slug` + `nivel_mb` (usa o nível de conjuração efetivo da ficha). Desligue para ver o catálogo completo (ex.: referência, mesa).
- A faixa de texto sob o título do modal combina **custo em PM por círculo** (regra MB) com uma **pré-visualização** de CD base (10 + modificador da chave), modificador e PM máx. de conjuração, quando a classe MB é conjuradora.

## Regenerar o catálogo

- Fonte de verdade da listagem: `backend/app/games/tormenta/data/sources/listagem_magias_mb_pp307-317.txt`.
- Script: `backend/scripts/build_magias_mb_catalogo_from_listagem_txt.py` → gera `magias_mb_catalogo.json`.
- Checagem leve (duplicatas, slugs, campos mínimos): `python backend/scripts/check_magias_mb_catalogo.py` (exit 1 se erros).

## API útil

- `GET /api/v1/tormenta/regras/magias` — catálogo paginado (`q`, `circulo`, `tipo`, `escola`, `skip`, `limit`). Com `catalogo_por_classe_mb=true`, `classe_mb_slug` e `nivel_mb` (e opcionalmente `conjuracao_manual_mb=true` para não filtrar), o servidor restringe ao tipo de lista e ao círculo máximo (`magias_progressao_mb_t20.py`). Cada item inclui `descricao_curta` e o campo reservado `descricao_longa` (normalmente `null`).
- `GET /api/v1/tormenta/regras/conjuracao-preview` — `classe_slug`, `nivel`, atributos `*_valor`, opcional `nivel_conjurador`; resposta inclui `magias_lista_tipo` e `magias_circulo_max` para a UI alinhar o catálogo.
