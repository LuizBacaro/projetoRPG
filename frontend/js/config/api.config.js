/**
 * Configuração da API — Single Responsibility (SOLID)
 * Determina a URL base conforme o ambiente (dev vs produção)
 *
 * ✅ Compatível com ES modules  → import { getApiUrl } from '...'
 * ✅ Compatível com scripts globais → window.getApiUrl('/combatentes')
 */

/** @type {boolean} true se estiver rodando em produção */
const IS_PRODUCTION = window.location.hostname === 'arena-de-combate-rpg.com.br';

/**
 * Em produção: '' (string vazia) — frontend servido pelo mesmo FastAPI,
 *              chamadas são relativas ao próprio domínio
 * Em dev:      'http://localhost:8000'
 * @type {string}
 */
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

/**
 * Monta URL completa: BASE_URL + /api + endpoint
 * @param {string} endpoint - ex: '/combatentes'
 * @returns {string}
 */
export const getApiUrl = (endpoint) => {
    return `${BASE_URL}${API_CONFIG.API_PREFIX}${endpoint}`;
};

/**
 * Ponte para scripts não-modulares (DanoCuraService, CondicaoService, ModalDanoCura)
 * que são carregados via <script> puro sem type="module"
 * Única linha adicionada em relação à versão original ✅
 */
window.getApiUrl  = getApiUrl;
window.API_CONFIG = API_CONFIG;

export { IS_PRODUCTION, BASE_URL };