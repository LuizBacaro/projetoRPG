/**
 * RF-T13 — secção Ameaça (NPC/monstro): metadados + bloco estilo livro.
 */
(function (global) {
    'use strict';

    const PAPEIS = ['solo', 'lacaio', 'especial'];

    function q(id) {
        return document.getElementById(id);
    }

    function tipoAtual() {
        const el = q('f_tipo');
        return el ? String(el.value || 'jogador').toLowerCase() : 'jogador';
    }

    function personagemId() {
        const el = q('fichaId');
        const n = el ? Number(el.value) : NaN;
        return Number.isFinite(n) && n > 0 ? n : null;
    }

    function isAmeacaTipo(t) {
        const x = String(t || '').toLowerCase();
        return x === 'npc' || x === 'monstro';
    }

    function ameacaMinima() {
        return {
            nd: 1,
            papel_combate: 'solo',
            tipo_criatura: 'Humanoide',
            percepcao: 0,
            sentidos: '',
            atributos_nulos: [],
            pericias_fortes: [],
            pericias_fracas_bonus: 0,
            acoes: {
                corpo_a_corpo: [],
                distancia: [],
                especiais: [],
                magias: [],
            },
            equipamento_tesouro: '',
            texto_override: null,
        };
    }

    function lerCamposForm() {
        const ndEl = q('f_ameaca_nd');
        const papelEl = q('f_ameaca_papel');
        const tipoEl = q('f_ameaca_tipo_criatura');
        const percEl = q('f_ameaca_percepcao');
        const sentEl = q('f_ameaca_sentidos');
        const equipEl = q('f_ameaca_equip');
        const blocoEl = q('f_ameaca_bloco');
        const fonteEl = q('f_ameaca_fonte');
        const overrideAtivo = fonteEl && fonteEl.value === 'override';

        let nd = 1;
        if (ndEl && String(ndEl.value).trim() !== '') {
            const n = Number(ndEl.value);
            if (Number.isFinite(n)) nd = Math.max(0, Math.floor(n));
        }

        let papel = 'solo';
        if (papelEl) {
            const p = String(papelEl.value || '').toLowerCase();
            if (PAPEIS.includes(p)) papel = p;
        }

        let percepcao = 0;
        if (percEl && String(percEl.value).trim() !== '') {
            const n = Number(percEl.value);
            if (Number.isFinite(n)) percepcao = n;
        }

        const prev = global.__t20AmeacaCache && typeof global.__t20AmeacaCache === 'object'
            ? global.__t20AmeacaCache
            : ameacaMinima();

        const out = {
            ...prev,
            nd,
            papel_combate: papel,
            tipo_criatura: tipoEl ? String(tipoEl.value || '').trim() || 'Humanoide' : 'Humanoide',
            percepcao,
            sentidos: sentEl ? String(sentEl.value || '').trim() : '',
            equipamento_tesouro: equipEl ? String(equipEl.value || '').trim() : '',
            texto_override: overrideAtivo && blocoEl ? String(blocoEl.value || '').trim() || null : null,
        };
        if (!out.acoes || typeof out.acoes !== 'object') {
            out.acoes = ameacaMinima().acoes;
        }
        return out;
    }

    function aplicarCamposForm(am) {
        const a = am && typeof am === 'object' ? am : ameacaMinima();
        global.__t20AmeacaCache = { ...ameacaMinima(), ...a };
        if (q('f_ameaca_nd')) q('f_ameaca_nd').value = a.nd != null ? String(a.nd) : '1';
        if (q('f_ameaca_papel')) {
            const p = String(a.papel_combate || 'solo').toLowerCase();
            q('f_ameaca_papel').value = PAPEIS.includes(p) ? p : 'solo';
        }
        if (q('f_ameaca_tipo_criatura')) {
            q('f_ameaca_tipo_criatura').value = a.tipo_criatura || 'Humanoide';
        }
        if (q('f_ameaca_percepcao')) {
            q('f_ameaca_percepcao').value =
                a.percepcao != null && a.percepcao !== '' ? String(a.percepcao) : '0';
        }
        if (q('f_ameaca_sentidos')) q('f_ameaca_sentidos').value = a.sentidos || '';
        if (q('f_ameaca_equip')) {
            q('f_ameaca_equip').value = a.equipamento_tesouro || '';
        }
        if (q('f_ameaca_fonte')) {
            q('f_ameaca_fonte').value = a.texto_override ? 'override' : 'gerado';
        }
        if (q('f_ameaca_bloco') && a.texto_override) {
            q('f_ameaca_bloco').value = String(a.texto_override);
        }
    }

    function atualizarUiPorTipo() {
        const t = tipoAtual();
        const secao = q('t20SecaoAmeaca');
        const wrapConv = q('t20AmeacaConverterWrap');
        if (secao) secao.hidden = !isAmeacaTipo(t);
        if (wrapConv) {
            const isMestre =
                typeof AuthService !== 'undefined' &&
                typeof AuthService.isMestre === 'function' &&
                AuthService.isMestre();
            wrapConv.hidden = !(t === 'jogador' && isMestre);
        }
        const badge = q('t20AmeacaFonteBadge');
        if (badge && q('f_ameaca_fonte')) {
            const f = q('f_ameaca_fonte').value;
            badge.textContent = f === 'override' ? 'Texto manual' : 'Gerado pelo motor';
            badge.classList.toggle('t20-ameaca-fonte-badge--override', f === 'override');
        }
    }

    function aplicarPayload(j) {
        if (!j || typeof j !== 'object') {
            aplicarCamposForm(ameacaMinima());
            atualizarUiPorTipo();
            return;
        }
        let am = j.ameaca && typeof j.ameaca === 'object' ? { ...j.ameaca } : null;
        if (!am) {
            am = ameacaMinima();
            if (j.nd != null) am.nd = j.nd;
            if (j.tipo_criatura) am.tipo_criatura = String(j.tipo_criatura);
        }
        aplicarCamposForm(am);
        atualizarUiPorTipo();
        const pid = personagemId();
        if (pid && isAmeacaTipo(tipoAtual()) && !am.texto_override) {
            void carregarBloco();
        }
    }

    function lerAmeacaParaFichaJson() {
        if (!isAmeacaTipo(tipoAtual())) {
            return undefined;
        }
        const am = lerCamposForm();
        global.__t20AmeacaCache = am;
        return am;
    }

    async function carregarBloco() {
        const pid = personagemId();
        const ta = q('f_ameaca_bloco');
        if (!pid || !ta) return null;
        try {
            const svc = new TormentaPersonagemService();
            const body = await svc.obterBlocoAmeaca(pid);
            ta.value = body.texto || '';
            if (q('f_ameaca_fonte')) q('f_ameaca_fonte').value = body.fonte || 'gerado';
            if (q('f_ameaca_nd') && body.nd != null) q('f_ameaca_nd').value = String(body.nd);
            if (q('f_ameaca_papel') && body.papel_combate) {
                const p = String(body.papel_combate).toLowerCase();
                if (PAPEIS.includes(p)) q('f_ameaca_papel').value = p;
            }
            atualizarUiPorTipo();
            return body;
        } catch (e) {
            if (typeof Toast !== 'undefined' && Toast.error) {
                Toast.error(e.message || 'Falha ao carregar bloco');
            }
            return null;
        }
    }

    async function regenerar() {
        const pid = personagemId();
        if (!pid) {
            if (typeof Toast !== 'undefined' && Toast.error) {
                Toast.error('Salve a ficha antes de regenerar o bloco.');
            }
            return;
        }
        try {
            const svc = new TormentaPersonagemService();
            const body = await svc.regenerarBlocoAmeaca(pid, { limpar_override: true });
            if (q('f_ameaca_bloco')) q('f_ameaca_bloco').value = body.texto || '';
            if (q('f_ameaca_fonte')) q('f_ameaca_fonte').value = 'gerado';
            if (global.__t20AmeacaCache) global.__t20AmeacaCache.texto_override = null;
            atualizarUiPorTipo();
            if (typeof Toast !== 'undefined' && Toast.success) {
                Toast.success('Bloco regenerado');
            }
        } catch (e) {
            if (typeof Toast !== 'undefined' && Toast.error) {
                Toast.error(e.message || 'Falha ao regenerar');
            }
        }
    }

    async function salvarOverride() {
        const pid = personagemId();
        const ta = q('f_ameaca_bloco');
        if (!pid || !ta) {
            if (typeof Toast !== 'undefined' && Toast.error) {
                Toast.error('Salve a ficha antes de gravar o texto.');
            }
            return;
        }
        const am = lerCamposForm();
        am.texto_override = String(ta.value || '').trim() || null;
        if (q('f_ameaca_fonte')) q('f_ameaca_fonte').value = am.texto_override ? 'override' : 'gerado';
        global.__t20AmeacaCache = am;
        try {
            const svc = new TormentaPersonagemService();
            const atual = await svc.obter(pid);
            const fj = { ...(atual.ficha_json || {}), ameaca: am };
            await svc.atualizar(pid, { ficha_json: fj });
            atualizarUiPorTipo();
            if (typeof Toast !== 'undefined' && Toast.success) {
                Toast.success(am.texto_override ? 'Texto manual salvo' : 'Override limpo');
            }
        } catch (e) {
            if (typeof Toast !== 'undefined' && Toast.error) {
                Toast.error(e.message || 'Falha ao salvar override');
            }
        }
    }

    async function copiarBloco() {
        const ta = q('f_ameaca_bloco');
        const txt = ta ? String(ta.value || '') : '';
        if (!txt.trim()) {
            if (typeof Toast !== 'undefined' && Toast.error) Toast.error('Bloco vazio');
            return;
        }
        try {
            await navigator.clipboard.writeText(txt);
            if (typeof Toast !== 'undefined' && Toast.success) Toast.success('Bloco copiado');
        } catch (_) {
            if (ta) {
                ta.focus();
                ta.select();
            }
            if (typeof Toast !== 'undefined' && Toast.info) {
                Toast.info('Selecione o texto e copie (Ctrl+C)');
            }
        }
    }

    async function converter() {
        const pid = personagemId();
        if (!pid) {
            if (typeof Toast !== 'undefined' && Toast.error) {
                Toast.error('Salve a ficha antes de converter.');
            }
            return;
        }
        const tipoSel = q('f_ameaca_converter_tipo');
        const papelSel = q('f_ameaca_converter_papel');
        const tipo = tipoSel ? tipoSel.value : 'monstro';
        const papel = papelSel ? papelSel.value : 'solo';
        try {
            const svc = new TormentaPersonagemService();
            const novo = await svc.converterAmeaca(pid, {
                tipo,
                papel_combate: papel,
            });
            if (typeof Toast !== 'undefined' && Toast.success) {
                Toast.success(`Ameaça criada: ${novo.nome} (#${novo.id})`);
            }
            const url = `/games/tormenta/pages/ficha-personagem.html?id=${novo.id}`;
            global.location.href = url;
        } catch (e) {
            if (typeof Toast !== 'undefined' && Toast.error) {
                Toast.error(e.message || 'Falha ao converter');
            }
        }
    }

    function bind() {
        const tipoEl = q('f_tipo');
        if (tipoEl && !tipoEl.dataset.ameacaBound) {
            tipoEl.dataset.ameacaBound = '1';
            tipoEl.addEventListener('change', () => {
                atualizarUiPorTipo();
                if (isAmeacaTipo(tipoAtual()) && personagemId()) void carregarBloco();
            });
        }
        const map = [
            ['btnAmeacaCopiar', copiarBloco],
            ['btnAmeacaRegenerar', regenerar],
            ['btnAmeacaSalvarOverride', salvarOverride],
            ['btnAmeacaRecarregar', carregarBloco],
            ['btnAmeacaConverter', converter],
        ];
        map.forEach(([id, fn]) => {
            const el = q(id);
            if (el && !el.dataset.ameacaBound) {
                el.dataset.ameacaBound = '1';
                el.addEventListener('click', (ev) => {
                    ev.preventDefault();
                    void fn();
                });
            }
        });
        if (q('f_ameaca_bloco') && !q('f_ameaca_bloco').dataset.ameacaBound) {
            q('f_ameaca_bloco').dataset.ameacaBound = '1';
            q('f_ameaca_bloco').addEventListener('input', () => {
                if (q('f_ameaca_fonte')) q('f_ameaca_fonte').value = 'override';
                atualizarUiPorTipo();
            });
        }
        atualizarUiPorTipo();
    }

    global.T20AmeacaBloco = {
        ameacaMinima,
        aplicarPayload,
        lerAmeacaParaFichaJson,
        atualizarUiPorTipo,
        carregarBloco,
        bind,
    };
})(typeof window !== 'undefined' ? window : globalThis);
