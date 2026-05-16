# Plano de Melhorias — Magias e Grimorio

> Checklist incremental focado nos requisitos dos documentos:
> - requisistos_cadastro_magias/documento_v1_20260330.json
> - requisistos_cadastro_grimorio/grimorio_v1_20260330.json

---

## Magias (Admin)

- [x] M01 — RF16–RF20: Importacao via Excel (.xlsx/.xls)
  - [x] Backend: upload de arquivo (.xlsx/.xls)
  - [x] Backend: validacao por linha
  - [x] Backend: preview antes de confirmar
  - [x] Backend: importacao parcial com relatorio de erros
  - [x] Backend: download de modelo de planilha
  - [x] Frontend: tela de importacao (upload/preview/confirmar)
  - [x] Frontend: baixar relatorio de erros e estados de progresso

- [x] M02 — RF10–RF11: Historico de alteracoes de magias
  - [x] Backend: persistir snapshot anterior/novo por alteracao (criacao, edicao, desativacao, reativacao, exclusao)
  - [x] Backend: endpoint de consulta (`GET /magias/{id}/historico`)
  - [x] Frontend: exibicao do historico (lista/modal)

- [x] M03 — RF08: Separacao clara PT-BR x EN no formulario
  - [x] Abas separadas no modal: "Dados principais (PT-BR)" e "Tradução (EN)"

- [x] M04 — RF28–RF29: Tela de visualizacao completa + alternancia PT/EN

- [x] M05 — RF32–RF33: Ordenacao e paginacao na listagem admin
  - Ordenar por nome/escola/nivel
  - Seletor 20/50/100

- [x] M06 — rn_011: Validacao de dominios permitidos (lista fixa D&D 3.5)

---

## Grimorio

- [x] G01 — RF08–RF09 + rn_012–rn_013: Adicao automatica por nivel para classes de acesso completo
  - [x] Backend: sincronizacao automatica por nivel para Clerigo, Druida, Ranger e Paladino ao listar grimorio
  - [x] Backend: origem `AUTO_NIVEL` e protecao contra duplicacao
  - [x] Backend: filtros de alinhamento e dominios de Clerigo com dados de Combatente expostos

- [x] G02 — RF11–RF12 + rn_001..rn_007: Validacao de alinhamento e dominios opostos
  - [x] Backend: filtros/restricoes implementados no GrimorioService para alinhamento e dominios opostos
  - [x] Backend: bloqueio na adicao manual quando magia divina conflita com alinhamento/dominios
  - [x] Backend: alinhamento/dominios expostos no modelo/API de Combatente
  - [x] Frontend: ficha permite visualizar e editar alinhamento/dominios do personagem

- [x] G03 — RF15: Controle de limite de magias conhecidas por classe/nivel
  - [x] Backend: bloqueio por limite de magias conhecidas (Bardo/Feiticeiro) por nivel de magia
  - [x] Backend: bloqueio de adicao manual acima do nivel maximo conjuravel para a classe
  - [x] Politica Mago definida: grimorio aberto por aprendizado (sem teto de conhecidas por nivel)

- [x] G04 — RF02: Secao separada para magias de dominio no grimorio do Clerigo
  - [x] Backend: resposta do grimorio com metadados de dominio (`magia_e_magia_dominio`, `magia_dominios`)
  - [x] Frontend: secao dedicada "Magias de Dominio" no grimorio de Clerigo

- [x] G05 — RF07 + rn_008: Mensagem e regras para Ranger/Paladino abaixo do nivel 4
  - [x] Backend: bloqueio de adicao manual de magia para Ranger/Paladino abaixo do nivel 4
  - [x] Backend: notificacao informativa `SEM_MAGIAS_ATE_NIVEL_4`
  - [x] Frontend: mensagem dedicada na UI do grimorio e estado visual para classe sem acesso

- [x] G06 — RF10: Notificacoes de magias adicionadas automaticamente
  - [x] Backend: emissao de notificacao `MAGIAS_ADICIONADAS` ao sincronizar magias automáticas por nível
  - [x] Frontend: realce visual dedicado para diferenciar notificacao de auto-adicao

- [x] G07 — RF30: Navegacao anterior/proximo no modal de detalhes
  - [x] Modal com anterior/proximo sem fechar
  - [x] Indicador de posicao e atalhos por teclado (setas/esq-dir + Esc)

---

## Andamento

- [x] Etapa 1 concluida: M01 (backend + frontend)
- [x] Etapa 2 concluida: M02, M03, M04, M05, M06 (todos os itens de Magias Admin)
- [x] Etapa 3 concluida: G01–G07 (todos os itens de Grimorio)
- [x] Consolidacao: lista de dominios centralizada no backend (`GET /magias/dominios`); FichaPersonagemController carrega dinamicamente com fallback
- [x] Mapeamento Feiticeiro→Mago ja aplicado no backend (magias.py linha 120–121)
