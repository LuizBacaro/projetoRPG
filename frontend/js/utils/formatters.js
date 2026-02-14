/**
 * Formatadores de dados
 */

export const formatters = {
    
    /**
     * Formata HP com indicador de crítico
     */
    formatarHP(hpAtual, hpMaximo) {
        const percentual = (hpAtual / hpMaximo) * 100;
        const isCritico = percentual < 25;
        
        return {
            texto: `${hpAtual}/${hpMaximo}`,
            percentual,
            isCritico,
            classe: isCritico ? 'hp-critical' : ''
        };
    },
    
    /**
     * Formata tipo para exibição
     */
    formatarTipo(tipo) {
        const tipos = {
            'jogador': 'Jogador',
            'monstro': 'Monstro',
            'npc': 'NPC'
        };
        return tipos[tipo] || tipo;
    },
    
    /**
     * Formata pontos com separador de milhares
     */
    formatarPontos(pontos) {
        return pontos.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
    }
};