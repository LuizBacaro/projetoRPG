/**
 * CondicaoService
 * SOLID: SRP - apenas comunicação HTTP com a API de condições
 */
export class CondicaoService {
    constructor(baseUrl = '/api/v1') {
        this.baseUrl = baseUrl;
    }

    async listarTodas() {
        const res = await fetch(`${this.baseUrl}/condicoes`);
        if (!res.ok) throw new Error('Erro ao carregar condições');
        return res.json();
    }

    async listarDoCombatente(combatenteId) {
        const res = await fetch(`${this.baseUrl}/condicoes/combatente/${combatenteId}`);
        if (!res.ok) throw new Error('Erro ao carregar condições do combatente');
        return res.json();
    }

    async aplicar(combatenteId, condicaoId) {
        const res = await fetch(`${this.baseUrl}/condicoes/combatente/${combatenteId}`, {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ condicao_id: condicaoId }),
        });
        if (!res.ok) throw new Error('Erro ao aplicar condição');
        return res.json();
    }

    async remover(combatenteId, condicaoId) {
        const res = await fetch(
            `${this.baseUrl}/condicoes/combatente/${combatenteId}/${condicaoId}`,
            { method: 'DELETE' }
        );
        if (!res.ok) throw new Error('Erro ao remover condição');
        return res.json();
    }

    async removerTodas(combatenteId) {
        const res = await fetch(
            `${this.baseUrl}/condicoes/combatente/${combatenteId}`,
            { method: 'DELETE' }
        );
        if (!res.ok) throw new Error('Erro ao remover condições');
        return res.json();
    }
}