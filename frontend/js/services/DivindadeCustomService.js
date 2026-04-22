/**
 * DivindadeCustomService
 * Classe global (sem export) — carregada via <script> no dashboard.
 * SRP: comunicacao HTTP com os endpoints /divindades/custom e
 *       /magias/divindades/catalogo (catalogo unificado).
 */

class DivindadeCustomService {

    constructor() {
        this.baseUrl = window.getApiUrl('');
    }

    _getAuthHeader() {
        if (typeof window !== 'undefined' && window.AuthService && typeof window.AuthService.getToken === 'function') {
            const token = window.AuthService.getToken();
            if (token) return { 'Authorization': `Bearer ${token}` };
        }
        const token = localStorage.getItem('token');
        return token ? { 'Authorization': `Bearer ${token}` } : {};
    }

    async _request(path, options = {}, fallbackMessage = 'Erro na operação') {
        const res = await fetch(`${this.baseUrl}${path}`, {
            ...(options || {}),
            headers: {
                ...(options?.headers || {}),
                ...this._getAuthHeader(),
            },
        });

        if (res.status === 401) {
            if (typeof window !== 'undefined' && window.AuthService && typeof window.AuthService.logout === 'function') {
                window.AuthService.logout();
            }
            throw new Error('Token inválido ou expirado. Faça login novamente.');
        }

        if (!res.ok) {
            throw new Error(await this._extrairMensagemErro(res, fallbackMessage));
        }

        return res;
    }

    async _extrairMensagemErro(res, fallback) {
        try {
            const err = await res.json();
            if (err && typeof err.detail === 'string' && err.detail.trim()) {
                return err.detail;
            }
        } catch (_) {
            // mantem fallback se nao for JSON
        }
        return `HTTP ${res.status}: ${fallback}`;
    }

    /** Lista apenas as divindades customizadas (criadas pelo Mestre). */
    async listarCustomizadas() {
        const res = await this._request('/divindades/custom', {
            headers: { 'Content-Type': 'application/json' },
        }, 'Erro ao listar divindades customizadas');
        return res.json();
    }

    /** Lista catalogo unificado (oficial + customizadas) com `origem` em cada item. */
    async listarCatalogoUnificado() {
        const res = await this._request('/magias/divindades/catalogo', {
            headers: { 'Content-Type': 'application/json' },
        }, 'Erro ao carregar catálogo de divindades');
        return res.json();
    }

    /** Cria uma divindade de campanha (Mestre/Admin). */
    async criar(payload) {
        const res = await this._request('/divindades/custom', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload || {}),
        }, 'Erro ao criar divindade');
        return res.json();
    }

    /** Remove uma divindade customizada (Mestre/Admin). */
    async deletar(divindadeId) {
        const res = await fetch(`${this.baseUrl}/divindades/custom/${encodeURIComponent(divindadeId)}`, {
            method: 'DELETE',
            headers: {
                ...this._getAuthHeader(),
            },
        });
        if (res.status === 401) {
            if (typeof window !== 'undefined' && window.AuthService && typeof window.AuthService.logout === 'function') {
                window.AuthService.logout();
            }
            throw new Error('Token inválido ou expirado. Faça login novamente.');
        }
        if (!res.ok && res.status !== 204) {
            throw new Error(await this._extrairMensagemErro(res, 'Erro ao excluir divindade'));
        }
        return true;
    }
}

window.DivindadeCustomService = DivindadeCustomService;
