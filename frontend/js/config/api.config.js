/**
 * Configuração centralizada da API
 * Single Responsibility: única fonte de verdade para URLs
 * Compatível com ES modules (import) E scripts globais (window)
 */

const IS_PRODUCTION = !['localhost', '127.0.0.1'].includes(window.location.hostname);

const BASE_URL = IS_PRODUCTION ? '' : 'http://127.0.0.1:8000';

const API_CONFIG = {
    BASE_URL,
    API_PREFIX: '/api',
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
const getApiUrl = (endpoint) => {
    return `${BASE_URL}${API_CONFIG.API_PREFIX}${endpoint}`;
};

// ✅ Expõe globalmente para scripts não-modulares (DanoCuraService, CondicaoService, ModalDanoCura)
window.getApiUrl  = getApiUrl;
window.API_CONFIG = API_CONFIG;

// ✅ Exporta para ES modules (ConfiguracaoController, CombatenteService, etc.)
export { getApiUrl, API_CONFIG, IS_PRODUCTION, BASE_URL };