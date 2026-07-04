/**
 * Dashboard wizard v1.3 — passo 2: raça/classe (Versátil, Suraggel, Arcanista, PV sugerido).
 */
(function (global) {
    'use strict';

    let cfg = null;

    function q(id) {
        return document.getElementById(id);
    }

    function isV13Wizard() {
        return (
            cfg &&
            cfg.regraVersao === 'v13' &&
            global.T20DashWizardV13 &&
            global.T20DashWizardV13.isWizardAtivo &&
            global.T20DashWizardV13.isWizardAtivo()
        );
    }

    function slugifyPoder(texto) {
        return String(texto || '')
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '')
            .toLowerCase()
            .replace(/[^a-z0-9]+/g, '_')
            .replace(/^_|_$/g, '');
    }

    function getRacaRow() {
        if (cfg && typeof cfg.getRacaRow === 'function') {
            const sel = q('cadRacaSelect');
            return cfg.getRacaRow((sel && sel.value) || '');
        }
        return null;
    }

    function classeSlug() {
        const sel = q('cadClasseMb');
        return sel && sel.value ? String(sel.value).trim().toLowerCase() : '';
    }

    function getCadRacialDeltasStep2() {
        return (global.__t20GetCadRacialDeltas && global.__t20GetCadRacialDeltas()) || {};
    }

    function conValorCadastro() {
        const n = Number(q('cadCon') && q('cadCon').value);
        const base = Number.isFinite(n) ? Math.floor(n) : 0;
        return base + (getCadRacialDeltasStep2().con || 0);
    }

    function nivelCadastro() {
        const n = parseInt(String(q('cadNivel') && q('cadNivel').value || '1'), 10);
        return Number.isFinite(n) && n >= 0 ? n : 1;
    }

    function atualizarLabelsRaciaisV13(row) {
        const hint = q('cadRacialMais2Hint');
        const lab1 = q('cadLabelRacaMais2a');
        const lab2 = q('cadLabelRacaMais2b');
        const labM1 = q('cadLabelRacaMais1');
        if (!isV13Wizard()) {
            if (hint) {
                hint.textContent =
                    'Raça MB: +2 em duas habilidades diferentes (ex.: Humano, Lefou).';
            }
            if (lab1) lab1.textContent = '1º +2';
            if (lab2) lab2.textContent = '2º +2';
            if (labM1) labM1.textContent = 'Raça MB: +2 em uma habilidade (Meio-orc)';
            return;
        }
        if (row && row.escolhe_tres_mais1) {
            if (hint) {
                hint.textContent =
                    'v1.3: +1 em três atributos diferentes (Tabela 1-2). Escolha três habilidades distintas.';
            }
            if (lab1) lab1.textContent = '1º +1';
            if (lab2) lab2.textContent = '2º +1';
            if (labM1) labM1.textContent = '3º +1';
        } else if (row && row.escolhe_duas_mais2) {
            if (hint) hint.textContent = 'Raça MB: +2 em duas habilidades diferentes.';
            if (lab1) lab1.textContent = '1º +2';
            if (lab2) lab2.textContent = '2º +2';
        }
    }

    function atualizarUiHumanoVersatil() {
        const wrap = q('cadWrapHumanoVersatil');
        const wrapPod = q('cadWrapHumanoVersatilPoder');
        const sel = q('cadHumanoVersatil');
        const slug = (q('cadRacaSelect') && q('cadRacaSelect').value) || '';
        const show = isV13Wizard() && slug === 'humano';
        if (wrap) wrap.style.display = show ? '' : 'none';
        if (!show) {
            if (sel) sel.value = 'duas_pericias';
            if (wrapPod) wrapPod.style.display = 'none';
            const inp = q('cadHumanoVersatilPoderNome');
            if (inp) inp.value = '';
            return;
        }
        const modo = (sel && sel.value) || 'duas_pericias';
        if (wrapPod) wrapPod.style.display = modo === 'pericia_poder' ? '' : 'none';
        if (modo !== 'pericia_poder') {
            const inp = q('cadHumanoVersatilPoderNome');
            if (inp) inp.value = '';
        }
    }

    function atualizarUiSuraggel() {
        const wrap = q('cadWrapSuraggel');
        const slug = (q('cadRacaSelect') && q('cadRacaSelect').value) || '';
        const row = getRacaRow();
        const show = isV13Wizard() && slug === 'suraggel' && row && row.escolhe_suraggel_subtipo;
        if (wrap) wrap.style.display = show ? '' : 'none';
        if (!show && q('cadSuraggelSubtipo')) q('cadSuraggelSubtipo').value = '';
    }

    function atualizarUiArcanistaCaminho() {
        const wrap = q('cadWrapArcanistaCaminho');
        const show = isV13Wizard() && classeSlug() === 'arcanista';
        if (wrap) wrap.style.display = show ? '' : 'none';
        if (!show && q('cadArcanistaCaminho')) q('cadArcanistaCaminho').value = '';
    }

    function atualizarUiPasso2() {
        const wrapPv = q('cadWrapPvSugerido');
        if (!isV13Wizard()) {
            if (wrapPv) wrapPv.style.display = 'none';
            ['cadWrapHumanoVersatil', 'cadWrapSuraggel', 'cadWrapArcanistaCaminho', 'cadWrapLefouDeformidade', 'cadWrapQareenEscolhas', 'cadWrapDahllanMagias', 'cadWrapOsteonMemoria', 'cadWrapSereiaMagias', 'cadWrapGolemEscolhas', 'cadWrapKlirenEscolhas', 'cadWrapSilfideMagias'].forEach((id) => {
                const el = q(id);
                if (el) el.style.display = 'none';
            });
            atualizarLabelsRaciaisV13(null);
            if (q('cadHintPvSugerido')) q('cadHintPvSugerido').textContent = '';
            return;
        }
        if (wrapPv) wrapPv.style.display = '';
        const row = getRacaRow();
        atualizarLabelsRaciaisV13(row);
        atualizarUiHumanoVersatil();
        atualizarUiSuraggel();
        atualizarUiArcanistaCaminho();
        if (global.T20EscolhasRaciaisV13) {
            global.T20EscolhasRaciaisV13.atualizarUiCadastro();
        }
        void atualizarPvSugerido(false);
    }

    function validarPasso2Extra() {
        if (!isV13Wizard()) return { ok: true };
        const slug = (q('cadRacaSelect') && q('cadRacaSelect').value) || '';
        const row = getRacaRow();

        if (slug === 'humano') {
            const modo = (q('cadHumanoVersatil') && q('cadHumanoVersatil').value) || 'duas_pericias';
            if (modo === 'pericia_poder') {
                const nom =
                    (q('cadHumanoVersatilPoderNome') && q('cadHumanoVersatilPoderNome').value.trim()) ||
                    '';
                if (!nom) {
                    return {
                        ok: false,
                        msg: 'Humano Versátil: informe o poder geral escolhido (1 perícia + 1 poder).',
                    };
                }
            }
        }

        if (slug === 'suraggel') {
            const sub = (q('cadSuraggelSubtipo') && q('cadSuraggelSubtipo').value) || '';
            if (!sub) {
                return { ok: false, msg: 'Suraggel: escolha o subtipo Aggelus ou Sulfure.' };
            }
        }

        if (classeSlug() === 'arcanista') {
            const cam = (q('cadArcanistaCaminho') && q('cadArcanistaCaminho').value) || '';
            if (!cam) {
                return {
                    ok: false,
                    msg: 'Arcanista v1.3: escolha o caminho Bruxo, Mago ou Feiticeiro (irreversível).',
                };
            }
        }

        if (global.T20EscolhasRaciaisV13) {
            const vEsc = global.T20EscolhasRaciaisV13.validarCadastro();
            if (!vEsc.ok) return vEsc;
        }

        return { ok: true };
    }

    function lerPayloadPasso2() {
        if (!isV13Wizard()) return {};
        const out = {};
        const slug = (q('cadRacaSelect') && q('cadRacaSelect').value) || '';

        if (slug === 'humano') {
            const modo = (q('cadHumanoVersatil') && q('cadHumanoVersatil').value) || 'duas_pericias';
            out.humano_versatil = modo;
            if (modo === 'pericia_poder') {
                const nom =
                    (q('cadHumanoVersatilPoderNome') && q('cadHumanoVersatilPoderNome').value.trim()) ||
                    '';
                out.humano_versatil_poder_slug = nom ? slugifyPoder(nom) : null;
            } else {
                out.humano_versatil_poder_slug = null;
            }
        }

        if (slug === 'suraggel') {
            const sub = (q('cadSuraggelSubtipo') && q('cadSuraggelSubtipo').value) || '';
            out.suraggel_subtipo = sub ? String(sub).trim().toLowerCase() : null;
        }

        if (classeSlug() === 'arcanista') {
            const cam = (q('cadArcanistaCaminho') && q('cadArcanistaCaminho').value) || '';
            out.arcanista_caminho = cam ? String(cam).trim().toLowerCase() : null;
        }

        if (global.T20EscolhasRaciaisV13) {
            Object.assign(out, global.T20EscolhasRaciaisV13.lerPayloadCadastro());
        }

        return out;
    }

    function resumoPasso2() {
        if (!isV13Wizard()) return '';
        const parts = [];
        const slug = (q('cadRacaSelect') && q('cadRacaSelect').value) || '';
        if (slug === 'humano') {
            const modo = (q('cadHumanoVersatil') && q('cadHumanoVersatil').value) || '';
            parts.push(
                modo === 'pericia_poder'
                    ? 'Humano Versátil: 1 perícia + 1 poder'
                    : 'Humano Versátil: 2 perícias'
            );
        }
        if (slug === 'suraggel') {
            const sub = q('cadSuraggelSubtipo') && q('cadSuraggelSubtipo').selectedOptions[0];
            if (sub) parts.push(`Suraggel: ${sub.textContent}`);
        }
        if (classeSlug() === 'arcanista') {
            const cam = q('cadArcanistaCaminho') && q('cadArcanistaCaminho').selectedOptions[0];
            if (cam) parts.push(`Arcanista: ${cam.textContent}`);
        }
        if (global.T20EscolhasRaciaisV13) {
            const extra = global.T20EscolhasRaciaisV13.resumoCadastro();
            if (extra) parts.push(extra);
        }
        return parts.join(' · ');
    }

    async function atualizarPvSugerido(aplicar) {
        const hint = q('cadHintPvSugerido');
        if (!isV13Wizard()) {
            if (hint) hint.textContent = '';
            return null;
        }
        const slug = classeSlug();
        if (!slug) {
            if (hint) hint.textContent = '';
            return null;
        }
        try {
            const _racDelPv = getCadRacialDeltasStep2();
            const payload = {
                classe_slug: slug,
                nivel: Math.max(1, nivelCadastro()),
                con_valor: conValorCadastro(),
                regraVersao: 'v13',
                for_valor: Math.floor(Number(q('cadFor') && q('cadFor').value) || 0) + (_racDelPv.for || 0),
                des_valor: Math.floor(Number(q('cadDes') && q('cadDes').value) || 0) + (_racDelPv.des || 0),
                int_valor: Math.floor(Number(q('cadInt') && q('cadInt').value) || 0) + (_racDelPv.int || 0),
                sab_valor: Math.floor(Number(q('cadSab') && q('cadSab').value) || 0) + (_racDelPv.sab || 0),
                car_valor: Math.floor(Number(q('cadCar') && q('cadCar').value) || 0) + (_racDelPv.car || 0),
            };
            if (slug === 'arcanista') {
                const cam = (q('cadArcanistaCaminho') && q('cadArcanistaCaminho').value) || '';
                if (cam) payload.arcanista_caminho = cam;
            }
            const prev = await new TormentaRegrasService().obterPvPreview(payload);
            if (!prev || !prev.encontrado || prev.pv_max == null) {
                if (hint) hint.textContent = '';
                return null;
            }
            const txt = `PV sugerido (v1.3): ${prev.pv_max}${prev.pm_max != null ? ` · PM: ${prev.pm_max}` : ''}`;
            if (hint) hint.textContent = txt;
            if (aplicar && q('cadPvMax')) {
                q('cadPvMax').value = String(prev.pv_max);
            }
            return prev;
        } catch (_e) {
            if (hint) hint.textContent = '';
            return null;
        }
    }

    function resetPasso2() {
        if (q('cadHumanoVersatil')) q('cadHumanoVersatil').value = 'duas_pericias';
        if (q('cadHumanoVersatilPoderNome')) q('cadHumanoVersatilPoderNome').value = '';
        if (q('cadSuraggelSubtipo')) q('cadSuraggelSubtipo').value = '';
        if (q('cadArcanistaCaminho')) q('cadArcanistaCaminho').value = '';
        if (global.T20EscolhasRaciaisV13) global.T20EscolhasRaciaisV13.resetCadastro();
        if (q('cadHintPvSugerido')) q('cadHintPvSugerido').textContent = '';
    }

    function bindOnce() {
        if (global.__t20DashStep2V13Bound) return;
        global.__t20DashStep2V13Bound = true;
        q('cadHumanoVersatil')?.addEventListener('change', () => {
            if (global.T20DashPericiasV13 && global.T20DashPericiasV13.invalidarPericias) {
                global.T20DashPericiasV13.invalidarPericias();
            }
            atualizarUiHumanoVersatil();
            if (global.T20DashWizardV13 && global.T20DashWizardV13.renderResumo) {
                global.T20DashWizardV13.renderResumo();
            }
        });
        q('cadSuraggelSubtipo')?.addEventListener('change', () => {
            if (cfg && typeof cfg.onRacaAttrChange === 'function') cfg.onRacaAttrChange();
            if (global.T20DashWizardV13 && global.T20DashWizardV13.renderResumo) {
                global.T20DashWizardV13.renderResumo();
            }
        });
        q('cadHumanoVersatilPoderNome')?.addEventListener('input', () => {
            if (global.T20DashWizardV13 && global.T20DashWizardV13.renderResumo) {
                global.T20DashWizardV13.renderResumo();
            }
        });
        q('cadArcanistaCaminho')?.addEventListener('change', () => {
            void atualizarPvSugerido(false);
            if (global.T20DashWizardV13 && global.T20DashWizardV13.renderResumo) {
                global.T20DashWizardV13.renderResumo();
            }
        });
        q('cadBtnAplicarPvSugerido')?.addEventListener('click', () => {
            void atualizarPvSugerido(true);
        });
        q('cadClasseMb')?.addEventListener('change', () => atualizarUiPasso2());
        q('cadNivel')?.addEventListener('change', () => {
            void atualizarPvSugerido(false);
        });
        q('cadCon')?.addEventListener('input', () => {
            void atualizarPvSugerido(false);
        });
    }

    function init(config) {
        cfg = config || {};
        bindOnce();
    }

    global.T20DashStep2V13 = {
        init,
        atualizarUiPasso2,
        validarPasso2Extra,
        lerPayloadPasso2,
        resumoPasso2,
        atualizarPvSugerido,
        resetPasso2,
    };
})(typeof window !== 'undefined' ? window : globalThis);
