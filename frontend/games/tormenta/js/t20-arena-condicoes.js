/**
 * Arena Tormenta — modal de condições MB (~p.220): alvos múltiplos + resumo + estado no painel do ativo.
 */
(function () {
    function esc(s) {
        return String(s ?? '')
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }

    function arenaRef() {
        return window.__t20ArenaRef;
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

    function rotuloDoInput(inp) {
        const canon = inp.getAttribute('data-cond-rotulo');
        if (canon && String(canon).trim()) return String(canon).trim();
        const lb = inp.closest('label');
        if (!lb) return '';
        const t = lb.innerText.replace(/\s+/g, ' ').trim();
        return t.length > 56 ? `${t.slice(0, 54)}…` : t;
    }

    function coletarTipsERotulos() {
        const tips = [];
        const rotulos = [];
        document.querySelectorAll('#t20ArenaCondicoesRoot input[type="checkbox"]:checked').forEach((cb) => {
            const tip = cb.getAttribute('data-tip');
            if (tip) tips.push(tip);
            const r = rotuloDoInput(cb);
            if (r) rotulos.push(r);
        });
        document.querySelectorAll('#t20ArenaCondicoesRoot input[type="radio"]:checked').forEach((r) => {
            if (r.name === 't20condTipoAtq') {
                const tip = r.getAttribute('data-tip');
                if (tip) tips.push(tip);
                const lab = rotuloDoInput(r);
                if (lab) rotulos.push(lab);
                return;
            }
            if (!r.value) return;
            const tip = r.getAttribute('data-tip');
            if (tip) tips.push(tip);
            const lab = rotuloDoInput(r);
            if (lab) rotulos.push(lab);
        });
        return { tips, rotulos };
    }

    function popularListaAlvosCond() {
        const host = document.getElementById('t20ArenaCondListaAlvos');
        const ar = arenaRef();
        if (!host || !ar) return;
        const ids = ar.ordemIds || [];
        const ativo = ids.length ? ids[ar.turnoIdx] : null;
        if (!ids.length) {
            host.innerHTML = '<p class="t20-arena-cb-vazio">Nenhum combatente no combate.</p>';
            return;
        }
        host.innerHTML = ids
            .map((id) => {
                const p = ar.byId[id];
                const nome = p ? esc(p.nome) : `#${id}`;
                const tipo = p ? String(p.tipo || '').toLowerCase() : '';
                const badge = tipo ? `<span class="t20-arena-cb-tipo t20-arena-cb-tipo--${esc(tipo)}">${esc(tipo)}</span>` : '';
                const ck = id === ativo ? ' checked' : '';
                return `<div class="t20-arena-cb-item"><input type="checkbox" class="t20-arena-cb-inp t20-cond-alvo-cb" id="t20cond-alvo-${id}" value="${id}"${ck} /><label class="t20-arena-cb-lbl" for="t20cond-alvo-${id}"><span class="t20-arena-cb-nome">${nome}</span>${badge}</label></div>`;
            })
            .join('');
    }

    function fecharCondDlg(dlg) {
        if (dlg && typeof dlg.close === 'function') dlg.close();
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
        const fechar = () => fecharCondDlg(dlg);

        if (btn && !btn.dataset.bound) {
            btn.dataset.bound = '1';
            btn.addEventListener('click', () => {
                if (!dlg || typeof dlg.showModal !== 'function') return;
                const ar = arenaRef();
                if (!ar || !ar.ativo || !ar.ordemIds.length) {
                    if (typeof Toast !== 'undefined' && Toast.error) Toast.error('Inicie o combate antes.');
                    return;
                }
                bindCondicoesOnce();
                popularListaAlvosCond();
                atualizarResumoCondicoes();
                dlg.showModal();
            });
        }

        ['t20ArenaModalCondFechar', 't20ArenaModalCondCancelar', 't20ArenaModalCondFecharFt'].forEach((id) => {
            const el = document.getElementById(id);
            if (!el || el.dataset.t20CondFecharBound) return;
            el.dataset.t20CondFecharBound = '1';
            el.addEventListener('click', fechar);
        });

        const btnApl = document.getElementById('t20ArenaModalCondAplicar');
        if (btnApl && !btnApl.dataset.bound) {
            btnApl.dataset.bound = '1';
            btnApl.addEventListener('click', async () => {
                const ar = arenaRef();
                if (!ar || !dlg) return;
                const alvos = Array.from(document.querySelectorAll('.t20-cond-alvo-cb:checked'))
                    .map((el) => Number(el.value))
                    .filter((id) => Number.isFinite(id) && id > 0);
                if (!alvos.length) {
                    if (typeof Toast !== 'undefined' && Toast.error) Toast.error('Marque ao menos um combatente.');
                    return;
                }
                const { tips, rotulos } = coletarTipsERotulos();
                if (!tips.length) {
                    if (typeof Toast !== 'undefined' && Toast.error) Toast.error('Marque situações ou modificadores antes de aplicar.');
                    return;
                }
                const api = window.__t20ArenaCombateSvc;
                if (!api || typeof api.aplicarCondicoesMb !== 'function') {
                    if (typeof Toast !== 'undefined' && Toast.error) Toast.error('Serviço de combate indisponível.');
                    return;
                }
                const payload = {};
                alvos.forEach((id) => {
                    payload[String(id)] = { tips: tips.slice(), rotulos: rotulos.slice() };
                });
                try {
                    btnApl.disabled = true;
                    const st = await api.aplicarCondicoesMb(payload);
                    if (typeof window.__t20ArenaApplyFromApi === 'function') window.__t20ArenaApplyFromApi(st);
                    else {
                        alvos.forEach((id) => {
                            ar.condPorId[id] = { tips: tips.slice(), rotulos: rotulos.slice() };
                        });
                    }
                    if (typeof window.__t20ArenaRenderCondStatus === 'function') window.__t20ArenaRenderCondStatus();
                    fecharCondDlg(dlg);
                    if (typeof Toast !== 'undefined' && Toast.success) Toast.success(`Cenário gravado para ${alvos.length} combatente(s).`);
                } catch (e) {
                    if (typeof Toast !== 'undefined' && Toast.error) Toast.error(e.message || 'Erro ao gravar condições.');
                } finally {
                    btnApl.disabled = false;
                }
            });
        }
    };
})();
