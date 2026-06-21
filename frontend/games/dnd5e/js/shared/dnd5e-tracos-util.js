/**
 * Utilitário D&D 5e — escolha de traços de antecedente (PHB).
 */
const Dnd5eTracosUtil = (() => {
    const CATEGORIAS = [
        { key: 'personalidade', label: 'Traço de personalidade' },
        { key: 'ideais', label: 'Ideal' },
        { key: 'lacos', label: 'Laço' },
        { key: 'fraquezas', label: 'Fraqueza' },
    ];

    function opcoesValidas(opcoes, categoria) {
        return Array.isArray(opcoes?.[categoria]) ? opcoes[categoria] : [];
    }

    function normalizarEscolhidos(raw, opcoes) {
        const out = {};
        CATEGORIAS.forEach(({ key }) => {
            const pool = new Set(opcoesValidas(opcoes, key));
            const lista = Array.isArray(raw?.[key]) ? raw[key] : raw?.[key] ? [raw[key]] : [];
            const escolhido = lista.map((x) => String(x || '').trim()).find((x) => x && pool.has(x));
            out[key] = escolhido ? [escolhido] : [];
        });
        return out;
    }

    function tracosEstaoCompletos(tracos) {
        return CATEGORIAS.every(({ key }) => Array.isArray(tracos?.[key]) && tracos[key].length > 0);
    }

    function validarEscolha(tracos, opcoes) {
        return tracosEstaoCompletos(normalizarEscolhidos(tracos, opcoes));
    }

    function getEscolhidosDoHost(host) {
        if (!host) return null;
        const out = {};
        CATEGORIAS.forEach(({ key }) => {
            const sel = host.querySelector(`select[data-traco-cat="${key}"]`);
            out[key] = sel && sel.value ? [sel.value] : [];
        });
        return out;
    }

    function sortearTracos(opcoes, rng) {
        const rand = rng || Math.random;
        const out = {};
        CATEGORIAS.forEach(({ key }) => {
            const pool = opcoesValidas(opcoes, key);
            if (!pool.length) {
                out[key] = [];
                return;
            }
            const idx = Math.floor(rand() * pool.length);
            out[key] = [pool[idx]];
        });
        return out;
    }

    function formatResumo(tracos) {
        if (!tracos) return '';
        const partes = [];
        CATEGORIAS.forEach(({ key, label }) => {
            const txt = (tracos[key] || []).join(' · ');
            if (txt) partes.push(`${label}: ${txt}`);
        });
        return partes.join(' · ');
    }

    /**
     * @param {object} opts
     * @param {HTMLElement} opts.host
     * @param {HTMLElement} [opts.hint]
     * @param {HTMLElement} [opts.btnSortear]
     * @param {object} opts.opcoes — tracos_opcoes do catálogo
     * @param {object} [opts.selecionados]
     * @param {string} opts.idPrefix
     * @param {function} [opts.onChange]
     */
    function renderEscolha({ host, hint, btnSortear, opcoes, selecionados, idPrefix, onChange }) {
        if (!host) return;
        const escolhidos = normalizarEscolhidos(selecionados, opcoes);
        if (hint) {
            hint.textContent =
                'Escolha um traço de personalidade, ideal, laço e fraqueza (PHB), ou sorteie.';
        }
        const linhas = CATEGORIAS.map(({ key, label }) => {
            const pool = opcoesValidas(opcoes, key);
            const id = `${idPrefix}_traco_${key}`;
            const val = escolhidos[key]?.[0] || '';
            const optsHtml =
                '<option value="">— Selecione —</option>' +
                pool.map((txt) => {
                    const safe = String(txt).replace(/"/g, '&quot;');
                    return `<option value="${safe}">${txt}</option>`;
                }).join('');
            return `
                <div class="dnd5e-traco-row">
                    <label class="ficha-label" for="${id}">${label}</label>
                    <select id="${id}" data-traco-cat="${key}">${optsHtml}</select>
                </div>`;
        });
        host.innerHTML = linhas.join('');
        host.hidden = false;
        host.querySelectorAll('select[data-traco-cat]').forEach((sel) => {
            const cat = sel.dataset.tracoCat;
            if (escolhidos[cat]?.[0]) sel.value = escolhidos[cat][0];
            sel.addEventListener('change', () => {
                if (typeof onChange === 'function') onChange(getEscolhidosDoHost(host));
            });
        });
        if (btnSortear) {
            btnSortear.hidden = false;
            btnSortear.onclick = () => {
                const sorteados = sortearTracos(opcoes);
                CATEGORIAS.forEach(({ key }) => {
                    const sel = host.querySelector(`select[data-traco-cat="${key}"]`);
                    if (sel) sel.value = sorteados[key]?.[0] || '';
                });
                if (typeof onChange === 'function') onChange(getEscolhidosDoHost(host));
            };
        }
    }

    return {
        CATEGORIAS,
        normalizarEscolhidos,
        tracosEstaoCompletos,
        validarEscolha,
        getEscolhidosDoHost,
        sortearTracos,
        formatResumo,
        renderEscolha,
    };
})();
