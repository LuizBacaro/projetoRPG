/**
 * Utilitário D&D 5e — escolha de idiomas do antecedente.
 */
const Dnd5eIdiomasUtil = (() => {
    const PLACEHOLDER_RE = /^idioma_extra_\d+$/i;

    function normalizarEscolhidos(raw, catalogo) {
        const validos = new Set((catalogo || []).map((i) => i.slug));
        const out = [];
        const seen = new Set();
        (raw || []).forEach((item) => {
            const slug = String(item || '').trim().toLowerCase();
            if (!slug || PLACEHOLDER_RE.test(slug) || !validos.has(slug) || seen.has(slug)) return;
            out.push(slug);
            seen.add(slug);
        });
        return out;
    }

    function nomeIdioma(slug, catalogo) {
        const row = (catalogo || []).find((i) => i.slug === slug);
        return row ? row.nome : slug;
    }

    function formatLista(slugs, catalogo) {
        return normalizarEscolhidos(slugs, catalogo)
            .map((s) => nomeIdioma(s, catalogo))
            .join(', ');
    }

    function validarEscolha(slugs, qtd, catalogo) {
        const q = Math.max(0, Number(qtd) || 0);
        const escolhidos = normalizarEscolhidos(slugs, catalogo);
        if (q === 0) return escolhidos.length === 0;
        return escolhidos.length === q;
    }

    function getEscolhidosDoHost(host, idPrefix) {
        if (!host) return [];
        return Array.from(host.querySelectorAll(`select[data-${idPrefix}-idx]`))
            .map((sel) => sel.value)
            .filter(Boolean);
    }

    /**
     * @param {object} opts
     * @param {HTMLElement} opts.host
     * @param {HTMLElement} [opts.hint]
     * @param {Array} opts.catalogo
     * @param {number} opts.qtd
     * @param {string[]} [opts.selecionados]
     * @param {string} opts.idPrefix
     * @param {function} [opts.onChange]
     */
    function renderEscolha({ host, hint, catalogo, qtd, selecionados, idPrefix, onChange }) {
        if (!host) return;
        const q = Math.max(0, Number(qtd) || 0);
        if (hint) {
            if (!q) {
                hint.textContent = 'Este antecedente não concede idiomas extras.';
            } else {
                hint.textContent = `Escolha ${q} idioma(s) extra(s).`;
            }
        }
        if (!q) {
            host.innerHTML = '';
            host.hidden = true;
            return;
        }
        host.hidden = false;
        const escolhidos = normalizarEscolhidos(selecionados, catalogo);
        const opts =
            '<option value="">— Selecione —</option>' +
            (catalogo || [])
                .map((i) => `<option value="${i.slug}">${i.nome}</option>`)
                .join('');
        const linhas = [];
        for (let i = 0; i < q; i += 1) {
            const id = `${idPrefix}_idioma_${i + 1}`;
            const val = escolhidos[i] || '';
            linhas.push(`
                <div class="dnd5e-idioma-row">
                    <label class="ficha-label" for="${id}">Idioma ${i + 1}</label>
                    <select id="${id}" data-${idPrefix}-idx="${i}">${opts}</select>
                </div>`);
        }
        host.innerHTML = linhas.join('');
        host.querySelectorAll(`select[data-${idPrefix}-idx]`).forEach((sel, idx) => {
            if (escolhidos[idx]) sel.value = escolhidos[idx];
            sel.addEventListener('change', () => {
                const picks = getEscolhidosDoHost(host, idPrefix);
                const dup = picks.filter((v, i, arr) => arr.indexOf(v) !== i);
                if (dup.length) {
                    sel.value = '';
                    Toast?.error?.('Cada idioma deve ser diferente.');
                }
                if (typeof onChange === 'function') onChange(getEscolhidosDoHost(host, idPrefix));
            });
        });
    }

    return {
        normalizarEscolhidos,
        nomeIdioma,
        formatLista,
        validarEscolha,
        getEscolhidosDoHost,
        renderEscolha,
    };
})();
