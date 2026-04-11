/**
 * CondicaoService
 * Classe global (sem export) — carregada via <script> no index.html
 * SOLID: SRP - apenas comunicação HTTP com a API de condições
 * ✅ CORRIGIDO: baseUrl agora aponta para /api/v1
 */

const _getCondicaoBaseUrl = () => window.getApiUrl('');

class CondicaoService {

    constructor() {
        this.baseUrl = _getCondicaoBaseUrl();
    }

    _getAuthHeader() {
        if (typeof AuthService !== 'undefined' && typeof AuthService.getAuthHeader === 'function') {
            return AuthService.getAuthHeader();
        }

        const token = localStorage.getItem('token');
        return token ? { 'Authorization': `Bearer ${token}` } : {};
    }

    async listarTodas() {
        try {
            const res = await fetch(`${this.baseUrl}/condicoes`, {
                headers: this._getAuthHeader(),
            });
            if (!res.ok) throw new Error(`HTTP ${res.status}: Erro ao carregar condições`);
            return res.json();
        } catch (error) {
            console.error('❌ CondicaoService.listarTodas:', error);
            throw error;
        }
    }

    async listarDoCombatente(combatenteId) {
        try {
            const res = await fetch(
                `${this.baseUrl}/condicoes/combatente/${combatenteId}`,
                {
                    headers: this._getAuthHeader(),
                }
            );
            if (!res.ok) throw new Error(`HTTP ${res.status}: Erro ao carregar condições do combatente`);
            return res.json();
        } catch (error) {
            console.error('❌ CondicaoService.listarDoCombatente:', error);
            throw error;
        }
    }

    async aplicar(combatenteId, condicaoId, durationTurnos = -1) {
        try {
            const res = await fetch(
                `${this.baseUrl}/condicoes/combatente/${combatenteId}`,
                {
                    method:  'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        ...this._getAuthHeader(),
                    },
                    body:    JSON.stringify({ 
                        condicao_id: condicaoId,
                        duracao_turnos: durationTurnos
                    }),
                }
            );
            if (!res.ok) throw new Error(`HTTP ${res.status}: Erro ao aplicar condição`);
            return res.json();
        } catch (error) {
            console.error('❌ CondicaoService.aplicar:', error);
            throw error;
        }
    }

    async remover(combatenteId, condicaoId) {
        try {
            const res = await fetch(
                `${this.baseUrl}/condicoes/combatente/${combatenteId}/${condicaoId}`,
                {
                    method: 'DELETE',
                    headers: this._getAuthHeader(),
                }
            );
            if (!res.ok) throw new Error(`HTTP ${res.status}: Erro ao remover condição`);
            return res.json();
        } catch (error) {
            console.error('❌ CondicaoService.remover:', error);
            throw error;
        }
    }

    async removerTodas(combatenteId) {
        try {
            const res = await fetch(
                `${this.baseUrl}/condicoes/combatente/${combatenteId}`,
                {
                    method: 'DELETE',
                    headers: this._getAuthHeader(),
                }
            );
            if (!res.ok) throw new Error(`HTTP ${res.status}: Erro ao remover todas as condições`);
            return res.json();
        } catch (error) {
            console.error('❌ CondicaoService.removerTodas:', error);
            throw error;
        }
    }
}