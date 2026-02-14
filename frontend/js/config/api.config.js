/**
 * Configurações da API
 */
export const API_CONFIG = {
    BASE_URL: 'http://127.0.0.1:8000',
    API_PREFIX: '/api',
    ENDPOINTS: {
        COMBATENTES: '/combatentes',
        COMBATE: '/combate'
    }
};

export const getApiUrl = (endpoint) => {
    return `${API_CONFIG.BASE_URL}${API_CONFIG.API_PREFIX}${endpoint}`;
};