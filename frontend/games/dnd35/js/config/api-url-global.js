/**
 * getApiUrl síncrono para páginas que carregam scripts clássicos antes de módulos ES.
 * Mantém a mesma regra de origem que api.config.js (local → origin; caso contrário → Render).
 */
(function (global) {
    var h = global.location.hostname;
    var isLocal =
        h === 'localhost' ||
        h === '127.0.0.1' ||
        h === '[::1]' ||
        (h.endsWith && h.endsWith('.localhost'));
    var RENDER_API_ORIGIN = 'https://projetorpg-7ih3.onrender.com';
    var base = isLocal ? global.location.origin : RENDER_API_ORIGIN;

    global.getApiUrl = function (path) {
        var p = path == null ? '' : String(path);
        if (p.charAt(0) !== '/') {
            p = '/' + p;
        }
        return base + '/api/v1' + p;
    };
})(typeof window !== 'undefined' ? window : self);
