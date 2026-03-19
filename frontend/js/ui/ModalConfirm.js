/**
 * ModalConfirm.js
 * Componente global de confirmação para ações destrutivas
 * SOLID: SRP - gerencia apenas UI de modal de confirmação
 * 
 * ✅ Exportado como módulo ES6
 */

export class ModalConfirm {
    /**
     * Mostra modal de confirmação
     * 
     * Opções:
     * {
     *   icone: string (emoji ou ícone),
     *   titulo: string,
     *   texto: string (HTML suportado),
     *   textoCancelar: string (default: "Cancelar"),
     *   textoConfirmar: string (default: "Confirmar"),
     *   classeConfirmar: string (CSS classes, default: "modal-confirm-ok"),
     *   onCancelar: function (callback ao cancelar),
     *   onConfirmar: function (callback ao confirmar)
     * }
     */
    static mostrar(opcoes = {}) {
        // ✅ Validação básica
        if (typeof opcoes !== 'object') {
            console.error('❌ ModalConfirm.mostrar() recebeu argumento inválido');
            return;
        }

        // ✅ Remover modal anterior se existir
        const anterior = document.getElementById('_modalConfirmGlobal');
        if (anterior) anterior.remove();

        // ✅ Criar overlay
        const overlay = document.createElement('div');
        overlay.id        = '_modalConfirmGlobal';
        overlay.className = 'modal-confirm-overlay';
        
        overlay.innerHTML = `
            <div class="modal-confirm-box">
                <div class="modal-confirm-header">
                    <span class="modal-confirm-icone">${opcoes.icone || '⚠️'}</span>
                    <h3 class="modal-confirm-titulo">${opcoes.titulo || 'Confirmar'}</h3>
                </div>
                <p class="modal-confirm-texto">${opcoes.texto || 'Deseja continuar?'}</p>
                <div class="modal-confirm-botoes">
                    <button class="modal-confirm-btn modal-confirm-cancelar" id="_confirmCancelar">
                        ${opcoes.textoCancelar || 'Cancelar'}
                    </button>
                    <button class="modal-confirm-btn ${opcoes.classeConfirmar || 'modal-confirm-ok'}" id="_confirmOk">
                        ${opcoes.textoConfirmar || 'Confirmar'}
                    </button>
                </div>
            </div>
        `;

        document.body.appendChild(overlay);

        // ✅ Trigger reflow para animação
        requestAnimationFrame(() => {
            overlay.classList.add('show');
        });

        // ✅ Funções de fechamento e callbacks
        const fechar = () => {
            overlay.classList.remove('show');
            setTimeout(() => {
                if (overlay.parentNode) overlay.remove();
            }, 250);
        };

        // Event: Cancelar
        document.getElementById('_confirmCancelar').addEventListener('click', () => {
            console.log('❌ Modal confirmação: Cancelado');
            fechar();
            if (typeof opcoes.onCancelar === 'function') opcoes.onCancelar();
        });

        // Event: Confirmar
        document.getElementById('_confirmOk').addEventListener('click', () => {
            console.log('✅ Modal confirmação: Confirmado');
            fechar();
            if (typeof opcoes.onConfirmar === 'function') opcoes.onConfirmar();
        });

        // Event: Clicar fora do modal
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                console.log('⊘ Modal confirmação: Clicou fora');
                fechar();
            }
        });

        // Event: ESC
        const onEsc = (e) => {
            if (e.key === 'Escape') {
                console.log('⊘ Modal confirmação: ESC pressionado');
                fechar();
                document.removeEventListener('keydown', onEsc);
            }
        };
        document.addEventListener('keydown', onEsc);

        console.log('📋 Modal confirmação aberto:', opcoes.titulo);
    }
}

console.log('✅ ModalConfirm exportado como módulo ES6');