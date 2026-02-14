/**
 * Componente Seletor de Tipo de Combatente
 * Princípio SOLID: Single Responsibility - apenas gerenciar seleção de tipo
 */
export class TipoSelector {
    
    /**
     * Mostra modal de seleção de tipo
     */
    static mostrar(onSelect) {
        const modalOverlay = document.createElement('div');
        modalOverlay.className = 'modal show';
        modalOverlay.style.zIndex = '2000';
        
        const modalContent = document.createElement('div');
        modalContent.className = 'modal-content';
        modalContent.style.maxWidth = '500px';
        
        modalContent.innerHTML = `
            <div class="modal-header">
                <h2>⚔️ Selecionar Tipo de Combatente</h2>
                <button class="modal-close">&times;</button>
            </div>
            <div style="padding: 2rem;">
                <p style="text-align: center; margin-bottom: 2rem; color: var(--cor-madeira); font-size: 1.1rem;">
                    Escolha o tipo de combatente que deseja cadastrar:
                </p>
                
                <div style="display: flex; flex-direction: column; gap: 1rem;">
                    <button class="tipo-option btn-add-jogador" data-tipo="jogador">
                        <span style="font-size: 2rem; margin-right: 0.8rem;">🛡️</span>
                        <div style="text-align: left;">
                            <strong style="font-size: 1.2rem; display: block; margin-bottom: 0.3rem;">Jogador</strong>
                            <small style="opacity: 0.8;">Personagens controlados pelos jogadores</small>
                        </div>
                    </button>
                    
                    <button class="tipo-option btn-add-monstro" data-tipo="monstro">
                        <span style="font-size: 2rem; margin-right: 0.8rem;">👹</span>
                        <div style="text-align: left;">
                            <strong style="font-size: 1.2rem; display: block; margin-bottom: 0.3rem;">Monstro</strong>
                            <small style="opacity: 0.8;">Criaturas hostis e inimigos</small>
                        </div>
                    </button>
                    
                    <button class="tipo-option btn-add-npc" data-tipo="npc">
                        <span style="font-size: 2rem; margin-right: 0.8rem;">🧙</span>
                        <div style="text-align: left;">
                            <strong style="font-size: 1.2rem; display: block; margin-bottom: 0.3rem;">NPC</strong>
                            <small style="opacity: 0.8;">Personagens não-jogadores e aliados</small>
                        </div>
                    </button>
                </div>
            </div>
        `;
        
        modalOverlay.appendChild(modalContent);
        document.body.appendChild(modalOverlay);
        
        // Event listeners
        const fechar = () => {
            modalOverlay.remove();
        };
        
        modalContent.querySelector('.modal-close').addEventListener('click', fechar);
        modalOverlay.addEventListener('click', (e) => {
            if (e.target === modalOverlay) fechar();
        });
        
        const botoesTipo = modalContent.querySelectorAll('.tipo-option');
        botoesTipo.forEach(btn => {
            btn.addEventListener('click', () => {
                const tipo = btn.dataset.tipo;
                fechar();
                onSelect(tipo);
            });
        });
    }
}