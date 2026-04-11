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

    async _extrairMensagemErro(res, fallbackMessage) {
        try {
            const errorData = await res.json();
            if (errorData && typeof errorData.detail === 'string' && errorData.detail.trim()) {
                return errorData.detail;
            }
        } catch (_) {
            // Mantem fallback de mensagem quando resposta nao e JSON valido
        }

        return `HTTP ${res.status}: ${fallbackMessage}`;
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
            if (!res.ok) {
                throw new Error(await this._extrairMensagemErro(res, 'Erro ao aplicar condição'));
            }
            return res.json();
        } catch (error) {
            console.error('❌ CondicaoService.aplicar:', error);
            throw error;
        }
    }

    async aplicarEmMassa(combatenteIds, condicaoId, duracaoTurnos = -1) {
        try {
            const res = await fetch(
                `${this.baseUrl}/condicoes/combatentes/aplicar`,
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        ...this._getAuthHeader(),
                    },
                    body: JSON.stringify({
                        combatente_ids: combatenteIds,
                        condicao_id: condicaoId,
                        duracao_turnos: duracaoTurnos,
                    }),
                }
            );

            if (res.ok) {
                return res.json();
            }

            if (res.status === 404 || res.status === 405) {
                console.warn('⚠️ Endpoint batch de condições indisponível, aplicando fallback por combatente');
                await Promise.all(
                    combatenteIds.map((id) => this.aplicar(id, condicaoId, duracaoTurnos))
                );

                return {
                    combatente_ids: combatenteIds,
                    total_aplicados: combatenteIds.length,
                    condicao_id: condicaoId,
                    duracao_turnos: duracaoTurnos,
                };
            }

            throw new Error(await this._extrairMensagemErro(res, 'Erro ao aplicar condição em massa'));
        } catch (error) {
            console.error('❌ CondicaoService.aplicarEmMassa:', error);
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