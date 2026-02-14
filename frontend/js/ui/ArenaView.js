/**
 * View da Arena de Combate
 * Princípio SOLID: Single Responsibility - apenas renderizar arena
 */
export class ArenaView {
    
    /**
     * Renderiza todos os combatentes na arena
     */
    render(combate, onAplicarDano, onUpdateHP) {
        const container = document.getElementById('arenaContainer');
        container.innerHTML = '';
        
        if (!combate || !combate.combatentes || combate.combatentes.length === 0) {
            container.innerHTML = '<p class="empty-state">Nenhum combatente no combate</p>';
            return;
        }
        
        combate.combatentes.forEach((combatente, index) => {
            const isAtivo = combatente.id === combate.combatente_ativo_id;
            const card = this.renderCombatenteCard(combatente, isAtivo, onAplicarDano, onUpdateHP);
            container.appendChild(card);
        });
    }
    
    /**
     * Renderiza um card de combatente na arena
     */
    renderCombatenteCard(combatente, isAtivo, onAplicarDano, onUpdateHP) {
        const card = document.createElement('div');
        const isMorto = !combatente.estaVivo();
        const isCritico = combatente.estaCritico();
        
        card.className = `arena-combatente ${isAtivo ? 'ativo' : ''} ${isMorto ? 'morto' : ''}`;
        
        // Calcular cor da barra de HP
        const hpPercent = combatente.getHPPercentual();
        let corHP = '#32CD32'; // Verde
        if (hpPercent < 25) {
            corHP = '#DC143C'; // Vermelho
        } else if (hpPercent < 50) {
            corHP = '#FFA500'; // Laranja
        } else if (hpPercent < 75) {
            corHP = '#FFD700'; // Amarelo
        }
        
        card.innerHTML = `
            ${combatente.foto_url 
                ? `<img src="${combatente.foto_url}" alt="${combatente.nome}" class="arena-combatente-foto">` 
                : '<div class="arena-combatente-foto" style="background: linear-gradient(135deg, #d4a574 0%, #b8926a 100%); display: flex; align-items: center; justify-content: center; font-size: 4rem;">👤</div>'}
            
            <div class="arena-combatente-info">
                <div class="arena-combatente-header">
                    <h3>${combatente.nome}</h3>
                    <span class="badge ${combatente.getBadgeClass()}">${combatente.tipo}</span>
                </div>
                
                <p class="combatente-classe">${combatente.classe} - Nível ${combatente.nivel}</p>
                
                <div class="arena-combatente-hp">
                    <div class="hp-bar">
                        <div class="hp-fill" style="width: ${hpPercent}%; background: linear-gradient(90deg, ${corHP} 0%, ${corHP}dd 100%);"></div>
                    </div>
                    <div class="hp-text-editable">
                        <span>HP:</span>
                        <input 
                            type="number" 
                            class="hp-input ${isCritico ? 'hp-critical' : ''}" 
                            value="${combatente.hp_atual}" 
                            min="0" 
                            max="${combatente.hp_maximo}"
                            data-id="${combatente.id}"
                            ${isMorto ? 'disabled' : ''}
                        >
                        <span>/</span>
                        <span>${combatente.hp_maximo}</span>
                    </div>
                </div>
                
                <div class="arena-combatente-actions">
                    <button class="btn btn-danger" data-id="${combatente.id}" data-dano="10" ${isMorto ? 'disabled' : ''}>
                        -10 HP
                    </button>
                    <button class="btn btn-danger" data-id="${combatente.id}" data-dano="20" ${isMorto ? 'disabled' : ''}>
                        -20 HP
                    </button>
                </div>
            </div>
        `;
        
        // Event listeners
        const hpInput = card.querySelector('.hp-input');
        if (hpInput) {
            hpInput.addEventListener('change', (e) => {
                const novoHP = parseInt(e.target.value);
                onUpdateHP(combatente.id, novoHP);
            });
        }
        
        const botoesAplicarDano = card.querySelectorAll('.btn-danger');
        botoesAplicarDano.forEach(btn => {
            btn.addEventListener('click', () => {
                const id = parseInt(btn.dataset.id);
                const dano = parseInt(btn.dataset.dano);
                onAplicarDano(id, dano);
            });
        });
        
        return card;
    }
}