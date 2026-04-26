/**
 * Script clássico (não-module): deve correr antes de `api-url-global.js` e de
 * qualquer `<script type="module">` que importe `render-api-origin.js` / `api.config.js`.
 *
 * Única string literal da origem HTTPS da API (Render) no frontend.
 */
(function (g) {
    g.__ARENA_RENDER_API_ORIGIN__ = 'https://projetorpg-7ih3.onrender.com';
})(typeof window !== 'undefined' ? window : typeof globalThis !== 'undefined' ? globalThis : self);
