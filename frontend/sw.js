/**
 * Service Worker - Cache de Perícias
 * Permite que o usuário acesse as perícias mesmo offline
 */

const CACHE_NAME = 'pericias-v1';
const urlsToCache = [
    '/pericias.html',
    '/css/variables.css',
    '/css/layout.css',
    '/css/style.css',
    '/css/pericias.css',
    '/services/PericiaService.js'
];

// Instalar Service Worker
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            console.log('📦 Cache instalado');
            return cache.addAll(urlsToCache);
        })
    );
});

// Usar cache quando disponível
self.addEventListener('fetch', (event) => {
    event.respondWith(
        caches.match(event.request).then((response) => {
            return response || fetch(event.request);
        })
    );
});

// Limpar cache antigo
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    if (cacheName !== CACHE_NAME) {
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});