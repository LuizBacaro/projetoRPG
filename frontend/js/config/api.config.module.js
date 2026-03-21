/**
 * api.config.module.js
 * Para importação em módulos ES6
 * SRP: Exportar apenas para módulos
 */

const IS_PRODUCTION = window.location.hostname === 'arena-de-combate-rpg.com.br';
const BASE_URL = IS_PRODUCTION ? '' : 'http://localhost:8000';

const API_CONFIG = {
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

export { IS_PRODUCTION, BASE_URL, API_CONFIG, getApiUrl };