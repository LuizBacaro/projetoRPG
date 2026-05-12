/**
 * Origem da API em produção: definida por `render-api-origin-boot.js` em
 * `window.__ARENA_RENDER_API_ORIGIN__` (evita duplicar a URL em ESM).
 *
 * Importante: ler sempre em tempo de chamada — não exportar constante
 * congelada na primeira avaliação do módulo (cache do browser + ordem de scripts).
 *
 * Se `ARENA_RENDER_API_ORIGIN` no build da Vercel for por engano o domínio do front
 * (apex/www arena-de-combate-rpg.com.br), os pedidos iam para /api no Vercel → 404.
 * Corrigimos em runtime para a API no Render (alinhado ao default do inject).
 */
const _FALLBACK_API_RENDER = "https://projetorpg-7ih3.onrender.com";

function _hostnameLooksLikeArenaStaticSite(hostname) {
    return (
        hostname === "arena-de-combate-rpg.com.br" ||
        hostname === "www.arena-de-combate-rpg.com.br"
    );
}

export function getRenderApiOrigin() {
    if (typeof window === "undefined" || !window.__ARENA_RENDER_API_ORIGIN__) {
        throw new Error(
            'Arena: inclua <script src="/js/shared/render-api-origin-boot.js"></script> ' +
                "antes dos módulos que importam render-api-origin.js ou api.config.js"
        );
    }
    var raw = String(window.__ARENA_RENDER_API_ORIGIN__).trim();
    if (!raw) {
        return _FALLBACK_API_RENDER;
    }
    try {
        var u = new URL(raw);
        if (_hostnameLooksLikeArenaStaticSite(u.hostname)) {
            return _FALLBACK_API_RENDER;
        }
    } catch (_e) {
        return _FALLBACK_API_RENDER;
    }
    return raw;
}
