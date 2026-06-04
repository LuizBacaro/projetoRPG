/**
 * Sessão JWT: warm-up da API, refresh silencioso e POST com retry em 503 (cold start).
 */
import { getApiUrl } from '/games/dnd35/js/config/api.config.js?v=20260604';

const STORAGE_TOKEN = 'token';
const STORAGE_REFRESH = 'refresh_token';
const STORAGE_USUARIO = 'usuario';

export function getApiOrigin() {
    return getApiUrl('/auth/me').replace(/\/api\/v1\/auth\/me$/, '');
}

export function persistSession(data, { clearGame = true } = {}) {
    if (!data || !data.access_token) {
        return;
    }
    localStorage.setItem(STORAGE_TOKEN, data.access_token);
    if (data.refresh_token) {
        localStorage.setItem(STORAGE_REFRESH, data.refresh_token);
    }
    if (data.usuario) {
        localStorage.setItem(STORAGE_USUARIO, JSON.stringify(data.usuario));
    }
    if (clearGame) {
        localStorage.removeItem('game_slug_ativo');
        localStorage.removeItem('game_nome_ativo');
    }
}

export function clearSession() {
    localStorage.removeItem(STORAGE_TOKEN);
    localStorage.removeItem(STORAGE_REFRESH);
    localStorage.removeItem(STORAGE_USUARIO);
    localStorage.removeItem('game_slug_ativo');
    localStorage.removeItem('game_nome_ativo');
}

function sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Acorda o Render / confirma que a API responde antes do login.
 */
export async function warmupApi({ timeoutMs = 25000 } = {}) {
    const url = `${getApiOrigin()}/health/live`;
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeoutMs);
    try {
        const res = await fetch(url, { method: 'GET', signal: controller.signal });
        return res.ok;
    } catch (_err) {
        return false;
    } finally {
        clearTimeout(timer);
    }
}

export async function refreshSession() {
    const refreshToken = localStorage.getItem(STORAGE_REFRESH);
    if (!refreshToken) {
        return null;
    }
    const res = await fetch(getApiUrl('/auth/refresh'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refreshToken }),
    });
    if (!res.ok) {
        return null;
    }
    const data = await res.json();
    persistSession(data, { clearGame: false });
    return data;
}

export async function trySilentRefresh() {
    const data = await refreshSession();
    return Boolean(data && data.access_token);
}

/**
 * POST JSON com retry em 503/502/504 (startup do banco ou cold start).
 */
export async function postJsonWithRetry(
    endpoint,
    body,
    {
        maxAttempts = 4,
        baseDelayMs = 800,
        onRetry = null,
    } = {}
) {
    let lastResponse = null;
    let lastError = null;

    for (let attempt = 1; attempt <= maxAttempts; attempt++) {
        try {
            const res = await fetch(getApiUrl(endpoint), {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body),
            });
            lastResponse = res;
            if (res.ok || (res.status !== 503 && res.status !== 502 && res.status !== 504)) {
                return res;
            }
            if (attempt < maxAttempts && typeof onRetry === 'function') {
                onRetry(attempt, res.status);
            }
        } catch (err) {
            lastError = err;
            if (attempt < maxAttempts && typeof onRetry === 'function') {
                onRetry(attempt, 0);
            }
        }
        if (attempt < maxAttempts) {
            const jitter = Math.floor(Math.random() * 200);
            await sleep(baseDelayMs * attempt + jitter);
        }
    }

    if (lastResponse) {
        return lastResponse;
    }
    throw lastError || new Error('Falha de rede');
}

export async function fetchOAuthGoogleStatus() {
    try {
        const res = await fetch(getApiUrl('/auth/oauth/google/status'));
        if (!res.ok) {
            return { google_enabled: false };
        }
        return await res.json();
    } catch (_err) {
        return { google_enabled: false };
    }
}

export function redirectAfterLogin() {
    window.location.href = '/pages/selecionar-jogo.html';
}
