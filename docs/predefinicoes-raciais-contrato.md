# Pre-definicoes Raciais (Contrato Proposto)

Este documento descreve o contrato recomendado para usar o catalogo de racas em pre-definicoes de personagem.

## Fonte canonica

- Planilha: `Caracteristicas especiais.xlsx` (aba `Raças`)
- Gerador: `processar_caracteristicas_especiais_excel.py`
- Saida: `docs/dados/racas_caracteristicas_catalogo.json`

## Estrutura do catalogo JSON

Cada item em `racas` contem:

- `slug`: identificador estavel (`humanos`, `anoes`, `elfos`...)
- `nome`: nome exibivel da raca
- `modificadores_habilidade`: lista de objetos `{ atributo, valor }`
- `tamanho`: `Pequeno`, `Médio`, etc.
- `deslocamento_metros`: inteiro (ex.: 6, 9)
- `idiomas_iniciais`: lista de strings
- `talentos_especiais`: lista de strings
- `habilidades_especiais`: lista de strings
- `resistencias`: lista de strings
- `modificadores_ataque`: lista de strings
- `modificadores_defesa`: lista de strings
- `modificadores_pericia`: lista de strings
- `classe_favorecida`: string

## Contrato backend sugerido

### 1) Listar racas

- `GET /api/v1/racas`
- Response (resumo):
  - `slug`, `nome`, `tamanho`, `deslocamento_metros`, `classe_favorecida`

### 2) Detalhe da raca

- `GET /api/v1/racas/{slug}`
- Response (completo):
  - todos os campos do catalogo

### 3) Preview de pre-definicao em combatente

- `POST /api/v1/racas/{slug}/preview`
- Payload:
  - `base_attributes`: atributos atuais de entrada (forca, destreza, etc.)
  - `tipo` e `classe` opcionais (caso regras futuras variem por tipo/classe)
- Response:
  - `attributes_result` (base + modificadores raciais)
  - `defaults` (tamanho, deslocamento, idiomas, classe favorecida)
  - `passivos` (talentos/habilidades/resistencias/modificadores)
  - `warnings` (ex.: dado textual nao estruturado)

### 4) Aplicacao na criacao/edicao

- Durante `POST /combatentes` e `PUT /combatentes/{id}`:
  - entrada opcional `raca_slug`
  - backend aplica pre-definicoes com flag de controle:
    - `aplicar_predefinicoes_raciais=true|false` (default `true` na criacao)

## Regras operacionais recomendadas

- Pre-definicoes raciais devem ser aplicadas no backend (fonte unica de verdade).
- Frontend usa endpoint de preview para UX/transparencia antes de salvar.
- Campos textuais de beneficios devem permanecer como listas de string inicialmente.
- Nao interpretar automaticamente todos os textos em bonus numerico sem whitelist de regras.
- Sempre manter fallback para combatentes legados sem `raca_slug`.

## Escopo de primeira entrega

1. Disponibilizar endpoints `GET /racas` e `GET /racas/{slug}`.
2. Integrar `raca_slug` no fluxo de criacao de combatente.
3. Aplicar apenas:
   - modificadores de atributos,
   - tamanho,
   - deslocamento,
   - idiomas iniciais.
4. Exibir passivos textuais na ficha sem automatizar todos os calculos.

## Observacoes de normalizacao

- O catalogo atual preserva termos da planilha (alguns em texto livre).
- Antes de automatizar bonus numericos de combate/pericia/resistencia, criar tabela de regras estruturadas por tipo de bonus.
