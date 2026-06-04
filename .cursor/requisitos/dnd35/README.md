# Requisitos D&D 3.5 (Arena TTRPG)

Especificações em `*.md` desta pasta descrevem mecânicas **D&D 3.5** (modificadores de habilidade, BBA, slots de magia 3.5, etc.).

**Antes de implementar:** seguir o gate em [.cursor/requisitos/README.md](../README.md) e [AGENTS.md](../../../AGENTS.md).

## Jogo distinto de D&D 5E

**`dnd35` e `dnd5e` são dois `game_slug` separados.** Nunca tratar como a mesma edição nem como “variante” uma da outra.

| | **D&D 3.5 (`dnd35`)** | **D&D 5E (`dnd5e`)** |
|---|------------------------|----------------------|
| Requisitos | Esta pasta (`dnd35/`) | [.cursor/requisitos/dnd5e/](../dnd5e/) |
| Backend | `backend/app/games/dnd35/` | `backend/app/games/dnd5e/` |
| Frontend | `frontend/games/dnd35/` | `frontend/games/dnd5e/` |
| Skill conjuração | [dnd-spellcasting-conventions](../../skills/dnd-spellcasting-conventions/SKILL.md) (3.5) | Não usar skill 3.5 para 5e |
| Exemplo meio-elfo | +2 CHA, +2 perícias | +2 CHA, dois +1 em atributos, 1 perícia |

### Proibido

- Implementar RF de `dnd5e/` em código `dnd35/` (ou o inverso).
- Copiar UI, catálogo, fórmulas ou payloads entre os dois sem issue explícita de equivalência.
- Reutilizar utilitários de um jogo no outro (ex.: `dnd5e-raca-util.js` em `frontend/games/dnd35/`).
- Ler requisito 5e ao alterar ficha/arena 3.5, salvo para **documentar divergência** — não para portar regra.

### Permitido

- Código **compartilhado da plataforma** em `app.shared.*`, `frontend/js/shared/`, auth, deploy — sem regras de jogo.

## Código de produção

| Área | Caminho |
|------|---------|
| API / regras / seeds | `backend/app/games/dnd35/` |
| Ficha, grimório, arena | `frontend/games/dnd35/` |
| Conjuração (canónico) | [docs/regras-conjuracao-dnd-arena.md](../../../docs/regras-conjuracao-dnd-arena.md) |

## Mapa RF (esta pasta)

| Ficheiro | Tema |
|----------|------|
| `01-habilidades-dnd35.md` | Seis atributos, modificadores, ganhos por nível |
| `02-raças-dnd35.md` | Sete raças, ajustes e traços |
| `03-classes-dnd35.md` | Classes e progressão 3.5 |
| `04-combate-dnd35.md` | Combate e arena 3.5 (incl. vínculos animais via `incluir_vinculos`) |
| `05-magia-dnd35.md` | Magia e slots 3.5 |
| `06-pericias-dnd35.md` | Perícias |
| `07-talentos-feitos-dnd35.md` | Talentos (feats) |
| `08-equipamento-dnd35.md` | Equipamento |
| `09-companheiro-animal-dnd35.md` | Companheiro animal (**Druida / Ranger**) |
| `10-familiar-dnd35.md` | Familiar (**Mago / Feiticeiro**; PHB p. ~40; ficha + arena) |
| `11-monstros-dnd35.md` | Monstros/NPC (DMG) — bestiário mínimo e trilha futura |
