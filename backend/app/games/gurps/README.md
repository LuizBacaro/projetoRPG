# `backend/app/games/gurps/` — GURPS

Backend do sistema **GURPS** na plataforma multi-jogo.

## Escopo de implementação (G0.2)

O backend GURPS segue **Lite primeiro**:

- Priorizar ficha e arena jogáveis conforme GURPS Lite.
- Itens do *Módulo Personagens* (catálogos extensos, pré-requisitos avançados) entram apenas por issues explícitas.
- Ordem de turno na arena: **Velocidade básica (VB)**, desempate por **DX**, depois sorteio.

## API (`/api/v1/gurps/...`)

| Prefixo | Descrição |
|--------|-----------|
| `/gurps/personagens` | CRUD da ficha (atributos, vantagens, desvantagens, perícias, totais de pontos). |
| `/gurps/campanhas` | Campanhas (mestre/admin). |
| `/gurps/combate` | Arena: iniciar / status / avançar turno / finalizar (lista de IDs separada do combate D&D 3.5). |

Todas as rotas usam `dependencies=[Depends(requer_game_gurps)]` — com `MULTI_GAME_STRICT_MODE=true`, o JWT deve trazer `game_slug=gurps`.

## Persistência

Migration: `b1a2c3d4e5f6_add_gurps_core_tables.py` — tabelas `gurps_campanhas`, `gurps_personagens`, filhos de lista (`gurps_personagem_*`) e `gurps_combates`.

## Frontend

Páginas em `frontend/games/gurps/pages/` (`dashboard.html`, `ficha-personagem.html`), servidas em `/games/gurps/...`.

## Catálogo

`gurps` está **disponível** no seed em `app/shared/startup/game_catalog.py`. Membership é criado automaticamente com os slugs em `AUTO_ENROLL_MEMBERSHIP_GAME_SLUGS` (`app/shared/constants.py`).

## `extras_json` (G4.4)

`extras_json` existe para campos de ficha que ainda não viraram coluna canônica no banco.

### Contrato atual

- Tipo: objeto JSON (`dict`), nunca lista/string solta.
- Limite: `65_536` bytes em UTF-8 após serialização.
- Versionamento: chave `v` (inteiro). O backend preenche `v=1` quando omitido.
- Semântica: payload livre, mas as chaves abaixo são as mais esperadas hoje.

### Chaves de uso frequente (v1)

- `enc`: blocos de encargo/movimento.
- `hit`: anotações de localizações de acerto.
- `arma`: notas rápidas da arma da ficha.
- `equipamento`: bloco textual/objeto de equipamento extra.
- `rd` / `armadura_rd`: RD simplificada usada no fluxo de dano quando presente.

### Regra de evolução para colunas

Promover campo de `extras_json` para coluna SQL quando cumprir todos:

1. aparece de forma recorrente no fluxo de jogo (não só anotação);
2. precisa de filtro/ordenação/validação forte no backend;
3. já possui regra de negócio estável (sem semântica oscilante entre mesas).

### Estratégia de migração sem quebra

1. adicionar coluna nova (+ migration) sem remover dado antigo;
2. leitura prioriza coluna, com fallback em `extras_json`;
3. escrita passa a gravar na coluna e mantém compatibilidade por uma janela;
4. job de backfill opcional para registros legados;
5. após estabilizar, marcar chave de `extras_json` como deprecada na documentação.
