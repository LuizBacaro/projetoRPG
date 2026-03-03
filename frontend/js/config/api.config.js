/**
 * Configuração centralizada da API
 * Single Responsibility: única fonte de verdade para URLs
 * Open/Closed: novos ambientes sem modificar consumidores
 */

const IS_PRODUCTION = !['localhost', '127.0.0.1'].includes(window.location.hostname);

const BASE_URL = IS_PRODUCTION ? '' : 'http://127.0.0.1:8000';

export const API_CONFIG = {
    BASE_URL,
    API_PREFIX:    '/api',
    API_V1_PREFIX: '/api',   // backend usa /api (não /api/v1)
    ENDPOINTS: {
        COMBATENTES: '/combatentes',
        COMBATE:     '/combate',
        CONDICOES:   '/condicoes',
    }
};

/**
 * Monta URL completa: BASE_URL + /api + endpoint
 * @param {string} endpoint - ex: '/combatentes'
 * @returns {string}
 */
export const getApiUrl = (endpoint) => {
    return `${BASE_URL}${API_CONFIG.API_PREFIX}${endpoint}`;
};

export { IS_PRODUCTION, BASE_URL };