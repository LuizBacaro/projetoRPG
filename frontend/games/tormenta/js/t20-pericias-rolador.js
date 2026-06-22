/**
 * Calculadora e rolador de perícias MB (API `/tormenta/regras/pericias/*`).
 */
(function () {
    const regras = () => new TormentaRegrasService();

    function q(id) {
        return document.getElementById(id);
    }

    let dcDialogBound = false;
    let dcResolve = null;

    function bindDcDialog() {
        if (dcDialogBound) return;
        const dlg = q('t20ModalPericiaDc');
        if (!dlg) return;
        dcDialogBound = true;

        const fechar = () => {
            if (typeof dlg.close === 'function') dlg.close();
            if (dcResolve) {
                dcResolve(null);
                dcResolve = null;
            }
        };

        q('t20PericiaDcFechar')?.addEventListener('click', fechar);
        q('t20PericiaDcCancelar')?.addEventListener('click', fechar);
        dlg.addEventListener('cancel', (ev) => {
            ev.preventDefault();
            fechar();
        });

        q('t20PericiaDcRolar')?.addEventListener('click', () => {
            const inp = q('t20PericiaDcInput');
            const raw = inp ? String(inp.value).trim() : '';
            const dc = raw === '' ? 15 : Number(raw);
            if (!Number.isFinite(dc) || dc < 1) {
                if (typeof Toast !== 'undefined' && Toast.error) {
                    Toast.error('Informe uma CD válida (1–99).');
                }
                inp?.focus();
                return;
            }
            if (typeof dlg.close === 'function') dlg.close();
            if (dcResolve) {
                dcResolve(Math.min(99, Math.max(1, Math.round(dc))));
                dcResolve = null;
            }
        });

        q('t20PericiaDcInput')?.addEventListener('keydown', (ev) => {
            if (ev.key === 'Enter') {
                ev.preventDefault();
                q('t20PericiaDcRolar')?.click();
            }
        });
    }

    function pedirDcPericia(nome) {
        bindDcDialog();
        const dlg = q('t20ModalPericiaDc');
        if (!dlg) {
            const dcInp = window.prompt(`DC para ${nome} (padrão 15):`, '15');
            if (dcInp == null) return Promise.resolve(null);
            return Promise.resolve(Number(dcInp) || 15);
        }

        const titulo = q('t20PericiaDcTitulo');
        const label = q('t20PericiaDcLabel');
        const hint = q('t20PericiaDcHint');
        const inp = q('t20PericiaDcInput');
        if (titulo) titulo.textContent = `Teste: ${nome}`;
        if (label) label.textContent = `CD para ${nome} (padrão 15)`;
        if (hint) {
            hint.textContent =
                'Informe a Classe de Dificuldade (CD) do teste. O resultado será 1d20 + bônus da perícia.';
        }
        if (inp) {
            inp.value = '15';
        }

        return new Promise((resolve) => {
            dcResolve = resolve;
            if (typeof dlg.showModal === 'function') {
                dlg.showModal();
            } else {
                dlg.setAttribute('open', '');
            }
            setTimeout(() => {
                inp?.focus();
                inp?.select?.();
            }, 40);
        });
    }

    function nivelPersonagem() {
        const n = Number(q('f_nivel') && q('f_nivel').value);
        return Number.isFinite(n) && n >= 1 ? n : 1;
    }

    function slugRaca() {
        const sel = q('f_raca_select');
        return sel && sel.value && sel.value !== '__livre__' ? sel.value : '';
    }

    function bonusRacialPericia(nome) {
        const c = window.__t20TracosRaciaisCache;
        if (!c || !c.pericias_bonus) return 0;
        return Number(c.pericias_bonus[nome] || 0);
    }

    async function calcularBonusLinha(tr) {
        const nomeEl = tr.querySelector('.t20-p-nome');
        const nome = nomeEl ? nomeEl.textContent.trim() : '';
        const treinado = Boolean(tr.querySelector('.p-treinado')?.checked);
        const modAt = Number(tr.querySelector('.p-mod')?.value || 0);
        const outros = Number(tr.querySelector('.p-out')?.value || 0);
        const grad = Number(tr.querySelector('.p-total')?.value || 0);
        const deClasse = tr.classList.contains('t20-pericia-de-classe-row');
        const body = {
            nivel: nivelPersonagem(),
            mod_atributo: modAt,
            treinado,
            graduacao: grad,
            outros,
            racial_bonus: bonusRacialPericia(nome),
            slug_raca: slugRaca(),
            nome_pericia: nome,
            pericia_de_classe: deClasse,
            penalidade_armadura: 0,
        };
        const res = await regras().calcularBonusPericia(body);
        return res;
    }

    async function rolarPericia(tr) {
        const nomeEl = tr.querySelector('.t20-p-nome');
        const nome = nomeEl ? nomeEl.textContent.trim() : 'Perícia';
        const dc = await pedirDcPericia(nome);
        if (dc == null) return;
        try {
            const calc = await calcularBonusLinha(tr);
            const roll = await regras().rolarPericia({
                bonus: calc.bonus_total,
                dc,
            });
            let msg = `${nome}: 1d20=${roll.d20} + ${roll.bonus} = ${roll.total} vs DC ${dc} → `;
            msg += roll.sucesso ? 'SUCESSO' : 'FALHA';
            if (roll.falha_critica) msg += ' (falha crítica)';
            if (roll.sucesso_critico) msg += ' (sucesso crítico)';
            if (calc.percepcao_passiva != null) {
                msg += ` · Passiva: ${calc.percepcao_passiva}`;
            }
            if (typeof Toast !== 'undefined' && Toast.info) Toast.info(msg);
            else alert(msg);
        } catch (e) {
            if (typeof Toast !== 'undefined' && Toast.error) Toast.error(e.message || 'Erro ao rolar');
        }
    }

    function injetarBotoesRolar() {
        const tbl = document.querySelector('#tblPericias thead tr');
        const tb = document.querySelector('#tblPericias tbody');
        if (!tbl || !tb || tbl.dataset.rollCol) return;
        tbl.dataset.rollCol = '1';
        const th = document.createElement('th');
        th.textContent = 'Teste';
        th.title = 'Rolar 1d20 + bônus vs DC';
        tbl.appendChild(th);
        tb.querySelectorAll('tr').forEach((tr) => {
            const td = document.createElement('td');
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'tormenta-btn tormenta-btn--sm';
            btn.textContent = '🎲';
            btn.title = 'Rolar teste de perícia';
            btn.addEventListener('click', () => rolarPericia(tr));
            td.appendChild(btn);
            tr.appendChild(td);
        });
    }

    document.addEventListener('DOMContentLoaded', () => {
        bindDcDialog();
        const obs = new MutationObserver(() => {
            if (document.querySelector('#tblPericias tbody tr')) injetarBotoesRolar();
        });
        const tb = document.querySelector('#tblPericias tbody');
        if (tb) obs.observe(tb, { childList: true });
        setTimeout(injetarBotoesRolar, 800);
    });
})();
