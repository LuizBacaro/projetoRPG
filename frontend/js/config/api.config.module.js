/**
 * api.config.module.js
 * Para importação em módulos ES6
 * SRP: Exportar apenas para módulos
 */

const _hostname = window.location.hostname;
const IS_PRODUCTION =
    _hostname === 'arena-de-combate-rpg.com.br' || _hostname === 'www.arena-de-combate-rpg.com.br';
const BASE_URL = IS_PRODUCTION ? '' : window.location.origin;

const API_CONFIG = {
    BASE_URL: BASE_URL,
    API_PREFIX: '/api/v1',
    ENDPOINTS: {
        COMBATENTES: '/combatentes',
        COMBATE: '/combate',
        CONDICOES: '/condicoes'
    },
    RESILIENCE: {
        RETRY_ATTEMPTS: 3,
        RETRY_BASE_DELAY_MS: 300,
        CIRCUIT_BREAKER_THRESHOLD: 3,
        CIRCUIT_BREAKER_COOLDOWN_MS: 8000,
    },
};

function getApiUrl(endpoint) {
    return BASE_URL + API_CONFIG.API_PREFIX + endpoint;
}

function sleep(ms) {
    return new Promise(function(resolve) { setTimeout(resolve, ms); });
}

function installFetchResilience() {
    if (typeof window === 'undefined' || typeof window.fetch !== 'function') {
        return;
    }

    if (window.__ARENA_FETCH_RESILIENCE_INSTALLED__) {
        return;
    }

    window.__ARENA_FETCH_RESILIENCE_INSTALLED__ = true;

    var originalFetch = window.fetch.bind(window);
    var breaker = {
        state: 'closed', // closed | open | half-open
        failures: 0,
        openedAt: 0,
    };

    function openCircuit() {
        breaker.state = 'open';
        breaker.openedAt = Date.now();
        window.dispatchEvent(new CustomEvent('api:circuit-open', {
            detail: {
                threshold: API_CONFIG.RESILIENCE.CIRCUIT_BREAKER_THRESHOLD,
                cooldownMs: API_CONFIG.RESILIENCE.CIRCUIT_BREAKER_COOLDOWN_MS,
            },
        }));
    }

    function closeCircuit() {
        breaker.state = 'closed';
        breaker.failures = 0;
        breaker.openedAt = 0;
        window.dispatchEvent(new CustomEvent('api:circuit-close'));
    }

    function shouldRetry(method, response, error) {
        if (error) {
            return error.name !== 'AbortError';
        }

        if (!response) {
            return false;
        }

        if (response.status >= 500) {
            return true;
        }

        return false;
    }

    function isIdempotentMethod(method) {
        return ['GET', 'HEAD', 'OPTIONS'].indexOf(method) !== -1;
    }

    window.fetch = async function(input, init) {
        var requestInit = init || {};
        var method = (requestInit.method || 'GET').toUpperCase();
        var url = typeof input === 'string' ? input : (input && input.url) || '';
        var isApiCall = url.indexOf(API_CONFIG.API_PREFIX) !== -1 || url.indexOf('/api/') !== -1;

        if (!isApiCall) {
            return originalFetch(input, requestInit);
        }

        if (breaker.state === 'open') {
            var elapsed = Date.now() - breaker.openedAt;
            if (elapsed < API_CONFIG.RESILIENCE.CIRCUIT_BREAKER_COOLDOWN_MS) {
                var fastFail = new Error('Circuit breaker aberto para API. Aguarde alguns segundos e tente novamente.');
                fastFail.name = 'CircuitBreakerOpenError';
                throw fastFail;
            }
            breaker.state = 'half-open';
        }

        var allowRetry = isIdempotentMethod(method);
        var maxAttempts = allowRetry ? API_CONFIG.RESILIENCE.RETRY_ATTEMPTS : 1;
        var lastError = null;
        var lastResponse = null;

        for (var attempt = 1; attempt <= maxAttempts; attempt++) {
            try {
                var response = await originalFetch(input, requestInit);
                lastResponse = response;

                if (response.ok) {
                    if (breaker.state === 'half-open' || breaker.failures > 0) {
                        closeCircuit();
                    }
                    return response;
                }

                var retryableByStatus = shouldRetry(method, response, null);
                if (!retryableByStatus || attempt === maxAttempts) {
                    if (retryableByStatus) {
                        breaker.failures += 1;
                        if (breaker.failures >= API_CONFIG.RESILIENCE.CIRCUIT_BREAKER_THRESHOLD) {
                            openCircuit();
                        }
                    } else if (breaker.state === 'half-open') {
                        closeCircuit();
                    }
                    return response;
                }
            } catch (error) {
                lastError = error;
                var retryableByError = shouldRetry(method, null, error);

                if (!retryableByError || attempt === maxAttempts) {
                    if (retryableByError) {
                        breaker.failures += 1;
                        if (breaker.failures >= API_CONFIG.RESILIENCE.CIRCUIT_BREAKER_THRESHOLD) {
                            openCircuit();
                        }
                    }
                    throw error;
                }
            }

            var jitter = Math.floor(Math.random() * 80);
            var delayMs = (API_CONFIG.RESILIENCE.RETRY_BASE_DELAY_MS * Math.pow(2, attempt - 1)) + jitter;
            await sleep(delayMs);
        }

        if (lastError) {
            throw lastError;
        }

        return lastResponse;
    };
}

installFetchResilience();

export { IS_PRODUCTION, BASE_URL, API_CONFIG, getApiUrl };