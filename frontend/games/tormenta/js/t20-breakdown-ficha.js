/**
 * RF-T12a — breakdown visível de CA, perícias e ataques na ficha Tormenta.
 */
(function (global) {
    'use strict';

    let debouncePericias = null;
    let seqPericias = 0;

    function q(id) {
        return document.getElementById(id);
    }

    function getRegraVersao() {
        if (typeof global.getRegraVersaoAtiva === 'function') {
            return global.getRegraVersaoAtiva();
        }
        return global.T20RegraVersao ? global.T20RegraVersao.DEFAULT_NOVA_FICHA : 'v13';
    }

    function vitaisApi() {
        return global.T20FichaVitais || null;
    }

    function fmtSigned(n) {
        const v = Number(n) || 0;
        return v > 0 ? `+${v}` : String(v);
    }

    function bonusRacialPericia(nome) {
        const c = global.__t20TracosRaciaisCache;
        if (!c || !c.pericias_bonus) return 0;
        return Number(c.pericias_bonus[nome] || 0);
    }

    function parseInp(id) {
        const el = q(id);
        if (!el) return 0;
        const s = String(el.value).trim();
        if (s === '' || s === '-') return 0;
        const n = parseInt(s, 10);
        return Number.isFinite(n) ? n : 0;
    }

    function montarFormulaPlanilhaAtaque(pfx, modHabLbl) {
        const bba = parseInp(`t20Atq${pfx}Bba`);
        const modHab = parseInp(`t20Atq${pfx}Modhab`);
        const modTam = parseInp(`t20Atq${pfx}Modtam`);
        const outros = parseInp(`t20Atq${pfx}Outros`);
        const total = parseInp(`t20Atq${pfx}Total`);
        const parts = [`BBA ${fmtSigned(bba)}`, `${modHabLbl} ${fmtSigned(modHab)}`];
        if (modTam) parts.push(`tam ${fmtSigned(modTam)}`);
        if (outros) parts.push(`outros ${fmtSigned(outros)}`);
        return `${parts.join(' + ')} = ${fmtSigned(total)}`;
    }

    function tituloPlanilhaAtaque(pfx, modHabLbl, rotulo) {
        const bba = parseInp(`t20Atq${pfx}Bba`);
        const modHab = parseInp(`t20Atq${pfx}Modhab`);
        const modTam = parseInp(`t20Atq${pfx}Modtam`);
        const outros = parseInp(`t20Atq${pfx}Outros`);
        const total = parseInp(`t20Atq${pfx}Total`);
        let t = `${rotulo}\nBBA: ${fmtSigned(bba)}\n${modHabLbl}: ${fmtSigned(modHab)}`;
        t += `\nTamanho: ${fmtSigned(modTam)}`;
        t += `\nOutros: ${fmtSigned(outros)}`;
        t += `\n= ${fmtSigned(total)}`;
        return t;
    }

    function inferTipoAtaqueArma(a) {
        const alc = String((a && a.alcance) || '').toLowerCase();
        const nome = String((a && a.nome) || '').toLowerCase();
        const blob = `${alc} ${nome}`;
        if (/dist|alcance|metro|\barco\b|besta|funda|azagaia|estilingue|dardo/.test(blob)) {
            return 'dist';
        }
        return 'cac';
    }

    function parseBonusAtaqueRaw(raw) {
        if (global.T20ProficienciaArma && global.T20ProficienciaArma.parseBonusAtaque) {
            return global.T20ProficienciaArma.parseBonusAtaque(raw);
        }
        const s = String(raw == null ? '' : raw)
            .trim()
            .replace(/^\+/, '');
        if (s === '' || s === '—' || s === '-') return 0;
        const n = Number(s);
        return Number.isFinite(n) ? Math.trunc(n) : 0;
    }

    function slugClasseMb() {
        if (typeof global.t20SlugClasseMb === 'function') {
            return global.t20SlugClasseMb();
        }
        const el = q('f_classe_mb');
        return el && el.value ? String(el.value).trim() : '';
    }

    function formulaAtaqueArma(a) {
        const raw = a.bonus_ataque != null && String(a.bonus_ataque).trim() !== '' ? a.bonus_ataque : a.teste;
        const base = parseBonusAtaqueRaw(raw);
        const rv = getRegraVersao();
        const isV13 = global.T20RegraVersao && global.T20RegraVersao.isV13(rv);
        const tipo = inferTipoAtaqueArma(a);
        const pfx = tipo === 'dist' ? 'Dist' : 'Cac';
        const modLbl = tipo === 'dist' ? 'DES' : 'FOR';
        const planilhaTotal = parseInp(`t20Atq${pfx}Total`);

        let formula = '';
        if (base === planilhaTotal) {
            formula = montarFormulaPlanilhaAtaque(pfx, modLbl);
        } else {
            formula = `bônus gravado ${fmtSigned(base)}`;
            if (planilhaTotal) {
                formula += ` (planilha ${tipo === 'dist' ? 'à dist.' : 'corpo a corpo'}: ${fmtSigned(planilhaTotal)})`;
            }
        }

        if (isV13 && global.T20ProficienciaArma) {
            const aj = global.T20ProficienciaArma.ajustarBonusAtaque(raw, slugClasseMb(), {
                nomeArma: a.nome,
                proficienciaArma: a.proficiencia_arma,
            });
            if (aj.penalidade_nao_proficiente > 0) {
                formula += ` −5 (não proficiente em ${aj.proficiencia_arma}) = ${fmtSigned(aj.bonus_efetivo)}`;
            }
        }

        if (a.bonus_ativo === false) {
            formula += ' · bônus inativo (limite de empunhados)';
        }

        return formula;
    }

    function aplicarBreakdownLinhaAtaque(atkEl, a) {
        if (!atkEl || !a) return;
        const formula = formulaAtaqueArma(a);
        atkEl.title = formula;
        atkEl.setAttribute('aria-label', `Ataque: ${atkEl.textContent}. ${formula}`);
    }

    function atualizarAtaquesPlanilha() {
        const cacBd = q('t20AtqCacBreakdown');
        const distBd = q('t20AtqDistBreakdown');
        const cacTot = q('t20AtqCacTotal');
        const distTot = q('t20AtqDistTotal');
        const cacFormula = montarFormulaPlanilhaAtaque('Cac', 'FOR');
        const distFormula = montarFormulaPlanilhaAtaque('Dist', 'DES');
        if (cacBd) cacBd.textContent = cacFormula;
        if (distBd) distBd.textContent = distFormula;
        if (cacTot) cacTot.title = tituloPlanilhaAtaque('Cac', 'FOR', 'Ataque corpo a corpo');
        if (distTot) distTot.title = tituloPlanilhaAtaque('Dist', 'DES', 'Ataque à distância');
    }

    function atualizarListaAtaquesBreakdown() {
        const lista = q('t20FichaAtaquesLista');
        if (!lista) return;
        const linhas = lista.querySelectorAll('.ficha-ataque-linha');
        const ataques =
            typeof global.t20AtaquesLista !== 'undefined' && Array.isArray(global.t20AtaquesLista)
                ? global.t20AtaquesLista
                : [];
        linhas.forEach((row, i) => {
            const atkEl = row.querySelector('.ficha-ataque-bonus');
            const a = ataques[i];
            if (atkEl && a) aplicarBreakdownLinhaAtaque(atkEl, a);
        });
    }

    function itensCaDetalhados() {
        const api = vitaisApi();
        const itens = api && api.getArmaduras ? api.getArmaduras() : global.t20ArmadurasEquipadas || [];
        return (itens || [])
            .map((it) => ({
                nome: String((it && (it.nome || it.nome_item || it.titulo)) || 'Proteção').trim() || 'Proteção',
                bonus: Number(it && it.bonus_ca) || 0,
            }))
            .filter((it) => it.bonus !== 0);
    }

    function montarTextoItensCa(itens) {
        if (!itens.length) return '';
        return itens.map((it) => `${it.nome} ${fmtSigned(it.bonus)}`).join(' · ');
    }

    function atualizarCa() {
        const caBd = q('fichaCaBreakdown');
        const caVal = q('fichaCa');
        if (!caBd) return;

        const api = vitaisApi();
        const rv = getRegraVersao();
        const isV13 = global.T20RegraVersao && global.T20RegraVersao.isV13(rv);
        const total = api && api.calcularCaTotal ? api.calcularCaTotal() : Number(caVal && caVal.textContent) || 10;
        const itens = itensCaDetalhados();
        const itensTxt = montarTextoItensCa(itens);
        const arm = itens.reduce((acc, it) => acc + it.bonus, 0);

        if (isV13) {
            const desAttr = Math.trunc(Number((q('fichaDesResumo') && q('fichaDesResumo').value) || 0));
            const desFmt = fmtSigned(desAttr);
            const armaduras = api && api.getArmaduras ? api.getArmaduras() : global.t20ArmadurasEquipadas || [];
            const pesada =
                global.T20RegraVersao && global.T20RegraVersao.temArmaduraPesada(armaduras);
            let linha = '';
            let titulo = '';
            if (pesada) {
                linha = itensTxt
                    ? `10 + ${itensTxt} = ${total} (v1.3; pesada — DES ${desFmt} não aplica)`
                    : `10 = ${total} (v1.3; armadura pesada — DES ${desFmt} não aplica)`;
                titulo = `CA v1.3\n10 (base)`;
                if (itens.length) {
                    itens.forEach((it) => {
                        titulo += `\n${it.nome}: ${fmtSigned(it.bonus)}`;
                    });
                }
                titulo += `\nDES ${desFmt}: ignorado (armadura pesada)\n= ${total}`;
            } else {
                const desPart = `DES ${desFmt}`;
                if (itensTxt) {
                    linha = `10 + ${desPart} + ${itensTxt} = ${total} (v1.3)`;
                } else {
                    linha = `10 + ${desPart} = ${total} (v1.3)`;
                }
                titulo = `CA v1.3\n10 (base)\n${desPart}`;
                if (itens.length) {
                    itens.forEach((it) => {
                        titulo += `\n${it.nome}: ${fmtSigned(it.bonus)}`;
                    });
                }
                titulo += `\n= ${total}`;
            }
            caBd.textContent = linha;
            if (caVal) caVal.title = titulo;
            return;
        }

        const base = api && api.getCaBaseSemItens ? api.getCaBaseSemItens() : 10;
        if (arm === 0) {
            caBd.textContent = `CA salva: ${base} (sem bônus de itens)`;
            if (caVal) caVal.title = `CA MB\nBase salva: ${base}\n= ${total}`;
        } else {
            const resumoItens = itensTxt || `itens ${fmtSigned(arm)}`;
            caBd.textContent = `Base ${base} + ${resumoItens} = ${total}`;
            let titulo = `CA MB\nBase salva: ${base}`;
            if (itens.length) {
                itens.forEach((it) => {
                    titulo += `\n${it.nome}: ${fmtSigned(it.bonus)}`;
                });
            } else {
                titulo += `\nItens: ${fmtSigned(arm)}`;
            }
            titulo += `\n= ${total}`;
            if (caVal) caVal.title = titulo;
        }
    }

    function montarFormulaPericia(tr, calc, isV13) {
        const mod = Number(tr.querySelector('.p-mod')?.value || 0);
        const outrosInp = Number(tr.querySelector('.p-out')?.value || 0);
        const grad = Number(tr.querySelector('.p-total')?.value || 0);
        const nome = tr.querySelector('.t20-p-nome')?.textContent?.trim() || '';
        const racial = bonusRacialPericia(nome);
        const treinado = Boolean(tr.querySelector('.p-treinado')?.checked);
        const parts = [];

        if (isV13) {
            const attr = tr.getAttribute('data-per-attr');
            const attrLbl = attr ? String(attr).toUpperCase() : 'Atrib.';
            parts.push(`${attrLbl} ${fmtSigned(mod)}`);
        } else {
            parts.push(`mod ${fmtSigned(mod)}`);
        }

        const meio = calc.meio_nivel != null ? calc.meio_nivel : 0;
        if (meio) parts.push(`½ nv ${fmtSigned(meio)}`);

        if (treinado && calc.bonus_treinamento) {
            parts.push(`treino ${fmtSigned(calc.bonus_treinamento)}`);
        } else if (treinado) {
            parts.push('treino +0');
        }

        if (!isV13 && grad) parts.push(`grad ${fmtSigned(grad)}`);

        const outrosEff = isV13 ? outrosInp + grad : outrosInp;
        if (outrosEff) parts.push(`outros ${fmtSigned(outrosEff)}`);

        if (racial) parts.push(`racial ${fmtSigned(racial)}`);

        const pen = calc.penalidade_armadura_aplicada || 0;
        if (pen) parts.push(`pen. armadura −${pen}`);

        const total = calc.bonus_total != null ? calc.bonus_total : 0;
        return `${parts.join(' + ').replace(/\+ −/g, '− ')} = ${fmtSigned(total)}`;
    }

    function parseHalfNv(tr) {
        const raw = tr.querySelector('.t20-p-half')?.textContent || '0';
        const n = Number(String(raw).replace(/[^\d+-]/g, ''));
        return Number.isFinite(n) ? n : 0;
    }

    function previewRapidoBonusPericia(tr) {
        const valEl = tr.querySelector('.t20-p-bonus-val');
        if (!valEl) return;
        const rv = getRegraVersao();
        const isV13 = global.T20RegraVersao && global.T20RegraVersao.isV13(rv);
        const mod = Number(tr.querySelector('.p-mod')?.value || 0);
        const outros = Number(tr.querySelector('.p-out')?.value || 0);
        const grad = Number(tr.querySelector('.p-total')?.value || 0);
        const half = parseHalfNv(tr);
        const outrosEff = isV13 ? outros + grad : outros;
        const parcial = mod + half + outrosEff;
        valEl.textContent = fmtSigned(parcial);
        const cell = tr.querySelector('.t20-p-bonus-cell');
        if (cell) {
            cell.title = isV13
                ? `Prévia: Atrib. ${fmtSigned(mod)} + Out ${fmtSigned(outrosEff)} + ½ nv ${fmtSigned(half)} (calculando treino e penalidades…)`
                : `Prévia: mod ${fmtSigned(mod)} + outros ${fmtSigned(outrosEff)} + ½ nv ${fmtSigned(half)}…`;
        }
    }

    function previewRapidoTodasPericias() {
        document.querySelectorAll('#tblPericias tbody tr[data-per-idx]').forEach((tr) => {
            previewRapidoBonusPericia(tr);
        });
    }

    function aplicarCalcBonusLinha(tr, calc) {
        const valEl = tr.querySelector('.t20-p-bonus-val');
        if (!valEl) return;
        const rv = getRegraVersao();
        const isV13 = global.T20RegraVersao && global.T20RegraVersao.isV13(rv);
        const total = calc.bonus_total != null ? calc.bonus_total : 0;
        const formula = montarFormulaPericia(tr, calc, isV13);
        valEl.textContent = fmtSigned(total);
        valEl.classList.toggle('t20-p-bonus-val--bloqueado', calc.pode_usar === false);
        const cell = tr.querySelector('.t20-p-bonus-cell');
        if (cell) {
            cell.title = formula;
            cell.setAttribute('aria-label', `Bônus total: ${fmtSigned(total)}. ${formula}`);
        }
        const bd = tr.querySelector('.t20-p-breakdown');
        if (bd) bd.textContent = formula;
    }

    async function atualizarLinhaBonusPericia(tr) {
        const valEl = tr.querySelector('.t20-p-bonus-val');
        if (!valEl || !global.T20PericiasRolador) return;
        try {
            const calc = await global.T20PericiasRolador.calcularBonusLinha(tr);
            aplicarCalcBonusLinha(tr, calc);
        } catch (_e) {
            valEl.textContent = '—';
            valEl.classList.remove('t20-p-bonus-val--bloqueado');
        }
    }

    async function atualizarTodasPericias() {
        const rows = Array.from(
            document.querySelectorAll('#tblPericias tbody tr[data-per-idx]')
        );
        if (!rows.length || !global.T20PericiasRolador) return;
        const mySeq = ++seqPericias;
        try {
            const calcs = await global.T20PericiasRolador.calcularBonusLote(rows);
            if (mySeq !== seqPericias) return;
            rows.forEach((tr, idx) => {
                const calc = calcs[idx];
                if (calc) aplicarCalcBonusLinha(tr, calc);
            });
        } catch (_e) {
            if (mySeq !== seqPericias) return;
            rows.forEach((tr) => {
                const valEl = tr.querySelector('.t20-p-bonus-val');
                if (valEl) {
                    valEl.textContent = '—';
                    valEl.classList.remove('t20-p-bonus-val--bloqueado');
                }
            });
        }
    }

    function agendarPericias() {
        previewRapidoTodasPericias();
        if (debouncePericias) clearTimeout(debouncePericias);
        debouncePericias = setTimeout(() => {
            debouncePericias = null;
            void atualizarTodasPericias();
        }, 300);
    }

    function bindOnce() {
        if (global.__t20BreakdownFichaBound) return;
        global.__t20BreakdownFichaBound = true;

        const tb = document.querySelector('#tblPericias tbody');
        if (tb) {
            tb.addEventListener('change', () => agendarPericias());
            tb.addEventListener('input', () => agendarPericias());
        }

        [
            'f_nivel',
            'f_raca_select',
            'f_classe_mb',
            'fichaDesResumo',
            'fichaForResumo',
            'fichaConResumo',
            'fichaIntResumo',
            'fichaSabResumo',
            'fichaCarResumo',
            't20AtqCacModtam',
            't20AtqCacOutros',
            't20AtqDistModtam',
            't20AtqDistOutros',
        ].forEach((id) => {
            const el = q(id);
            el?.addEventListener('change', () => {
                atualizarCa();
                agendarPericias();
                atualizarAtaquesPlanilha();
            });
            el?.addEventListener('input', () => {
                atualizarCa();
                agendarPericias();
                atualizarAtaquesPlanilha();
            });
        });
    }

    function init() {
        bindOnce();
        atualizarCa();
        agendarPericias();
        atualizarAtaquesPlanilha();
    }

    global.T20BreakdownFicha = {
        init,
        atualizarCa,
        agendarPericias,
        atualizarTodasPericias,
        atualizarAtaquesPlanilha,
        atualizarListaAtaquesBreakdown,
        formulaAtaqueArma,
        aplicarBreakdownLinhaAtaque,
    };
})(typeof window !== 'undefined' ? window : globalThis);
