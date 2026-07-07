# ADR 0005 — RBAC: mestre por campanha vs perfil global `mestre`

**Status:** aceite (implementado)  
**Data:** 2026-07  
**Contexto:** cadastro simplificado (PR 1) e RBAC por jogo (Tormenta, D&D 3.5, GURPS)

## Contexto

O cadastro público pedia escolha **mestre/jogador** e criava campanha D&D 3.5 no registro. Isso gerava:

- Fricção no onboarding (decisão antes de usar a plataforma).
- Acoplamento do Auth Hub ao módulo D&D 3.5.
- Confusão entre “mestre da plataforma” e “mestre de uma mesa”.

A mesma pessoa pode jogar em uma campanha e mestrar em outra.

## Decisão

1. **Cadastro público** (`POST /auth/registro`): sempre `perfil=jogador`. Campos legados `perfil` e `campanha_nome` são ignorados.
2. **Mestre na mesa** (Arena, monstros/NPCs, gestão de campanha): concedido quando o usuário é `mestre_id` de ao menos uma campanha **no jogo atual** (tabela `*_campanhas` do slug).
3. **Compatibilidade legada:** contas com `perfil=mestre` ou `administrador` continuam com acesso de GM em todos os jogos já migrados, via `usuario_e_mestre_global_ou_admin()` em `deps.py`.
4. **Admin global** permanece para governança (catálogos, usuários, magias D&D 3.5 admin, etc.).

### Matriz por jogo (pós-migração)

| Recurso | Jogador | Jogador + campanha própria | `perfil=mestre` legado | Admin |
|---------|---------|----------------------------|------------------------|-------|
| CRUD campanhas próprias | sim | sim | sim | sim (todas) |
| Arena / combate GM | não | sim | sim | sim |
| Monstros / NPCs | não | sim | sim | sim |
| Fichas tipo jogador | sim | sim | sim | sim |

Helpers por jogo: `usuario_e_mestre_dnd35`, `usuario_e_mestre_tormenta`, `usuario_e_mestre_gurps` e guards `requer_mestre_<jogo>_ou_admin`.

Frontend: `AuthService.carregarPodeMestrarNoJogoAtual()` consulta `GET /<jogo>/campanhas`; aba Campanhas visível para todos; Arena desbloqueia após criar campanha ou se já houver campanhas.

## Consequências

**Positivas**

- Modelo alinhado ao uso real de mesa de RPG.
- Onboarding mais simples; mestria é opt-in por jogo.
- RBAC testável por jogo sem alterar o enum global de uma vez.

**Negativas**

- Dupla fonte de verdade temporária (`perfil=mestre` global **ou** campanha).
- Contas legadas `mestre` sem campanha mantêm privilégio até rodar o script de limpeza.

## Depreciação de `PerfilUsuario.MESTRE`

- **Não** usar em novos cadastros (público nem rotina operacional).
- Admin pode ainda atribuir via `POST /usuarios` (casos excepcionais); preferir campanha.
- Script `backend/scripts/rebaixar_mestres_sem_campanha.py` rebaixa `mestre` → `jogador` quem não é `mestre_id` em nenhuma campanha (D&D 3.5, Tormenta, GURPS).
- Remoção do enum `MESTRE` fica para fase futura, após migração de produção e auditoria.

## Alternativas consideradas

| Alternativa | Motivo de rejeição |
|-------------|-------------------|
| Remover `MESTRE` do enum já | Quebra contas e tokens existentes sem janela de migração |
| Mestre só por campanha, sem legado | Perderia acesso de contas antigas até backfill manual |
| Flag `is_gm` global por usuário | Não modela “mestre só nesta mesa” |

## Revisão

Reavaliar quando D&D 5e e demais jogos adotarem o mesmo padrão de campanha, ou quando o script de rebaixamento tiver sido aplicado em produção com métricas estáveis.
