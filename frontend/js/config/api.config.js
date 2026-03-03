/**
 * Configuração centralizada da API
 * Single Responsibility: única fonte de verdade para URLs
 * Carregado via <script> — sem módulos ES6
 */
(function () {
    const IS_PRODUCTION = !['localhost', '127.0.0.1'].includes(window.location.hostname);

    window.API_CONFIG = {
        BASE_URL:   IS_PRODUCTION ? '' : 'http://127.0.0.1:8000',
        API_PREFIX: '/api',
        ENDPOINTS: {
            COMBATENTES: '/combatentes',
            COMBATE:     '/combate',
            CONDICOES:   '/condicoes',
        }
    };

    window.getApiUrl = function (endpoint) {
        return `${window.API_CONFIG.BASE_URL}${window.API_CONFIG.API_PREFIX}${endpoint}`;
    };
})();