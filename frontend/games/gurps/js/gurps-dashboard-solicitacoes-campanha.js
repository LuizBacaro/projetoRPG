/**
 * Popup de solicitações pendentes para mestre — dashboard GURPS.
 */
(function (global) {
    let pollTimer = null;
    let fila = [];
    let processando = false;

    function esc(s) {
        if (s == null) return '';
        return String(s)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');
    }

    async function mostrarProxima(campSvc, Toast, onAceita) {
        if (processando || !fila.length) return;
        processando = true;
        const sol = fila.shift();
        const texto = `O jogador <strong>${esc(sol.solicitante_nome || '—')}</strong> quer entrar na campanha <strong>${esc(sol.campanha_nome || '—')}</strong> com o personagem <strong>${esc(sol.personagem_nome || '—')}</strong>.`;

        const confirmar = global.ModalConfirm && global.ModalConfirm.mostrar;
        if (!confirmar) {
            const ok = global.confirm(
                `${sol.solicitante_nome} solicita entrada de ${sol.personagem_nome} em ${sol.campanha_nome}. Aceitar?`
            );
            try {
                if (ok) {
                    await campSvc.aceitarSolicitacao(sol.id);
                    if (Toast && Toast.success) Toast.success('Jogador aceito na campanha.');
                    if (onAceita) onAceita(sol);
                } else {
                    await campSvc.recusarSolicitacao(sol.id);
                    if (Toast && Toast.info) Toast.info('Solicitação recusada.');
                }
            } catch (e) {
                if (Toast && Toast.error) Toast.error(e.message || 'Erro');
            }
            processando = false;
            void mostrarProxima(campSvc, Toast, onAceita);
            return;
        }

        global.ModalConfirm.mostrar({
            titulo: 'Pedido de entrada na campanha',
            texto,
            textoConfirmar: 'Aceitar',
            textoCancelar: 'Recusar',
            classeConfirmar: 'modal-confirm-btn-primary',
            classeCancelar: 'modal-confirm-btn-perigo',
            onConfirmar: async () => {
                try {
                    await campSvc.aceitarSolicitacao(sol.id);
                    if (Toast && Toast.success) Toast.success('Jogador aceito na campanha.');
                    if (onAceita) onAceita(sol);
                } catch (e) {
                    if (Toast && Toast.error) Toast.error(e.message || 'Erro ao aceitar');
                } finally {
                    processando = false;
                    void mostrarProxima(campSvc, Toast, onAceita);
                }
            },
            onCancelar: async () => {
                try {
                    await campSvc.recusarSolicitacao(sol.id);
                    if (Toast && Toast.info) Toast.info('Solicitação recusada.');
                } catch (e) {
                    if (Toast && Toast.error) Toast.error(e.message || 'Erro ao recusar');
                } finally {
                    processando = false;
                    void mostrarProxima(campSvc, Toast, onAceita);
                }
            },
        });
    }

    global.GurpsCampanhaSolicitacoesMestre = {
        async verificar(opts) {
            const Toast = opts && opts.Toast ? opts.Toast : global.Toast;
            const onAceita =
                opts && typeof opts.onAceita === 'function' ? opts.onAceita : null;
            const campSvc = new global.GurpsCampanhaService();
            try {
                const rows = await campSvc.listarSolicitacoesPendentes();
                if (!rows.length) return;
                fila = rows.slice();
                void mostrarProxima(campSvc, Toast, onAceita);
            } catch (_e) {
                /* silencioso */
            }
        },

        iniciarPolling(opts, intervalMs) {
            const ms = Number(intervalMs) > 0 ? Number(intervalMs) : 90000;
            this.pararPolling();
            const tick = () => void this.verificar(opts);
            tick();
            pollTimer = global.setInterval(tick, ms);
        },

        pararPolling() {
            if (pollTimer) {
                global.clearInterval(pollTimer);
                pollTimer = null;
            }
        },
    };
})(typeof window !== 'undefined' ? window : this);
