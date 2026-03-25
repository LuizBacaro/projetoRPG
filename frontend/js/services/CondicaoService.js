/**
 * CondicaoService
 * Classe global (sem export) — carregada via <script> no index.html
 * SOLID: SRP - apenas comunicação HTTP com a API de condições
 * ✅ CORRIGIDO: baseUrl agora aponta para /api/v1
 */

const _getCondicaoBaseUrl = () => {
    const isProduction = !['localhost', '127.0.0.1'].includes(window.location.hostname);
    return isProduction
        ? '/api/v1'
        : 'http://127.0.0.1:8000/api/v1';   // ✅ /api → /api/v1
};

class CondicaoService {

    constructor() {
        this.baseUrl = _getCondicaoBaseUrl();
        console.log('✅ CondicaoService inicializado. baseUrl:', this.baseUrl);
    }

    async listarTodas() {
        try {
            const res = await fetch(`${this.baseUrl}/condicoes`);
            if (!res.ok) throw new Error(`HTTP ${res.status}: Erro ao carregar condições`);
            return res.json();
        } catch (error) {
            console.error('❌ CondicaoService.listarTodas:', error);
            throw error;
        }
    }

    async listarDoCombatente(combatenteId) {
        try {
            console.log(`📡 GET condições do combatente: ${combatenteId}`);
            const res = await fetch(
                `${this.baseUrl}/condicoes/combatente/${combatenteId}`
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
            console.log(`📡 POST aplicar condição ${condicaoId} → combatente ${combatenteId} (duração: ${durationTurnos})`);
            const res = await fetch(
                `${this.baseUrl}/condicoes/combatente/${combatenteId}`,
                {
                    method:  'POST',
                    headers: { 'Content-Type': 'application/json' },
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
            console.log(`📡 DELETE condição ${condicaoId} → combatente ${combatenteId}`);
            const res = await fetch(
                `${this.baseUrl}/condicoes/combatente/${combatenteId}/${condicaoId}`,
                { method: 'DELETE' }
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
            console.log(`📡 DELETE todas condições → combatente ${combatenteId}`);
            const res = await fetch(
                `${this.baseUrl}/condicoes/combatente/${combatenteId}`,
                { method: 'DELETE' }
            );
            if (!res.ok) throw new Error(`HTTP ${res.status}: Erro ao remover todas as condições`);
            return res.json();
        } catch (error) {
            console.error('❌ CondicaoService.removerTodas:', error);
            throw error;
        }
    }
}