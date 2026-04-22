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
        if (typeof AuthService !== 'undefined' && typeof AuthService.getAuthHeader === 'function') {
            return AuthService.getAuthHeader();
        }
        const token = localStorage.getItem('token');
        return token ? { 'Authorization': `Bearer ${token}` } : {};
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
        const res = await fetch(`${this.baseUrl}/divindades/custom`, {
            headers: {
                'Content-Type': 'application/json',
                ...this._getAuthHeader(),
            },
        });
        if (!res.ok) {
            throw new Error(await this._extrairMensagemErro(res, 'Erro ao listar divindades customizadas'));
        }
        return res.json();
    }

    /** Lista catalogo unificado (oficial + customizadas) com `origem` em cada item. */
    async listarCatalogoUnificado() {
        const res = await fetch(`${this.baseUrl}/magias/divindades/catalogo`, {
            headers: {
                'Content-Type': 'application/json',
                ...this._getAuthHeader(),
            },
        });
        if (!res.ok) {
            throw new Error(await this._extrairMensagemErro(res, 'Erro ao carregar catálogo de divindades'));
        }
        return res.json();
    }

    /** Cria uma divindade de campanha (Mestre/Admin). */
    async criar(payload) {
        const res = await fetch(`${this.baseUrl}/divindades/custom`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...this._getAuthHeader(),
            },
            body: JSON.stringify(payload || {}),
        });
        if (!res.ok) {
            throw new Error(await this._extrairMensagemErro(res, 'Erro ao criar divindade'));
        }
        return res.json();
    }

    /** Remove uma divindade customizada (Mestre/Admin). */
    async deletar(divindadeId) {
        const res = await fetch(`${this.baseUrl}/divindades/custom/${encodeURIComponent(divindadeId)}`, {
            method: 'DELETE',
            headers: this._getAuthHeader(),
        });
        if (!res.ok && res.status !== 204) {
            throw new Error(await this._extrairMensagemErro(res, 'Erro ao excluir divindade'));
        }
        return true;
    }
}

window.DivindadeCustomService = DivindadeCustomService;
