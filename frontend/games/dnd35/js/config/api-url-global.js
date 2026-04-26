/**
 * getApiUrl síncrono para páginas que carregam scripts clássicos antes de módulos ES.
 * Exige `render-api-origin-boot.js` antes deste ficheiro (define `window.__ARENA_RENDER_API_ORIGIN__`).
 */
(function (global) {
    var h = global.location.hostname;
    var isLocal =
        h === 'localhost' ||
        h === '127.0.0.1' ||
        h === '[::1]' ||
        (h.endsWith && h.endsWith('.localhost'));
    var RENDER_API_ORIGIN = global.__ARENA_RENDER_API_ORIGIN__;
    if (!RENDER_API_ORIGIN) {
        throw new Error(
            'Arena: carregue /js/shared/render-api-origin-boot.js antes de api-url-global.js'
        );
    }
    var base = isLocal ? global.location.origin : RENDER_API_ORIGIN;

    global.getApiUrl = function (path) {
        var p = path == null ? '' : String(path);
        if (p.charAt(0) !== '/') {
            p = '/' + p;
        }
        return base + '/api/v1' + p;
    };
})(typeof window !== 'undefined' ? window : self);
