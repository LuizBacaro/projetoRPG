/**
 * RF-T12c — rolagem contextual na ficha (perícias, ataques, iniciativa).
 * RF-T04i — diálogo de CD também aceita seletor de uso (lista vertical).
 */
(function (global) {
    'use strict';

    const LOG_MAX = 12;
    let dialogBound = false;
    let dialogResolve = null;

    function q(id) {
        return document.getElementById(id);
    }

    function regras() {
        return new TormentaRegrasService();
    }

    function toastInfo(msg) {
        if (typeof Toast !== 'undefined' && Toast.info) Toast.info(msg);
        else alert(msg);
    }

    function toastError(msg) {
        if (typeof Toast !== 'undefined' && Toast.error) Toast.error(msg);
        else alert(msg);
    }

    function registrarLog(texto) {
        if (!texto) return;
        const arr = global.__t20LogMesa || [];
        arr.unshift({ ts: Date.now(), texto: String(texto) });
        if (arr.length > LOG_MAX) arr.length = LOG_MAX;
        global.__t20LogMesa = arr;
        const el = q('fichaUltimaRolagem');
        if (el) el.textContent = texto;
    }

    function usosFieldset() {
        return q('t20PericiaDcUsos');
    }

    function usosListEl() {
        return q('t20PericiaDcUsosList');
    }

    function limparUsosUi() {
        const fs = usosFieldset();
        const list = usosListEl();
        if (fs) {
            fs.hidden = true;
            fs.setAttribute('aria-hidden', 'true');
        }
        if (list) list.innerHTML = '';
        const dlg = q('t20ModalPericiaDc');
        if (dlg) {
            dlg.classList.remove('t20-dialog-pericia-dc--com-usos');
            delete dlg.dataset.t20TemUsos;
        }
    }

    function usoSelecionadoId() {
        const checked = usosListEl()?.querySelector('input[name="t20PericiaDcUso"]:checked');
        return checked ? String(checked.value) : null;
    }

    function montarUsosUi(usos, usoDefaultId) {
        const fs = usosFieldset();
        const list = usosListEl();
        const dlg = q('t20ModalPericiaDc');
        if (!fs || !list || !dlg || !Array.isArray(usos) || !usos.length) {
            limparUsosUi();
            return;
        }
        const def =
            usoDefaultId && usos.some((u) => u.id === usoDefaultId)
                ? usoDefaultId
                : usos[0].id;
        list.innerHTML = usos
            .map((u) => {
                const id = `t20PericiaDcUso_${u.id}`;
                const checked = u.id === def ? ' checked' : '';
                const hint = u.hint
                    ? `<span class="t20-pericia-dc-uso__hint">${escapeHtml(u.hint)}</span>`
                    : '';
                return `<label class="t20-pericia-dc-uso" for="${id}">
                    <input type="radio" name="t20PericiaDcUso" id="${id}" value="${escapeAttr(u.id)}"${checked} />
                    <span class="t20-pericia-dc-uso__body">
                        <span class="t20-pericia-dc-uso__rotulo">${escapeHtml(u.rotulo)}</span>
                        ${hint}
                    </span>
                </label>`;
            })
            .join('');
        fs.hidden = false;
        fs.setAttribute('aria-hidden', 'false');
        dlg.classList.add('t20-dialog-pericia-dc--com-usos');
        dlg.dataset.t20TemUsos = '1';
        syncUsoHighlight();
        list.querySelectorAll('input[name="t20PericiaDcUso"]').forEach((inp) => {
            inp.addEventListener('change', syncUsoHighlight);
        });
    }

    function syncUsoHighlight() {
        const list = usosListEl();
        if (!list) return;
        list.querySelectorAll('.t20-pericia-dc-uso').forEach((lab) => {
            const on = Boolean(lab.querySelector('input:checked'));
            lab.classList.toggle('is-selected', on);
            lab.setAttribute('aria-checked', on ? 'true' : 'false');
        });
    }

    function escapeHtml(text) {
        return String(text)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }

    function escapeAttr(text) {
        return escapeHtml(text).replace(/'/g, '&#39;');
    }

    function resolverRetornoConfirmacao(val) {
        const dlg = q('t20ModalPericiaDc');
        if (dlg && dlg.dataset.t20TemUsos === '1') {
            return { valor: val, usoId: usoSelecionadoId() };
        }
        return val;
    }

    function bindDialogoRolagem() {
        if (dialogBound) return;
        const dlg = q('t20ModalPericiaDc');
        if (!dlg) return;
        dialogBound = true;

        const fechar = (valor) => {
            if (typeof dlg.close === 'function') dlg.close();
            if (dialogResolve) {
                dialogResolve(valor);
                dialogResolve = null;
            }
        };

        q('t20PericiaDcFechar')?.addEventListener('click', () => fechar(null));
        q('t20PericiaDcCancelar')?.addEventListener('click', () => fechar(null));
        dlg.addEventListener('cancel', (ev) => {
            ev.preventDefault();
            fechar(null);
        });

        const confirmar = () => {
            const inp = q('t20PericiaDcInput');
            const modo = dlg.dataset.t20RollModo || 'dc';
            const raw = inp ? String(inp.value).trim() : '';
            if (modo === 'ca' && raw === '') {
                fechar(resolverRetornoConfirmacao(null));
                return;
            }
            const val = raw === '' ? (modo === 'dc' ? 15 : null) : Number(raw);
            if (val != null && (!Number.isFinite(val) || val < 0 || val > 99)) {
                toastError(modo === 'ca' ? 'Informe uma Defesa válida (0–99) ou deixe vazio.' : 'Informe uma CD válida (1–99).');
                inp?.focus();
                return;
            }
            if (modo === 'dc' && (val == null || val < 1)) {
                toastError('Informe uma CD válida (1–99).');
                inp?.focus();
                return;
            }
            if (dlg.dataset.t20TemUsos === '1' && !usoSelecionadoId()) {
                toastError('Escolha o uso da perícia.');
                usosListEl()?.querySelector('input')?.focus();
                return;
            }
            const num = val == null ? null : Math.round(val);
            fechar(resolverRetornoConfirmacao(num));
        };

        q('t20PericiaDcRolar')?.addEventListener('click', confirmar);

        q('t20PericiaDcInput')?.addEventListener('keydown', (ev) => {
            if (ev.key === 'Enter') {
                ev.preventDefault();
                confirmar();
            }
        });

        usosListEl()?.addEventListener('keydown', (ev) => {
            if (ev.key === 'Enter') {
                ev.preventDefault();
                confirmar();
            }
        });
    }

    /**
     * @param {object} opts
     * @param {'dc'|'ca'} [opts.modo]
     * @param {string} [opts.titulo]
     * @param {string} [opts.label]
     * @param {string} [opts.hint]
     * @param {string|number} [opts.defaultVal]
     * @param {{ id: string, rotulo: string, hint?: string }[]} [opts.usos]
     * @param {string} [opts.usoDefault]
     * @param {string} [opts.usoLegend]
     * @returns {Promise<number|null|{ valor: number|null, usoId: string|null }|undefined>}
     *   Sem usos: número (CD/CA) ou null (cancelar / CA vazia).
     *   Com usos: { valor, usoId } ou null (cancelar).
     */
    function pedirValorRolagem(opts) {
        bindDialogoRolagem();
        const o = opts || {};
        const temUsos = Array.isArray(o.usos) && o.usos.length > 0;
        const dlg = q('t20ModalPericiaDc');
        if (!dlg) {
            const promptTxt = o.modo === 'ca' ? 'Defesa do alvo (vazio = só rolar):' : 'CD (padrão 15):';
            const raw = global.prompt(promptTxt, o.defaultVal != null ? String(o.defaultVal) : '15');
            if (raw == null) return Promise.resolve(temUsos ? null : undefined);
            if (o.modo === 'ca' && String(raw).trim() === '') {
                return Promise.resolve(temUsos ? { valor: null, usoId: o.usoDefault || null } : null);
            }
            const num = Number(raw) || 15;
            if (!temUsos) return Promise.resolve(num);
            let usoId = o.usoDefault || (o.usos[0] && o.usos[0].id) || null;
            if (o.usos.length > 1) {
                const labels = o.usos.map((u, i) => `${i + 1}=${u.rotulo}`).join(', ');
                const escolha = global.prompt(`Uso (${labels}):`, '1');
                if (escolha == null) return Promise.resolve(null);
                const idx = Number(escolha) - 1;
                if (Number.isFinite(idx) && o.usos[idx]) usoId = o.usos[idx].id;
            }
            return Promise.resolve({ valor: num, usoId });
        }

        dlg.dataset.t20RollModo = o.modo === 'ca' ? 'ca' : 'dc';
        const titulo = q('t20PericiaDcTitulo');
        const label = q('t20PericiaDcLabel');
        const hint = q('t20PericiaDcHint');
        const inp = q('t20PericiaDcInput');
        const btn = q('t20PericiaDcRolar');
        const legend = q('t20PericiaDcUsosLegend');
        if (titulo) titulo.textContent = o.titulo || 'Rolagem';
        if (label) label.textContent = o.label || 'Valor';
        if (hint) hint.textContent = o.hint || '';
        if (legend) legend.textContent = o.usoLegend || 'Uso do teste';
        if (inp) {
            inp.min = o.modo === 'ca' ? '0' : '1';
            inp.value = o.defaultVal != null ? String(o.defaultVal) : o.modo === 'ca' ? '' : '15';
        }
        if (btn) btn.textContent = o.modo === 'ca' ? 'Rolar ataque' : 'Rolar teste';

        if (temUsos) montarUsosUi(o.usos, o.usoDefault);
        else limparUsosUi();

        return new Promise((resolve) => {
            dialogResolve = resolve;
            if (typeof dlg.showModal === 'function') dlg.showModal();
            else dlg.setAttribute('open', '');
            setTimeout(() => {
                if (temUsos) {
                    const sel = usosListEl()?.querySelector('input:checked') || usosListEl()?.querySelector('input');
                    sel?.focus();
                } else {
                    inp?.focus();
                    inp?.select?.();
                }
            }, 40);
        });
    }

    function exibirResultadoPericia(nome, roll, calc) {
        let msg = `${nome}: 1d20=${roll.d20} + ${roll.bonus} = ${roll.total} vs CD ${roll.dc} → `;
        msg += roll.sucesso ? 'SUCESSO' : 'FALHA';
        if (calc && calc.penalidade_armadura_aplicada > 0) {
            msg += ` (pen. −${calc.penalidade_armadura_aplicada})`;
        }
        if (roll.falha_critica) msg += ' (falha crítica)';
        if (roll.sucesso_critico) msg += ' (sucesso crítico)';
        if (calc && calc.percepcao_passiva != null) {
            msg += ` · Passiva: ${calc.percepcao_passiva}`;
        }
        toastInfo(msg);
        registrarLog(msg);
    }

    function exibirResultadoAtaque(nome, roll) {
        let msg = `${nome}: 1d20=${roll.d20} + ${roll.bonus} = ${roll.total}`;
        if (roll.ca_alvo != null) {
            msg += ` vs Defesa ${roll.ca_alvo} → ${roll.acertou ? 'ACERTO' : 'ERRO'}`;
        }
        if (roll.falha_critica) msg += ' (falha crítica)';
        if (roll.ameaca_critica) msg += ' (ameaça crítica)';
        toastInfo(msg);
        registrarLog(msg);
    }

    function exibirResultadoIniciativa(roll) {
        const msg = `Iniciativa: 1d20=${roll.d20} + ${roll.modificador} = ${roll.total}`;
        toastInfo(msg);
        registrarLog(msg);
    }

    function parseInp(id) {
        const el = q(id);
        if (!el) return 0;
        const s = String(el.value).trim();
        if (s === '' || s === '-') return 0;
        const n = parseInt(s, 10);
        return Number.isFinite(n) ? n : 0;
    }

    function bonusEfetivoArma(a) {
        const raw = a.bonus_ataque != null && String(a.bonus_ataque).trim() !== '' ? a.bonus_ataque : a.teste;
        if (global.T20ProficienciaArma && global.T20RegraVersao?.isV13?.(getRegraVersao())) {
            const slug =
                typeof global.t20SlugClasseMb === 'function'
                    ? global.t20SlugClasseMb()
                    : (q('f_classe_mb') && q('f_classe_mb').value) || '';
            const aj = global.T20ProficienciaArma.ajustarBonusAtaque(raw, slug, {
                nomeArma: a.nome,
                proficienciaArma: a.proficiencia_arma,
            });
            return aj.bonus_efetivo;
        }
        if (global.T20ProficienciaArma) {
            return global.T20ProficienciaArma.parseBonusAtaque(raw);
        }
        const n = Number(String(raw || '').replace(/^\+/, ''));
        return Number.isFinite(n) ? Math.trunc(n) : 0;
    }

    function getRegraVersao() {
        if (typeof global.getRegraVersaoAtiva === 'function') return global.getRegraVersaoAtiva();
        return 'v13';
    }

    async function rolarPlanilhaAtaque(tipo) {
        const pfx = tipo === 'dist' ? 'Dist' : 'Cac';
        const rotulo = tipo === 'dist' ? 'Ataque à distância' : 'Ataque corpo a corpo';
        const ca = await pedirValorRolagem({
            modo: 'ca',
            titulo: rotulo,
            label: 'Defesa do alvo (opcional)',
            hint: 'Deixe vazio para rolar só 1d20 + bônus, sem comparar com a Defesa.',
            defaultVal: '',
        });
        if (ca === undefined) return;
        try {
            const payload = {
                bab: parseInp(`t20Atq${pfx}Bba`),
                mod_atributo: parseInp(`t20Atq${pfx}Modhab`),
                bonus_tamanho: parseInp(`t20Atq${pfx}Modtam`),
                bonus_arma: parseInp(`t20Atq${pfx}Outros`),
                penalidades: 0,
            };
            if (ca != null) payload.ca_alvo = ca;
            const roll = await regras().rolarAtaque(payload);
            exibirResultadoAtaque(rotulo, roll);
        } catch (e) {
            toastError(e.message || 'Erro ao rolar ataque');
        }
    }

    async function rolarArmaLista(a) {
        if (!a || a.bonus_ativo === false) {
            toastError('Bônus de ataque inativo (limite de empunhados).');
            return;
        }
        const nome = (a.nome && String(a.nome).trim()) || 'Ataque';
        const ca = await pedirValorRolagem({
            modo: 'ca',
            titulo: `Ataque: ${nome}`,
            label: 'Defesa do alvo (opcional)',
            hint: 'Deixe vazio para rolar só 1d20 + bônus.',
            defaultVal: '',
        });
        if (ca === undefined) return;
        try {
            const payload = { bonus: bonusEfetivoArma(a) };
            if (ca != null) payload.ca_alvo = ca;
            const roll = await regras().rolarAtaque(payload);
            exibirResultadoAtaque(nome, roll);
        } catch (e) {
            toastError(e.message || 'Erro ao rolar ataque');
        }
    }

    async function rolarIniciativaFicha() {
        let mod = 0;
        const modEl = q('fichaDesModResumo');
        if (modEl) {
            const t = String(modEl.textContent || '').replace(/\s/g, '').replace(/^\+/, '');
            const n = parseInt(t, 10);
            if (Number.isFinite(n)) mod = n;
        }
        try {
            const roll = await regras().rolarIniciativa({ mod_destreza: mod });
            exibirResultadoIniciativa(roll);
        } catch (e) {
            toastError(e.message || 'Erro ao rolar iniciativa');
        }
    }

    function bindFichaRolagens() {
        if (global.__t20RolagemContextualBound) return;
        global.__t20RolagemContextualBound = true;

        document.body.addEventListener('click', (ev) => {
            const tgt = ev.target;
            if (!(tgt instanceof Element)) return;

            const iniBox = tgt.closest('.ficha-ini-box--rolavel');
            if (iniBox && q('fichaIniciativa') && iniBox.contains(q('fichaIniciativa'))) {
                void rolarIniciativaFicha();
                return;
            }

            const cac = tgt.closest('[data-t20-roll="cac"]');
            if (cac) {
                void rolarPlanilhaAtaque('cac');
                return;
            }
            const dist = tgt.closest('[data-t20-roll="dist"]');
            if (dist) {
                void rolarPlanilhaAtaque('dist');
                return;
            }

            const armaRow = tgt.closest('.ficha-ataque-linha.t20-ataque--rolavel');
            if (armaRow) {
                const idx = Number(armaRow.dataset.atqIdx);
                const lista = global.t20AtaquesLista || [];
                const a = Number.isFinite(idx) ? lista[idx] : null;
                if (a) void rolarArmaLista(a);
            }
        });

        q('fichaIniciativa')?.addEventListener('keydown', (ev) => {
            if (ev.key === 'Enter' || ev.key === ' ') {
                ev.preventDefault();
                void rolarIniciativaFicha();
            }
        });
    }

    function init() {
        bindDialogoRolagem();
        bindFichaRolagens();
    }

    global.T20RolagemContextual = {
        init,
        pedirValorRolagem,
        exibirResultadoPericia,
        exibirResultadoAtaque,
        exibirResultadoIniciativa,
        registrarLog,
        rolarPlanilhaAtaque,
        rolarArmaLista,
        rolarIniciativaFicha,
    };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})(typeof window !== 'undefined' ? window : globalThis);
