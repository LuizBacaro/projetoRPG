/**
 * ModalConfirm.js
 * Componente global de confirmação para ações destrutivas
 */

class ModalConfirm {
    static mostrar(opcoes = {}) {
        if (typeof opcoes !== 'object') {
            console.error('❌ ModalConfirm.mostrar() recebeu argumento inválido');
            return;
        }

        // Remover modal anterior
        const anterior = document.getElementById('_modalConfirmGlobal');
        if (anterior) anterior.remove();

        // IDs únicos
        const overlayId = '_modal_' + Date.now();
        const confirmId = '_confirmOk_' + Date.now();
        const cancelId = '_confirmCancelar_' + Date.now();

        const overlay = document.createElement('div');
        overlay.id = overlayId;
        overlay.className = 'modal-confirm-overlay';
        overlay.innerHTML = `
            <div class="modal-confirm-box">
                <div class="modal-confirm-header">
                    <span class="modal-confirm-icone">${opcoes.icone || '⚠️'}</span>
                    <h3 class="modal-confirm-titulo">${opcoes.titulo || 'Confirmar'}</h3>
                </div>
                <p class="modal-confirm-texto">${opcoes.texto || 'Deseja continuar?'}</p>
                <div class="modal-confirm-botoes">
                    <button class="modal-confirm-btn modal-confirm-cancelar" id="${cancelId}" type="button">
                        ${opcoes.textoCancelar || 'Cancelar'}
                    </button>
                    <button class="modal-confirm-btn ${opcoes.classeConfirmar || 'modal-confirm-ok'}" id="${confirmId}" type="button">
                        ${opcoes.textoConfirmar || 'Confirmar'}
                    </button>
                </div>
            </div>
        `;

        document.body.appendChild(overlay);

        const fechar = () => {
            overlay.classList.remove('show');
            setTimeout(() => { if (overlay.parentNode) overlay.remove(); }, 250);
        };

        // Guardar funções globalmente para onclick
        window['_confirmOkFn_' + confirmId] = () => {
            fechar();
            if (opcoes.onConfirmar) opcoes.onConfirmar();
        };

        window['_confirmCancelFn_' + cancelId] = () => {
            fechar();
            if (opcoes.onCancelar) opcoes.onCancelar();
        };

        // Adicionar onclick aos botões
        const btnOk = document.getElementById(confirmId);
        const btnCancel = document.getElementById(cancelId);

        if (btnOk) btnOk.setAttribute('onclick', `window['_confirmOkFn_${confirmId}']();`);
        if (btnCancel) btnCancel.setAttribute('onclick', `window['_confirmCancelFn_${cancelId}']();`);

        // Focus no botão OK
        if (btnOk) btnOk.focus();

        // Keyboard navigation: Tab para navegar, Enter para confirmar, ESC para cancelar
        const handleKeydown = (e) => {
            if (e.key === 'Escape') {
                fechar();
                document.removeEventListener('keydown', handleKeydown);
            } else if (e.key === 'Enter') {
                if (document.activeElement === btnOk) {
                    e.preventDefault();
                    window['_confirmOkFn_' + confirmId]();
                } else if (document.activeElement === btnCancel) {
                    e.preventDefault();
                    window['_confirmCancelFn_' + cancelId]();
                }
                document.removeEventListener('keydown', handleKeydown);
            } else if (e.key === 'Tab') {
                e.preventDefault();
                if (document.activeElement === btnOk) {
                    btnCancel.focus();
                } else {
                    btnOk.focus();
                }
            }
        };
        document.addEventListener('keydown', handleKeydown);

        // Clique fora da modal
        overlay.onclick = (e) => {
            if (e.target === overlay) fechar();
        };

        // Animar
        requestAnimationFrame(() => {
            overlay.classList.add('show');
        });

    }
}

window.ModalConfirm = ModalConfirm;
