/**
 * PericiaService - Gerencia comunicação com backend de perícias
 * Single Responsibility: Apenas fazer requisições HTTP
 */

class PericiaService {
    constructor(apiUrl = '/api/v1') {
        this.baseUrl = `${apiUrl}/pericias`;
    }

    // ========== PERÍCIAS DISPONÍVEIS ==========

    async obterTodasPericias(skip = 0, limit = 100) {
        try {
            const response = await fetch(`${this.baseUrl}?skip=${skip}&limit=${limit}`);
            if (!response.ok) throw new Error('Erro ao obter perícias');
            return await response.json();
        } catch (error) {
            console.error('Erro em obterTodasPericias:', error);
            throw error;
        }
    }

    async obterPericiasPorAtributo(atributo) {
        try {
            const response = await fetch(`${this.baseUrl}?atributo=${atributo}`);
            if (!response.ok) throw new Error('Erro ao obter perícias');
            return await response.json();
        } catch (error) {
            console.error('Erro em obterPericiasPorAtributo:', error);
            throw error;
        }
    }

    async obterPericia(periciaId) {
        try {
            const response = await fetch(`${this.baseUrl}/${periciaId}`);
            if (!response.ok) throw new Error('Perícia não encontrada');
            return await response.json();
        } catch (error) {
            console.error('Erro em obterPericia:', error);
            throw error;
        }
    }

    // ========== PERÍCIAS DO JOGADOR ==========

    async adicionarPericiaJogador(combatenteId, periciaId, graduacao = 0) {
        try {
            const response = await fetch(`${this.baseUrl}/${combatenteId}/adicionar`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    pericia_id: periciaId,
                    graduacao: graduacao
                })
            });
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Erro ao adicionar perícia');
            }
            return await response.json();
        } catch (error) {
            console.error('Erro em adicionarPericiaJogador:', error);
            throw error;
        }
    }

    async obterPerienciasJogador(combatenteId) {
        try {
            const response = await fetch(`${this.baseUrl}/${combatenteId}/listar`);
            if (!response.ok) throw new Error('Erro ao obter perícias do jogador');
            return await response.json();
        } catch (error) {
            console.error('Erro em obterPerienciasJogador:', error);
            throw error;
        }
    }

    async atualizarPericiaJogador(combatenteId, periciaJogadorId, graduacao, bonusOutros = 0) {
        try {
            const response = await fetch(
                `${this.baseUrl}/${combatenteId}/pericia/${periciaJogadorId}`,
                {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        graduacao: graduacao,
                        bonus_outros: bonusOutros
                    })
                }
            );
            if (!response.ok) throw new Error('Erro ao atualizar perícia');
            return await response.json();
        } catch (error) {
            console.error('Erro em atualizarPericiaJogador:', error);
            throw error;
        }
    }

    async deletarPericiaJogador(combatenteId, periciaJogadorId) {
        try {
            const response = await fetch(
                `${this.baseUrl}/${combatenteId}/pericia/${periciaJogadorId}`,
                { method: 'DELETE' }
            );
            if (!response.ok) throw new Error('Erro ao deletar perícia');
            return true;
        } catch (error) {
            console.error('Erro em deletarPericiaJogador:', error);
            throw error;
        }
    }

    async obterEstatisticasPericias(combatenteId) {
        try {
            const response = await fetch(`${this.baseUrl}/${combatenteId}/estatisticas`);
            if (!response.ok) throw new Error('Erro ao obter estatísticas');
            return await response.json();
        } catch (error) {
            console.error('Erro em obterEstatisticasPericias:', error);
            throw error;
        }
    }
}

// Exportar para uso global
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PericiaService;
}