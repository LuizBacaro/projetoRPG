/**
 * graceful-degradation.js
 * Helpers para inicializacao resiliente do frontend.
 */

function _normalizeError(error, fallbackMessage) {
    if (!error) return fallbackMessage;
    if (typeof error === 'string') return error;
    if (typeof error.message === 'string' && error.message.trim()) return error.message.trim();
    return fallbackMessage;
}

function _showToast(message) {
    if (window.Toast && typeof window.Toast.error === 'function') {
        window.Toast.error(message);
        return true;
    }

    if (window.NotificationService && typeof window.NotificationService.erro === 'function') {
        window.NotificationService.erro(message);
        return true;
    }

    if (window.NotificationService && typeof window.NotificationService.mostrarErro === 'function') {
        window.NotificationService.mostrarErro(message);
        return true;
    }

    return false;
}

function _injectBanner(scope, message) {
    const id = `degraded-${scope}`;
    if (document.getElementById(id)) return;

    const banner = document.createElement('div');
    banner.id = id;
    banner.style.cssText = [
        'position:fixed',
        'top:0',
        'left:0',
        'right:0',
        'z-index:9999',
        'padding:10px 14px',
        'background:#7f1d1d',
        'color:#fff',
        'font-size:14px',
        'box-shadow:0 2px 8px rgba(0,0,0,.25)',
    ].join(';');
    banner.textContent = message;
    document.body.appendChild(banner);
}

export function reportDegradedMode(scope, error, fallbackMessage) {
    const message = _normalizeError(error, fallbackMessage);
    console.error(`[graceful:${scope}]`, error || message);
    if (!_showToast(message)) {
        _injectBanner(scope, message);
    }
    return message;
}

export function safeBootstrap(scope, factory, fallbackMessage) {
    try {
        return factory();
    } catch (error) {
        reportDegradedMode(scope, error, fallbackMessage || `Falha ao iniciar ${scope}.`);
        return null;
    }
}

export async function safeBootstrapAsync(scope, factory, fallbackMessage) {
    try {
        return await factory();
    } catch (error) {
        reportDegradedMode(scope, error, fallbackMessage || `Falha ao iniciar ${scope}.`);
        return null;
    }
}

export function installGlobalErrorGuards(scope) {
    if (window.__gracefulGuardsInstalled) return;
    window.__gracefulGuardsInstalled = true;

    window.addEventListener('error', (event) => {
        reportDegradedMode(
            scope || 'app',
            event.error || event.message,
            'Ocorreu um erro inesperado. Alguns recursos podem ficar indisponiveis.'
        );
    });

    window.addEventListener('unhandledrejection', (event) => {
        reportDegradedMode(
            scope || 'app',
            event.reason,
            'Falha assíncrona nao tratada. A interface entrou em modo degradado.'
        );
    });
}
