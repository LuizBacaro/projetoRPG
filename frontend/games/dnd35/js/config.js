const CONFIG = {
    API_URL: (() => {
        const hostname = window.location.hostname;

        if (hostname === 'localhost' || hostname === '127.0.0.1') {
            return 'http://localhost:8000';
        }

        // Backend e frontend servidos pelo mesmo serviço Render — mesmo origin
        return '';
    })(),

    API_VERSION: '/api',
    REQUEST_TIMEOUT: 10000,
};

Object.freeze(CONFIG);