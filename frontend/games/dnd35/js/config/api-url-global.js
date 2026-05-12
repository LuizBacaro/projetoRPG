/**
 * getApiUrl síncrono para páginas que carregam scripts clássicos antes de módulos ES.
 * Exige `render-api-origin-boot.js` antes deste ficheiro (define `window.__ARENA_RENDER_API_ORIGIN__`).
 */
(function (global) {
    function hostname() {
        return (global.location && global.location.hostname) || '';
    }

    function isLocalHost(h) {
        return (
            h === 'localhost' ||
            h === '127.0.0.1' ||
            h === '[::1]' ||
            (h.endsWith && h.endsWith('.localhost'))
        );
    }

    global.getApiUrl = function (path) {
        var h = hostname();
        var isLocal = isLocalHost(h);
        var apiOrigin = isLocal ? global.location.origin : global.__ARENA_RENDER_API_ORIGIN__;
        if (!apiOrigin) {
            throw new Error(
                'Arena: carregue /js/shared/render-api-origin-boot.js antes de api-url-global.js'
            );
        }
        var p = path == null ? '' : String(path);
        if (p.charAt(0) !== '/') {
            p = '/' + p;
        }
        return apiOrigin + '/api/v1' + p;
    };
})(typeof window !== 'undefined' ? window : self);
