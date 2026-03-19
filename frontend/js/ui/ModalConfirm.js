/**
 * ModalConfirm.js
 * Componente global de confirmação para ações destrutivas
 * SOLID: SRP - gerencia apenas UI de modal de confirmação
 * 
 * ✅ Carregado como GLOBAL SCRIPT (sem export)
 */

class ModalConfirm {
    static mostrar(opcoes = {}) {
        if (typeof opcoes !== 'object') {
            console.error('❌ ModalConfirm.mostrar() recebeu argumento inválido');
            return;
        }

        const anterior = document.getElementById('_modalConfirmGlobal');
        if (anterior) anterior.remove();

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

        requestAnimationFrame(() => {
            overlay.classList.add('show');
        });

        const fechar = () => {
            overlay.classList.remove('show');
            setTimeout(() => {
                if (overlay.parentNode) overlay.remove();
            }, 250);
        };

        document.getElementById('_confirmCancelar').addEventListener('click', () => {
            console.log('❌ Modal confirmação: Cancelado');
            fechar();
            if (typeof opcoes.onCancelar === 'function') opcoes.onCancelar();
        });

        document.getElementById('_confirmOk').addEventListener('click', () => {
            console.log('✅ Modal confirmação: Confirmado');
            fechar();
            if (typeof opcoes.onConfirmar === 'function') opcoes.onConfirmar();
        });

        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                console.log('⊘ Modal confirmação: Clicou fora');
                fechar();
            }
        });

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

// ✅ Registrar globalmente (SEM export)
window.ModalConfirm = ModalConfirm;
console.log('✅ ModalConfirm registrado em window');