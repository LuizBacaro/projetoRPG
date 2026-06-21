/**
 * Modal de confirmação D&D 5e — estilo alinhado à ficha (substitui window.confirm).
 */
const Dnd5eConfirmModal = (() => {
    let overlay = null;

    function fechar() {
        if (!overlay) return;
        overlay.classList.remove('is-open');
        overlay.setAttribute('aria-hidden', 'true');
        setTimeout(() => {
            overlay?.remove();
            overlay = null;
        }, 220);
    }

    /**
     * @param {object} opcoes
     * @param {string} [opcoes.titulo]
     * @param {string} [opcoes.icone]
     * @param {string} [opcoes.texto]
     * @param {string} [opcoes.detalhe]
     * @param {string} [opcoes.textoConfirmar]
     * @param {string} [opcoes.textoCancelar]
     * @param {string} [opcoes.variante] — repouso | perigo | padrao
     * @returns {Promise<boolean>}
     */
    function confirmar(opcoes = {}) {
        return new Promise((resolve) => {
            fechar();

            const variante = opcoes.variante || 'padrao';
            overlay = document.createElement('div');
            overlay.className = `f5e-confirm-overlay f5e-confirm--${variante}`;
            overlay.setAttribute('role', 'dialog');
            overlay.setAttribute('aria-modal', 'true');
            overlay.setAttribute('aria-labelledby', 'f5e_confirm_titulo');
            overlay.innerHTML = `
                <div class="f5e-confirm-box">
                    <div class="f5e-confirm-header">
                        <span class="f5e-confirm-icone" aria-hidden="true">${opcoes.icone || '⚠️'}</span>
                        <h2 class="f5e-confirm-titulo" id="f5e_confirm_titulo">${opcoes.titulo || 'Confirmar'}</h2>
                    </div>
                    <p class="f5e-confirm-texto">${opcoes.texto || 'Deseja continuar?'}</p>
                    ${opcoes.detalhe ? `<ul class="f5e-confirm-detalhe">${opcoes.detalhe}</ul>` : ''}
                    <div class="f5e-confirm-acoes">
                        <button type="button" class="f5e-confirm-btn f5e-confirm-btn-cancelar" data-acao="cancelar">
                            ${opcoes.textoCancelar || 'Cancelar'}
                        </button>
                        <button type="button" class="f5e-confirm-btn f5e-confirm-btn-ok" data-acao="ok">
                            ${opcoes.textoConfirmar || 'Confirmar'}
                        </button>
                    </div>
                </div>
            `;

            const finalizar = (ok) => {
                fechar();
                resolve(ok);
            };

            overlay.querySelector('[data-acao="ok"]')?.addEventListener('click', () => finalizar(true));
            overlay.querySelector('[data-acao="cancelar"]')?.addEventListener('click', () => finalizar(false));
            overlay.addEventListener('click', (e) => {
                if (e.target === overlay) finalizar(false);
            });

            const onKey = (e) => {
                if (e.key === 'Escape') {
                    finalizar(false);
                    document.removeEventListener('keydown', onKey);
                }
            };
            document.addEventListener('keydown', onKey);

            document.body.appendChild(overlay);
            requestAnimationFrame(() => {
                overlay.classList.add('is-open');
                overlay.setAttribute('aria-hidden', 'false');
                overlay.querySelector('[data-acao="ok"]')?.focus();
            });
        });
    }

    return { confirmar };
})();
