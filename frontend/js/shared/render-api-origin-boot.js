/**
 * Script clássico (não-module): deve correr antes de `api-url-global.js` e de
 * qualquer `<script type="module">` que importe `render-api-origin.js` / `api.config.js`.
 *
 * Regras:
 * - Vercel (*.vercel.app): front e API em hosts diferentes → fallback para API Render de prod
 *   (sobrescrito no build por `scripts/inject-render-api-origin.cjs` + ARENA_RENDER_API_ORIGIN).
 * - Domínio Arena em produção: API continua no Render (mesmo padrão que o inject força em Vercel).
 * - Resto (localhost, outro *.onrender.com com FastAPI+estático no mesmo serviço): mesma origem
 *   que a página → evita CORS no login em projetorpg-dev, etc.
 */
(function (g) {
    var prodApiRender = 'https://projetorpg-7ih3.onrender.com';
    if (!g.location || !g.location.hostname) {
        g.__ARENA_RENDER_API_ORIGIN__ = prodApiRender;
        return;
    }
    var h = g.location.hostname;
    if (h.endsWith('.vercel.app')) {
        g.__ARENA_RENDER_API_ORIGIN__ = prodApiRender;
        return;
    }
    if (
        h === 'arena-de-combate-rpg.com.br' ||
        h === 'www.arena-de-combate-rpg.com.br'
    ) {
        g.__ARENA_RENDER_API_ORIGIN__ = prodApiRender;
        return;
    }
    g.__ARENA_RENDER_API_ORIGIN__ = g.location.origin;
})(typeof window !== 'undefined' ? window : typeof globalThis !== 'undefined' ? globalThis : self);
