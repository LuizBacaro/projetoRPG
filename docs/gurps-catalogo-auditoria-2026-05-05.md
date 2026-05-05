# Auditoria do Catalogo GURPS (2026-05-05)

## Escopo

Atualizacao do arquivo `backend/app/games/gurps/catalogs/gurps_personagens_sumario_catalogo.json` com:

- completude de `vantagens`, `desvantagens` e `pericias`;
- deduplicacao por nome normalizado;
- normalizacao de grafia/ruido de OCR;
- validacao via seed e endpoint da API.

## Fontes utilizadas

- `GURPS 4E - Modulo Basico - Personagens.pdf`
- tabelas:
  - vantagens: paginas 297-298;
  - desvantagens: paginas 299-300;
  - pericias: paginas 301-305.

## Resultado final

- vantagens: **177**
- desvantagens: **138**
- pericias: **128**
- duplicatas: **0** nas tres listas
- entradas com `Consultar livro`: **0** em vantagens/desvantagens

## Correcao de truncamentos

Foram corrigidos cortes que encerravam a lista antes do fim da tabela:

- pericias parava em `Materiais Perigosos/NTf`;
- vantagens parava em `Queda de Gato`;
- desvantagens parava em `Preguica`.

## Normalizacoes de OCR (exemplos)

- `Acessorios` -> `Acessorios`
- `Carga Util` -> `Carga Util`
- `Adestramento de Atiiniais` -> `Adestramento de Animais`
- `Luta Greco-llomana` -> `Luta Greco-Romana`
- `Macjuiagem/NT` -> `Maquiagem/NT`
- `Matcmatica/NT` -> `Matematica/NT`
- `Veneficio/NT` -> `Veneficio/NT`

## Validacao de dados

Seed executado com sucesso:

- comando: `python3 scripts/seed_gurps_catalogo_ficha.py`
- resultado: `177 vantagens, 138 desvantagens, 128 pericias`

Validacao via API autenticada:

- endpoint: `GET /api/v1/gurps/personagens/catalogo/lite-ficha`
- retorno: `177 vantagens`, `138 desvantagens`, `128 pericias`

## Observacoes

- houve consolidacao de uma duplicata em desvantagens apos normalizacao (`Aversao`).
- catalogo pronto para uso em ambiente de desenvolvimento e staging.
