/**
 * Service Worker - Cache de Perícias (D&D 3.5)
 * Caminhos alinhados ao bundle em /games/dnd35/
 */

const CACHE_NAME = 'pericias-v2-dnd35';
const urlsToCache = [
    '/games/dnd35/pages/pericias.html',
    '/games/dnd35/css/variables.css',
    '/games/dnd35/css/layout.css',
    '/games/dnd35/css/style.css',
    '/games/dnd35/css/pericias.css',
    '/games/dnd35/js/services/PericiaService.js'
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.addAll(urlsToCache);
        })
    );
});

self.addEventListener('fetch', (event) => {
    event.respondWith(
        caches.match(event.request).then((response) => {
            return response || fetch(event.request);
        })
    );
});

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
