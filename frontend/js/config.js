const CONFIG = {
    API_URL: (() => {
        const hostname = window.location.hostname;

        if (hostname === 'localhost' || hostname === '127.0.0.1') {
            return 'http://localhost:8000';
        }

        // ✅ URL do Railway (domínio próprio após DNS propagar)
        return 'https://arena-de-combate-rpg.com.br';
    })(),

    API_VERSION: '/api',
    REQUEST_TIMEOUT: 10000,
};

Object.freeze(CONFIG);