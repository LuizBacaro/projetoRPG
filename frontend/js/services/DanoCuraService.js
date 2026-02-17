/**
 * Service responsável pela lógica de negócio de dano e cura
 * Single Responsibility Principle: apenas gerencia dano/cura
 */
class DanoCuraService {
    constructor(combatenteRepository) {
        this.combatenteRepository = combatenteRepository;
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

        const promessas = combatenteIds.map(id => 
            this.combatenteRepository.aplicarDano(id, valorDano)
        );

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

        const promessas = combatenteIds.map(id => 
            this.combatenteRepository.aplicarCura(id, valorCura)
        );

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