var IS_PRODUCTION = window.location.hostname === 'arena-de-combate-rpg.com.br';
var BASE_URL = IS_PRODUCTION ? '' : 'http://localhost:8000';

var API_CONFIG = {
    BASE_URL: BASE_URL,
    API_PREFIX: '/api/v1',
    ENDPOINTS: {
        COMBATENTES: '/combatentes',
        COMBATE: '/combate',
        CONDICOES: '/condicoes'
    }
};

function getApiUrl(endpoint) {
    return BASE_URL + API_CONFIG.API_PREFIX + endpoint;
}

window.getApiUrl = getApiUrl;
window.API_CONFIG = API_CONFIG;

export { IS_PRODUCTION, BASE_URL, API_CONFIG, getApiUrl };