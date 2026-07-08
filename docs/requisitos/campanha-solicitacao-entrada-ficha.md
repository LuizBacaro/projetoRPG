# Solicitação de entrada em campanha (ficha → mestre)

**Status:** implementado (Tormenta 20, D&D 3.5 e GURPS)  
**Data:** 2026-07  
**Relacionado:** [ADR 0005 — RBAC campanha vs perfil global](../adr/0005-rbac-campanha-vs-perfil-global.md)

## Problema

O campo **Campanha** na ficha era texto livre (`ficha_json.campanha`), sem vínculo com `campanha_id` no banco. Jogadores não conseguiam pedir entrada numa mesa existente; o mestre não tinha fluxo de aprovação.

## Decisão

1. **Fonte da verdade:** `personagem.campanha_id` (FK `*_campanhas.id`). O nome exibido vem da campanha ou de cache em `ficha_json.campanha` (legado).
2. **Entrada na mesa:** jogador **solicita**; mestre **aceita** ou **recusa**. Enquanto pendente, `campanha_id` permanece `null`.
3. **Exceção:** se o jogador já é `mestre_id` da campanha escolhida, a API **vincula direto** (sem solicitação).
4. **Descoberta:** `GET /<jogo>/campanhas/disponiveis` lista campanhas do jogo (id, nome, mestre_nome) para qualquer usuário autenticado no jogo.

## Contrato API (por jogo — Tormenta: `/api/v1/tormenta/campanhas`)

| Método | Rota | Quem | Efeito |
|--------|------|------|--------|
| GET | `/disponiveis` | autenticado no jogo | Lista campanhas para select na ficha |
| POST | `/solicitacoes` | dono do personagem | Cria solicitação `pendente` ou vincula se for mestre da campanha |
| GET | `/solicitacoes/minhas?personagem_id=` | dono do personagem | Solicitação ativa (pendente) do PJ |
| GET | `/solicitacoes/pendentes` | mestre de campanha / admin | Fila da aba «Pedidos de Acesso» + badge |
| GET | `/solicitacoes/historico` | mestre de campanha / admin | Pedidos resolvidos (aceitos/recusados/cancelados), aba «Histórico» |
| POST | `/solicitacoes/{id}/aceitar` | mestre da campanha / admin | `personagem.campanha_id = campanha_id`, status `aceita` |
| POST | `/solicitacoes/{id}/recusar` | mestre da campanha / admin | status `recusada` |
| DELETE | `/solicitacoes/{id}` | solicitante | Cancela solicitação `pendente` |

### Corpo `POST /solicitacoes`

```json
{ "campanha_id": 12, "personagem_id": 9 }
```

### Regras de negócio

- Personagem deve ser `tipo=jogador` e `dono_id = usuário`.
- Não solicitar se `personagem.campanha_id` já estiver preenchido (outra mesa).
- Uma solicitação `pendente` por par `(personagem_id, campanha_id)`.
- Mestre da campanha não pode solicitar a própria mesa como jogador externo — vinculação direta via checklist no dashboard ou auto-aceite na API.
- Monstros/NPCs: apenas mestre associa via mesa (`campanha_id` no POST do dashboard).

## Persistência (Tormenta)

Tabela `tormenta_campanha_solicitacoes`:

- `campanha_id`, `personagem_id`, `solicitante_id`
- `status`: `pendente` | `aceita` | `recusada` | `cancelada`
- índice único parcial: uma `pendente` por `(personagem_id, campanha_id)`

## Frontend

### Ficha (`ficha-personagem.html`)

- `<select id="f_campanha">` com opção vazia + campanhas de `/disponiveis`.
- Estados UI:
  - **Vinculado:** select desabilitado, valor = campanha atual (`campanha_id`).
  - **Pendente:** hint “Aguardando aprovação do mestre…”, botão cancelar.
  - **Livre:** ao escolher campanha → `POST /solicitacoes` (não grava `campanha_id` no PATCH da ficha).
- Módulo: `frontend/games/tormenta/js/t20-ficha-campanha-solicitacao.js`.
- `ficha_json.campanha` continua como rótulo legado; sincronizado ao aceitar.

### Dashboard (mestre)

- Aba/sub-aba dedicada **«Pedidos de Acesso»** (não mais popup bloqueante):
  - **Tormenta:** aba na mesa da campanha (ao lado de Combatentes/Arena), filtrada pela campanha ativa; badge com contagem de pendentes.
  - **D&D 3.5 / GURPS:** sub-aba dentro de Campanhas listando pedidos de todas as mesas do mestre (com nome da campanha por linha); badge no botão da sub-aba.
- Filtro **Pendentes / Histórico** por aba; histórico usa `GET /solicitacoes/historico`.
- Polling (~90s) apenas atualiza o badge e emite **toast leve** ao chegar novos pedidos; a decisão é tomada quando o mestre quiser.
- Aceitar/recusar por linha; após aceitar, mesa lista o PJ via `GET /personagens?campanha_id=`.

## Cache

- `fetch` com `cache: 'no-store'` nas listas e filas.
- Query `?v=` nos JS novos após deploy.

## Replicação para outros jogos

1. Copiar tabela `*_campanha_solicitacoes` e model no pacote `app.games.<slug>`.
2. Repetir rotas em `api/v1/campanhas.py` do jogo.
3. Service espelhando regras acima (ajustar model de personagem).
4. Frontend: adaptar prefixo API no `*CampanhaService` e módulo `*-ficha-campanha-solicitacao.js`.
5. Testes em `test_<slug>_campanhas_api.py`.

**Status por jogo:** Tormenta (referência), D&D 3.5 (`/campanhas`), GURPS (`/gurps/campanhas`) — implementados em 2026-07.

## Testes manuais (Tormenta)

1. Mestre A cria campanha “Mesa Alpha”.
2. Jogador B abre ficha do PJ → select mostra “Mesa Alpha”.
3. B escolhe campanha → toast “Solicitação enviada”.
4. A abre dashboard Campanhas → popup com pedido de B → Aceitar.
5. B recarrega ficha → campanha vinculada; mesa de A lista o PJ.
6. B tenta outra campanha → bloqueado (já vinculado).
7. Recusar: C solicita, A recusa → select volta ao livre.
