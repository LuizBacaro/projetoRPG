/**
 * Service responsável pela lógica de negócio de dano e cura
 * Single Responsibility Principle: apenas gerencia dano/cura
 */
class DanoCuraService {
    constructor() {
        this.API_URL = 'http://127.0.0.1:8000';
    }

    /**
     * Aplica dano a um combatente
     */
    async aplicarDano(combatenteId, valorDano) {
        try {
            const response = await fetch(`${this.API_URL}/combatentes/${combatenteId}/hp`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    hp_atual: valorDano,
                    operacao: 'dano'
                })
            });

            if (!response.ok) {
                throw new Error('Erro ao aplicar dano');
            }

            const combatente = await response.json();
            return combatente;

        } catch (erro) {
            console.error('Erro ao aplicar dano:', erro);
            throw erro;
        }
    }

    /**
     * Aplica cura a um combatente
     */
    async aplicarCura(combatenteId, valorCura) {
        try {
            const response = await fetch(`${this.API_URL}/combatentes/${combatenteId}/hp`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    hp_atual: valorCura,
                    operacao: 'cura'
                })
            });

            if (!response.ok) {
                throw new Error('Erro ao aplicar cura');
            }

            const combatente = await response.json();
            return combatente;

        } catch (erro) {
            console.error('Erro ao aplicar cura:', erro);
            throw erro;
        }
    }

    /**
     * Aplica dano a múltiplos combatentes
     * @param {Array<number>} combatenteIds - IDs dos combatentes
     * @param {number} valorDano - Valor do dano
     * @returns {Promise<Array>} Resultado das atualizações
     */
    async aplicarDanoEmMassa(combatenteIds, valorDano) {
        if (!valorDano || valorDano <= 0) {
            throw new Error('Valor de dano inválido');
        }

        const promessas = combatenteIds.map(id => this.aplicarDano(id, valorDano));
        return await Promise.all(promessas);
    }

    /**
     * Aplica cura a múltiplos combatentes
     * @param {Array<number>} combatenteIds - IDs dos combatentes
     * @param {number} valorCura - Valor da cura
     * @returns {Promise<Array>} Resultado das atualizações
     */
    async aplicarCuraEmMassa(combatenteIds, valorCura) {
        if (!valorCura || valorCura <= 0) {
            throw new Error('Valor de cura inválido');
        }

        const promessas = combatenteIds.map(id => this.aplicarCura(id, valorCura));
        return await Promise.all(promessas);
    }

    /**
     * Valida se os valores de dano/cura são mutuamente exclusivos
     * @param {number} dano - Valor do dano
     * @param {number} cura - Valor da cura
     * @returns {Object} { valido: boolean, tipo: 'dano'|'cura'|null }
     */
    validarEntrada(dano, cura) {
        const temDano = dano && dano > 0;
        const temCura = cura && cura > 0;

        if (temDano && temCura) {
            return { 
                valido: false, 
                erro: 'Não é possível aplicar dano e cura simultaneamente',
                tipo: null 
            };
        }

        if (!temDano && !temCura) {
            return { 
                valido: false, 
                erro: 'Informe um valor de dano ou cura',
                tipo: null 
            };
        }

        return { 
            valido: true, 
            tipo: temDano ? 'dano' : 'cura',
            valor: temDano ? dano : cura
        };
    }
}