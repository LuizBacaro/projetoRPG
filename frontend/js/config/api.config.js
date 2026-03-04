/**
 * Configuração da API — Single Responsibility (SOLID)
 * Compatível com ES modules (import) E scripts globais (window)
 */

const IS_PRODUCTION = window.location.hostname === 'arena-de-combate-rpg.com.br';

const BASE_URL = IS_PRODUCTION ? '' : 'http://localhost:8000';

export const API_CONFIG = {
    BASE_URL,
    API_PREFIX: '/api',
    ENDPOINTS: {
        COMBATENTES: '/combatentes',
        COMBATE:     '/combate',
        CONDICOES:   '/condicoes',
    }
};

export const getApiUrl = (endpoint) => {
    return `${BASE_URL}${API_CONFIG.API_PREFIX}${endpoint}`;
};

// ✅ Ponte para scripts não-modulares (DanoCuraService, CondicaoService, ModalDanoCura)
window.getApiUrl  = getApiUrl;
window.API_CONFIG = API_CONFIG;

export { IS_PRODUCTION, BASE_URL };