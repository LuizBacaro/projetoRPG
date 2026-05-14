/**
 * Arena Tormenta — modal de condições especiais (MB ~p.220).
 */
(function () {
    function esc(s) {
        return String(s ?? '')
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }

    function atualizarResumoCondicoes() {
        const out = document.getElementById('t20ArenaCondResumo');
        if (!out) return;
        const tips = [];
        document.querySelectorAll('#t20ArenaCondicoesRoot input[type="checkbox"]:checked').forEach((cb) => {
            const t = cb.getAttribute('data-tip');
            if (t) tips.push(t);
        });
        document.querySelectorAll('#t20ArenaCondicoesRoot input[type="radio"]:checked').forEach((r) => {
            if (r.name === 't20condTipoAtq') return;
            const t = r.getAttribute('data-tip');
            if (t && (r.name === 't20condModAtq' || r.name === 't20condModCa')) tips.push(t);
        });
        if (!tips.length) {
            out.innerHTML =
                '<span class="t20-arena-cond-resumo-vazio">Marque situações ou escolha modificadores da tabela do livro para montar um lembrete na mesa.</span>';
            return;
        }
        out.innerHTML = `<ul class="t20-arena-cond-resumo-ul">${tips.map((x) => `<li>${esc(x)}</li>`).join('')}</ul>`;
    }

    function bindCondicoesOnce() {
        const root = document.getElementById('t20ArenaCondicoesRoot');
        if (!root || root.dataset.bound) return;
        root.dataset.bound = '1';
        root.addEventListener('change', atualizarResumoCondicoes);
        atualizarResumoCondicoes();
    }

    window.__t20ArenaCondicoesInit = function () {
        bindCondicoesOnce();
        const dlg = document.getElementById('t20ArenaModalCondicoes');
        const btn = document.getElementById('t20ArenaBtnCondicoes');
        const fechar = () => {
            if (dlg && typeof dlg.close === 'function') dlg.close();
        };
        if (btn && !btn.dataset.bound) {
            btn.dataset.bound = '1';
            btn.addEventListener('click', () => {
                if (!dlg || typeof dlg.showModal !== 'function') return;
                bindCondicoesOnce();
                atualizarResumoCondicoes();
                dlg.showModal();
            });
        }
        ['t20ArenaModalCondFechar', 't20ArenaModalCondFecharFt'].forEach((id) => {
            const el = document.getElementById(id);
            if (!el || el.dataset.t20CondFecharBound) return;
            el.dataset.t20CondFecharBound = '1';
            el.addEventListener('click', fechar);
        });
    };
})();
