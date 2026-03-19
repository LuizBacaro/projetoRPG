/**
 * ModalConfirm.js
 * SRP: utilitário de confirmação customizado — substitui confirm() nativo
 * DIP: não depende de nenhum controller — pode ser importado por qualquer módulo
 * OCP: extensível via parâmetros (icone, classe, callbacks) sem modificar o core
 *
 * USO:
 *   import { ModalConfirm } from '../ui/ModalConfirm.js';
 *
 *   ModalConfirm.mostrar({
 *       icone:          '🗑️',
 *       titulo:         'Deletar',
 *       texto:          'Deseja deletar <strong>X</strong>?',
 *       textoConfirmar: '🗑️ Deletar',
 *       classeConfirmar: 'modal-confirm-btn-perigo',
 *       onConfirmar:    () => executarDelecao(),
 *   });
 */

export class ModalConfirm {

    /**
     * Exibe o modal de confirmação customizado
     * @param {Object} opcoes
     * @param {string}   opcoes.icone           - Emoji do header (padrão: '⚠️')
     * @param {string}   opcoes.titulo          - Título do modal
     * @param {string}   opcoes.texto           - Corpo da mensagem (aceita HTML)
     * @param {string}   opcoes.textoCancelar   - Label do botão cancelar (padrão: 'Cancelar')
     * @param {string}   opcoes.textoConfirmar  - Label do botão confirmar (padrão: 'Confirmar')
     * @param {string}   opcoes.classeConfirmar - Classe CSS extra no botão confirmar
     * @param {Function} opcoes.onConfirmar     - Callback ao confirmar
     * @param {Function} opcoes.onCancelar      - Callback ao cancelar (opcional)
     */
    static mostrar(opcoes = {}) {
        // Remove instância anterior se existir (evita empilhamento)
        ModalConfirm._removerExistente();

        const overlay = ModalConfirm._criarOverlay(opcoes);
        document.body.appendChild(overlay);

        // Anima entrada
        requestAnimationFrame(() => overlay.classList.add('show'));

        // Bind de eventos
        ModalConfirm._bindEventos(overlay, opcoes);
    }

    // ──────────────────────────────────────────
    // PRIVADO
    // ──────────────────────────────────────────

    static _removerExistente() {
        const anterior = document.getElementById('_modalConfirmGlobal');
        if (anterior) anterior.remove();
    }

    static _criarOverlay(opcoes) {
        const overlay     = document.createElement('div');
        overlay.id        = '_modalConfirmGlobal';
        overlay.className = 'modal-confirm-overlay';
        overlay.innerHTML = `
            <div class="modal-confirm-box">
                <div class="modal-confirm-header">
                    <span class="modal-confirm-icone">${opcoes.icone  || '⚠️'}</span>
                    <h3 class="modal-confirm-titulo">${opcoes.titulo  || 'Confirmar'}</h3>
                </div>
                <p class="modal-confirm-texto">${opcoes.texto         || 'Deseja continuar?'}</p>
                <div class="modal-confirm-botoes">
                    <button class="modal-confirm-btn modal-confirm-cancelar" id="_confirmCancelar">
                        ${opcoes.textoCancelar  || 'Cancelar'}
                    </button>
                    <button class="modal-confirm-btn ${opcoes.classeConfirmar || 'modal-confirm-ok'}" id="_confirmOk">
                        ${opcoes.textoConfirmar || 'Confirmar'}
                    </button>
                </div>
            </div>
        `;
        return overlay;
    }

    static _bindEventos(overlay, opcoes) {
        const fechar = () => ModalConfirm._fechar(overlay);

        document.getElementById('_confirmCancelar')
            .addEventListener('click', () => {
                fechar();
                if (opcoes.onCancelar) opcoes.onCancelar();
            });

        document.getElementById('_confirmOk')
            .addEventListener('click', () => {
                fechar();
                if (opcoes.onConfirmar) opcoes.onConfirmar();
            });

        // Fechar ao clicar fora da box
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) fechar();
        });

        // Fechar com ESC
        const onEsc = (e) => {
            if (e.key === 'Escape') {
                fechar();
                document.removeEventListener('keydown', onEsc);
            }
        };
        document.addEventListener('keydown', onEsc);
    }

    static _fechar(overlay) {
        overlay.classList.remove('show');
        setTimeout(() => {
            if (overlay.parentNode) overlay.remove();
        }, 250);
    }
}