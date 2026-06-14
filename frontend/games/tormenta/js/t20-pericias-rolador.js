/**
 * Calculadora e rolador de perícias MB (API `/tormenta/regras/pericias/*`).
 */
(function () {
    const regras = () => new TormentaRegrasService();

    function q(id) {
        return document.getElementById(id);
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
        const dcInp = window.prompt(`DC para ${nome} (padrão 15):`, '15');
        if (dcInp == null) return;
        const dc = Number(dcInp) || 15;
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
        const obs = new MutationObserver(() => {
            if (document.querySelector('#tblPericias tbody tr')) injetarBotoesRolar();
        });
        const tb = document.querySelector('#tblPericias tbody');
        if (tb) obs.observe(tb, { childList: true });
        setTimeout(injetarBotoesRolar, 800);
    });
})();
