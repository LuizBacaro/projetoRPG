/**
 * Mesa da campanha — sub-abas dinâmicas e workspace (combatentes + arena) dentro de Campanhas.
 */
(function (global) {
    function esc(s) {
        if (s == null) return '';
        return String(s)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }

    global.__t20CampanhaWorkspaceInit = function (opts) {
        if (!opts) return;

        const onSelecionarCampanha =
            typeof opts.onSelecionarCampanha === 'function' ? opts.onSelecionarCampanha : null;
        const onSairCampanha = typeof opts.onSairCampanha === 'function' ? opts.onSairCampanha : null;

        const onAbrirArena = typeof opts.onAbrirArena === 'function' ? opts.onAbrirArena : null;
        const onAbrirPedidos = typeof opts.onAbrirPedidos === 'function' ? opts.onAbrirPedidos : null;

        let campanhaMesaAtivaId = null;

        function subChaveMesa(id) {
            return `mesa-${id}`;
        }

        function esconderTodosPanes() {
            document.getElementById('t20campSubabaCadastro')?.classList.remove('t20-camp-subaba-pane--active');
            document.getElementById('t20campSubabaSessoes')?.classList.remove('t20-camp-subaba-pane--active');
            document.getElementById('t20campSubabaWorkspace')?.classList.remove('t20-camp-subaba-pane--active');
        }

        function desmarcarSubAbas() {
            document.querySelectorAll('#t20campSubAbas .t20-camp-subaba-btn').forEach((b) => {
                b.classList.remove('t20-camp-subaba-btn--active');
            });
        }

        function ativarSubaba(which) {
            desmarcarSubAbas();
            esconderTodosPanes();
            const btn = document.querySelector(`#t20campSubAbas [data-t20camp-sub="${which}"]`);
            if (btn) btn.classList.add('t20-camp-subaba-btn--active');
            if (which === 'cadastro') {
                document.getElementById('t20campSubabaCadastro')?.classList.add('t20-camp-subaba-pane--active');
                campanhaMesaAtivaId = null;
                if (onSairCampanha) onSairCampanha();
                return;
            }
            if (which === 'sessoes') {
                document.getElementById('t20campSubabaSessoes')?.classList.add('t20-camp-subaba-pane--active');
                campanhaMesaAtivaId = null;
                if (onSairCampanha) onSairCampanha();
                return;
            }
            if (which.startsWith('mesa-')) {
                const id = Number(which.replace('mesa-', ''));
                if (!Number.isFinite(id) || id <= 0) return;
                campanhaMesaAtivaId = id;
                document.getElementById('t20campSubabaWorkspace')?.classList.add('t20-camp-subaba-pane--active');
                if (onSelecionarCampanha) onSelecionarCampanha(id);
            }
        }

        function ativarWsPane(which) {
            document.querySelectorAll('.t20-camp-ws-nav-btn').forEach((b) => {
                b.classList.toggle('t20-camp-ws-nav-btn--active', b.getAttribute('data-camp-ws') === which);
            });
            const comb = document.getElementById('t20campWsCombatentes');
            const arena = document.getElementById('t20campWsArena');
            const pedidos = document.getElementById('t20campWsPedidos');
            if (comb) comb.classList.toggle('t20-camp-ws-pane--active', which === 'combatentes');
            if (arena) arena.classList.toggle('t20-camp-ws-pane--active', which === 'arena');
            if (pedidos) pedidos.classList.toggle('t20-camp-ws-pane--active', which === 'pedidos');
            if (which === 'arena' && onAbrirArena) onAbrirArena();
            if (which === 'pedidos' && onAbrirPedidos) onAbrirPedidos();
        }

        function renderBotoesCampanhas(campanhas) {
            const host = document.getElementById('t20campSubAbasCampanhas');
            if (!host) return;
            const lista = Array.isArray(campanhas) ? campanhas : [];
            if (!lista.length) {
                host.innerHTML = '';
                return;
            }
            host.innerHTML = lista
                .map((c) => {
                    const id = Number(c.id);
                    const nome = esc(c.nome || `Campanha #${id}`);
                    const ativo = campanhaMesaAtivaId === id ? ' t20-camp-subaba-btn--active' : '';
                    return `<button type="button" class="t20-camp-subaba-btn t20-camp-subaba-btn--mesa${ativo}" data-t20camp-sub="mesa-${id}" title="Mesa de mestre desta campanha">🎲 ${nome}</button>`;
                })
                .join('');
        }

        function abrirCampanha(id) {
            const num = Number(id);
            if (!Number.isFinite(num) || num <= 0) return;
            campanhaMesaAtivaId = num;
            if (global.__t20DashCampanhas && typeof global.__t20DashCampanhas.ativarSubaba === 'function') {
                global.__t20DashCampanhas.ativarSubaba(`mesa-${num}`);
            }
            ativarWsPane('combatentes');
        }

        document.querySelector('.t20-camp-ws-nav')?.addEventListener('click', (ev) => {
            const btn = ev.target.closest('[data-camp-ws]');
            if (!btn) return;
            ativarWsPane(btn.getAttribute('data-camp-ws') || 'combatentes');
        });

        const bloq = document.getElementById('t20ArenaBloqueioJogador');
        if (bloq) bloq.hidden = true;

        function sairMesa() {
            campanhaMesaAtivaId = null;
        }

        global.__t20CampanhaWorkspace = {
            renderBotoesCampanhas,
            abrirCampanha,
            sairMesa,
            getCampanhaAtivaId: () => campanhaMesaAtivaId,
            ativarSubabaCadastro: () => ativarSubaba('cadastro'),
        };
    };
})(typeof window !== 'undefined' ? window : this);
