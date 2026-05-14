---
description: "Regras para alteracoes no frontend da Arena: arquitetura mista modulo/global, autenticacao, binds de eventos e qualidade visual."
applyTo: "frontend/**/*.{html,css,js}"
---

# Frontend Instructions

- A base e mista: parte usa ES Modules e parte usa scripts globais em `window`.
- Antes de refatorar, confirme o modo de carregamento do arquivo (modulo vs global).
- Nao converter para modulo sem controlar toda a cadeia de carregamento.

## API e Auth

- Use `window.getApiUrl(...)` ou helper de config existente; nao hardcode de API sem necessidade.
- Para auth no frontend, prefira `AuthService.getAuthHeader()` ou `AuthService.getToken()` com fallback consistente.
- Preserve envio de `Authorization: Bearer <token>` em servicos protegidos.

## Eventos e UI

- Evite novos handlers inline (`onclick`, `onchange`); prefira `addEventListener` em bootstrap/controlador.
- Em paginas administrativas, prefira `Toast` e `ModalConfirm` aos `alert()` e `confirm()` quando disponiveis.
- Manter direcao visual forte, intencional e responsiva; evitar UI generica.
- Reaproveitar tokens de `frontend/css/variables.css` quando possivel.

## Overlays estilo `equipamentos-overlay` (Tormenta e reaproveitamento D&D 3.5)

- Em `tormenta-ficha-dnd-parity.css`, a classe **`.equipamentos-overlay`** fica com `display: flex`, `position: fixed` e cobre o ecrã inteiro (modal sempre “montado”).
- Em **fichas Tormenta** (`tormenta-ficha.css`), cada overlay com esse padrão **tem de** ter uma regra do tipo `#meuModal.equipamentos-overlay:not(.is-open) { display: none !important; pointer-events: none; }` e o JavaScript deve **só** mostrar o modal com `classList.add('is-open')` e esconder com `remove('is-open')` (igual a `#modalEquipamentos` e `#modalTalentosMb`).
- **Não** confiar só em `aria-hidden` ou `style="display:none"` no HTML se o ficheiro de paridade continuar a forçar `display: flex` no overlay — o utilizador fica com a página bloqueada.
- Novo modal no mesmo padrão: acrescentar o **mesmo selector** em `tormenta-ficha.css` ao lado dos existentes, ou documentar exceção explícita no CSS de paridade.

## Convencoes Locais

- A Arena e sensivel a cache de script; se bug persistir apos patch correto, considerar cache-busting controlado.

## Especificacao minima (integracao)

- Integracao nova ou alteracao de contrato: alinhar campos ao **OpenAPI / schemas** do backend; criterios de aceite no PR/issue quando houver mudanca de comportamento visivel.
- Detalhe do fluxo: [docs/fluxo-spec-driven-leve.md](../../docs/fluxo-spec-driven-leve.md).
- Na tela de usuarios, manter filtros, badges de estado e acoes de governanca claramente visiveis.
