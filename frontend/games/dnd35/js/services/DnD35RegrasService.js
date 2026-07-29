/**
 * Catálogo de regras D&D 3.5 (bestiário MM e futuros endpoints /dnd35/regras/*).
 */
(function (global) {
    'use strict';

    class DnD35RegrasService {
        _headers() {
            const h = { Accept: 'application/json' };
            if (typeof AuthService !== 'undefined' && AuthService.getToken) {
                const t = AuthService.getToken();
                if (t) h.Authorization = `Bearer ${t}`;
            }
            return h;
        }

        async _handleJson(res, fallback) {
            if (res.status === 401 && typeof AuthService !== 'undefined' && AuthService.logout) {
                AuthService.logout();
            }
            if (!res.ok) {
                let detail = fallback;
                try {
                    const body = await res.json();
                    if (body && body.detail) detail = String(body.detail);
                } catch {
                    /* ignore */
                }
                throw new Error(detail);
            }
            return res.json();
        }

        _urlBestiario() {
            return window.getApiUrl('/dnd35/regras/bestiario');
        }

        async listarBestiarioCatalogo(params = {}) {
            const q = new URLSearchParams();
            if (params.q) q.set('q', params.q);
            if (params.skip != null) q.set('skip', String(params.skip));
            if (params.limit != null) q.set('limit', String(params.limit));
            if (params.tipo) q.set('tipo', params.tipo);
            if (params.nd_min != null) q.set('nd_min', String(params.nd_min));
            if (params.nd_max != null) q.set('nd_max', String(params.nd_max));
            const qs = q.toString();
            const res = await fetch(this._urlBestiario() + (qs ? `?${qs}` : ''), {
                headers: this._headers(),
                cache: 'no-store',
            });
            return this._handleJson(res, 'Erro ao carregar bestiário');
        }

        async obterBestiarioDetalhe(slug) {
            const s = encodeURIComponent(String(slug || '').trim());
            const res = await fetch(`${this._urlBestiario()}/${s}`, {
                headers: this._headers(),
                cache: 'no-store',
            });
            return this._handleJson(res, 'Criatura não encontrada no bestiário');
        }
    }

    global.DnD35RegrasService = DnD35RegrasService;
})(typeof window !== 'undefined' ? window : globalThis);
