/**
 * Utilitário D&D 5e — sincronizar ouro inicial da classe (espelha backend).
 */
const Dnd5eOuroClasseUtil = (() => {
    function formatRollHint(roll) {
        if (!roll || roll.total == null) return '';
        const dados = Array.isArray(roll.dados) && roll.dados.length ? roll.dados.join(' + ') : '';
        const mult = Number(roll.multiplicador) > 1 ? ` × ${roll.multiplicador}` : '';
        const base = dados ? `${dados}${mult}` : String(roll.total);
        const formula = roll.formula ? `${roll.formula}: ` : '';
        return `${formula}${base} = ${roll.total} gp`;
    }

    /**
     * @param {object} params
     * @param {object} params.inventarioState
     * @param {string|null} params.slugAtual
     * @param {string|null} params.slugAplicado
     * @param {number} params.ouroAplicado
     * @param {object|null} params.roll — resposta de rolar-ouro-classe
     * @param {boolean} [params.forcar]
     */
    function sincronizarOuro({
        inventarioState,
        slugAtual,
        slugAplicado,
        ouroAplicado,
        roll,
        forcar = false,
    }) {
        const atual = slugAtual ? String(slugAtual).trim().toLowerCase() : null;
        const aplicado = slugAplicado ? String(slugAplicado).trim().toLowerCase() : null;
        const ouroPrev = Number(ouroAplicado) || 0;

        if (
            !forcar &&
            atual === aplicado &&
            ouroPrev > 0 &&
            roll == null
        ) {
            return {
                changed: false,
                inventarioState,
                meta: {
                    classe_ouro_slug: aplicado,
                    ouro_classe_aplicado: ouroPrev,
                    ouro_classe_rolagem: [],
                    ouro_classe_formula: '',
                },
            };
        }

        const state = {
            ...(inventarioState || {}),
            equipamentos: [...((inventarioState && inventarioState.equipamentos) || [])],
            consumiveis: [...((inventarioState && inventarioState.consumiveis) || [])],
            ouro_po: Number(inventarioState?.ouro_po) || 0,
        };

        state.ouro_po = Math.max(0, state.ouro_po - ouroPrev);

        const meta = {
            classe_ouro_slug: atual,
            ouro_classe_aplicado: 0,
            ouro_classe_rolagem: [],
            ouro_classe_formula: roll?.formula || '',
        };

        if (atual && roll) {
            meta.ouro_classe_aplicado = Number(roll.total) || 0;
            meta.ouro_classe_rolagem = [...(roll.dados || [])];
            meta.ouro_classe_formula = String(roll.formula || '');
            state.ouro_po += meta.ouro_classe_aplicado;
        }

        return { changed: true, inventarioState: state, meta };
    }

    return {
        formatRollHint,
        sincronizarOuro,
    };
})();
