/**
 * Componente de Ordem de Iniciativa
 * Princípio SOLID: Single Responsibility - renderizar ordem de iniciativa
 */
import { escapeHtml } from '../utils/formatters.js';

export class OrdemIniciativa {
    
    /**
     * Renderiza o painel de ordem de iniciativa
     */
    static render(combate) {
        const container = document.getElementById('ordemIniciativaContainer');
        
        if (!container) return;
        
        if (!combate || !combate.combatentes || combate.combatentes.length === 0) {
            container.innerHTML = '<p class="empty-state">Nenhum combatente</p>';
            return;
        }
        
        // Ordenar combatentes por iniciativa (maior para menor)
        const combatentesOrdenados = [...combate.combatentes].sort((a, b) => b.iniciativa - a.iniciativa);
        
        container.innerHTML = '';
        
        combatentesOrdenados.forEach((combatente, index) => {
            const isAtivo = combatente.id === combate.combatente_ativo_id;
            const isMorto = combatente.hp_atual <= 0;
            
            const item = document.createElement('div');
            item.className = `ordem-item ${isAtivo ? 'ordem-ativo' : ''} ${isMorto ? 'ordem-morto' : ''}`;
            
            // Ícone de status
            let statusIcon = '';
            if (isAtivo) {
                statusIcon = '<span class="ordem-status-icon ordem-status-ativo">⚔️</span>';
            } else if (isMorto) {
                statusIcon = '<span class="ordem-status-icon ordem-status-morto">💀</span>';
            } else {
                statusIcon = `<span class="ordem-status-icon ordem-status-aguardando">${index + 1}</span>`;
            }
            
            item.innerHTML = `
                ${statusIcon}
                <div class="ordem-info">
                    <div class="ordem-nome">${escapeHtml(combatente.nome)}</div>
                    <div class="ordem-detalhes">
                        <span class="ordem-iniciativa">Ini: ${combatente.iniciativa}</span>
                        <span class="ordem-hp ${combatente.hp_atual < combatente.hp_maximo * 0.25 ? 'ordem-hp-critical' : ''}">
                            HP: ${combatente.hp_atual}/${combatente.hp_maximo}
                        </span>
                    </div>
                </div>
            `;
            
            container.appendChild(item);
        });
    }
}