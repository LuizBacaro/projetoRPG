# Progressao de Classes na Ficha (BBA, Resistencias e Habilidades Especiais)

Este documento consolida a implantacao da progressao automatica por classe/nivel e defesas derivadas na plataforma Arena TTRPG.

## Objetivo

Implementar, de ponta a ponta, o consumo das tabelas de classe (D&D 3.5) para preencher automaticamente na ficha:

- BBA (Bonus Base de Ataque), incluindo ataques iterativos.
- Resistencias (Fortitude, Reflexos, Vontade) com separacao entre base e total.
- Defesas (CA, Toque, Surpresa) calculadas automaticamente.
- Iniciativa para jogadores conforme regra de Destreza e talento.
- Habilidades Especiais por classe, com exibicao agrupada por nivel.

## Fonte de dados

- Catalogo consolidado: `docs/dados/tabelas_classes_catalogo.json`.
- Planilhas de origem: pasta `tabelas_classes_excel/`.
- Mapeamento de classes para tabelas: `backend/app/core/bonus_base_ataque.py` (`_TABLE_BY_CLASS`).

## Backend

### Motor de progressao

Arquivo: `backend/app/core/bonus_base_ataque.py`

- `calcular_bonus_base_ataque(classe, nivel)`: tenta catalogo e aplica fallback por progressao.
- `calcular_resistencias_base(classe, nivel)`: tenta catalogo e aplica fallback por progressao de TR.
- `calcular_habilidades_especiais_por_nivel(classe, nivel)`: extrai a coluna "Especial" cumulativamente ate o nivel alvo e retorna estrutura agrupada:
  - `[{ "nivel": 1, "habilidades": [...] }, ...]`
- `calcular_habilidades_especiais(classe, nivel)`: fallback legado em lista plana.

### Service de Combatente

Arquivo: `backend/app/services/combatente_service.py`

- Na criacao/atualizacao:
  - recalcula BBA;
  - recalcula resistencias base e total;
  - recalcula defesas (`ca`, `toque`, `surpresa`);
  - aplica regra de iniciativa para jogador (`mod DES + bonus de talento`);
  - preenche `habilidades_especiais`.
- Persistencia de `habilidades_especiais`:
  - formato atual preferencial: JSON string com agrupamento por nivel;
  - formato legado suportado: string simples separada por `|`.
- Sincronizacao em memoria (`_sincronizar_progressao_em_memoria`) corrige registros legados durante leitura.

### Inicializacao e backfill

Arquivo: `backend/app/core/init_db.py`

- `sincronizar_bonus_base_ataque_combatentes` atualiza dados legados:
  - BBA,
  - resistencias base/total,
  - defesas (CA/Toque/Surpresa),
  - habilidades especiais.

### Armadura/Item de Protecao e defesa

Arquivos:

- `backend/app/services/armadura_protecao_service.py`
- `backend/app/services/combatente_service.py`
- `backend/app/api/v1/armaduras_protecao.py`

Regras:

- O `bonus_ca` usado para defesa vem dos itens vinculados em `armaduras_protecao_jogador`.
- Incremento/decremento:
  - ao adicionar item de protecao, o bonus entra no total;
  - ao remover item, o bonus sai do total.
- Recalculo automatico e persistente:
  - `toque = 10 + mod DES`
  - `surpresa = 10 + bonus_ca_total_itens`
  - `ca = 10 + mod DES + bonus_ca_total_itens`
- Fallback legado:
  - quando nao ha itens vinculados, o backend preserva compatibilidade usando `ca` persistida para inferir bonus legado.

### Schema guard

Arquivo: `backend/app/main.py`

- Guard para coluna legada:
  - `combatentes.habilidades_especiais` (cria se nao existir).

## Banco de dados

Modelo: `backend/app/models/combatente.py`

- Campo adicionado:
  - `habilidades_especiais` (`String`, default vazio).

Observacao:

- Campo armazena texto para compatibilidade.
- Quando possivel, persistimos JSON serializado para permitir agrupamento por nivel no frontend.

## Contrato de API

Schema: `backend/app/schemas/combatente.py`

- `CombatenteResponse` expoe:
  - `bonus_base_ataque`,
  - `fortitude_base`, `reflexos_base`, `vontade_base`,
  - `habilidades_especiais`.

## Frontend

### Ficha de Personagem

Arquivos:

- `frontend/pages/ficha-personagem.html`
- `frontend/js/controllers/FichaPersonagemController.js`
- `frontend/css/ficha-personagem.css`
- `frontend/js/models/Combatente.js`

Implementacoes:

- Iniciativa com transparencia:
  - exibicao do valor final;
  - breakdown visual: `DES +X + talento +Y (+ outros quando aplicavel)`.
- Bloco novo abaixo de Resistencias:
  - "Habilidades Especiais".
  - renderiza agrupado por nivel (`Nivel N: habilidade1, habilidade2`).
- Compatibilidade de renderizacao:
  - se `habilidades_especiais` vier como JSON, usa agrupamento por nivel;
  - se vier em formato legado string, faz fallback para lista simples.

## Regras de negocio aplicadas

- BBA e TRs base seguem tabela da classe no catalogo; fallback por progressao canonica quando necessario.
- TR total = TR base + modificador de atributo:
  - Fortitude usa CON;
  - Reflexos usa DES;
  - Vontade usa SAB.
- Defesas:
  - Toque usa apenas Destreza (`10 + mod DES`);
  - Surpresa usa apenas bonus de armadura (`10 + bonus_ca_total_itens`);
  - CA usa Destreza + armadura (`10 + mod DES + bonus_ca_total_itens`).
- Fonte do bonus de armadura:
  - campo `bonus_ca` de cada item em `Armadura/Item de Protecao`.
  - soma de todos os itens ativos vinculados ao combatente.
- Fluxo incremental:
  - adicionar item aumenta `surpresa/ca` imediatamente;
  - remover item reduz `surpresa/ca` imediatamente.
- Jogador:
  - Iniciativa = modificador de Destreza.
  - Talento "Iniciativa Aprimorada" concede +4 adicional.
- Habilidades Especiais:
  - acumulativas ate o nivel atual;
  - deduplicadas;
  - apresentadas por nivel.

## Testes

Arquivo principal:

- `backend/tests/test_combatentes_api.py`

Coberturas atuais relevantes:

- BBA calculado por classe/nivel.
- Resistencias base e total.
- Defesas recalculadas por DES + bonus de armadura.
- Add/remove de item de protecao incrementa/decrementa `surpresa` e `ca`.
- Recalculo ao trocar classe/nivel.
- Bonus de iniciativa por talento.

## Rollout e operacao

- Ambiente legado e tolerado via schema guards + sincronizacao em memoria.
- Reinicio do backend aplica guardas de schema e sincroniza progressao quando necessario.
- Frontend permanece resiliente a formatos antigos de `habilidades_especiais`.

## Proximos passos sugeridos

- Expor em contrato dedicado `habilidades_especiais_por_nivel` (objeto tipado na API) para remover parsing de string no frontend.
- Adicionar testes unitarios especificos para parser de "Especial" por classe.
- Opcional: incluir tooltip explicando origem das habilidades (tabela de classe + nivel).
