/**
 * Calculadora e rolador de perícias MB (API `/tormenta/regras/pericias/*`).
 * RF-T04i — seletor de uso no momento da rolagem (via T20PericiasUsos + diálogo contextual).
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

    /**
     * @returns {Promise<{ valor: number, usoId: string|null }|null>}
     */
    function pedirDcPericia(nome, opts) {
        const o = opts || {};
        const usos = Array.isArray(o.usos) ? o.usos : [];
        const usoDefault = o.usoDefault || null;
        const normalizar = (v) => {
            if (v == null) return null;
            if (typeof v === 'object' && v.valor != null) {
                return { valor: v.valor, usoId: v.usoId || null };
            }
            if (typeof v === 'number') return { valor: v, usoId: usoDefault };
            return null;
        };

        if (window.T20RolagemContextual && window.T20RolagemContextual.pedirValorRolagem) {
            const hintBase =
                'Informe a Classe de Dificuldade (CD) do teste. O resultado será 1d20 + bônus da perícia.';
            const hintUsos = usos.length
                ? 'Escolha o uso e a CD. O nome do uso aparece no resultado da rolagem.'
                : hintBase;
            return window.T20RolagemContextual.pedirValorRolagem({
                modo: 'dc',
                titulo: `Teste: ${nome}`,
                label: `CD para ${nome} (padrão 15)`,
                hint: hintUsos,
                defaultVal: 15,
                usos: usos.length ? usos : undefined,
                usoDefault: usoDefault || undefined,
                usoLegend: 'Uso do teste',
            }).then(normalizar);
        }
        bindDcDialog();
        const dlg = q('t20ModalPericiaDc');
        if (!dlg) {
            const dcInp = window.prompt(`DC para ${nome} (padrão 15):`, '15');
            if (dcInp == null) return Promise.resolve(null);
            return Promise.resolve({ valor: Number(dcInp) || 15, usoId: usoDefault });
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
            dcResolve = (v) => resolve(v == null ? null : { valor: v, usoId: usoDefault });
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

    function getRegraVersaoRolador() {
        if (typeof window.getRegraVersaoAtiva === 'function') {
            return window.getRegraVersaoAtiva();
        }
        return window.T20RegraVersao ? window.T20RegraVersao.DEFAULT_NOVA_FICHA : 'v13';
    }

    function itensProtecaoEquipados() {
        const raw =
            typeof window.t20ArmadurasEquipadas !== 'undefined' ? window.t20ArmadurasEquipadas : [];
        if (window.T20PenalidadeArmadura && window.T20PenalidadeArmadura.itensProtecaoPayload) {
            return window.T20PenalidadeArmadura.itensProtecaoPayload(raw);
        }
        return raw;
    }

    /**
     * Nome exibido na linha (ex.: «Ofício (alquimia)»).
     */
    function nomeExibidoLinha(tr) {
        const nomeEl = tr.querySelector('.t20-p-nome');
        return nomeEl ? nomeEl.textContent.trim() : '';
    }

    /**
     * Nome canônico do catálogo — usado no bônus racial e no lookup do backend.
     * Especialidades de Ofício exibem «Ofício (x)» mas resolvem como «Ofício».
     */
    function nomeCanonLinha(tr) {
        const canon = tr && tr.getAttribute ? tr.getAttribute('data-per-nome-canon') : '';
        if (canon && canon.trim()) return canon.trim();
        return nomeExibidoLinha(tr);
    }

    function slugLinha(tr) {
        const slug = tr && tr.getAttribute ? tr.getAttribute('data-per-slug') : '';
        if (slug && slug.trim()) return slug.trim().toLowerCase();
        const usos = window.T20PericiasUsos;
        if (usos && usos.normalizarSlug) {
            return usos.normalizarSlug(nomeCanonLinha(tr));
        }
        return '';
    }

    /**
     * @param {HTMLElement} tr
     * @param {{ usoId?: string|null }} [opts]
     * Preview Σ: sem uso → uso_atletismo_natacao false (pen. de natação só na rolagem com Nadar).
     */
    function buildBonusBody(tr, opts) {
        const o = opts || {};
        const nome = nomeCanonLinha(tr);
        const slug = slugLinha(tr);
        const treinado = Boolean(tr.querySelector('.p-treinado')?.checked);
        const modAt = Number(tr.querySelector('.p-mod')?.value || 0);
        const outros = Number(tr.querySelector('.p-out')?.value || 0);
        const grad = Number(tr.querySelector('.p-total')?.value || 0);
        const deClasse = tr.classList.contains('t20-pericia-de-classe-row');
        const rv = getRegraVersaoRolador();
        const isV13 = window.T20RegraVersao && window.T20RegraVersao.isV13(rv);
        const usosApi = window.T20PericiasUsos;
        const temSeletorUso = Boolean(usosApi && usosApi.temUsos(slug || nome));

        let usoNat = false;
        if (o.usoId != null && o.usoId !== '') {
            usoNat = usosApi
                ? usosApi.usoAtletismoNatacao(slug || nome, o.usoId)
                : String(o.usoId) === 'nadar';
        } else if (!temSeletorUso) {
            // Legado: checkbox 🏊 só se não houver seletor RF-T04i.
            usoNat = Boolean(tr.querySelector('.p-pen-natacao')?.checked);
        }

        const body = {
            nivel: nivelPersonagem(),
            mod_atributo: modAt,
            treinado,
            graduacao: isV13 ? 0 : grad,
            outros: isV13 ? outros + grad : outros,
            racial_bonus: bonusRacialPericia(nome),
            slug_raca: slugRaca(),
            nome_pericia: nome,
            pericia_de_classe: deClasse,
            regraVersao: rv,
        };
        if (isV13) {
            body.itens_protecao = itensProtecaoEquipados();
            body.uso_atletismo_natacao = usoNat;
            body.penalidade_sobrecarga_carga = Boolean(
                window.__t20CargaState && window.__t20CargaState.sobrecarga
            );
            const slugEl = document.getElementById('f_classe_mb');
            if (slugEl && slugEl.value) {
                body.tormenta_classe_mb_slug = String(slugEl.value).trim();
            }
        } else {
            body.penalidade_armadura = 0;
        }
        return body;
    }

    async function calcularBonusLinha(tr, opts) {
        const res = await regras().calcularBonusPericia(buildBonusBody(tr, opts));
        return res;
    }

    async function calcularBonusLote(trs) {
        const rows = Array.isArray(trs) ? trs : [];
        if (!rows.length) return [];
        const bodies = rows.map((tr) => buildBonusBody(tr));
        return regras().calcularBonusPericiaLote(bodies);
    }

    async function rolarPericia(tr) {
        const nomeExibido = nomeExibidoLinha(tr) || 'Perícia';
        const nomeCanon = nomeCanonLinha(tr) || nomeExibido;
        const slug = slugLinha(tr);
        const treinado = Boolean(tr.querySelector('.p-treinado')?.checked);
        const soTreina = Boolean(tr.querySelector('.p-so-treina')?.checked);
        if (soTreina && !treinado) {
            const msg = `${nomeExibido}: perícia somente treinada — marque «Treinado» antes de rolar.`;
            if (typeof Toast !== 'undefined' && Toast.error) Toast.error(msg);
            else alert(msg);
            return;
        }

        const usosApi = window.T20PericiasUsos;
        const usos = usosApi ? usosApi.usosDaPericia(slug || nomeCanon) : [];
        const usoDefault = usosApi && usos.length ? usosApi.usoDefault(slug || nomeCanon) : null;

        const pedida = await pedirDcPericia(nomeExibido, { usos, usoDefault });
        if (pedida == null || pedida.valor == null) return;
        const dc = pedida.valor;
        const usoId = pedida.usoId || null;

        if (usosApi && usoId) usosApi.lembrarUso(slug || nomeCanon, usoId);

        const nomeResultado =
            usosApi && usoId
                ? usosApi.formatarNomeComUso(nomeExibido, slug || nomeCanon, usoId)
                : nomeExibido;

        try {
            const calc = await calcularBonusLinha(tr, { usoId });
            if (calc.pode_usar === false) {
                const msg = calc.motivo_bloqueio || `${nomeResultado}: não pode usar sem treino.`;
                if (typeof Toast !== 'undefined' && Toast.error) Toast.error(msg);
                else alert(msg);
                return;
            }
            const roll = await regras().rolarPericia({
                bonus: calc.bonus_total,
                dc,
            });
            if (window.T20RolagemContextual && window.T20RolagemContextual.exibirResultadoPericia) {
                window.T20RolagemContextual.exibirResultadoPericia(nomeResultado, roll, calc);
            } else {
                let msg = `${nomeResultado}: 1d20=${roll.d20} + ${roll.bonus} = ${roll.total} vs DC ${dc} → `;
                msg += roll.sucesso ? 'SUCESSO' : 'FALHA';
                if (calc.penalidade_armadura_aplicada > 0) {
                    msg += ` (pen. armadura −${calc.penalidade_armadura_aplicada})`;
                }
                if (roll.falha_critica) msg += ' (falha crítica)';
                if (roll.sucesso_critico) msg += ' (sucesso crítico)';
                if (calc.percepcao_passiva != null) {
                    msg += ` · Passiva: ${calc.percepcao_passiva}`;
                }
                if (typeof Toast !== 'undefined' && Toast.info) Toast.info(msg);
                else alert(msg);
            }
        } catch (e) {
            if (typeof Toast !== 'undefined' && Toast.error) Toast.error(e.message || 'Erro ao rolar');
        }
    }

    function removerColunaTesteLegada() {
        const tbl = document.querySelector('#tblPericias');
        const theadTr = document.querySelector('#tblPericias thead tr');
        if (!theadTr) return;
        const ths = theadTr.querySelectorAll('th');
        const lastTh = ths[ths.length - 1];
        if (!lastTh || lastTh.textContent.trim() !== 'Teste') return;
        lastTh.remove();
        document.querySelectorAll('#tblPericias tbody tr').forEach((tr) => {
            const tds = tr.querySelectorAll('td');
            const lastTd = tds[tds.length - 1];
            if (lastTd && lastTd.querySelector('.tormenta-btn')) {
                lastTd.remove();
            }
        });
        if (tbl) delete tbl.querySelector('thead tr')?.dataset.rollCol;
    }

    function bindRolarPericiasNaFicha() {
        const tbl = document.querySelector('#tblPericias');
        if (!tbl || tbl.dataset.rollBound === '1') return;
        tbl.dataset.rollBound = '1';
        tbl.addEventListener('click', (ev) => {
            if (ev.target.closest('input, button, label, .t20-oficio-esp-wrap')) return;
            const nomeEl = ev.target.closest('.t20-p-nome--rolavel');
            const bonusCell = ev.target.closest('.t20-p-bonus-cell');
            if (!nomeEl && !bonusCell) return;
            const tr = (nomeEl || bonusCell).closest('tr');
            if (tr) rolarPericia(tr);
        });
    }

    function initRoladorPericias() {
        if (!window.T20RolagemContextual) bindDcDialog();
        removerColunaTesteLegada();
        bindRolarPericiasNaFicha();
        const tb = document.querySelector('#tblPericias tbody');
        if (!tb || tb.dataset.rollObs === '1') return;
        tb.dataset.rollObs = '1';
        const obs = new MutationObserver(() => {
            removerColunaTesteLegada();
        });
        obs.observe(tb, { childList: true });
    }

    document.addEventListener('DOMContentLoaded', () => {
        initRoladorPericias();
        setTimeout(initRoladorPericias, 800);
    });

    function encontrarLinhaPorSlug(slug) {
        const s = String(slug || '').trim().toLowerCase();
        if (!s) return null;
        return document.querySelector(`#tblPericias tbody tr[data-per-slug="${s}"]`);
    }

    function encontrarLinhaPorNome(nome) {
        const alvo = String(nome || '').trim().toLowerCase();
        if (!alvo) return null;
        const rows = document.querySelectorAll('#tblPericias tbody tr');
        for (let i = 0; i < rows.length; i++) {
            const el = rows[i].querySelector('.t20-p-nome');
            const txt = el ? String(el.textContent || '').trim().toLowerCase() : '';
            if (txt === alvo) return rows[i];
        }
        return null;
    }

    window.T20PericiasRolador = {
        buildBonusBody,
        calcularBonusLinha,
        calcularBonusLote,
        encontrarLinhaPorSlug,
        encontrarLinhaPorNome,
        rolarPericia,
        initRolador: initRoladorPericias,
    };
})();
