/**
 * Pedidos de acesso à campanha (visão do mestre) — dashboard Tormenta.
 *
 * Substitui o antigo popup bloqueante por:
 *  - Aba "Pedidos de Acesso" dentro da mesa da campanha, com a lista filtrada
 *    pela campanha ativa e botões aceitar/recusar por pedido.
 *  - Filtro Pendentes / Histórico (aceitos, recusados e cancelados).
 *  - Badge com a contagem de pendentes da campanha ativa.
 *  - Toast leve (não bloqueante) quando surgem novos pedidos.
 */
(function (global) {
    let pollTimer = null;
    let cachePendentes = [];
    let cacheHistorico = [];
    let historicoCarregado = false;
    let campanhaAtivaId = null;
    let filtro = 'pendentes';
    let opts = {};
    let idsNotificados = new Set();

    const STATUS_LABEL = {
        aceita: 'Aceito',
        recusada: 'Recusado',
        cancelada: 'Cancelado pelo jogador',
        pendente: 'Pendente',
    };

    function esc(s) {
        if (s == null) return '';
        return String(s)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }

    function getToast() {
        return (opts && opts.Toast) || global.Toast || null;
    }

    function getServico() {
        return new global.TormentaCampanhaService();
    }

    function daCampanha(rows, id) {
        const alvo = Number(id);
        if (!Number.isFinite(alvo) || alvo <= 0) return [];
        return rows.filter((s) => Number(s.campanha_id) === alvo);
    }

    function pendentesDaCampanha(id) {
        return daCampanha(cachePendentes, id).filter((s) => s.status === 'pendente');
    }

    async function buscarPendentes() {
        try {
            const rows = await getServico().listarSolicitacoesPendentes();
            cachePendentes = Array.isArray(rows) ? rows : [];
        } catch (_e) {
            cachePendentes = [];
        }
        return cachePendentes;
    }

    async function buscarHistorico() {
        try {
            const rows = await getServico().listarHistoricoSolicitacoes();
            cacheHistorico = Array.isArray(rows) ? rows : [];
            historicoCarregado = true;
        } catch (_e) {
            cacheHistorico = [];
        }
        return cacheHistorico;
    }

    function atualizarBadge() {
        const badge = document.getElementById('t20campPedidosBadge');
        if (!badge) return;
        const n = pendentesDaCampanha(campanhaAtivaId).length;
        badge.textContent = String(n);
        badge.hidden = n === 0;
    }

    function fmtData(iso) {
        if (!iso) return '';
        const d = new Date(iso);
        if (Number.isNaN(d.getTime())) return '';
        return d.toLocaleDateString('pt-BR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
        });
    }

    function cardPendente(s) {
        const jogador = esc(s.solicitante_nome || '—');
        const personagem = esc(s.personagem_nome || '—');
        return `
        <div class="t20-camp-pedido-card" data-pedido-id="${Number(s.id)}">
            <div class="t20-camp-pedido-info">
                <span class="t20-camp-pedido-jogador">${jogador}</span>
                <span class="t20-camp-pedido-detalhe">quer entrar com o personagem <strong>${personagem}</strong></span>
            </div>
            <div class="t20-camp-pedido-acoes">
                <button type="button" class="tormenta-btn tormenta-btn--primary" data-pedido-aceitar="${Number(s.id)}">Aceitar</button>
                <button type="button" class="tormenta-btn t20-camp-pedido-btn-recusar" data-pedido-recusar="${Number(s.id)}">Recusar</button>
            </div>
        </div>`;
    }

    function cardHistorico(s) {
        const jogador = esc(s.solicitante_nome || '—');
        const personagem = esc(s.personagem_nome || '—');
        const status = String(s.status || '').toLowerCase();
        const label = STATUS_LABEL[status] || status || '—';
        const quando = fmtData(s.resolved_at || s.updated_at || s.created_at);
        const quandoTxt = quando ? ` · ${quando}` : '';
        return `
        <div class="t20-camp-pedido-card t20-camp-pedido-card--hist">
            <div class="t20-camp-pedido-info">
                <span class="t20-camp-pedido-jogador">${jogador}</span>
                <span class="t20-camp-pedido-detalhe">personagem <strong>${personagem}</strong></span>
            </div>
            <span class="t20-camp-pedido-status t20-camp-pedido-status--${esc(status)}">${esc(label)}${quandoTxt}</span>
        </div>`;
    }

    function atualizarFiltrosUi() {
        document.querySelectorAll('[data-pedidos-filtro]').forEach((b) => {
            b.classList.toggle(
                't20-camp-pedidos-filtro--active',
                b.getAttribute('data-pedidos-filtro') === filtro
            );
        });
    }

    function renderLista() {
        const host = document.getElementById('t20campPedidosLista');
        if (!host) return;

        if (!campanhaAtivaId) {
            host.innerHTML = '<p class="tormenta-cell-muted">Selecione uma campanha acima.</p>';
            return;
        }

        if (filtro === 'historico') {
            const rows = daCampanha(cacheHistorico, campanhaAtivaId);
            if (!historicoCarregado) {
                host.innerHTML = '<p class="tormenta-cell-muted">Carregando histórico…</p>';
                return;
            }
            if (!rows.length) {
                host.innerHTML = '<p class="tormenta-cell-muted">Nenhum pedido resolvido nesta campanha.</p>';
                return;
            }
            host.innerHTML = rows.map(cardHistorico).join('');
            return;
        }

        const pendentes = pendentesDaCampanha(campanhaAtivaId);
        if (!pendentes.length) {
            host.innerHTML = '<p class="tormenta-cell-muted">Nenhum pedido de acesso pendente nesta campanha.</p>';
            return;
        }
        host.innerHTML = pendentes.map(cardPendente).join('');
    }

    function refreshUi() {
        atualizarBadge();
        atualizarFiltrosUi();
        renderLista();
    }

    async function resolver(id, aceitar) {
        const svc = getServico();
        const Toast = getToast();
        const card = document.querySelector(`.t20-camp-pedido-card[data-pedido-id="${Number(id)}"]`);
        card?.querySelectorAll('button').forEach((b) => (b.disabled = true));
        try {
            if (aceitar) {
                await svc.aceitarSolicitacao(id);
                if (Toast && Toast.success) Toast.success('Jogador aceito na campanha.');
            } else {
                await svc.recusarSolicitacao(id);
                if (Toast && Toast.info) Toast.info('Solicitação recusada.');
            }
            cachePendentes = cachePendentes.filter((s) => Number(s.id) !== Number(id));
            idsNotificados.delete(Number(id));
            historicoCarregado = false;
            refreshUi();
            if (aceitar && typeof opts.onAceita === 'function') {
                opts.onAceita({ campanha_id: campanhaAtivaId });
            }
        } catch (e) {
            if (Toast && Toast.error) Toast.error(e.message || 'Erro ao processar pedido.');
            card?.querySelectorAll('button').forEach((b) => (b.disabled = false));
        }
    }

    async function aplicarFiltro(novo) {
        filtro = novo === 'historico' ? 'historico' : 'pendentes';
        atualizarFiltrosUi();
        if (filtro === 'historico' && !historicoCarregado) {
            renderLista();
            await buscarHistorico();
        }
        renderLista();
    }

    let listenersBound = false;
    function bindListenersUmaVez() {
        if (listenersBound) return;
        listenersBound = true;
        const host = document.getElementById('t20campPedidosLista');
        host?.addEventListener('click', (ev) => {
            const btnAceitar = ev.target.closest('[data-pedido-aceitar]');
            if (btnAceitar) {
                void resolver(Number(btnAceitar.getAttribute('data-pedido-aceitar')), true);
                return;
            }
            const btnRecusar = ev.target.closest('[data-pedido-recusar]');
            if (btnRecusar) {
                void resolver(Number(btnRecusar.getAttribute('data-pedido-recusar')), false);
            }
        });
        document.querySelectorAll('[data-pedidos-filtro]').forEach((b) => {
            b.addEventListener('click', () => {
                void aplicarFiltro(b.getAttribute('data-pedidos-filtro'));
            });
        });
        document
            .getElementById('t20campPedidosRecarregar')
            ?.addEventListener('click', () => void atualizar());
    }

    function notificarNovos() {
        const Toast = getToast();
        const novos = cachePendentes.filter(
            (s) => s.status === 'pendente' && !idsNotificados.has(Number(s.id))
        );
        cachePendentes.forEach((s) => {
            if (s.status === 'pendente') idsNotificados.add(Number(s.id));
        });
        if (novos.length && Toast && Toast.info) {
            const msg =
                novos.length === 1
                    ? 'Novo pedido de acesso a uma campanha. Veja em «Pedidos de Acesso» na mesa.'
                    : `${novos.length} novos pedidos de acesso. Veja em «Pedidos de Acesso» na mesa.`;
            Toast.info(msg);
        }
    }

    async function atualizar() {
        await buscarPendentes();
        if (filtro === 'historico') {
            historicoCarregado = false;
            await buscarHistorico();
        }
        refreshUi();
    }

    global.T20CampanhaSolicitacoesMestre = {
        /** Define a campanha cuja fila é exibida no painel/badge. */
        setCampanhaAtiva(id) {
            campanhaAtivaId = Number(id) || null;
            bindListenersUmaVez();
            refreshUi();
        },

        /** Abre/atualiza o painel de pedidos da campanha ativa. */
        async abrirPainel(id) {
            if (id != null) campanhaAtivaId = Number(id) || null;
            bindListenersUmaVez();
            await buscarPendentes();
            if (filtro === 'historico') {
                historicoCarregado = false;
                await buscarHistorico();
            }
            refreshUi();
        },

        /** Recarrega a fila e atualiza badge + painel. */
        atualizar,

        iniciarPolling(config, intervalMs) {
            opts = config || {};
            bindListenersUmaVez();
            const ms = Number(intervalMs) > 0 ? Number(intervalMs) : 90000;
            this.pararPolling();
            const tick = async () => {
                await buscarPendentes();
                notificarNovos();
                refreshUi();
            };
            void tick();
            pollTimer = global.setInterval(() => void tick(), ms);
        },

        pararPolling() {
            if (pollTimer) {
                global.clearInterval(pollTimer);
                pollTimer = null;
            }
        },
    };
})(typeof window !== 'undefined' ? window : this);
