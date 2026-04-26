/**
 * Origem da API em produção: definida por `render-api-origin-boot.js` em
 * `window.__ARENA_RENDER_API_ORIGIN__` (evita duplicar a URL em ESM).
 */
function resolveRenderApiOrigin() {
    if (typeof window === 'undefined' || !window.__ARENA_RENDER_API_ORIGIN__) {
        throw new Error(
            'Arena: inclua <script src="/js/shared/render-api-origin-boot.js"></script> ' +
            'antes dos módulos que importam render-api-origin.js ou api.config.js'
        );
    }
    return window.__ARENA_RENDER_API_ORIGIN__;
}

export const RENDER_API_ORIGIN = resolveRenderApiOrigin();
