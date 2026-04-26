/**
 * Re-export do módulo principal (evita duplicar origem da API e resiliência do fetch).
 * Preferir importar diretamente de `./api.config.js`.
 */
export { IS_PRODUCTION, BASE_URL, API_CONFIG, getApiUrl } from './api.config.js';
