/**
 * Retry/circuit breaker para fetch da API (cold start Render → 503).
 * Compatível com scripts clássicos (ficha Tormenta não carrega api.config.js).
 * Idempotente com o wrapper ES module em games/dnd35/js/config/api.config.js.
 */
(function (global) {
    if (typeof global === 'undefined' || typeof global.fetch !== 'function') return;
    if (global.__ARENA_FETCH_RESILIENCE_INSTALLED__) return;
    global.__ARENA_FETCH_RESILIENCE_INSTALLED__ = true;

    var RETRY_ATTEMPTS = 3;
    var RETRY_ATTEMPTS_REGRAS_POST = 5;
    var RETRY_BASE_DELAY_MS = 300;
    var RETRY_BASE_DELAY_MS_503 = 900;
    var CIRCUIT_BREAKER_THRESHOLD = 5;
    var CIRCUIT_BREAKER_COOLDOWN_MS = 8000;

    var originalFetch = global.fetch.bind(global);
    var breaker = { state: 'closed', failures: 0, openedAt: 0 };

    function sleep(ms) {
        return new Promise(function (resolve) {
            setTimeout(resolve, ms);
        });
    }

    function openCircuit() {
        breaker.state = 'open';
        breaker.openedAt = Date.now();
    }

    function closeCircuit() {
        breaker.state = 'closed';
        breaker.failures = 0;
        breaker.openedAt = 0;
    }

    function isIdempotentMethod(method) {
        return ['GET', 'HEAD', 'OPTIONS'].indexOf(method) !== -1;
    }

    function isApiCall(url) {
        return url.indexOf('/api/v1') !== -1 || url.indexOf('/api/') !== -1;
    }

    function isSafeRetryablePost(url) {
        return !!url && url.indexOf('/tormenta/regras/') !== -1;
    }

    function maxAttemptsFor(method, url) {
        if (isIdempotentMethod(method)) return RETRY_ATTEMPTS;
        if (method === 'POST' && isSafeRetryablePost(url)) return RETRY_ATTEMPTS_REGRAS_POST;
        return 1;
    }

    function shouldRetry(response, error) {
        if (error) return error.name !== 'AbortError';
        if (!response) return false;
        return response.status >= 500;
    }

    global.fetch = async function (input, init) {
        var requestInit = init || {};
        var method = (requestInit.method || 'GET').toUpperCase();
        var url = typeof input === 'string' ? input : (input && input.url) || '';

        if (!isApiCall(url)) {
            return originalFetch(input, requestInit);
        }

        if (breaker.state === 'open') {
            var elapsed = Date.now() - breaker.openedAt;
            if (elapsed < CIRCUIT_BREAKER_COOLDOWN_MS) {
                var fastFail = new Error(
                    'Circuit breaker aberto para API. Aguarde alguns segundos e tente novamente.'
                );
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
                    if (breaker.state === 'half-open' || breaker.failures > 0) closeCircuit();
                    return response;
                }

                var retryable = shouldRetry(response, null) && maxAttempts > 1;
                if (!retryable || attempt === maxAttempts) {
                    if (retryable && response.status !== 503) {
                        breaker.failures += 1;
                        if (breaker.failures >= CIRCUIT_BREAKER_THRESHOLD) openCircuit();
                    } else if (breaker.state === 'half-open') {
                        closeCircuit();
                    }
                    return response;
                }
            } catch (error) {
                lastError = error;
                var retryErr = shouldRetry(null, error) && maxAttempts > 1;
                if (!retryErr || attempt === maxAttempts) {
                    if (retryErr) {
                        breaker.failures += 1;
                        if (breaker.failures >= CIRCUIT_BREAKER_THRESHOLD) openCircuit();
                    }
                    throw error;
                }
            }

            var jitter = Math.floor(Math.random() * 120);
            var statusHint = lastResponse && lastResponse.status;
            var base =
                statusHint === 503 || statusHint === 502 || statusHint === 504
                    ? RETRY_BASE_DELAY_MS_503
                    : RETRY_BASE_DELAY_MS;
            await sleep(base * Math.pow(2, attempt - 1) + jitter);
        }

        if (lastError) throw lastError;
        return lastResponse;
    };
})(typeof window !== 'undefined' ? window : self);
