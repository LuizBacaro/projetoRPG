/**
 * Origem da API em produção: definida por `render-api-origin-boot.js` em
 * `window.__ARENA_RENDER_API_ORIGIN__` (evita duplicar a URL em ESM).
 *
 * Importante: ler sempre em tempo de chamada — não exportar constante
 * congelada na primeira avaliação do módulo (cache do browser + ordem de scripts).
 */
export function getRenderApiOrigin() {
    if (typeof window === 'undefined' || !window.__ARENA_RENDER_API_ORIGIN__) {
        throw new Error(
            'Arena: inclua <script src="/js/shared/render-api-origin-boot.js"></script> ' +
                'antes dos módulos que importam render-api-origin.js ou api.config.js'
        );
    }
    return window.__ARENA_RENDER_API_ORIGIN__;
}
