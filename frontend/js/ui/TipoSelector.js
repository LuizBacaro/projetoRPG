/**
 * Componente de Seleção de Tipo de Combatente
 */

export class TipoSelector {
    /**
     * Mostra o seletor de tipo
     */
    static mostrar(callback) {
        console.log('🎯 TipoSelector.mostrar() chamado');
        
        // Remover modal anterior se existir
        const modalAntigo = document.getElementById('modalSeletorTipo');
        if (modalAntigo) {
            modalAntigo.remove();
        }
        
        // Criar novo modal
        const modal = this.criarModal();
        document.body.appendChild(modal);
        
        console.log('✅ Modal seletor criado e adicionado ao DOM');
        
        // Configurar eventos
        const botoes = modal.querySelectorAll('.tipo-option');
        console.log(`📍 Encontrados ${botoes.length} botões no modal`);
        
        botoes.forEach((botao) => {
            botao.addEventListener('click', () => {
                const tipo = botao.dataset.tipo;
                console.log(`✅ Clique no botão tipo: ${tipo}`);
                
                this.fechar();
                
                if (callback) {
                    callback(tipo);
                }
            });
        });

        const btnFechar = modal.querySelector('.modal-close');
        if (btnFechar) {
            btnFechar.addEventListener('click', () => this.fechar());
        }
        
        // Mostrar modal
        setTimeout(() => {
            modal.classList.add('show');
            console.log('✅ Modal seletor exibido');
        }, 50);
    }
    
    /**
     * Cria o HTML do modal
     */
    static criarModal() {
        const modal = document.createElement('div');
        modal.id = 'modalSeletorTipo';
        modal.className = 'modal';
        
        modal.innerHTML = `
            <div class="modal-content" style="max-width: 600px;">
                <div class="modal-header">
                    <h2>⚔️ Escolha o Tipo de Combatente</h2>
                    <button class="modal-close" type="button">&times;</button>
                </div>
                <div style="padding: 2rem; display: flex; flex-direction: column; gap: 1rem;">
                    <button class="tipo-option btn-add-jogador" data-tipo="jogador" style="display: flex; align-items: center; padding: 1.5rem; border-radius: 12px; cursor: pointer; transition: all 0.3s; font-family: var(--fonte-texto); font-size: 1rem; text-align: left;">
                        <span style="font-size: 2rem; margin-right: 0.8rem;">🧙</span>
                        <div>
                            <strong style="font-size: 1.2rem; display: block; margin-bottom: 0.3rem;">Jogador</strong>
                            <small style="opacity: 0.8;">Personagens controlados pelos jogadores</small>
                        </div>
                    </button>
                    
                    <button class="tipo-option btn-add-monstro" data-tipo="monstro" style="display: flex; align-items: center; padding: 1.5rem; border-radius: 12px; cursor: pointer; transition: all 0.3s; font-family: var(--fonte-texto); font-size: 1rem; text-align: left;">
                        <span style="font-size: 2rem; margin-right: 0.8rem;">👹</span>
                        <div>
                            <strong style="font-size: 1.2rem; display: block; margin-bottom: 0.3rem;">Monstro</strong>
                            <small style="opacity: 0.8;">Criaturas hostis e inimigos</small>
                        </div>
                    </button>
                    
                    <button class="tipo-option btn-add-npc" data-tipo="npc" style="display: flex; align-items: center; padding: 1.5rem; border-radius: 12px; cursor: pointer; transition: all 0.3s; font-family: var(--fonte-texto); font-size: 1rem; text-align: left;">
                        <span style="font-size: 2rem; margin-right: 0.8rem;">🤝</span>
                        <div>
                            <strong style="font-size: 1.2rem; display: block; margin-bottom: 0.3rem;">NPC</strong>
                            <small style="opacity: 0.8;">Personagens não-jogadores e aliados</small>
                        </div>
                    </button>
                </div>
            </div>
        `;
        
        return modal;
    }
    
    /**
     * Fecha o modal
     */
    static fechar() {
        console.log('🚪 Fechando modal seletor');
        const modal = document.getElementById('modalSeletorTipo');
        if (modal) {
            modal.classList.remove('show');
            setTimeout(() => modal.remove(), 300);
        }
    }
}