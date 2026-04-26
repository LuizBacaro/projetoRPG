# `frontend/games/dnd35/`

Bundle visual do sistema **Dungeons & Dragons 3.5**.

> Pacote em construção. As páginas e CSS reais ainda vivem em
> `frontend/{pages,css,js}/`. A migração será feita em PR separado
> depois que `backend/app/games/dnd35/` estiver totalmente extraído.

## O que pertence aqui (alvo)

| Subpasta              | Conteúdo                                                                  |
|-----------------------|---------------------------------------------------------------------------|
| `pages/`              | `dashboard.html`, `arena-combate.html`, `ficha-personagem.html`, `magias.html`, `pericias.html`, `pericias-ficha.html`, `arena.html` |
| `css/`                | `arena.css`, `combatentes.css`, `ficha-personagem.css`, `grimorio.css`, `magias-admin.css`, `pericias.css`, `pericias_novo.css`, `modal-condicao.css`, `item-card-unified.css` |
| `js/services/`        | Clientes HTTP do backend D&D 3.5 (`CombatenteService`, `MagiaService`, `AtaqueService`, `ArmaduraProtecaoService`, `CampanhaService`, `CondicaoService`, `DanoCuraService`, `DivindadeCustomService`, `EquipamentoService`, `GrimorioService`, `MagiaPreparadaService`, `MagiaSlotService`, `MagiasAdminService`, `PericiaService`, `TalentoService`) |
| `js/controllers/`     | `ArenaController`, `CondicaoController`, `ConfiguracaoController`, `FichaPersonagemController`, `GrimorioController`, `MagiasAdminController`, `PericiaController`, `PericiaFichaController` |

## O que NÃO pertence aqui

- `AuthService`, `UsuarioService`, `MembershipsAdminService`,
  `NotificationService`, `UploadService` → globais, ficam em
  `frontend/js/services/` (futuro `frontend/shared/`).
- `Toast`, `ModalConfirm`, `layout.css`, `variables.css`, `botoes.css`,
  `responsivo.css` → globais.
- `pages/login.html`, `pages/selecionar-jogo.html`, `pages/usuarios.html`
  → globais (Auth Hub UI).
