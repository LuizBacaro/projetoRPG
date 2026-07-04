/**
 * Traços raciais mecânicos — MB e v1.3 (API `/tormenta/regras/tracos-raciais-preview`).
 */
(function () {
    const regras = () => new TormentaRegrasService();

    function q(id) {
        return document.getElementById(id);
    }

    function getRegraVersaoTracos() {
        if (typeof window.getRegraVersaoAtiva === 'function') {
            return window.getRegraVersaoAtiva();
        }
        return window.T20RegraVersao ? window.T20RegraVersao.DEFAULT_NOVA_FICHA : 'v13';
    }

    function getHumanoVersatilAtivo() {
        const el = q('f_humano_versatil');
        const v = el && el.value ? String(el.value).trim() : '';
        return v || 'duas_pericias';
    }

    function readResSpan(id) {
        const el = q(id);
        if (!el) return 0;
        const v = el.getAttribute('data-valor');
        if (v != null && v !== '') return Number(v) || 0;
        const t = String(el.textContent || '').replace(/[^\d+-]/g, '');
        return Number(t) || 0;
    }

    function setResSpan(id, val) {
        const el = q(id);
        if (!el) return;
        const n = Number(val) || 0;
        const s = n >= 0 ? `+${n}` : String(n);
        el.textContent = s;
        el.setAttribute('data-valor', String(n));
    }

    function formatTamanhoDeslocLinha(data) {
        if (!data || data.encontrado === false) return '';
        const parts = [];
        if (data.tamanho_label) parts.push(data.tamanho_label);
        if (data.deslocamento_m != null) parts.push(`${data.deslocamento_m} m`);
        if (data.deslocamento_natacao_m) parts.push(`natação ${data.deslocamento_natacao_m} m`);
        if (data.deslocamento_pairar_m) parts.push(`pairar ${data.deslocamento_pairar_m} m`);
        if (data.deslocamento_voo_m) parts.push(`voo ${data.deslocamento_voo_m} m (PM)`);
        if (data.desloc_nao_reduz_armadura_carga) {
            parts.push('desloc. não reduzido por armadura/carga');
        }
        return parts.join(' · ');
    }

    function payloadTamanhoDesloc(data) {
        if (!data || data.encontrado === false) return {};
        return {
            tamanho_racial_ui: data.tamanho_ui || null,
            tamanho_racial_slug: data.tamanho || null,
            deslocamento_racial_m: data.deslocamento_m != null ? data.deslocamento_m : null,
            deslocamento_natacao_m: data.deslocamento_natacao_m || null,
            deslocamento_voo_m: data.deslocamento_voo_m || null,
            deslocamento_pairar_m: data.deslocamento_pairar_m || null,
            desloc_nao_reduz_armadura_carga: Boolean(data.desloc_nao_reduz_armadura_carga),
        };
    }

    function aplicarCamposTamanhoDesloc(data, opts) {
        if (!data) return;
        const modoFicha = !opts || opts.modo !== 'cadastro';
        if (modoFicha && data.deslocamento_m != null && q('f_desl')) {
            q('f_desl').value = String(data.deslocamento_m);
        }
        if (modoFicha && data.tamanho_ui && q('f_tam')) {
            q('f_tam').value = data.tamanho_ui;
        }
        if (modoFicha && typeof atualizarTagsHeader === 'function') {
            atualizarTagsHeader();
        }
        window.__t20TracosRaciaisCadCache = data;
        const hintCad = q('cadRacaTamanhoDeslocHint');
        if (hintCad) {
            const linha = formatTamanhoDeslocLinha(data);
            hintCad.textContent = linha ? `Tamanho/desloc. (v1.3): ${linha}` : '';
        }
    }

    function montarHintMecanicos(data, rv) {
        const parts = [];
        const lv = window.T20RegraVersao && window.T20RegraVersao.isV13(rv) ? 'v1.3' : 'MB';
        const td = formatTamanhoDeslocLinha(data);
        if (td) parts.push(td);
        if (data.ca_bonus) {
            const tamHint = data.tamanho_label || 'raça';
            const sinal = data.ca_bonus > 0 ? '+' : '';
            parts.push(`CA ${sinal}${data.ca_bonus} (${tamHint})`);
        } else if (data.ca_bonus < 0) {
            parts.push(`CA ${data.ca_bonus} (${data.tamanho_label || 'Grande'})`);
        }
        if (data.ataque_bonus) parts.push(`Ataque +${data.ataque_bonus} (tamanho)`);
        if (data.manobra_bonus) {
            const sinal = data.manobra_bonus > 0 ? '+' : '';
            parts.push(`Manobras ${sinal}${data.manobra_bonus}`);
        }
        if (data.armas_aumentadas) parts.push('Armas aumentadas');
        if (data.ca_vs_grande_ou_maior) parts.push(`CA +${data.ca_vs_grande_ou_maior} vs Grande+`);
        if (data.fortitude_bonus) parts.push(`Fort +${data.fortitude_bonus}`);
        if (data.reflexos_bonus) parts.push(`Ref +${data.reflexos_bonus}`);
        if (data.vontade_bonus) parts.push(`Von +${data.vontade_bonus}`);
        if (data.furtividade_bonus) parts.push(`Furtividade +${data.furtividade_bonus}`);
        const pb = data.pericias_bonus || {};
        Object.keys(pb).forEach((k) => parts.push(`${k} +${pb[k]}`));
        if (data.pericias_treinadas_extra) {
            parts.push(`${data.pericias_treinadas_extra} perícia(s) treinada(s) extra`);
        }
        const rd = data.reducao_dano || {};
        Object.keys(rd).forEach((k) => {
            if (rd[k]) parts.push(`RD ${rd[k]} (${k})`);
        });
        const im = data.imunidades_dano || {};
        Object.keys(im).forEach((k) => {
            if (im[k]) parts.push(`Imune ${k}`);
        });
        (data.escolhas_resumo || []).forEach((line) => parts.push(line));
        (data.magias_inatas || []).forEach((m) => parts.push(`Magia inata: ${m}`));
        return parts.length ? `Bônus raciais (${lv}): ${parts.join(' · ')}` : '';
    }

    async function fetchTracosPreview(slug) {
        const rv = getRegraVersaoTracos();
        const opts = { regraVersao: rv };
        if (rv === 'v13' && slug === 'humano') {
            opts.humanoVersatil = getHumanoVersatilAtivo();
        }
        if (rv === 'v13' && window.T20EscolhasRaciaisV13) {
            Object.assign(opts, window.T20EscolhasRaciaisV13.optsPreviewTracos(slug));
        }
        if (rv === 'v13' && slug === 'duende' && window.T20DuendeV13) {
            Object.assign(opts, window.T20DuendeV13.optsPreviewTracos());
        }
        return regras().obterTracosRaciaisPreview(slug, opts);
    }

    async function aplicarTracosRaciais(slug, opts) {
        window.__t20TracosRaciaisCache = null;
        if (!slug || slug === '__livre__') {
            window.__t20TracosRaciaisCadCache = null;
            const hintCad = q('cadRacaTamanhoDeslocHint');
            if (hintCad) hintCad.textContent = '';
            return null;
        }
        const rv = getRegraVersaoTracos();
        try {
            const data = await fetchTracosPreview(slug);
            window.__t20TracosRaciaisCache = data;
            const modoCad = opts && opts.modo === 'cadastro';
            if (rv === 'v13') {
                aplicarCamposTamanhoDesloc(data, { modo: modoCad ? 'cadastro' : 'ficha' });
            }
            if (!modoCad) {
                const fort = readResSpan('fichaFort');
                const ref = readResSpan('fichaReflex');
                const von = readResSpan('fichaVont');
                if (fort === 0 && data.fortitude_bonus) setResSpan('fichaFort', data.fortitude_bonus);
                if (ref === 0 && data.reflexos_bonus) setResSpan('fichaReflex', data.reflexos_bonus);
                if (von === 0 && data.vontade_bonus) setResSpan('fichaVont', data.vontade_bonus);
                if (typeof atualizarResistenciasBreakdownTormenta === 'function') {
                    atualizarResistenciasBreakdownTormenta();
                }
                const hint = q('t20TracosMecanicosHint');
                if (hint) hint.textContent = montarHintMecanicos(data, rv);
                if (typeof window.t20ValidarPericiasOrcamentoMb === 'function') {
                    window.t20ValidarPericiasOrcamentoMb();
                }
                if (data.pericias_treinadas_escolha && window.T20EscolhasRaciaisV13) {
                    window.T20EscolhasRaciaisV13.aplicarPericiasTreinadas(data.pericias_treinadas_escolha);
                }
            }
            return data;
        } catch (e) {
            console.warn('Traços raciais:', e);
            return null;
        }
    }

    async function aplicarTracosRaciaisCadastro(slug) {
        if (!window.T20RegraVersao || !window.T20RegraVersao.isV13(getRegraVersaoTracos())) {
            return null;
        }
        return aplicarTracosRaciais(slug, { modo: 'cadastro' });
    }

    function lerPayloadTamanhoDeslocCadastro() {
        const data = window.__t20TracosRaciaisCadCache;
        return payloadTamanhoDesloc(data);
    }

    window.__t20AplicarTracosRaciaisMecanicos = aplicarTracosRaciais;
    window.T20TracosRaciaisV13 = {
        aplicarTracosRaciaisCadastro,
        lerPayloadTamanhoDeslocCadastro,
        payloadTamanhoDesloc,
        formatTamanhoDeslocLinha,
    };

    document.addEventListener('DOMContentLoaded', () => {
        const sel = q('f_raca_select');
        if (sel && !sel.dataset.tracosMecBound) {
            sel.dataset.tracosMecBound = '1';
            sel.addEventListener('change', () => {
                aplicarTracosRaciais(sel.value);
            });
        }
        const hv = q('f_humano_versatil');
        if (hv && !hv.dataset.tracosMecBound) {
            hv.dataset.tracosMecBound = '1';
            hv.addEventListener('change', () => {
                const slug = (q('f_raca_select') && q('f_raca_select').value) || '';
                if (slug === 'humano') aplicarTracosRaciais(slug);
            });
        }
    });
})();
