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

    async function aplicarTracosRaciais(slug) {
        window.__t20TracosRaciaisCache = null;
        if (!slug || slug === '__livre__') return null;
        const rv = getRegraVersaoTracos();
        const opts = { regraVersao: rv };
        if (rv === 'v13' && slug === 'humano') {
            opts.humanoVersatil = getHumanoVersatilAtivo();
        }
        try {
            const data = await regras().obterTracosRaciaisPreview(slug, opts);
            window.__t20TracosRaciaisCache = data;
            if (data.deslocamento_m != null && q('f_desl')) {
                q('f_desl').value = String(data.deslocamento_m);
            }
            if (data.tamanho && q('f_tam')) {
                const tam = data.tamanho === 'pequeno' ? 'P' : 'M';
                q('f_tam').value = tam;
            }
            if (typeof atualizarTagsHeader === 'function') atualizarTagsHeader();
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
            if (hint) {
                const parts = [];
                const lv =
                    window.T20RegraVersao && window.T20RegraVersao.isV13(rv) ? 'v1.3' : 'MB';
                if (data.ca_bonus) parts.push(`CA +${data.ca_bonus} (Pequeno)`);
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
                hint.textContent = parts.length
                    ? `Bônus raciais (${lv}): ${parts.join(' · ')}`
                    : '';
            }
            if (typeof window.t20ValidarPericiasOrcamentoMb === 'function') {
                window.t20ValidarPericiasOrcamentoMb();
            }
            return data;
        } catch (e) {
            console.warn('Traços raciais:', e);
            return null;
        }
    }

    window.__t20AplicarTracosRaciaisMecanicos = aplicarTracosRaciais;

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
