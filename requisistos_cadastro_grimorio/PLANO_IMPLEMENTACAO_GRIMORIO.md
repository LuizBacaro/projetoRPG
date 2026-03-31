# Plano de Implementacao - Grimorio (v1)

Base: requisitos de `grimório_v1_20260330.json`.
Objetivo: fechar 100% dos RFs com rastreabilidade e validacao objetiva.

## 1) Status Atual (diagnostico rapido)

### Implementados
- RF01, RF02, RF04, RF05, RF06, RF07, RF08, RF09, RF10, RF11, RF12, RF13, RF14, RF15, RF16, RF17, RF18, RF19, RF20, RF21, RF22, RF23, RF24, RF25, RF26, RF27, RF29, RF30.

### Parciais
- Sem itens parciais na versao atual.

### Pendentes/Com divergencia relevante
- Sem pendencias criticas abertas nesta fase; seguir backlog dos itens parciais.

---

## 2) Plano por Prioridade

## P1 - Regras de negocio criticas (fechar primeiro)

### [x] RF11 - Excluir automaticamente magias incompativeis por alinhamento
- Problema atual: regras bloqueiam adicao, mas nao removem automaticamente magias ja existentes apos mudanca de alinhamento.
- Entrega esperada:
  - Rotina de reconciliacao ao listar/notificar ou ao salvar perfil magico.
  - Remocao automatica dos itens invalidos no grimorio daquela classe.
- Validacao:
  - Teste automatizado cobrindo mudanca de alinhamento e exclusao automatica.

### [x] RF12 - Excluir automaticamente magias de dominios opostos (clerigo)
- Problema atual: filtro e bloqueio existem para adicao, mas falta reconciliacao para estoque ja gravado.
- Entrega esperada:
  - Reconciliacao de dominio oposto para CLERIGO no fluxo de sincronizacao.
- Validacao:
  - Teste com troca de dominios e remocao automatica no grimorio.

### [x] RF14 - Notificacao de magias pendentes com niveis
- Problema atual: notificacao `SELECAO_PENDENTE` informa somente quantidade total.
- Entrega esperada:
  - Incluir distribuicao por nivel no campo `dados` (ex.: `{ quantidade_pendente, por_nivel: {0: x, 1: y, ...} }`).
- Validacao:
  - Teste de API verificando payload completo da notificacao.

---

## P2 - UX funcional de selecao e detalhe

### [x] RF16 - Filtros completos na selecao (titulo, escola, nivel, componentes)
- Problema atual: painel de adicionar filtra apenas por texto.
- Entrega esperada:
  - Controles de filtro no painel de adicao.
  - Aplicacao combinada dos filtros.
- Validacao:
  - Teste de interface/manual com combinacoes de filtros.

### [x] RF17 - Preview completo antes de adicionar
- Problema atual: nao ha preview completo dedicado no fluxo de adicao.
- Entrega esperada:
  - Preview lateral/modal da magia selecionada no painel de adicao.
- Validacao:
  - Fluxo: selecionar magia -> visualizar detalhes -> confirmar adicao.

### [x] RF28 - Modal de detalhes 100% aderente ao schema
- Problema atual: divergencia de nomes de campos no frontend para alguns atributos (subescola e alvo/area), podendo exibir "-" indevidamente.
- Entrega esperada:
  - Ajustar mapeamento para nomes canonicos do backend.
  - Conferir exibicao de todos os campos listados no RF28.
- Validacao:
  - Caso de teste com magia preenchida em todos os campos de detalhe.

---

## P3 - Fechamento de cobertura e refinos

### [x] RF10 - Notificacao de novas magias deve listar quais magias entraram
- Problema atual: mostra apenas quantidade.
- Entrega esperada:
  - Salvar lista resumida de nomes/ids no `dados` da notificacao `MAGIAS_ADICIONADAS`.
- Validacao:
  - Teste da notificacao com lista de itens adicionados.

### [x] RF27 - Exibir paginas por nivel (Mago)
- Problema atual: mostra total geral, sem quebra por nivel.
- Entrega esperada:
  - Componente visual com contagem por nivel + total.
- Validacao:
  - Conferencia com conjunto de magias de niveis mistos.

### [x] RF03 - Card resumido (conjuracao e alcance visiveis no card)
- Problema atual: parte desses dados esta mais forte no detalhe que no resumo.
- Entrega esperada:
  - Garantir os campos exigidos no card resumido sem poluir layout.
- Validacao:
  - Inspecao visual e checklist de campos do RF03.

### [x] RF09 - Adicao automatica de dominio (conforme regra de dominio do clerigo)
- Entrega realizada:
  - Testes dedicados de progressao por nivel + dominios escolhidos.
- Validacao:
  - Cenarios com clerigo, dois dominios e niveis diferentes.

### [x] RF13 e RF15 - Revisao final de aderencia
- RF13: garantir que a selecao mostra somente magias validas por classe e nivel (inclusive casos limite).
- RF15: manter limites de conhecidas por tabela para classes aplicaveis e cobertura de regressao.
- Validacao:
  - Matriz de testes por classe (Bardo, Feiticeiro, Mago).
- Entrega realizada:
  - Frontend: painel de selecao de adicao passou a exibir apenas magias da classe e dentro do nivel conjuravel.
  - Backend: matriz de regressao validada para Bardo, Feiticeiro e Mago.

---

## 3) Sequencia sugerida de execucao

1. Sprint A (P1): RF11, RF12, RF14.
2. Sprint B (P2): RF16, RF17, RF28.
3. Sprint C (P3): RF10, RF27, RF03, RF09, revisao RF13/RF15.

---

## 4) Checklist de conclusao por item

Para marcar um RF como concluido, exigir:
- [ ] Implementacao no backend/frontend (quando aplicavel)
- [ ] Teste automatizado cobrindo o cenario principal
- [ ] Teste de regressao de cenario relacionado
- [ ] Validacao manual no fluxo da ficha
- [ ] Atualizacao deste plano (status + data)

---

## 5) Log de acompanhamento

### 2026-03-31
- Diagnostico inicial consolidado e plano criado.
- Pendencias prioritarias mapeadas: RF11, RF12, RF14, RF16, RF17, RF28, RF10, RF27.
- Sprint A iniciada e etapa tecnica concluida para RF11/RF12/RF14.
- Backend: reconciliacao automatica de magias invalidas por alinhamento/dominio adicionada no fluxo de listagem.
- Backend: notificacao `SELECAO_PENDENTE` passou a incluir `por_nivel` com distribuicao de pendencias.
- Frontend: texto da notificacao atualizado para exibir niveis pendentes quando disponiveis.
- Testes: `backend/tests/test_grimorio_api.py` atualizado e validado (20 passed).
- Sprint B iniciada.
- RF16 concluido com filtros completos no painel de adicao (titulo, escola, nivel e componentes).
- RF17 concluido com preview da magia antes da confirmacao de adicao.
- RF28 concluido com ajuste de mapeamento de campos e exibicao de niveis por classe no modal.
- Sprint C iniciada.
- RF10 concluido com payload de notificacao enriquecido (`magias_nomes`) e exibicao no frontend.
- RF27 concluido com indicador de paginas por nivel no cabecalho do grimorio de Mago.
- Teste novo validado: `test_grimorio_notificacao_magias_adicionadas_inclui_nomes` (1 passed).
- RF09 concluido com testes dedicados:
  - `test_grimorio_clerigo_auto_adiciona_apenas_dominios_escolhidos_no_nivel`
  - `test_grimorio_clerigo_adiciona_magia_de_dominio_ao_subir_nivel`
  - Resultado: 2 passed.
- RF13/RF15 avancaram com testes de regressao para Bardo:
  - `test_grimorio_limita_magias_conhecidas_bardo_por_nivel`
  - `test_grimorio_bardo_bloqueia_adicao_acima_nivel_conjuravel`
  - Resultado: 2 passed.
- RF13/RF15 concluidos com matriz completa por classe:
  - Feiticeiro: limite por nivel + bloqueio acima do nivel conjuravel.
  - Mago: sem limite de conhecidas + bloqueio acima do nivel conjuravel.
  - Bardo: limite por nivel + bloqueio acima do nivel conjuravel.
  - Resultado: 6 passed.
- Refino UX no painel "Adicionar do catálogo da classe":
  - contador dinamico de resultados e magia selecionada;
  - atalho de teclado (↑/↓ para navegar e Enter para adicionar);
  - CTA "Adicionar esta magia" fixo no preview em desktop para reduzir rolagem.
  - atalhos extras de navegacao (PgUp/PgDn, Home/End) para listas longas;
  - resumo com posicao da selecao (ex.: 5/87) para orientar o usuario;
  - protecao contra Enter duplo para evitar adicao repetida acidental.

### Proxima atualizacao
- Executar validacao manual final de interface (ficha + grimorio) e consolidar checklist de encerramento.

### Andamento atual
- Sprint C em andamento em 2026-03-31.
- RF03: card resumido passou a exibir conjuracao e alcance na listagem.
- RF28: modal passou a exibir componentes detalhados com complemento de componente_extra quando houver.
- Validacao backend concluida: suite completa `backend/tests/test_grimorio_api.py` executada com sucesso.
- Resultado final: 26 passed em 13.14s.
- UX do painel de adicao refinada para listas longas com foco em legibilidade e velocidade de selecao.

## 6) Checklist Manual de Encerramento (UI)

### Fluxo principal do grimorio
- [ ] Abrir grimorio em personagem conjurador e validar carregamento sem erros no console.
- [ ] Confirmar agrupamento por nivel e contadores por grupo.
- [ ] Confirmar filtros da listagem principal: titulo, escola, nivel, componentes e favoritas.

### Painel de adicionar (RF16/RF17/RF13)
- [ ] Validar filtros do painel de adicionar: titulo, escola, nivel e componentes.
- [ ] Validar preview antes de adicionar (nome, nivel, escola, componentes, conjuracao, alcance e descricao).
- [ ] Confirmar que magias acima do nivel conjuravel nao aparecem para selecao.

### Modal de detalhes (RF28/RF29/RF30)
- [ ] Conferir campos do modal: escola, subescola, descritor, niveis por classe, componentes detalhados, conjuracao, alcance, alvo/area, duracao, resistencia, RM, descricao e anotacoes.
- [ ] Validar navegacao anterior/proxima sem fechar modal.
- [ ] Validar favoritar/anotar/remover (Mago) via modal.

### Notificacoes e regras (RF10/RF11/RF12/RF14/RF18)
- [ ] Validar notificacao de magias adicionadas com quantidade e nomes.
- [ ] Validar notificacao de selecao pendente com distribuicao por nivel.
- [ ] Validar notificacao de troca disponivel para Bardo/Feiticeiro em nivel valido.
- [ ] Validar reconciliacao automatica ao alterar alinhamento/dominios de Clerigo.

## 7) Roteiro Guiado de Validacao Manual (Execucao Unica)

Use este roteiro na ordem para validar tudo com o menor retrabalho.

### Preparacao
- [ ] Subir backend e frontend no ambiente local.
- [ ] Abrir a ficha de um personagem Clerigo e um Mago (IDs conhecidos no seu ambiente).
- [ ] Abrir console do navegador para monitorar erros.

### Bloco A - Listagem, filtros e cards (RF01, RF03, RF04, RF05)
1. Abrir Grimorio do personagem conjurador.
- Esperado: carrega sem erro visual/console; grupos por nivel aparecem.
2. Usar busca por titulo, filtro de escola, nivel e componente.
- Esperado: filtros combinam corretamente os resultados.
3. Ativar favoritas.
- Esperado: somente magias favoritas ficam visiveis.
4. Verificar card resumido.
- Esperado: card mostra nome, nivel, escola, componentes, conjuracao e alcance.

### Bloco B - Selecao manual (RF13, RF16, RF17)
1. Abrir painel Adicionar magia conhecida.
2. Aplicar filtros do painel (titulo, escola, nivel, componente).
- Esperado: lista responde aos 4 filtros.
3. Clicar em Preview de uma magia.
- Esperado: painel de preview mostra nome, nivel, escola, componentes, conjuracao, alcance e descricao.
4. Confirmar adicao no preview.
- Esperado: magia entra no grimorio e some da lista de disponiveis.
5. Testar classe/nível limite (ex.: Bardo/Feiticeiro/Mago em nivel baixo).
- Esperado: magias acima do nivel conjuravel nao aparecem para selecao.

### Bloco C - Modal de detalhes (RF28, RF29, RF30)
1. Abrir detalhes de uma magia.
- Esperado: modal mostra escola, subescola, descritor, niveis por classe, componentes detalhados, conjuracao, alcance, alvo/area, duracao, resistencia, RM, descricao e anotacoes.
2. Navegar Anterior/Proxima.
- Esperado: troca de magia sem fechar o modal.
3. Editar anotacao no modal.
- Esperado: anotacao persistida e reapresentada.

### Bloco D - Regras divinas e notificacoes (RF09, RF10, RF11, RF12, RF14, RF18)
1. No Clerigo, ajustar alinhamento para um valor que bloqueie uma magia existente.
- Esperado: reconciliacao remove automaticamente magia incompativel.
2. No Clerigo, ajustar dominios para criar dominio oposto a uma magia de dominio existente.
- Esperado: magia de dominio oposto e removida automaticamente.
3. Simular subida de nivel/classe com auto adicao.
- Esperado: notificacao MAGIAS_ADICIONADAS mostra quantidade e nomes das magias.
4. Verificar SELECAO_PENDENTE para Bardo/Feiticeiro.
- Esperado: notificacao mostra quantidade pendente e distribuicao por nivel.
5. Verificar TROCA_DISPONIVEL em nivel valido.
- Esperado: badge/notificacao de troca aparece para Bardo/Feiticeiro conforme regra.

### Criterio de encerramento
- [ ] Todos os blocos acima validados sem erro funcional.
- [ ] Sem erro no console durante os fluxos principais.
- [ ] Registrar evidencias (print ou anotacao curta) no log da sprint.
