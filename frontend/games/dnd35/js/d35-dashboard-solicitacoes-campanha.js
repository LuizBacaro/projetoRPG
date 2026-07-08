/**
 * Pedidos de acesso às campanhas (visão do mestre) — dashboard D&D 3.5.
 *
 * Sub-aba "Pedidos de Acesso" dentro de Campanhas: lista os pedidos de todas as
 * campanhas do mestre, com filtro Pendentes / Histórico e botões aceitar/recusar.
 * Badge com a contagem de pendentes e toast leve (não bloqueante) para novos pedidos.
 */
(function (global) {
    let pollTimer = null;
    let cachePendentes = [];
    let cacheHistorico = [];
    let historicoCarregado = false;
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
        return new global.CampanhaService();
    }

    async function buscarPendentes() {
        try {
            const rows = await getServico().listarSolicitacoesPendentes();
            cachePendentes = Array.isArray(rows) ? rows.filter((s) => s.status === 'pendente') : [];
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
        const badge = document.getElementById('d35PedidosBadge');
        if (!badge) return;
        const n = cachePendentes.length;
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
        const campanha = esc(s.campanha_nome || '—');
        return `
        <div class="d35-pedido-card" data-pedido-id="${Number(s.id)}">
            <div class="d35-pedido-info">
                <span class="d35-pedido-jogador">${jogador}</span>
                <span class="d35-pedido-detalhe">quer entrar em <strong>${campanha}</strong> com o personagem <strong>${personagem}</strong></span>
            </div>
            <div class="d35-pedido-acoes">
                <button type="button" class="btn-dash-save" data-pedido-aceitar="${Number(s.id)}">Aceitar</button>
                <button type="button" class="btn-dash-cancel d35-pedido-btn-recusar" data-pedido-recusar="${Number(s.id)}">Recusar</button>
            </div>
        </div>`;
    }

    function cardHistorico(s) {
        const jogador = esc(s.solicitante_nome || '—');
        const personagem = esc(s.personagem_nome || '—');
        const campanha = esc(s.campanha_nome || '—');
        const status = String(s.status || '').toLowerCase();
        const label = STATUS_LABEL[status] || status || '—';
        const quando = fmtData(s.resolved_at || s.updated_at || s.created_at);
        const quandoTxt = quando ? ` · ${quando}` : '';
        return `
        <div class="d35-pedido-card d35-pedido-card--hist">
            <div class="d35-pedido-info">
                <span class="d35-pedido-jogador">${jogador}</span>
                <span class="d35-pedido-detalhe"><strong>${campanha}</strong> · personagem <strong>${personagem}</strong></span>
            </div>
            <span class="d35-pedido-status d35-pedido-status--${esc(status)}">${esc(label)}${quandoTxt}</span>
        </div>`;
    }

    function atualizarFiltrosUi() {
        document.querySelectorAll('[data-d35-pedidos-filtro]').forEach((b) => {
            b.classList.toggle(
                'active',
                b.getAttribute('data-d35-pedidos-filtro') === filtro
            );
        });
    }

    function renderLista() {
        const host = document.getElementById('d35PedidosLista');
        if (!host) return;

        if (filtro === 'historico') {
            if (!historicoCarregado) {
                host.innerHTML = '<p class="dash-divcustom-vazio">Carregando histórico…</p>';
                return;
            }
            if (!cacheHistorico.length) {
                host.innerHTML = '<p class="dash-divcustom-vazio">Nenhum pedido resolvido ainda.</p>';
                return;
            }
            host.innerHTML = cacheHistorico.map(cardHistorico).join('');
            return;
        }

        if (!cachePendentes.length) {
            host.innerHTML = '<p class="dash-divcustom-vazio">Nenhum pedido de acesso pendente.</p>';
            return;
        }
        host.innerHTML = cachePendentes.map(cardPendente).join('');
    }

    function refreshUi() {
        atualizarBadge();
        atualizarFiltrosUi();
        renderLista();
    }

    async function resolver(id, aceitar) {
        const svc = getServico();
        const Toast = getToast();
        const card = document.querySelector(`.d35-pedido-card[data-pedido-id="${Number(id)}"]`);
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
            if (aceitar && typeof opts.onAceita === 'function') opts.onAceita({ id });
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
        const host = document.getElementById('d35PedidosLista');
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
        document.querySelectorAll('[data-d35-pedidos-filtro]').forEach((b) => {
            b.addEventListener('click', () => void aplicarFiltro(b.getAttribute('data-d35-pedidos-filtro')));
        });
        document
            .getElementById('d35PedidosRecarregar')
            ?.addEventListener('click', () => void atualizar());
    }

    function notificarNovos() {
        const Toast = getToast();
        const novos = cachePendentes.filter((s) => !idsNotificados.has(Number(s.id)));
        cachePendentes.forEach((s) => idsNotificados.add(Number(s.id)));
        if (novos.length && Toast && Toast.info) {
            const msg =
                novos.length === 1
                    ? 'Novo pedido de acesso a uma campanha. Veja em Campanhas → «Pedidos de Acesso».'
                    : `${novos.length} novos pedidos de acesso. Veja em Campanhas → «Pedidos de Acesso».`;
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

    global.D35CampanhaSolicitacoesMestre = {
        /** Abre/atualiza a sub-aba de pedidos. */
        async abrirPainel() {
            bindListenersUmaVez();
            await buscarPendentes();
            if (filtro === 'historico') {
                historicoCarregado = false;
                await buscarHistorico();
            }
            refreshUi();
        },

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
