// API em produção: origem do Render (boot) ou mesmo host; dev local = mesma origem. CORS: ALLOWED_ORIGINS no Render.
import { getRenderApiOrigin } from '/js/shared/render-api-origin.js?v=3';
var _h = typeof window !== 'undefined' ? window.location.hostname : '';
var IS_LOCAL =
    _h === 'localhost' ||
    _h === '127.0.0.1' ||
    _h === '[::1]' ||
    _h.endsWith('.localhost');
var IS_PRODUCTION = _h === 'arena-de-combate-rpg.com.br' || _h === 'www.arena-de-combate-rpg.com.br';

function resolveApiBaseUrl() {
    if (IS_LOCAL && typeof window !== 'undefined') {
        return window.location.origin;
    }
    return getRenderApiOrigin();
}

var API_CONFIG = {
    get BASE_URL() {
        return resolveApiBaseUrl();
    },
    API_PREFIX: '/api/v1',
    ENDPOINTS: {
        COMBATENTES: '/combatentes',
        COMBATE: '/combate',
        CONDICOES: '/condicoes'
    },
    RESILIENCE: {
        RETRY_ATTEMPTS: 3,
        RETRY_BASE_DELAY_MS: 300,
        /** POSTs de preview Tormenta em cold start Render (503 readiness/DB). */
        RETRY_ATTEMPTS_REGRAS_POST: 5,
        RETRY_BASE_DELAY_MS_503: 900,
        CIRCUIT_BREAKER_THRESHOLD: 5,
        CIRCUIT_BREAKER_COOLDOWN_MS: 8000,
    },
};

function getApiUrl(endpoint) {
    return resolveApiBaseUrl() + API_CONFIG.API_PREFIX + endpoint;
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

        // 502/503/504: cold start Render, readiness middleware, Neon momentâneo
        if (response.status === 502 || response.status === 503 || response.status === 504) {
            return true;
        }

        if (response.status >= 500) {
            return true;
        }

        return false;
    }

    function isIdempotentMethod(method) {
        return ['GET', 'HEAD', 'OPTIONS'].indexOf(method) !== -1;
    }

    /**
     * POSTs de `/tormenta/regras/*` são cálculos (preview/validar) sem mutar ficha —
     * seguros para retry em 503 de cold start (o login já fazia isso via auth-session).
     */
    function isSafeRetryablePost(url) {
        if (!url) return false;
        return url.indexOf('/tormenta/regras/') !== -1;
    }

    function maxAttemptsFor(method, url) {
        if (isIdempotentMethod(method)) {
            return API_CONFIG.RESILIENCE.RETRY_ATTEMPTS;
        }
        if (method === 'POST' && isSafeRetryablePost(url)) {
            return API_CONFIG.RESILIENCE.RETRY_ATTEMPTS_REGRAS_POST;
        }
        return 1;
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

        var maxAttempts = maxAttemptsFor(method, url);
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

                var retryableByStatus = shouldRetry(method, response, null) && maxAttempts > 1;
                if (!retryableByStatus || attempt === maxAttempts) {
                    if (retryableByStatus && response.status !== 503) {
                        // 503 de cold start não deve abrir o breaker (rajadas da ficha)
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
                var retryableByError = shouldRetry(method, null, error) && maxAttempts > 1;

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

            var jitter = Math.floor(Math.random() * 120);
            var statusHint = lastResponse && lastResponse.status;
            var base =
                statusHint === 503 || statusHint === 502 || statusHint === 504
                    ? API_CONFIG.RESILIENCE.RETRY_BASE_DELAY_MS_503
                    : API_CONFIG.RESILIENCE.RETRY_BASE_DELAY_MS;
            var delayMs = base * Math.pow(2, attempt - 1) + jitter;
            await sleep(delayMs);
        }

        if (lastError) {
            throw lastError;
        }

        return lastResponse;
    };
}

installFetchResilience();

window.getApiUrl = getApiUrl;
window.API_CONFIG = API_CONFIG;

export { IS_PRODUCTION, API_CONFIG, getApiUrl, resolveApiBaseUrl as BASE_URL };