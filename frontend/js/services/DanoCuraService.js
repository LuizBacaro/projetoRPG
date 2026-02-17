/**
 * Service responsável pela lógica de negócio de dano e cura
 * Single Responsibility Principle: apenas gerencia dano/cura
 * 
 * VERSÃO COM PERSISTÊNCIA: Faz requisições HTTP para o backend
 */
class DanoCuraService {
    constructor() {
        this.API_URL = 'http://127.0.0.1:8000/api';  // ← ADICIONAR /api
        console.log('✅ DanoCuraService inicializado (modo com persistência)');
    }

    /**
     * Aplica dano a um combatente
     * @param {number} combatenteId - ID do combatente
     * @param {number} valorDano - Valor do dano
     * @returns {Promise<Object>} Dados atualizados do combatente
     */
    async aplicarDano(combatenteId, valorDano) {
        try {
            const response = await fetch(`${this.API_URL}/combatentes/${combatenteId}/dano`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    valor: valorDano
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Erro ao aplicar dano');
            }

            const resultado = await response.json();
            console.log(`💥 ${resultado.mensagem}`);
            
            return resultado;

        } catch (erro) {
            console.error('❌ Erro ao aplicar dano:', erro);
            throw erro;
        }
    }

    /**
     * Aplica cura a um combatente
     * @param {number} combatenteId - ID do combatente
     * @param {number} valorCura - Valor da cura
     * @returns {Promise<Object>} Dados atualizados do combatente
     */
    async aplicarCura(combatenteId, valorCura) {
        try {
            const response = await fetch(`${this.API_URL}/combatentes/${combatenteId}/cura`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    valor: valorCura
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Erro ao aplicar cura');
            }

            const resultado = await response.json();
            console.log(`💚 ${resultado.mensagem}`);
            
            return resultado;

        } catch (erro) {
            console.error('❌ Erro ao aplicar cura:', erro);
            throw erro;
        }
    }

    /**
     * Aplica dano a múltiplos combatentes
     * @param {Array<number>} combatenteIds - IDs dos combatentes
     * @param {number} valorDano - Valor do dano
     * @returns {Promise<Array>} Resultados das atualizações
     */
    async aplicarDanoEmMassa(combatenteIds, valorDano) {
        if (!valorDano || valorDano <= 0) {
            throw new Error('Valor de dano inválido');
        }

        console.log(`⚔️ Aplicando ${valorDano} de dano a ${combatenteIds.length} combatente(s)`);

        // Executar todas as requisições em paralelo
        const promessas = combatenteIds.map(id => this.aplicarDano(id, valorDano));
        
        try {
            const resultados = await Promise.all(promessas);
            return resultados;
        } catch (erro) {
            console.error('❌ Erro ao aplicar dano em massa:', erro);
            throw erro;
        }
    }

    /**
     * Aplica cura a múltiplos combatentes
     * @param {Array<number>} combatenteIds - IDs dos combatentes
     * @param {number} valorCura - Valor da cura
     * @returns {Promise<Array>} Resultados das atualizações
     */
    async aplicarCuraEmMassa(combatenteIds, valorCura) {
        if (!valorCura || valorCura <= 0) {
            throw new Error('Valor de cura inválido');
        }

        console.log(`💚 Aplicando ${valorCura} de cura a ${combatenteIds.length} combatente(s)`);

        // Executar todas as requisições em paralelo
        const promessas = combatenteIds.map(id => this.aplicarCura(id, valorCura));
        
        try {
            const resultados = await Promise.all(promessas);
            return resultados;
        } catch (erro) {
            console.error('❌ Erro ao aplicar cura em massa:', erro);
            throw erro;
        }
    }

    /**
     * Valida se os valores de dano/cura são mutuamente exclusivos
     * @param {number} dano - Valor do dano
     * @param {number} cura - Valor da cura
     * @returns {Object} { valido: boolean, tipo: 'dano'|'cura'|null, valor: number }
     */
    validarEntrada(dano, cura) {
        const temDano = dano && dano > 0;
        const temCura = cura && cura > 0;

        if (temDano && temCura) {
            return { 
                valido: false, 
                erro: 'Não é possível aplicar dano e cura simultaneamente',
                tipo: null,
                valor: 0
            };
        }

        if (!temDano && !temCura) {
            return { 
                valido: false, 
                erro: 'Informe um valor de dano ou cura',
                tipo: null,
                valor: 0
            };
        }

        return { 
            valido: true, 
            tipo: temDano ? 'dano' : 'cura',
            valor: temDano ? dano : cura
        };
    }

    /**
     * Atualiza HP diretamente (usado para sincronizar com backend)
     * @param {number} combatenteId - ID do combatente
     * @param {number} novoHP - Novo valor de HP
     * @returns {Promise<Object>} Dados atualizados
     */
    async atualizarHP(combatenteId, novoHP) {
        try {
            const response = await fetch(`${this.API_URL}/combatentes/${combatenteId}/hp?hp_atual=${novoHP}`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error('Erro ao atualizar HP');
            }

            return await response.json();

        } catch (erro) {
            console.error('❌ Erro ao atualizar HP:', erro);
            throw erro;
        }
    }
}