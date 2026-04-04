const CONFIG = {
    API_URL: (() => {
        const hostname = window.location.hostname;

        if (hostname === 'localhost' || hostname === '127.0.0.1') {
            return 'http://localhost:8000';
        }

        // ✅ API no Render — separada do frontend (Vercel)
        // Substitua pela URL gerada pelo Render ao criar o serviço
        return 'https://arena-de-combate-rpg-api.onrender.com';
    })(),

    API_VERSION: '/api',
    REQUEST_TIMEOUT: 10000,
};

Object.freeze(CONFIG);