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

/**
 * Escapa caracteres HTML para prevenir XSS em innerHTML.
 * Usar sempre que interpolar dados do servidor/usuário em templates HTML.
 */
export function escapeHtml(str) {
    if (str == null) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

// Disponibilizar globalmente para scripts não-module
window.escapeHtml = escapeHtml;