/**
 * Utilitários compartilhados — condições de arena (ficha + combate).
 */
const Dnd5eCondicoesUtil = {
    DURACAO_PERMANENTE: -1,

    normalizarLista(raw) {
        const porSlug = {};
        (raw || []).forEach((item) => {
            const c = this.normalizarItem(item);
            if (c && c.slug) porSlug[c.slug] = c;
        });
        return Object.keys(porSlug)
            .sort()
            .map((slug) => porSlug[slug]);
    },

    normalizarItem(raw) {
        if (typeof raw === 'string') {
            return { slug: raw.toLowerCase(), duracao_turnos: this.DURACAO_PERMANENTE };
        }
        if (raw && raw.slug) {
            const d = parseInt(raw.duracao_turnos, 10);
            const out = {
                slug: String(raw.slug).toLowerCase(),
                duracao_turnos: Number.isFinite(d) ? d : this.DURACAO_PERMANENTE,
            };
            if (raw.origem) out.origem = String(raw.origem);
            return out;
        }
        return null;
    },

    nomeCondicao(slug, catalogo) {
        const item = (catalogo || []).find((c) => c.slug === slug);
        return item ? item.nome : slug;
    },

    label(c, catalogo) {
        const nome = this.nomeCondicao(c.slug, catalogo);
        const d = c.duracao_turnos;
        const auto = c.origem === 'hp' ? ' (auto)' : '';
        if (d == null || d === this.DURACAO_PERMANENTE) return `${nome} ∞${auto}`;
        return `${nome} (${d}t)${auto}`;
    },

    slugs(lista) {
        return this.normalizarLista(lista).map((c) => c.slug);
    },
};
